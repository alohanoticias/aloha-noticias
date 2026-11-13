"""Busca jogos do Roblox por nome e baixa as miniaturas oficiais (definidas pelos próprios estúdios na página do jogo).
Uso: python3 site/roblox_jogos.py "Nome 1" "Nome 2" ...
Saída: site/candidatas/roblox/NN.jpg, lista.txt e folha.jpg (prévia numerada)."""
import io, json, sys, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
out = Path("site/candidatas/roblox"); out.mkdir(parents=True, exist_ok=True)
for f in out.glob("*"): f.unlink()
linhas, imgs, n = [], [], 0
import time
ids = [a.strip()[2:] for a in sys.argv[1:] if a.strip().startswith("u:")]
nomes = {}
if ids:
    info = json.loads(get("https://games.roblox.com/v1/games?universeIds=" + ",".join(ids)))
    for g in info.get("data", []):
        nomes[str(g["id"])] = g["name"]
        print(f"== {g['id']} -> {g['name']} | criador {g['creator']['name']} | place {g['rootPlaceId']} | jogando {g['playing']} | visitas {g['visits']} | criado {g['created'][:10]}")
    time.sleep(1)
    t = json.loads(get(f"https://thumbnails.roblox.com/v1/games/multiget/thumbnails?universeIds={','.join(ids)}&countPerUniverse=10&size=768x432&format=Png&isCircular=false"))
    for item in t["data"]:
        uid = str(item["universeId"])
        urls = [x["imageUrl"] for x in item["thumbnails"] if x.get("state") == "Completed"]
        for u in urls[:4]:
            n += 1
            try:
                im = Image.open(io.BytesIO(get(u))).convert("RGB")
            except Exception as e:
                print("ERRO img", u, e); continue
            im.save(out / f"{n:02d}.jpg", quality=92)
            linhas.append(f"{n:02d} {im.width}x{im.height} {nomes.get(uid, uid)} | {u}")
            imgs.append((n, im))
(out / "lista.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
if imgs:
    W, H, cols = 384, 216, 4
    rows = (len(imgs) + cols - 1) // cols
    folha = Image.new("RGB", (W * cols, H * rows), "white"); dr = ImageDraw.Draw(folha)
    for i, (k, im) in enumerate(imgs):
        x, y = (i % cols) * W, (i // cols) * H
        folha.paste(im.resize((W - 4, H - 4)), (x, y))
        dr.rectangle([x, y, x + 34, y + 22], fill="black"); dr.text((x + 6, y + 5), f"{k:02d}", fill="yellow")
    folha.save(out / "folha.jpg", quality=80)
