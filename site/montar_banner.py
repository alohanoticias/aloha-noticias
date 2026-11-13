"""Monta site/assets/img/banner.jpg (1920x300) com painéis inclinados a partir de site/banner.json.
Roda no GitHub (workflow 'Montar banner'): baixa as imagens, ignora as que falharem."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
from montar_capa import baixar, recorte
import urllib.parse, urllib.request


def cena_steam(appid, captura=None):
    """Cena oficial do jogo na Steam, sem texto: arte 'hero' (sem logo) ou, se faltar, a 1ª captura."""
    for u in () if captura is not None else (f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_hero.jpg",
              f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero.jpg"):
        try:
            return baixar(u), u
        except Exception:
            pass
    req = urllib.request.Request(f"https://store.steampowered.com/api/appdetails?appids={appid}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=40))[str(appid)]["data"]
    u = d["screenshots"][captura or 0]["path_full"]
    return baixar(u), u


def arte_wikipedia(titulo, lang="en"):
    """Capa oficial (pôster do filme / capa do jogo) do artigo da Wikipédia."""
    q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "pageimages", "piprop": "original",
                                "pilicense": "any", "redirects": 1, "titles": titulo})
    req = urllib.request.Request(f"https://{lang}.wikipedia.org/w/api.php?{q}",
                                 headers={"User-Agent": "AlohaNoticiasBot/1.0 (contato@alohanoticias.com)"})
    pags = json.load(urllib.request.urlopen(req, timeout=40))["query"]["pages"]
    for p in pags.values():
        if "original" in p:
            return p["original"]["source"]
    raise RuntimeError("sem imagem no artigo " + titulo)

RAIZ = Path(__file__).resolve().parent
W, H, INCL, DIV = 1920, 300, 46, 8
fotos = json.loads((RAIZ / "banner.json").read_text(encoding="utf-8"))["fotos"]
ok = []
for f in fotos:
    try:
        if f.get("steam"):
            img, url = cena_steam(f["steam"], f.get("captura"))
        elif f.get("arquivo"):
            url = str(RAIZ / f["arquivo"]); img = baixar(url)
        else:
            url = arte_wikipedia(f["wiki"]) if f.get("wiki") else f["url"]
            try:
                img = baixar(url)
            except Exception:
                if not f.get("url_alt"):
                    raise
                url = f["url_alt"]; img = baixar(url)
        ok.append((img, f.get("foco", [0.5, 0.42]), f.get("zoom", 1.0)))
        print("ok", f.get("wiki", ""), url[:110], img.size)
    except Exception as e:
        print("FALHOU", f["url"][:90], e)
if len(ok) < 4:
    sys.exit("poucas imagens carregaram; banner não alterado")
n = len(ok)
lw = W / n
tela = Image.new("RGB", (W, H), (10, 10, 10))
# começa uma faixa antes (só a pontinha aparece no canto esquerdo), para a divisa inclinada ficar visível
for i, (img, foco, zoom) in [(-1, ok[-1])] + list(enumerate(ok)):
    x0, x1 = round(i * lw), round((i + 1) * lw)
    pw = x1 - x0 + INCL + 2 * DIV
    painel = recorte(img, pw, H, foco, zoom)
    m = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(m)
    s = 2
    d.polygon([((x0 + INCL) * s, 0), ((x1 + INCL - DIV) * s, 0), ((x1 - DIV) * s, H * s), (x0 * s, H * s)], fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    cam = Image.new("RGB", (W, H), (10, 10, 10))
    cam.paste(painel, (x0, 0))
    tela = Image.composite(cam, tela, m)
# escurece a esquerda (onde fica a logo)
mask = Image.new("L", (W, H), 0)
px = mask.load()
for x in range(900):
    v = int(255 * 0.82 * (1 - x / 900))
    for y in range(H):
        px[x, y] = v
tela = Image.composite(Image.new("RGB", (W, H), (10, 10, 10)), tela, mask)
tela.save(RAIZ / "assets/img/banner.jpg", quality=88, optimize=True)
print("banner salvo", tela.size)
