"""Olhos desenhados (referencias/olhos/folha-olhos.png, 4 x 2):
 1 normal · 2 meio fechado · 3 fechado · 4 feliz (^ ^) · 5 surpreso · 6 bravo · 7 desconfiado · 8 pensativo
Cada par é encaixado nos olhos da pose "apresenta" (olho da frente pela íris; o de trás achatado pela
perspectiva e cortado no contorno da cabeça). Os olhos e sobrancelhas originais são apagados (pena
reconstruída) e os desenhos entram com a borda branca do rosto. Depois tudo é levado para cada pose.
Saída: rig/<pose>/olhos_desenho.npz
"""
import json, os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import preparar_mascote as PM

FOLHA = os.path.join(AQUI, "referencias", "olhos", "folha-olhos.png")
# âncoras (pose "apresenta", sem margem) e da célula 1 da folha
IRIS_FRENTE, IRIS_TRAS = (432, 336), (592, 308)
FOLHA_FRENTE, FOLHA_TRAS = (142, 317), (327, 321)
ESCALA = 0.64          # íris da folha (84 px) -> íris do personagem (54 px)
ACHATA_TRAS = 0.5      # o olho de trás está mais virado (perspectiva)


def celulas():
    f = cv2.imread(FOLHA, cv2.IMREAD_UNCHANGED)
    cw, ch = f.shape[1] // 4, f.shape[0] // 2
    out = []
    for r in range(2):
        for c in range(4):
            cel = f[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw].copy()
            a = cel[..., 3] > 40
            xs = np.where(a.any(0))[0]
            gaps = [(p, x) for p, x in zip(xs[:-1], xs[1:]) if x - p > 3]
            corte = int((gaps[0][0] + gaps[0][1]) / 2) if gaps else 255
            out.append((cel, corte))
    return out


def main():
    M_ = PM.MARGEM
    ref = PM.com_margem(cv2.imread(os.path.join(PM.HD, "apresenta.png"), cv2.IMREAD_UNCHANGED))
    base = PM.limpar(ref)
    C = PM.deslocar(json.load(open(os.path.join(AQUI, "poses.json")))["apresenta"], M_)
    H, W = base.shape[:2]
    cabeca = base[..., 3] > 128
    yy, xx = np.mgrid[0:H, 0:W]
    # ---- apaga olhos e sobrancelha originais
    frente = cv2.dilate(PM.poli_mask(base.shape, C["OLHO_ESQ_POLI"]) | PM.poli_mask(base.shape, C["SOBRANCELHA"]),
                        np.ones((13, 13), np.uint8)).astype(bool)
    tras = cv2.dilate(PM.poli_mask(base.shape, C["OLHO_DIR_POLI"]), np.ones((9, 9), np.uint8)).astype(bool)
    hsv = cv2.cvtColor(base[..., :3], cv2.COLOR_BGR2HSV)
    claro = (hsv[..., 2] > 150) & (hsv[..., 1] < 70) & cabeca
    escuro = (hsv[..., 2] < 95) & cabeca
    limpo = base.copy()
    limpo = PM.preencher(limpo, frente & cabeca, claro & ~frente, 3.0)
    limpo = PM.preencher(limpo, tras & cabeca, escuro & ~tras & ~frente, 2.0)
    limpo = np.dstack([limpo[..., :3], base[..., 3]])
    regiao = cv2.dilate((frente | tras).astype(np.uint8), np.ones((61, 61), np.uint8)).astype(bool)
    # ---- encaixa cada par
    camadas = []
    for cel, corte in celulas():
        lay = np.zeros((H, W, 4), np.float32)
        for lado in ("frente", "tras"):
            parte = cel.copy()
            if lado == "frente":
                parte[:, corte:, 3] = 0
                s_x = s_y = ESCALA; (fx, fy), (tx, ty) = FOLHA_FRENTE, (IRIS_FRENTE[0] + M_, IRIS_FRENTE[1] + M_)
            else:
                parte[:, :corte, 3] = 0
                s_x, s_y = ESCALA * ACHATA_TRAS, ESCALA; (fx, fy), (tx, ty) = FOLHA_TRAS, (IRIS_TRAS[0] + M_, IRIS_TRAS[1] + M_)
            T = np.float32([[s_x, 0, tx - s_x * fx], [0, s_y, ty - s_y * fy]])
            w = cv2.warpAffine(parte, T, (W, H), flags=cv2.INTER_AREA if False else cv2.INTER_CUBIC,
                               borderValue=(0, 0, 0, 0)).astype(np.float32)
            a = np.clip((w[..., 3:] / 255 - 0.4) / 0.45, 0, 1)      # borda firme: sem fio cinza em volta
            if lado == "tras":       # cortado no contorno da cabeça
                a *= cv2.erode(cabeca.astype(np.uint8), np.ones((5, 5), np.uint8))[..., None]
            # aro branco do rosto em volta do desenho (como no personagem)
            aro = cv2.GaussianBlur(cv2.dilate((a[..., 0] > 0.3).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 1.2)
            aro *= cabeca * (1.0 if lado == "frente" else 0.0)
            branco = np.array([236, 233, 238], np.float32)
            lay[..., :3] = lay[..., :3] * (1 - aro[..., None]) + branco * aro[..., None]
            lay[..., 3] = np.maximum(lay[..., 3], aro)
            lay[..., :3] = lay[..., :3] * (1 - a) + w[..., :3] * a
            lay[..., 3] = np.maximum(lay[..., 3], a[..., 0])
        lay[..., 3] *= 255
        camadas.append(lay.astype(np.uint8))
    # ---- leva para cada pose
    for pasta in sorted(os.listdir(PM.SAIDA)):
        rj = os.path.join(PM.SAIDA, pasta, "rig.json")
        if not os.path.exists(rj):
            continue
        r = json.load(open(rj))
        Mp = np.asarray(r.get("M_de_apresenta", [[1, 0, 0], [0, 1, 0]]), np.float64)
        Wp, Hp = r["tamanho"]
        reg_p = cv2.warpAffine(regiao.astype(np.uint8), Mp, (Wp, Hp), flags=cv2.INTER_NEAREST) > 0
        ys, xs = np.where(reg_p)
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        pose_base = cv2.imread(os.path.join(PM.SAIDA, pasta, "base.png"), cv2.IMREAD_UNCHANGED)
        cab_p = pose_base[..., 3] > 128
        # na pose: o "limpo" vem da apresenta só onde os olhos ficavam (mistura suave)
        apaga = cv2.warpAffine((frente | tras).astype(np.float32), Mp, (Wp, Hp), flags=cv2.INTER_LINEAR)
        apaga = cv2.GaussianBlur(cv2.dilate(apaga, np.ones((9, 9), np.uint8)), (0, 0), 3) * cab_p
        lp = cv2.warpAffine(limpo, Mp, (Wp, Hp), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0)).astype(np.float32)
        lim_p = pose_base.astype(np.float32)
        lim_p[..., :3] = lim_p[..., :3] * (1 - apaga[..., None]) + lp[..., :3] * apaga[..., None]
        dados = {"x0": x0, "y0": y0, "limpo": lim_p[y0:y1, x0:x1].astype(np.uint8)}
        for i, lay in enumerate(camadas, 1):
            lw = cv2.warpAffine(lay, Mp, (Wp, Hp), flags=cv2.INTER_CUBIC, borderValue=(0, 0, 0, 0))
            lw[..., 3] = (lw[..., 3] * cab_p).astype(np.uint8)
            dados[f"o{i}"] = lw[y0:y1, x0:x1]
        np.savez_compressed(os.path.join(PM.SAIDA, pasta, "olhos_desenho.npz"), **dados)
        print("olhos", pasta, (x1 - x0, y1 - y0))


if __name__ == "__main__":
    main()
