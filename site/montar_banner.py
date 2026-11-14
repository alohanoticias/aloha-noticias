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
    for u in () if captura is not None else (f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_hero_2x.jpg",
              f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_hero_2x.jpg",
              f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/library_hero.jpg",
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

try:  # aprimorador de imagem (Real-ESRGAN 4x), se o workflow instalou
    import numpy as np, torch
    from spandrel import ModelLoader
    torch.set_grad_enabled(False)
    import os; torch.set_num_threads(os.cpu_count() or 4)
    _modelo = ModelLoader().load_from_file(str(RAIZ.parent / "ia_modelos/RealESRGAN_x4plus.pth")).eval()

    def ampliar(img, tile=256, sobra=16):
        a = np.asarray(img, dtype=np.float32) / 255.0
        h, w, _ = a.shape
        out = np.zeros((h * 4, w * 4, 3), dtype=np.float32)
        for y in range(0, h, tile):
            for x in range(0, w, tile):
                y0, x0 = max(y - sobra, 0), max(x - sobra, 0)
                y1, x1 = min(y + tile + sobra, h), min(x + tile + sobra, w)
                t = torch.from_numpy(a[y0:y1, x0:x1].transpose(2, 0, 1).copy()).unsqueeze(0)
                r = _modelo(t)[0].clamp(0, 1).numpy().transpose(1, 2, 0)
                yy, xx = (y - y0) * 4, (x - x0) * 4
                hh, ww = min(tile, h - y) * 4, min(tile, w - x) * 4
                out[y * 4:y * 4 + hh, x * 4:x * 4 + ww] = r[yy:yy + hh, xx:xx + ww]
        return Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    print("IA de qualidade: ligada", flush=True)
except Exception as e:
    ampliar = None
    print("IA de qualidade: indisponível", e, flush=True)


def painel_qualidade(img, w, h, foco, zoom):
    """Recorta a região exata na resolução original, reconstrói em 4x com IA (tira serrilhado, borrão e
    quadriculado de JPEG) e reduz ao tamanho final: cada pixel do banner sai de 16 pixels reconstruídos."""
    esc = max(w / img.width, h / img.height) * zoom
    cw, ch = min(img.width, round(w / esc)), min(img.height, round(h / esc))
    x = round((img.width - cw) * foco[0]); y = round((img.height - ch) * foco[1])
    reg = img.crop((x, y, x + cw, y + ch)).convert("RGB")
    if ampliar is not None:
        try:
            if max(reg.size) > 680:  # região grande: reduz antes; a IA reconstrói o detalhe em 4x (sobra qualidade para o painel)
                e = 680 / max(reg.size); reg = reg.resize((round(reg.width * e), round(reg.height * e)), Image.LANCZOS)
            reg = ampliar(reg)
        except Exception as e:
            print("IA falhou neste painel, segue sem:", e)
    import time; print("   painel", time.strftime("%H:%M:%S"),, (cw, ch), "->", reg.size, "->", (w, h), flush=True)
    return reg.resize((w, h), Image.LANCZOS)


ESC = 2                       # o dobro da resolução: fica nítido em telas grandes e de celular
W, H, INCL, DIV = 1920 * ESC, 300 * ESC, 46 * ESC, 8 * ESC
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
                try:
                    import io
                    from PIL import Image as _I
                    rq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                                                             "Referer": url.split("/wp-content")[0] + "/"})
                    img = _I.open(io.BytesIO(urllib.request.urlopen(rq, timeout=40).read())).convert("RGB")
                    ok.append((img, f.get("foco", [0.5, 0.42]), f.get("zoom", 1.0)))
                    print("ok (navegador)", url[:110], img.size)
                    continue
                except Exception as e2:
                    print("falhou como navegador", e2)
                if not f.get("url_alt"):
                    raise
                url = f["url_alt"]; img = baixar(url)
        ok.append((img, f.get("foco", [0.5, 0.42]), f.get("zoom", 1.0)))
        print("ok", f.get("wiki", ""), url[:110], img.size)
    except Exception as e:
        print("FALHOU", f.get("nome") or f.get("url", "")[:90], e)
if len(ok) < 4:
    sys.exit("poucas imagens carregaram; banner não alterado")
n = len(ok)
lw = W / n
tela = Image.new("RGB", (W, H), (10, 10, 10))
# começa uma faixa antes (só a pontinha aparece no canto esquerdo), para a divisa inclinada ficar visível
for i, (img, foco, zoom) in [(-1, ok[-1])] + list(enumerate(ok)):
    x0, x1 = round(i * lw), round((i + 1) * lw)
    pw = x1 - x0 + INCL + 2 * DIV
    painel = painel_qualidade(img, pw, H, foco, zoom)
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
for x in range(900 * ESC):
    v = int(255 * 0.82 * (1 - x / (900 * ESC)))
    for y in range(H):
        px[x, y] = v
tela = Image.composite(Image.new("RGB", (W, H), (10, 10, 10)), tela, mask)
tela.save(RAIZ / "assets/img/banner.jpg", quality=93, subsampling=0, optimize=True, progressive=True)
import re, time
css = RAIZ / "assets/css/antigo.css"
css.write_text(re.sub(r"banner\.jpg\?v=[\w-]+", "banner.jpg?v=" + time.strftime("%Y%m%d%H%M"), css.read_text(encoding="utf-8")), encoding="utf-8")
print("banner salvo", tela.size)
