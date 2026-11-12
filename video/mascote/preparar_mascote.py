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
SOBRANCELHA = [(356, 152), (390, 141), (430, 150), (462, 166), (478, 186), (474, 206), (458, 203),
               (432, 190), (402, 184), (374, 184), (358, 177)]
PIVO_SOBRANCELHA = (360, 168)
OLHO_ESQ_POLI = [(379, 204), (384, 196), (396, 189), (412, 187), (426, 190), (438, 196), (448, 203), (453, 212),
                 (450, 224), (442, 234), (430, 240), (416, 238), (402, 231), (390, 221), (382, 211)]
OLHO_DIR_POLI = [(506, 185), (520, 181), (531, 185), (537, 196), (535, 212), (520, 215), (508, 211), (504, 198)]
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


def preencher(img, desconhecido, conhecido, sigma):
    """Preenche a área 'desconhecido' com as cores vizinhas 'conhecido' (pena e sombra continuam iguais)."""
    out = img.astype(np.float32).copy()
    k = conhecido.astype(np.float32) * (~desconhecido)
    for sg in (sigma, sigma * 2, sigma * 4):        # 3 passadas: perto primeiro, depois mais longe
        num = cv2.GaussianBlur(out[..., :3] * k[..., None], (0, 0), sg)
        den = cv2.GaussianBlur(k, (0, 0), sg)[..., None]
        cheio = num / np.maximum(den, 1e-4)
        ok = (den[..., 0] > 0.02) & desconhecido & (k < 0.5)
        out[ok, :3] = cheio[ok]
        k = np.maximum(k, ok.astype(np.float32))
    return out.astype(np.uint8)


def olho_fechado(img_bgra, poli, dil=2, cor_fixa=None):
    """Reconstrói a pele por cima do olho (interpolando, coluna a coluna, a pena de cima e a de baixo).
    Devolve recorte: x0, y0, máscara, pele (BGRA), topo[x], fundo[x]."""
    xs, ys = zip(*poli)
    x0, y0, x1, y1 = min(xs) - 14, min(ys) - 10, max(xs) + 15, max(ys) + 14
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.fillPoly(m, [np.array([(x - x0, y - y0) for x, y in poli], np.int32)], 1)
    m = cv2.dilate(m, np.ones((2 * dil + 1, 2 * dil + 1), np.uint8))
    reg = img_bgra[y0:y1, x0:x1].astype(np.float32)
    h, w = m.shape
    topo = np.full(w, -1.0); fundo = np.full(w, -1.0)
    for x in range(w):
        yy = np.where(m[:, x])[0]
        if len(yy):
            topo[x], fundo[x] = yy.min(), yy.max()
    hsv = cv2.cvtColor(reg[..., :3].astype(np.uint8), cv2.COLOR_BGR2HSV)
    if cor_fixa is not None:   # olho de trás: pálpebra feita das penas pretas em volta
        pena = (hsv[..., 2] < 95) & (reg[..., 3] > 200)
        pele = preencher(reg, m.astype(bool), pena & ~cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(bool), 2.0).astype(np.float32)
    else:
        pena = (hsv[..., 2] > 150) & (hsv[..., 1] < 70) & (reg[..., 3] > 200)
        pele = preencher(reg, m.astype(bool), pena & ~cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(bool), 3.0).astype(np.float32)
        pele[..., :3] *= 0.97                          # pálpebra um tiquinho mais escura que a pena
    fora = np.zeros(m.shape, np.uint8)
    if cor_fixa is not None:   # parte do olho de trás que passa do contorno da cabeça some ao fechar (em rampa)
        xs_ = np.arange(w)[None, :] + x0
        ys_ = np.arange(h)[:, None] + y0
        borda_x = 530 + (ys_ - 186) * 0.2            # contorno da cabeça (levemente inclinado)
        fora = (np.clip((xs_ - borda_x) / 4.0, 0, 1) * m * 255).astype(np.uint8)
    return dict(x0=x0, y0=y0, mask=m, pele=pele.astype(np.uint8), topo=topo, fundo=fundo, fora=fora)


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
    base_orig = base.copy()   # cores originais (antes de redesenhar o queixo)

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
    m_bin = (cv2.dilate(mand, np.ones((3, 3), np.uint8)) & lim).astype(bool)
    m_bin |= (lim > 0) & (yy > linha(BICO_BORDA, xx) - 5) & (yy < linha(BICO_BORDA, xx) + 10) & (xx > 398)
    m_dil = cv2.dilate(m_bin.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    borda_m = m_dil & ~cv2.erode(m_dil.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    claro_m = cv2.cvtColor(base_orig[..., :3], cv2.COLOR_BGR2GRAY) > 150
    m_dil &= ~(borda_m & claro_m & (yy > linha(BICO_BORDA, xx) + 3))      # sem fio claro na borda
    m_alfa = cv2.GaussianBlur(m_dil.astype(np.float32), (0, 0), 0.6)
    mandibula = np.dstack([base_orig[..., :3], (np.clip(m_alfa, 0, 1) * base_orig[..., 3]).astype(np.uint8)])
    mand = m_bin.astype(np.uint8)

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
    hsv_b = cv2.cvtColor(base[..., :3], cv2.COLOR_BGR2HSV)
    pena_px = (hsv_b[..., 2] > 140) & (hsv_b[..., 1] < 70) & (base[..., 3] > 200)
    conhecido = pena_px & ~cv2.dilate(lugar.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    cheio = preencher(base, pena, conhecido, 4.0)
    k = cv2.GaussianBlur(pena.astype(np.float32), (0, 0), 0.8)[..., None]
    base[..., :3] = (base[..., :3] * (1 - k) + cheio[..., :3] * k).astype(np.uint8)
    base[ar, 3] = 0
    pts = (np.array(QUEIXO_BORDA, np.float32) * 16).astype(np.int32)
    cv2.polylines(base, [pts], False, CONTORNO + (255,), 4, cv2.LINE_AA, shift=4)
    base[..., 3] = np.where(abaixo & lugar, np.maximum(base[..., 3], (pena * 255).astype(np.uint8)), base[..., 3])

    # ---- bico de cima por cima da mandíbula, recortado no contorno real do desenho
    borda_y = linha(BICO_BORDA, xx)
    laranja = (hsv[..., 0] >= 5) & (hsv[..., 0] <= 35) & (hsv[..., 1] > 90) & (hsv[..., 2] > 120)
    contorno_px = hsv[..., 2] < 60
    faixa_b = (yy >= borda_y - 3) & (yy <= borda_y + 9)
    bico_m = ((yy < borda_y - 3) | (faixa_b & (laranja | contorno_px))) & (xx > 385) & (xx < 640) & (yy > 150) & (yy < 400)
    bico_a = cv2.GaussianBlur(bico_m.astype(np.float32), (0, 0), 0.5) * (yy < borda_y + 10) * (base_orig[..., 3] / 255.0)
    bico_sup = np.dstack([base_orig[..., :3], (bico_a * 255).astype(np.uint8)])

    # ---- peso da cabeça: cai ao longo do pescoço
    s = linha(COLARINHO, xx) - yy
    w_cab = suave((s + 12) / 48.0) * suave((700 - xx) / 50.0)

    # ---- peso do antebraço
    ax, ay = BRACO_A; bx, by = BRACO_B
    nrm = np.hypot(bx - ax, by - ay)
    lado = ((bx - ax) * (yy - ay) - (by - ay) * (xx - ax)) / nrm      # <0 = lado do antebraço
    w_bra = suave((-lado + 8) / 46.0) * suave((790 - yy) / 30.0) * (xx > 560)

    # ---- pesos das expressões (sobrancelha e olho de perto)
    sob = np.zeros((h, w), np.uint8)
    cv2.fillPoly(sob, [np.array(SOBRANCELHA, np.int32)], 1)
    dsb = cv2.distanceTransform((1 - sob).astype(np.uint8), cv2.DIST_L2, 5)
    w_sob = suave(1 - dsb / 9.0)
    olho = np.zeros((h, w), np.uint8)
    cv2.fillPoly(olho, [np.array(OLHO_ESQ_POLI, np.int32)], 1)
    dol = cv2.distanceTransform((1 - olho).astype(np.uint8), cv2.DIST_L2, 5)
    w_olho = suave(1 - dol / 10.0)

    ot = np.zeros((h, w), np.uint8); cv2.fillPoly(ot, [np.array(OLHO_DIR_POLI, np.int32)], 1)
    dot = cv2.distanceTransform((1 - ot).astype(np.uint8), cv2.DIST_L2, 5)
    w_ot = suave(1 - dot / 5.0)
    x0, y0, x1, y1 = RECORTE
    c = lambda m: m[y0:y1, x0:x1].astype(np.float16)
    cv2.imwrite(os.path.join(SAIDA, "base.png"), base[y0:y1, x0:x1])
    cv2.imwrite(os.path.join(SAIDA, "mandibula.png"), mandibula[y0:y1, x0:x1])
    cv2.imwrite(os.path.join(SAIDA, "bico_sup.png"), bico_sup[y0:y1, x0:x1])
    olhos = {}
    for nome, poli in (("esq", OLHO_ESQ_POLI), ("dir", OLHO_DIR_POLI)):
        o = olho_fechado(base_orig, poli, dil=3 if nome == "esq" else 2, cor_fixa=(24, 21, 27) if nome == "dir" else None)
        for k_, v_ in o.items():
            olhos[f"{nome}_{k_}"] = np.array(v_) - (x0 if k_ == "x0" else y0 if k_ == "y0" else 0)
    np.savez_compressed(os.path.join(SAIDA, "olhos.npz"), **olhos)
    np.savez_compressed(os.path.join(SAIDA, "pesos.npz"), cabeca=c(w_cab), braco=c(w_bra), sobrancelha=c(w_sob), olho=c(w_olho), olho_tras=c(w_ot),
                        acima_bico=c(cv2.GaussianBlur((~abaixo).astype(np.float32), (0, 0), 0.8)))
    rel = lambda p: [p[0] - x0, p[1] - y0]
    olho = lambda o: dict(c=rel(o["c"]), r=list(o["r"]), ang=o["ang"], cor=list(o["cor"]))
    json.dump(dict(tamanho=[x1 - x0, y1 - y0], pivo_cabeca=rel(PIVO_CABECA), pivo_braco=rel(PIVO_BRACO),
                   dobradica=rel(DOBRADICA), regiao_boca=[300 - x0, 200 - y0, 640 - x0, 430 - y0],
                   regiao_braco=[560 - x0, 340 - y0, 1000 - x0, 800 - y0],
                   angulo_fechado=20.0, pivo_sobrancelha=rel(PIVO_SOBRANCELHA), centro_olho=rel((415, 213)), olho_tras_y=[183 - y0, 211 - y0], olho_esq=olho(OLHO_ESQ), olho_dir=olho(OLHO_DIR)),
              open(os.path.join(SAIDA, "rig.json"), "w"), indent=1)
    print("rig salvo em", SAIDA)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "referencias", "corpo-inteiro.png"))
