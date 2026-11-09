"""Baixa imagens e gera miniaturas para revisão visual (roda no GitHub: workflow 'Previas de imagens').
Uso: python3 site/previas.py urls <url...>   -> site/candidatas/previas/NN.jpg (+ lista.txt)
     python3 site/previas.py revisao         -> folhas de contato por artigo em site/candidatas/revisao/"""
import glob, io, json, re, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
RAIZ = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def baixar(u):
    h = {"User-Agent": ("AlohaNoticiasBot/1.0 (alohanoticias@gmail.com)" if "wikimedia.org" in u else UA), "Accept": "image/*,*/*;q=0.8"}
    if not u.startswith("http"):
        return Image.open(RAIZ / "publico" / u).convert("RGB")
    with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=40) as r:
        return Image.open(io.BytesIO(r.read(25_000_000))).convert("RGB")
def mini(im, w, h):
    im = im.copy(); im.thumbnail((w, h)); fundo = Image.new("RGB", (w, h), (30, 30, 30)); fundo.paste(im, ((w - im.width) // 2, (h - im.height) // 2)); return fundo, im.size
try: FONTE = ImageFont.load_default(size=15)
except Exception: FONTE = ImageFont.load_default()
modo = sys.argv[1] if len(sys.argv) > 1 else ""
if modo == "urls":
    out = RAIZ / "site/candidatas/previas"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*"): f.unlink()
    linhas = []
    for i, u in enumerate(sys.argv[2:], 1):
        try:
            im = baixar(u); m, _ = mini(im, 800, 450); m.save(out / f"{i:02d}.jpg", quality=80)
            linhas.append(f"{i:02d} {im.width}x{im.height} {u}")
        except Exception as e:
            linhas.append(f"{i:02d} ERRO {e} {u}")
    (out / "lista.txt").write_text("\n".join(linhas) + "\n")
elif modo == "revisao":
    out = RAIZ / "site/candidatas/revisao"; out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*"): f.unlink()
    artigos = []
    for tipo, pad in [("publicado", "site/conteudo/materias.json"), ("rascunho", "rascunhos/*.json"), ("agendado", "agendados/*.json")]:
        for arq in glob.glob(str(RAIZ / pad)):
            d = json.loads(Path(arq).read_text(encoding="utf-8"))
            for a in (d if isinstance(d, list) else [d]):
                imgs = [("capa", a["imagem"]["url"], a["imagem"].get("alt", ""))]
                for p in a["corpo"]:
                    m = re.match(r"!img (\S+)\|([^|]*)\|", p)
                    if m: imgs.append(("corpo", m.group(1), m.group(2)))
                artigos.append((tipo, a["slug"], a["titulo"], imgs))
    W, H, LH = 360, 203, 40
    lote, n = [], 0
    def salvar(lote, n):
        if not lote: return
        altura = sum(LH + H + 6 for _ in lote); folha = Image.new("RGB", (4 * W + 30, altura), (20, 20, 20)); d = ImageDraw.Draw(folha); y = 0
        for tipo, slug, tit, cels in lote:
            d.text((6, y + 4), f"[{tipo}] {tit[:120]}", fill=(255, 255, 255), font=FONTE)
            d.text((6, y + 22), slug[:60], fill=(150, 150, 150), font=FONTE)
            for i, (img, leg) in enumerate(cels[:4]):
                folha.paste(img, (i * (W + 10), y + LH)); d.text((i * (W + 10) + 4, y + LH + 4), leg[:48], fill=(255, 220, 0), font=FONTE)
            y += LH + H + 6
        folha.save(out / f"folha_{n:02d}.jpg", quality=82)
    for tipo, slug, tit, imgs in artigos:
        cels = []
        for k, (onde, u, alt) in enumerate(imgs):
            try:
                im, _ = mini(baixar(u), W, H)
            except Exception as e:
                im = Image.new("RGB", (W, H), (90, 0, 0)); ImageDraw.Draw(im).text((8, 8), "ERRO " + str(e)[:40], fill=(255, 255, 255))
            cels.append((im, f"{onde}: {alt}"))
        lote.append((tipo, slug, tit, cels))
        if len(lote) == 5: salvar(lote, n); n += 1; lote = []
    salvar(lote, n)
    (out / "indice.txt").write_text("\n".join(f"{t} {s} ({len(i)-1} fotos no corpo)" for t, s, _, i in artigos) + "\n")
