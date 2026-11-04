"""Abre cada imagem de outras fontes usada nos artigos (linhas !img) e mostra se carrega, com e sem Referer.
Uso: python3 site/checar_imagens_externas.py   (roda no GitHub: workflow 'Checar imagens externas')"""
import glob, json, re, sys, urllib.request
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
arqs = [RAIZ / "site/conteudo/materias.json"] + [Path(p) for p in glob.glob(str(RAIZ / "rascunhos/*.json")) + glob.glob(str(RAIZ / "agendados/*.json"))]
urls = {}
for a in arqs:
    for u in re.findall(r"!img (https?://[^|\"]+)\|", a.read_text(encoding="utf-8")):
        if "images.unsplash.com" not in u:
            urls.setdefault(u, set()).add(a.stem[:40])
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def abrir(u, ref):
    h = {"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8"}
    if ref: h["Referer"] = "https://alohanoticias.com/"
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=40) as r:
            return f"{r.status} {r.headers.get('Content-Type')} {len(r.read(3_000_000))}b"
    except Exception as e:
        return f"ERRO {e}"
for u, onde in urls.items():
    print(u[:150]); print("  em:", sorted(onde)); print("  sem referer:", abrir(u, False)); print("  com referer:", abrir(u, True))
