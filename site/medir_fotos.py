"""Mede a qualidade das fotos de origem das capas (tamanho, nitidez real e quadriculado de JPEG)."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import montar_capa as mc


def medir(img):
    g = np.asarray(img.convert("L"), dtype=np.float32)
    h, w = g.shape
    e = 960 / max(w, h)
    if e < 1:
        g = np.asarray(img.convert("L").resize((round(w * e), round(h * e)), Image.LANCZOS), dtype=np.float32)
    h, w = g.shape
    meio = np.asarray(Image.fromarray(g).resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BICUBIC), dtype=np.float32)
    nitidez = float(np.abs(g - meio).mean())          # detalhe que some ao reduzir pela metade
    dx = np.abs(np.diff(g, axis=1))
    borda = dx[:, 7::8].mean(); dentro = np.delete(dx, np.s_[7::8], axis=1).mean()
    bloco = float(borda / (dentro + 1e-6))             # >1 = quadriculado de compressão
    return nitidez, bloco


if __name__ == "__main__":
    for f in sorted((mc.RAIZ / "site/capas_fotos").glob("*.json")):
        spec = json.loads(f.read_text(encoding="utf-8"))
        for foto in spec.get("fotos", []):
            url = foto["url"] if isinstance(foto, dict) else foto
            try:
                img = mc.baixar(url)
                n, b = medir(img)
                print(f"MEDIDA {f.stem[:40]:40s} {img.size[0]:5d}x{img.size[1]:<5d} nitidez={n:5.2f} bloco={b:4.2f}", flush=True)
            except Exception as e:
                print(f"MEDIDA {f.stem[:40]:40s} ERRO {e}", flush=True)
