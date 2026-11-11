"""Coleta a imagem de compartilhamento (og:image) de páginas de trailer/filme e monta folhas de contato
para escolher imagens dos artigos de estreias. Roda no GitHub (workflow 'Coletar imagens de filmes').
Uso: python3 site/coletar_og.py   (lê site/filmes_paginas.json: [{"titulo":..., "url":...}])"""
import io, json, re, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw
RAIZ = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}
itens = json.loads((RAIZ / "filmes_paginas.json").read_text(encoding="utf-8"))
saida = RAIZ / "candidatas"; saida.mkdir(exist_ok=True)
res = []
def pegar(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
        return r.read()
for it in itens:
    t, u = it["titulo"], it["url"]
    try:
        if it.get("img"):
            img_url = it["img"]
        else:
            html = pegar(u).decode("utf-8", "ignore")
            m = (re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)', html) or
                 re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html))
            if not m: raise RuntimeError("sem og:image")
            img_url = m.group(1).replace("&amp;", "&")
        im = Image.open(io.BytesIO(pegar(img_url))).convert("RGB")
        res.append({"titulo": t, "pagina": u, "imagem": img_url, "dim": im.size})
        if it.get("recorte") and it.get("salvar"):
            # recorte opcional em resolução cheia (frações x0,y0,x1,y1) salvo em 1920x1080 no caminho indicado
            x0, y0, x1, y1 = it["recorte"]; w, h = im.size
            rc = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).resize((1920, 1080), Image.LANCZOS)
            destino = RAIZ / it["salvar"]; destino.parent.mkdir(parents=True, exist_ok=True)
            rc.save(destino, "JPEG", quality=90, optimize=True, progressive=True); print("recorte salvo", destino)
        im.thumbnail((1280, 1280)); im.save(saida / (re.sub(r"\W+", "-", t.lower()).strip("-") + ".jpg"), quality=85)
        print("ok", t, im.size, img_url[:110])
    except Exception as e:
        print("FALHOU", t, e)
(saida / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
# folhas de contato (3 colunas x 3 linhas)
W, H = 480, 270
for n in range(0, len(res), 9):
    lote = res[n:n + 9]
    folha = Image.new("RGB", (W * 3, (H + 24) * 3), (20, 20, 20))
    d = ImageDraw.Draw(folha)
    for i, r in enumerate(lote):
        x, y = (i % 3) * W, (i // 3) * (H + 24)
        im = Image.open(saida / (re.sub(r"\W+", "-", r["titulo"].lower()).strip("-") + ".jpg"))
        im.thumbnail((W, H)); folha.paste(im, (x, y + 24))
        d.text((x + 4, y + 6), f'{r["titulo"][:38]} {r["dim"][0]}x{r["dim"][1]}', fill=(255, 255, 255))
    folha.save(saida / f"folha-{n // 9 + 1}.jpg", quality=88)
