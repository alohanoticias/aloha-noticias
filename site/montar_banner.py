"""Monta site/assets/img/banner.jpg (1920x300) com painéis inclinados a partir de site/banner.json.
Roda no GitHub (workflow 'Montar banner'): baixa as imagens, ignora as que falharem."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
from montar_capa import baixar, recorte

RAIZ = Path(__file__).resolve().parent
W, H, INCL, DIV = 1920, 300, 46, 8
fotos = json.loads((RAIZ / "banner.json").read_text(encoding="utf-8"))["fotos"]
ok = []
for f in fotos:
    try:
        ok.append((baixar(f["url"]), f.get("foco", [0.5, 0.5])))
        print("ok", f["url"][:90])
    except Exception as e:
        print("FALHOU", f["url"][:90], e)
if len(ok) < 4:
    sys.exit("poucas imagens carregaram; banner não alterado")
n = len(ok)
lw = W / n
tela = Image.new("RGB", (W, H), (10, 10, 10))
for i, (img, foco) in enumerate(ok):
    x0, x1 = round(i * lw), round((i + 1) * lw)
    pw = x1 - x0 + INCL + 2 * DIV
    painel = recorte(img, pw, H, foco)
    m = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(m)
    s = 2
    d.polygon([((x0 + INCL) * s, 0), ((x1 + INCL - DIV) * s, 0), ((x1 - DIV) * s, H * s), (x0 * s, H * s)], fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    cam = Image.new("RGB", (W, H), (10, 10, 10))
    cam.paste(painel, (x0 - 0, 0))
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
