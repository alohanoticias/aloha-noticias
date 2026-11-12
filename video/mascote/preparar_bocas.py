"""Sincronia labial com os desenhos de bico (referencias/bocas/folha-bocas.png).

A folha tem 8 cabeças (4 x 2), na ordem:
 1 fechado (M/B/P, pausa) · 2 um pouco aberto · 3 meio aberto · 4 bem aberto (A)
 5 arredondado (O/U) · 6 esticado (E/I) · 7 rindo · 8 surpreso
Cada cabeça é alinhada à pose "apresenta" e só a região do bico é usada (olhos e penas do boneco
continuam os mesmos, então nada "pula" na troca). Depois o bico é levado para cada pose.
Saída: rig/<pose>/bocas.npz
"""
import json, os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import preparar_mascote as PM

FOLHA = os.path.join(AQUI, "referencias", "bocas", "folha-bocas.png")
LINHAS = [(0, 368), (440, 812)]          # faixas das cabeças (sem os rótulos)
# região do bico na pose "apresenta" (sem margem): do canto da boca até a ponta e o queixo, abaixo do olho
REGIAO = [(385, 390), (432, 380), (482, 368), (520, 336), (556, 306), (612, 292), (680, 312), (740, 352),
          (800, 420), (812, 500), (790, 580), (720, 590), (650, 600), (600, 628), (536, 636), (468, 606),
          (418, 548), (392, 474)]


def celulas():
    f = cv2.imread(FOLHA, cv2.IMREAD_UNCHANGED)
    cw = f.shape[1] // 4
    out = []
    for y0, y1 in LINHAS:
        for c in range(4):
            out.append(f[y0:y1, c * cw:(c + 1) * cw])
    h = min(c.shape[0] for c in out)
    return [c[:h] for c in out]


def para_ref(cels):
    """Transforma cada célula para o espaço da célula 1 (ECC só na cabeça, sem o bico)."""
    def g(c):
        x = cv2.cvtColor(c[..., :3], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255 * (c[..., 3] / 255.0)
        return cv2.GaussianBlur(x, (0, 0), 1.5)
    ref = cels[0]; h, w = ref.shape[:2]
    m = np.zeros((h, w), np.uint8); m[:int(h * 0.55), :int(w * 0.62)] = 255
    R = g(ref); Ws = [np.eye(2, 3)]
    for i, c in enumerate(cels[1:], 2):
        Wt = np.eye(2, 3, dtype=np.float32)
        try:
            cc, Wt = cv2.findTransformECC(R, g(c), Wt, cv2.MOTION_AFFINE,
                                          (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), m, 5)
        except cv2.error:
            cc = 0
        if cc < 0.95:          # olhos diferentes (rindo/surpreso) confundem: usa a da mesma fileira
            Wt = Ws[4] if i > 5 else Ws[1]
        Ws.append(np.asarray(Wt, np.float64))
    return [np.linalg.inv(np.vstack([W_, [0, 0, 1]]))[:2] for W_ in Ws]


def comp(a, b):
    return (np.vstack([a, [0, 0, 1]]) @ np.vstack([b, [0, 0, 1]]))[:2]


def main():
    cels = celulas()
    ref = PM.com_margem(cv2.imread(os.path.join(PM.HD, "apresenta.png"), cv2.IMREAD_UNCHANGED))
    C = PM.deslocar(json.load(open(os.path.join(AQUI, "poses.json")))["apresenta"], PM.MARGEM)
    # célula 1 -> apresenta (SIFT, célula ampliada 2x)
    c2 = cv2.resize(cels[0], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    M, n = PM.sift_transform(c2, ref, [0, 0, c2.shape[1], c2.shape[0]])
    # sift_transform leva 'ref'(1º arg) -> 'alvo'(2º): aqui célula2x -> apresenta
    M1 = np.asarray(M, np.float64); M1[:, :2] *= 2
    print("célula->apresenta: pontos", n, "escala", round(float(np.hypot(M1[0, 0], M1[1, 0])), 3))
    Mc = [comp(M1, inv) for inv in para_ref(cels)]
    H, W = ref.shape[:2]
    reg = PM.poli_mask(ref.shape, [(x + PM.MARGEM, y + PM.MARGEM) for x, y in REGIAO]).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    acima_gola = (yy < PM.linha(C["COLARINHO"], xx) - 3).astype(np.float32)
    bocas, mascaras = [], []
    for i, c in enumerate(cels):
        wc = cv2.warpAffine(c, Mc[i], (W, H), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
        wc[..., :3] = cv2.addWeighted(wc[..., :3], 1.5, cv2.GaussianBlur(wc[..., :3], (0, 0), 1.6), -0.5, 0)
        hsv = cv2.cvtColor(wc[..., :3], cv2.COLOR_BGR2HSV)
        bico = (((hsv[..., 0] >= 4) & (hsv[..., 0] <= 36) & (hsv[..., 1] > 90)) |
                (((hsv[..., 0] < 12) | (hsv[..., 0] > 165)) & (hsv[..., 1] > 60) & (hsv[..., 2] > 70))) & (wc[..., 3] > 128)
        perto = cv2.dilate(reg.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
        bico = cv2.dilate(bico.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32) * perto
        m = np.maximum(reg * acima_gola, bico)     # o queixo aberto pode passar na frente do colarinho
        m = cv2.GaussianBlur(m, (0, 0), 5.0)
        bocas.append(wc); mascaras.append(m)
    # leva para cada pose
    for pasta in sorted(os.listdir(PM.SAIDA)):
        rj = os.path.join(PM.SAIDA, pasta, "rig.json")
        if not os.path.exists(rj):
            continue
        r = json.load(open(rj))
        Mp = np.asarray(r.get("M_de_apresenta", [[1, 0, 0], [0, 1, 0]]), np.float64)
        Wp, Hp = r["tamanho"]
        ms = [cv2.warpAffine(m, Mp, (Wp, Hp), flags=cv2.INTER_LINEAR) for m in mascaras]
        uni = np.max(ms, axis=0) > 0.01
        ys, xs = np.where(uni)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        dados = {"x0": x0, "y0": y0}
        for i, (b, m) in enumerate(zip(bocas, ms), 1):
            bp = cv2.warpAffine(b, Mp, (Wp, Hp), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
            dados[f"b{i}"] = bp[y0:y1, x0:x1]
            dados[f"m{i}"] = m[y0:y1, x0:x1].astype(np.float16)
        np.savez_compressed(os.path.join(PM.SAIDA, pasta, "bocas.npz"), **dados)
        print("bocas", pasta, (x1 - x0, y1 - y0))


if __name__ == "__main__":
    main()
