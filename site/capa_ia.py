"""Remonta capas com as fotos de origem aprimoradas por IA (Real-ESRGAN, 4x) antes da montagem.
Mesmo layout, enquadramento, logo e título do site/capas_fotos/<slug>.json; só a qualidade das fotos muda.
Não troca nada no site: grava em ia_saida/ a capa nova e uma comparação antes/depois para aprovação.
Uso: python3 site/capa_ia.py --novas            (monta direto no site as capas que ainda não existem; usado pelo capas.yml)
     python3 site/capa_ia.py slug1 slug2 ...      (prévia em ia_saida/; precisa de torch, spandrel e dos modelos em ia_modelos/)
     python3 site/capa_ia.py --aplicar slug ...    (copia de ia_saida/ para a capa do site)"""
import json, shutil, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import montar_capa as mc

RAIZ = mc.RAIZ
SAIDA = RAIZ / "ia_saida"
CAPAS = RAIZ / "site/assets/img/capas"
MODELOS = {"foto": RAIZ / "ia_modelos/RealESRGAN_x4plus.pth",
           "anime": RAIZ / "ia_modelos/RealESRGAN_x4plus_anime_6B.pth"}
BASE = 960  # fotos maiores são reduzidas a este lado antes da IA: o detalhe real cabe aí, e a IA reconstrói em 4x

if sys.argv[1:2] == ["--aplicar"]:
    for slug in sys.argv[2:]:
        shutil.copy(SAIDA / f"{slug}.jpg", CAPAS / f"{slug}.jpg"); print("Aplicada:", slug)
    sys.exit(0)

import torch
from spandrel import ModelLoader

torch.set_grad_enabled(False)
_cache = {}


def modelo(tipo):
    if tipo not in _cache:
        _cache[tipo] = ModelLoader().load_from_file(str(MODELOS[tipo])).eval()
    return _cache[tipo]


def ampliar(img, tipo, tile=256, sobra=16):
    """Aumenta 4x em blocos (cabe na memória do GitHub)."""
    m = modelo(tipo)
    a = np.asarray(img, dtype=np.float32) / 255.0
    h, w, _ = a.shape
    out = np.zeros((h * 4, w * 4, 3), dtype=np.float32)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            y0, x0 = max(y - sobra, 0), max(x - sobra, 0)
            y1, x1 = min(y + tile + sobra, h), min(x + tile + sobra, w)
            t = torch.from_numpy(a[y0:y1, x0:x1].transpose(2, 0, 1)).unsqueeze(0)
            r = m(t)[0].clamp(0, 1).numpy().transpose(1, 2, 0)
            yy, xx = (y - y0) * 4, (x - x0) * 4
            hh, ww = min(tile, h - y) * 4, min(tile, w - x) * 4
            out[y * 4:y * 4 + hh, x * 4:x * 4 + ww] = r[yy:yy + hh, xx:xx + ww]
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8))


baixar_original = mc.baixar
tipo_atual = "foto"


def baixar_ia(url):
    """Regra de qualidade (foto por foto):
    IA completa se a foto é pequena, tem quadriculado de JPEG, está borrada ou é anime/ilustração;
    nas outras, retoque leve: metade IA, metade original (melhora sem deixar com cara de plástico)."""
    from medir_fotos import medir
    orig = baixar_original(url)
    w, h = orig.size
    nitidez, bloco = medir(orig)
    img = orig
    if max(w, h) > BASE:
        e = BASE / max(w, h)
        img = orig.resize((round(w * e), round(h * e)), Image.LANCZOS)
    ia = ampliar(img, tipo_atual)
    completa = max(w, h) < 1000 or bloco > 1.12 or nitidez < 1.0 or tipo_atual == "anime"
    print(f"   foto {w}x{h} nitidez={nitidez:.2f} bloco={bloco:.2f} -> {'IA completa' if completa else 'retoque leve'} ({tipo_atual})", flush=True)
    if completa:
        return ia
    return Image.blend(orig.convert("RGB"), ia.resize((w, h), Image.LANCZOS), 0.5)


mc.baixar = baixar_ia


def comparar(antes, depois, destino):
    """Capa inteira antes/depois + recorte 1:1 do centro."""
    W = 960
    a, d = antes.resize((W, 540)), depois.resize((W, 540))
    cx, cy = mc.L // 2, mc.A // 2
    ca, cd = antes.crop((cx - 480, cy - 270, cx + 480, cy + 270)), depois.crop((cx - 480, cy - 270, cx + 480, cy + 270))
    tela = Image.new("RGB", (W * 2 + 20, 540 * 2 + 20), "white")
    for i, im in enumerate([a, d, ca, cd]):
        tela.paste(im, ((i % 2) * (W + 20), (i // 2) * 560))
    dr = ImageDraw.Draw(tela)
    for i, txt in enumerate(["ANTES (site hoje)", "DEPOIS (IA)", "ANTES zoom 100%", "DEPOIS zoom 100%"]):
        x, y = (i % 2) * (W + 20), (i // 2) * 560
        dr.rectangle((x, y, x + 8 * len(txt) + 16, y + 26), fill="black")
        dr.text((x + 8, y + 7), txt, fill="white")
    tela.save(destino, quality=90)


EDITORIAS = {m["slug"]: m.get("editoria") for m in json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8"))}
SAIDA.mkdir(exist_ok=True)
falhou = False
novas = sys.argv[1:2] == ["--novas"]
slugs = sys.argv[2:] if novas else sys.argv[1:]
if novas and not slugs:
    slugs = [f.stem for f in sorted((RAIZ / "site/capas_fotos").glob("*.json")) if not (CAPAS / f"{f.stem}.jpg").exists()]
    print("Capas novas:", slugs or "nenhuma", flush=True)
for slug in slugs:
    spec = json.loads((RAIZ / f"site/capas_fotos/{slug}.json").read_text(encoding="utf-8"))
    ed = spec.get("editoria") or EDITORIAS.get(slug)
    tipo_atual = "anime" if ed == "anime" or spec.get("ia") == "anime" else "foto"
    print("Capa:", slug, flush=True)
    try:
        nova = mc.montar(spec)
        if novas:  # capa nova: vai direto para o site, já com a regra de qualidade
            nova.save(CAPAS / f"{slug}.jpg", "JPEG", quality=90, optimize=True, progressive=True)
            print("   pronta (no site)", flush=True); continue
        nova.save(SAIDA / f"{slug}.jpg", "JPEG", quality=90, optimize=True, progressive=True)
        atual = CAPAS / f"{slug}.jpg"
        if atual.exists():
            comparar(Image.open(atual).convert("RGB"), nova, SAIDA / f"comparar-{slug}.jpg")
        print("   pronta", flush=True)
    except Exception as e:
        falhou = True
        print(f"FALHOU {slug}: {type(e).__name__}: {e}", flush=True)
sys.exit(1 if falhou else 0)
