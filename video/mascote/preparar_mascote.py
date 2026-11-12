"""Prepara o mascote do Aloha Notícias para animação SEM recortes.

O personagem é uma imagem só. Cada movimento é uma deformação suave (campo de pesos):
  - cabeça: gira no pescoço; o peso cai devagar ao longo do pescoço (sem emenda no colarinho);
  - bico: a mandíbula gira na dobradiça do canto da boca; o queixo estica junto, como pele;
    o bico de cima fica parado e a borda entre os dois é o próprio contorno do desenho;
  - antebraço: dobra no cotovelo com transição suave na manga.
As pálpebras são desenhadas por cima (curvas que acompanham o olho).

Saída em rig/: base.png (personagem com borda limpa), pesos.npz, rig.json
Uso: python3 preparar_mascote.py [arte_corpo_inteiro_1024x1536.png]
"""
import json, os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "rig")

RECORTE = (60, 0, 1000, 960)
SEMENTES_FUNDO = [(300, 660), (410, 1100)]
COLARINHO = [(0, 335), (300, 345), (330, 356), (370, 376), (400, 387),
             (455, 396), (485, 376), (520, 366), (1024, 366)]
PIVO_CABECA = (430, 400)
CAVIDADE = [(409, 267), (430, 281), (450, 294), (470, 301), (490, 305), (505, 310),
            (501, 322), (495, 340), (487, 354), (473, 363), (457, 361), (440, 348),
            (430, 328), (420, 302), (411, 282)]
BICO_BORDA = [(300, 249), (380, 253), (398, 260), (415, 271), (430, 282), (450, 295), (470, 302),
              (490, 306), (505, 311), (520, 317), (545, 328), (575, 343), (600, 357), (618, 369), (1024, 375)]
DOBRADICA = (401, 259)
QUEIXO = [(388, 250), (440, 285), (486, 306), (494, 336), (484, 370), (472, 398), (388, 398)]
MANDIBULA_LIMITE = [(394, 250), (512, 304), (515, 322), (510, 340), (496, 372), (474, 390),
                    (446, 384), (424, 360), (410, 330), (400, 296)]
QUEIXO_BORDA = [(493, 322), (494, 336), (484, 370), (470, 394)]
OLHO_ESQ = dict(c=(413, 213), r=(31, 20), ang=5, cor=(234, 231, 236))
OLHO_DIR = dict(c=(518, 200), r=(11, 10), ang=0, cor=(44, 42, 48))
BRACO_A, BRACO_B = (690, 548), (705, 685)
PIVO_BRACO = (662, 648)
CONTORNO = (26, 23, 29)


def alfa_do_personagem(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    escuro = cv2.dilate((hsv[..., 2] < 75).astype(np.uint8), np.ones((3, 3), np.uint8))
    n, lab = cv2.connectedComponents((1 - escuro).astype(np.uint8), connectivity=4)
    fundo = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    for x, y in SEMENTES_FUNDO:
        fundo.add(lab[y, x])
    a = np.where(np.isin(lab, list(fundo)), 0, 255).astype(np.uint8)
    n, l2, st, _ = cv2.connectedComponentsWithStats(a)
    a = np.where(l2 == 1 + np.argmax(st[1:, 4]), 255, 0).astype(np.uint8)
    return cv2.erode(a, np.ones((3, 3), np.uint8))


def limpar_borda(img, a):
    """A faixa de 2 px da borda puxa para a cor do contorno: some o halo do fundo antigo."""
    dentro = cv2.erode(a, np.ones((5, 5), np.uint8))
    faixa = ((a > 0) & (dentro == 0))[..., None]
    rgb = img.astype(np.float32)
    k = np.clip((rgb.mean(axis=2, keepdims=True) - 55) / 110, 0, 1) * faixa
    rgb = rgb * (1 - k) + np.array(CONTORNO, np.float32) * k
    alfa = cv2.GaussianBlur(a, (0, 0), 0.85)
    return np.dstack([rgb.astype(np.uint8), alfa])


def linha(pts, x):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys)


def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def main(caminho):
    os.makedirs(SAIDA, exist_ok=True)
    for f in os.listdir(SAIDA):
        os.remove(os.path.join(SAIDA, f))
    img = cv2.imread(caminho)
    assert img.shape[:2] == (1536, 1024), "use a arte de corpo inteiro 1024x1536"
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = alfa_do_personagem(img)
    base = limpar_borda(img, a)

    # ---- peso da mandíbula (no espaço da arte)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    claro = (hsv[..., 2] > 150) & (hsv[..., 1] < 45)
    abaixo = yy > linha(BICO_BORDA, xx)
    cav = np.zeros((h, w), np.uint8); cv2.fillPoly(cav, [np.array(CAVIDADE, np.int32)], 1)
    caixa = np.zeros((h, w), bool); caixa[250:380, 396:522] = True
    cand = caixa & abaixo & ~claro
    cur = cav.astype(bool)
    for _ in range(60):
        nxt = cv2.dilate(cur.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (cand | cur)
        if (nxt == cur).all():
            break
        cur = nxt
    mand = cv2.morphologyEx(cur.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    dist = cv2.distanceTransform((1 - mand).astype(np.uint8), cv2.DIST_L2, 5)

    # ---- mandíbula vira peça rígida (com o contorno do próprio desenho)
    lim = np.zeros((h, w), np.uint8); cv2.fillPoly(lim, [np.array(MANDIBULA_LIMITE, np.int32)], 1)
    mand = cv2.dilate(mand, np.ones((3, 3), np.uint8)) & lim
    so_baixo = (yy > linha(BICO_BORDA, xx) + 1.0)
    m_bin = (mand > 0) & so_baixo
    m_alfa = cv2.GaussianBlur(m_bin.astype(np.float32), (0, 0), 0.6)
    # contorno da peça: a faixa de borda vira cor de contorno (sem fio claro)
    dd = cv2.distanceTransform(m_bin.astype(np.uint8), cv2.DIST_L2, 5)
    faixa = np.clip(1 - (dd - 1.0) / 2.0, 0, 1)[..., None] * m_bin[..., None]
    rgb_m = base[..., :3].astype(np.float32)
    kk = np.clip((rgb_m.mean(axis=2, keepdims=True) - 50) / 100, 0, 1) * faixa
    rgb_m = rgb_m * (1 - kk) + np.array(CONTORNO, np.float32) * kk
    rgb_b = cv2.GaussianBlur(rgb_m, (0, 0), 0.7)
    rgb_m = rgb_m * (1 - faixa) + rgb_b * faixa
    mandibula = np.dstack([rgb_m.astype(np.uint8), (m_alfa * base[..., 3]).astype(np.uint8)])
    # ---- queixo redesenhado embaixo dela: pena branca com sombra e contorno à direita
    queixo = np.zeros((h, w), np.uint8)
    cv2.fillPoly(queixo, [np.array(QUEIXO, np.int32)], 1)
    lugar = (mand > 0) & abaixo
    perto_borda = abaixo & (yy < linha(BICO_BORDA, xx) + 7)      # faixa logo abaixo do bico: fica escura (boca)
    pena = lugar & (queixo > 0) & ~perto_borda
    ar = lugar & (queixo == 0) & abaixo & ~perto_borda
    # sobras do desenho à direita do queixo (fora da mandíbula) viram ar
    sobra = abaixo & (queixo == 0) & (xx > 470) & (xx < 545) & (yy > 300) & (yy < linha(COLARINHO, xx) - 2)
    base[sobra & ~cv2.dilate(lugar.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~perto_borda, 3] = 0
    base[perto_borda & lugar, :3] = (40, 28, 70)   # interior escuro da boca (BGR)
    tom = np.clip((yy - 320) / 75, 0, 1)
    cor = np.stack([236 - 30 * tom, 233 - 30 * tom, 238 - 28 * tom], -1)
    k = cv2.GaussianBlur(pena.astype(np.float32), (0, 0), 1.0)[..., None]
    base[..., :3] = (base[..., :3] * (1 - k) + cor * k).astype(np.uint8)
    base[ar, 3] = 0
    pts = (np.array(QUEIXO_BORDA, np.float32) * 16).astype(np.int32)
    cv2.polylines(base, [pts], False, CONTORNO + (255,), 4, cv2.LINE_AA, shift=4)
    base[..., 3] = np.where(abaixo & lugar, np.maximum(base[..., 3], (pena * 255).astype(np.uint8)), base[..., 3])

    # ---- peso da cabeça: cai ao longo do pescoço
    s = linha(COLARINHO, xx) - yy
    w_cab = suave((s + 12) / 48.0) * suave((700 - xx) / 50.0)

    # ---- peso do antebraço
    ax, ay = BRACO_A; bx, by = BRACO_B
    nrm = np.hypot(bx - ax, by - ay)
    lado = ((bx - ax) * (yy - ay) - (by - ay) * (xx - ax)) / nrm      # <0 = lado do antebraço
    w_bra = suave((-lado + 8) / 46.0) * suave((790 - yy) / 30.0) * (xx > 560)

    x0, y0, x1, y1 = RECORTE
    c = lambda m: m[y0:y1, x0:x1].astype(np.float16)
    cv2.imwrite(os.path.join(SAIDA, "base.png"), base[y0:y1, x0:x1])
    cv2.imwrite(os.path.join(SAIDA, "mandibula.png"), mandibula[y0:y1, x0:x1])
    np.savez_compressed(os.path.join(SAIDA, "pesos.npz"), cabeca=c(w_cab), braco=c(w_bra),
                        acima_bico=c(cv2.GaussianBlur((~abaixo).astype(np.float32), (0, 0), 0.8)))
    rel = lambda p: [p[0] - x0, p[1] - y0]
    olho = lambda o: dict(c=rel(o["c"]), r=list(o["r"]), ang=o["ang"], cor=list(o["cor"]))
    json.dump(dict(tamanho=[x1 - x0, y1 - y0], pivo_cabeca=rel(PIVO_CABECA), pivo_braco=rel(PIVO_BRACO),
                   dobradica=rel(DOBRADICA), regiao_boca=[300 - x0, 200 - y0, 640 - x0, 430 - y0],
                   regiao_braco=[560 - x0, 340 - y0, 1000 - x0, 800 - y0],
                   angulo_fechado=20.0, olho_esq=olho(OLHO_ESQ), olho_dir=olho(OLHO_DIR)),
              open(os.path.join(SAIDA, "rig.json"), "w"), indent=1)
    print("rig salvo em", SAIDA)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "referencias", "corpo-inteiro.png"))
