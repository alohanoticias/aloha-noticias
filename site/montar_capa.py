"""Monta capas em colagem a partir de fotos livres (Unsplash, Pexels, Wikimedia).
Lê site/capas_fotos/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1200x675).
Formato do .json:
  {"layout": "tres" | "dois" | "um",
   "fotos": [{"url": "...", "foco": [0.5, 0.5]}, ...]}
Só monta o que ainda não existe (apague o .jpg para refazer). Uso: python3 site/montar_capa.py"""
import io, json, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

RAIZ = Path(__file__).resolve().parent.parent
L, A = 1200, 675
UA = {"User-Agent": "Mozilla/5.0 (compatible; AlohaCapas/1.0; +https://alohanoticias.com)"}
LAYOUTS = {
    "tres": [[(0, 0), (660, 0), (525, 675), (0, 675)],
             [(678, 0), (1200, 0), (1200, 322), (618, 322)],
             [(600, 340), (1200, 340), (1200, 675), (543, 675)]],
    "dois": [[(0, 0), (700, 0), (560, 675), (0, 675)],
             [(718, 0), (1200, 0), (1200, 675), (578, 675)]],
    "um": [[(0, 0), (1200, 0), (1200, 675), (0, 675)]],
}


def baixar(url):
    if url.startswith("/"):
        return Image.open(url).convert("RGB")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def recorte(img, w, h, foco):
    esc = max(w / img.width, h / img.height)
    img = img.resize((max(w, round(img.width * esc)), max(h, round(img.height * esc))), Image.LANCZOS)
    x = round((img.width - w) * foco[0]); y = round((img.height - h) * foco[1])
    return img.crop((x, y, x + w, y + h))


def montar(spec):
    poligonos = LAYOUTS[spec["layout"]]
    fotos = spec["fotos"]
    if len(fotos) != len(poligonos):
        raise SystemExit(f"layout {spec['layout']} pede {len(poligonos)} fotos")
    tela = Image.new("RGB", (L, A), "white")
    for pol, f in zip(poligonos, fotos):
        xs, ys = [p[0] for p in pol], [p[1] for p in pol]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        img = recorte(baixar(f["url"]), x1 - x0, y1 - y0, f.get("foco", [.5, .5]))
        img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.08)).enhance(1.04)
        m = Image.new("L", (L * 3, A * 3), 0)
        ImageDraw.Draw(m).polygon([(x * 3, y * 3) for x, y in pol], fill=255)
        m = m.resize((L, A), Image.LANCZOS).crop((x0, y0, x1, y1))
        tela.paste(img, (x0, y0), m)
    return tela


if __name__ == "__main__":
    pasta = RAIZ / "site/capas_fotos"
    saida = RAIZ / "site/assets/img/capas"
    saida.mkdir(parents=True, exist_ok=True)
    falhou = False
    for f in sorted(pasta.glob("*.json")):
        destino = saida / f"{f.stem}.jpg"
        if destino.exists():
            continue
        try:
            montar(json.loads(f.read_text(encoding="utf-8"))).save(destino, "JPEG", quality=88, optimize=True, progressive=True)
            print("Capa montada:", destino.name)
        except Exception as e:
            falhou = True
            print(f"FALHOU {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(1 if falhou else 0)
