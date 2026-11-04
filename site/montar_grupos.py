"""Junta imagens de vários filmes de uma mesma seção, lado a lado, em 1920x1080.
Lê site/grupos.json: [{"saida": "assets/img/estreias/x.jpg", "itens": [{"src": "URL ou caminho dentro de site/", "foco": [0.5, 0.5]}]}]
Cada imagem ocupa um painel com divisória branca. Pôsteres verticais aparecem inteiros sobre um fundo desfocado;
imagens horizontais são recortadas (ou inteiras com "modo": "conter", bom para logotipos) para preencher o painel (use "foco" para escolher o centro do recorte).
Uso: python3 site/montar_grupos.py  (roda no GitHub, pois baixa imagens externas)"""
import io, json, urllib.request
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
RAIZ = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
W, H, DIV = 1920, 1080, 10

def abrir(src):
    if src.startswith("http"):
        with urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=40) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGB")
    return Image.open(RAIZ / src).convert("RGB")

def cobrir(im, w, h, foco=(0.5, 0.5)):
    esc = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * esc) + 1, round(im.height * esc) + 1), Image.LANCZOS)
    x = min(max(round(im.width * foco[0] - w / 2), 0), im.width - w)
    y = min(max(round(im.height * foco[1] - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))

def painel(im, w, h, foco, conter=False):
    if im.width / im.height >= 1.2 and not conter:            # horizontal: preenche o painel
        return cobrir(im, w, h, foco)
    fundo = cobrir(im, w, h, (0.5, 0.5)).filter(ImageFilter.GaussianBlur(28))
    fundo = ImageEnhance.Brightness(fundo).enhance(0.45)
    esc = min(w * 0.94 / im.width, h * 0.94 / im.height)
    p = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    fundo.paste(p, ((w - p.width) // 2, (h - p.height) // 2))
    return fundo

for g in json.loads((RAIZ / "grupos.json").read_text(encoding="utf-8")):
    itens = g["itens"]; n = len(itens)
    tela = Image.new("RGB", (W, H), (244, 244, 244))
    larg = (W - DIV * (n - 1)) // n
    x = 0
    for i, it in enumerate(itens):
        w = larg if i < n - 1 else W - x
        tela.paste(painel(abrir(it["src"]), w, H, tuple(it.get("foco", (0.5, 0.5))), it.get("modo") == "conter"), (x, 0))
        x += w + DIV
    destino = RAIZ / g["saida"]; destino.parent.mkdir(parents=True, exist_ok=True)
    tela.save(destino, quality=90, optimize=True)
    print("ok", g["saida"], n)
