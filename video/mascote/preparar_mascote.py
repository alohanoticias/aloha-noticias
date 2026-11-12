"""Prepara o mascote do Aloha Notícias para animação, a partir das artes novas (poses em alta).

Cada pose vira um "boneco" animável, sem recortes aparentes:
  - cabeça gira no pescoço por deformação suave (sem emenda no colarinho);
  - o bico de baixo é a peça do próprio desenho girando na dobradiça; o bico de cima fica por cima,
    recortado no contorno real; o queixo que aparece é preenchido com a pena e a sombra vizinhas;
  - pálpebras reconstruídas com a pena em volta; sobrancelha e olho deformam para as expressões;
  - (só na pose "apresenta") o antebraço dobra no cotovelo.

As coordenadas são marcadas na pose "apresenta" (poses.json). Nas outras poses, a cabeça é localizada
automaticamente (SIFT) e as coordenadas são transportadas.
Saída: rig/<pose>/ (base.png, mandibula.png, bico_sup.png, pesos.npz, olhos.npz, rig.json)
Uso: python3 preparar_mascote.py
"""
import json, os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
HD = os.path.join(AQUI, "referencias", "poses-hd")
SAIDA = os.path.join(AQUI, "rig")
CONTORNO = (26, 23, 29)
PONTOS = ["COLARINHO", "CAVIDADE", "BICO_BORDA", "QUEIXO", "MANDIBULA_LIMITE", "QUEIXO_BORDA", "SOBRANCELHA",
          "OLHO_ESQ_POLI", "OLHO_DIR_POLI", "BRACO_A", "BRACO_B"]
UM_PONTO = ["PIVO_CABECA", "DOBRADICA", "PIVO_SOBRANCELHA", "PIVO_BRACO", "PONTA_BICO"]


def linha(pts, x):
    xs, ys = zip(*pts)
    return np.interp(x, xs, ys)


def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def poli_mask(shape, pts):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
    return m


def preencher(img, desconhecido, conhecido, sigma):
    """Preenche 'desconhecido' com as cores vizinhas 'conhecido' (pena e sombra continuam iguais)."""
    out = img.astype(np.float32).copy()
    k = conhecido.astype(np.float32) * (~desconhecido)
    for sg in (sigma, sigma * 2, sigma * 4, sigma * 8):
        num = cv2.GaussianBlur(out[..., :3] * k[..., None], (0, 0), sg)
        den = cv2.GaussianBlur(k, (0, 0), sg)[..., None]
        cheio = num / np.maximum(den, 1e-4)
        ok = (den[..., 0] > 0.02) & desconhecido & (k < 0.5)
        out[ok, :3] = cheio[ok]
        k = np.maximum(k, ok.astype(np.float32))
    return out.astype(np.uint8)


def limpar(img4):
    """Alfa da própria arte; tira pontinhos soltos e o halo claro da borda (sem pontos brancos)."""
    a = img4[..., 3].copy()
    duro = (a > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(duro)
    maior = 1 + np.argmax(st[1:, 4])
    duro = (lab == maior).astype(np.uint8)
    # buracos pequenos dentro do desenho
    inv = 1 - duro
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, 4] < 400:
            duro[lab == i] = 1
    a = np.where(duro > 0, np.maximum(a, 0), 0).astype(np.uint8)
    a = np.where(cv2.dilate(duro, np.ones((3, 3), np.uint8)) > 0, a, 0)
    dentro = cv2.erode(duro, np.ones((7, 7), np.uint8))
    faixa = ((a > 0) & (dentro == 0))[..., None]
    rgb = img4[..., :3].astype(np.float32)
    k = np.clip((rgb.mean(axis=2, keepdims=True) - 55) / 100, 0, 1) * faixa
    rgb = rgb * (1 - k) + np.array(CONTORNO, np.float32) * k
    return np.dstack([rgb.astype(np.uint8), a])


def olho_fechado(img, poli, dil, escuro, sobrancelha=None):
    xs, ys = zip(*poli)
    x0, y0 = int(min(xs)) - 20, int(min(ys)) - 16
    x1, y1 = int(max(xs)) + 21, int(max(ys)) + 20
    x0, y0 = max(0, x0), max(0, y0)
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.fillPoly(m, [np.array([(x - x0, y - y0) for x, y in poli], np.int32)], 1)
    m = cv2.dilate(m, np.ones((2 * dil + 1, 2 * dil + 1), np.uint8))
    if sobrancelha is not None:   # a pálpebra nunca cobre a sobrancelha
        sb = np.zeros_like(m)
        cv2.fillPoly(sb, [np.array([(x - x0, y - y0) for x, y in sobrancelha], np.int32)], 1)
        m &= ~cv2.dilate(sb, np.ones((3, 3), np.uint8)).astype(bool)
        m = m.astype(np.uint8)
    reg = img[y0:y1, x0:x1].astype(np.float32)
    h, w = m.shape
    topo = np.full(w, -1.0); fundo = np.full(w, -1.0)
    for x in range(w):
        yy = np.where(m[:, x])[0]
        if len(yy):
            topo[x], fundo[x] = yy.min(), yy.max()
    hsv = cv2.cvtColor(reg[..., :3].astype(np.uint8), cv2.COLOR_BGR2HSV)
    fora_m = ~cv2.dilate(m, np.ones((3, 3), np.uint8)).astype(bool)
    if escuro:     # olho de trás: a pálpebra é a pena preta da cabeça
        pena = (hsv[..., 2] < 95) & (reg[..., 3] > 200)
        pele = preencher(reg, m.astype(bool), pena & fora_m, 2.0).astype(np.float32)
    else:
        pena = (hsv[..., 2] > 150) & (hsv[..., 1] < 70) & (reg[..., 3] > 200)
        pele = preencher(reg, m.astype(bool), pena & fora_m, 3.0).astype(np.float32)
        pele[..., :3] *= 0.97
    return dict(x0=x0, y0=y0, mask=m, pele=pele.astype(np.uint8), topo=topo, fundo=fundo, escuro=int(escuro))


def preparar(nome, img4, C, saida):
    os.makedirs(saida, exist_ok=True)
    for f in os.listdir(saida):
        os.remove(os.path.join(saida, f))
    K = C.get("K", 1.0)                       # escala de detalhe (px) desta arte
    base = limpar(img4)
    base_orig = base.copy()
    img = base[..., :3]
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    borda_y = linha(C["BICO_BORDA"], xx)
    abaixo = yy > borda_y
    tem_boca = C.get("boca", True)
    lim_bx = cv2.boundingRect(np.array(C["MANDIBULA_LIMITE"], np.int32))
    mx0, my0, mw, mh = lim_bx
    regiao_boca = [int(mx0 - 60 * K), int(min(p[1] for p in C["BICO_BORDA"][:3]) - 160 * K),
                   int(C["PONTA_BICO"][0] + 30 * K), int(my0 + mh + 50 * K)]
    regiao_boca = [max(0, regiao_boca[0]), max(0, regiao_boca[1]), min(w, regiao_boca[2]), min(h, regiao_boca[3])]

    mandibula = np.zeros_like(base); bico_sup = np.zeros_like(base)
    if tem_boca:
        claro = (hsv[..., 2] > 150) & (hsv[..., 1] < 45)
        lim = poli_mask(base.shape, C["MANDIBULA_LIMITE"])
        cav = poli_mask(base.shape, C["CAVIDADE"])
        cand = (lim > 0) & abaixo & ~claro
        cur = cav.astype(bool)
        for _ in range(120):
            nxt = cv2.dilate(cur.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (cand | cur)
            if (nxt == cur).all():
                break
            cur = nxt
        mand = cv2.morphologyEx(cur.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        m_bin = (cv2.dilate(mand, np.ones((3, 3), np.uint8)) & lim).astype(bool)
        m_bin |= (lim > 0) & (yy > borda_y - 6 * K) & (yy < borda_y + 14 * K)
        m_dil = cv2.dilate(m_bin.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        borda_m = m_dil & ~cv2.erode(m_dil.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        claro_m = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) > 150
        m_dil &= ~(borda_m & claro_m & (yy > borda_y + 3 * K))
        m_alfa = cv2.GaussianBlur(m_dil.astype(np.float32), (0, 0), 0.6)
        mandibula = np.dstack([img, (np.clip(m_alfa, 0, 1) * base_orig[..., 3]).astype(np.uint8)])
        lugar = m_bin & abaixo
        # queixo: pena reconstruída com a sombra vizinha; à direita dele, ar
        queixo = poli_mask(base.shape, C["QUEIXO"])
        perto = abaixo & (yy < borda_y + 9 * K)
        pena = lugar & (queixo > 0) & ~perto
        ar = lugar & (queixo == 0) & ~perto
        base[perto & lugar, :3] = (40, 28, 70)
        hsv_b = cv2.cvtColor(base[..., :3], cv2.COLOR_BGR2HSV)
        pena_px = (hsv_b[..., 2] > 140) & (hsv_b[..., 1] < 70) & (base[..., 3] > 200)
        conhecido = pena_px & ~cv2.dilate(lugar.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        cheio = preencher(base, pena, conhecido, 4.0 * K)
        k = cv2.GaussianBlur(pena.astype(np.float32), (0, 0), 0.8)[..., None]
        base[..., :3] = (base[..., :3] * (1 - k) + cheio[..., :3] * k).astype(np.uint8)
        base[ar, 3] = 0
        pts = (np.array(C["QUEIXO_BORDA"], np.float32) * 16).astype(np.int32)
        cv2.polylines(base, [pts], False, CONTORNO + (255,), max(3, int(4 * K)), cv2.LINE_AA, shift=4)
        # bico de cima recortado no contorno real
        laranja = (hsv[..., 0] >= 5) & (hsv[..., 0] <= 35) & (hsv[..., 1] > 90) & (hsv[..., 2] > 120)
        contorno_px = hsv[..., 2] < 60
        faixa_b = (yy >= borda_y - 3 * K) & (yy <= borda_y + 12 * K)
        x0b, y0b, x1b, y1b = regiao_boca
        dentro_b = (xx >= x0b) & (xx < x1b) & (yy >= y0b) & (yy < y1b)
        bico_m = ((yy < borda_y - 3 * K) | (faixa_b & (laranja | contorno_px))) & dentro_b
        bico_a = cv2.GaussianBlur(bico_m.astype(np.float32), (0, 0), 0.5) * (yy < borda_y + 13 * K) * (base_orig[..., 3] / 255.0)
        bico_sup = np.dstack([img, (bico_a * 255).astype(np.uint8)])

    # pesos
    s = linha(C["COLARINHO"], xx) - yy
    w_cab = suave((s + 12 * K) / (48.0 * K)) * suave((C["LIMITE_CABECA_X"] - xx) / (50.0 * K))
    w_bra = np.zeros((h, w), np.float32)
    if C.get("BRACO_A"):
        (ax, ay), (bx, by) = C["BRACO_A"], C["BRACO_B"]
        nrm = np.hypot(bx - ax, by - ay)
        lado = ((bx - ax) * (yy - ay) - (by - ay) * (xx - ax)) / nrm
        w_bra = suave((-lado + 8 * K) / (46.0 * K)) * suave((C["BRACO_Y_MAX"] - yy) / (30.0 * K)) * (xx > C["BRACO_X_MIN"])
        # o canto da cabeça/bico (à esquerda e acima) nunca vai junto com o braço
        w_bra *= 1 - (1 - suave((xx - C["BRACO_PROTEGE_X"]) / (20.0 * K))) * (1 - suave((yy - C["BRACO_Y_MIN"]) / (20.0 * K)))
    sob = poli_mask(base.shape, C["SOBRANCELHA"])
    w_sob = suave(1 - cv2.distanceTransform((1 - sob).astype(np.uint8), cv2.DIST_L2, 5) / (16.0 * K))
    ol = poli_mask(base.shape, C["OLHO_ESQ_POLI"])
    w_olho = suave(1 - cv2.distanceTransform((1 - ol).astype(np.uint8), cv2.DIST_L2, 5) / (10.0 * K))

    f16 = lambda m: m.astype(np.float16)
    cv2.imwrite(os.path.join(saida, "base.png"), base)
    cv2.imwrite(os.path.join(saida, "mandibula.png"), mandibula)
    cv2.imwrite(os.path.join(saida, "bico_sup.png"), bico_sup)
    olhos = {}
    for lado_o, poli in (("esq", C["OLHO_ESQ_POLI"]), ("dir", C["OLHO_DIR_POLI"])):
        o = olho_fechado(base_orig, poli, dil=max(2, int(3 * K)) if lado_o == "esq" else max(2, int(2 * K)), escuro=lado_o == "dir",
                         sobrancelha=C["SOBRANCELHA"] if lado_o == "esq" else None)
        for k_, v_ in o.items():
            olhos[f"{lado_o}_{k_}"] = np.array(v_)
    np.savez_compressed(os.path.join(saida, "olhos.npz"), **olhos)
    np.savez_compressed(os.path.join(saida, "pesos.npz"), cabeca=f16(w_cab), braco=f16(w_bra), sobrancelha=f16(w_sob), olho=f16(w_olho))
    cen = np.array(C["OLHO_ESQ_POLI"], np.float32).mean(axis=0)
    json.dump(dict(tamanho=[w, h], K=K, boca=bool(tem_boca), braco=bool(C.get("BRACO_A")),
                   pivo_cabeca=list(C["PIVO_CABECA"]), pivo_braco=list(C.get("PIVO_BRACO") or [0, 0]),
                   dobradica=list(C["DOBRADICA"]), ponta_bico=list(C["PONTA_BICO"]), regiao_boca=regiao_boca,
                   regiao_braco=[int(C.get("BRACO_X_MIN", 0)), 0, w, int(C.get("BRACO_Y_MAX", h)) + 10] if C.get("BRACO_A") else [0, 0, 1, 1],
                   angulo_fechado=C.get("ANGULO_FECHADO", 20.0), pivo_sobrancelha=list(C["PIVO_SOBRANCELHA"]),
                   centro_olho=[float(cen[0]), float(cen[1])]),
              open(os.path.join(saida, "rig.json"), "w"), indent=1)
    print("rig", nome, "ok")


# ------------------------------------------------------------------ transporte das marcações
def sift_transform(ref, alvo, caixa_ref):
    """Similaridade (escala, giro, translação) que leva a cabeça de 'ref' para 'alvo'."""
    g1 = cv2.cvtColor(ref[..., :3], cv2.COLOR_BGR2GRAY); g2 = cv2.cvtColor(alvo[..., :3], cv2.COLOR_BGR2GRAY)
    m1 = np.zeros(g1.shape, np.uint8); x0, y0, x1, y1 = caixa_ref; m1[y0:y1, x0:x1] = 255
    m2 = (alvo[..., 3] > 0).astype(np.uint8) * 255
    m2[int(alvo.shape[0] * 0.62):] = 0                     # a cabeça está na parte de cima
    sift = cv2.SIFT_create(4000)
    k1, d1 = sift.detectAndCompute(g1, m1); k2, d2 = sift.detectAndCompute(g2, m2)
    bf = cv2.BFMatcher()
    pares = [m for m, n in bf.knnMatch(d1, d2, k=2) if m.distance < 0.72 * n.distance]
    p1 = np.float32([k1[m.queryIdx].pt for m in pares]); p2 = np.float32([k2[m.trainIdx].pt for m in pares])
    M, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=4.0, maxIters=5000)
    return M, int(inl.sum()) if inl is not None else 0


def transportar(C, M):
    T = lambda p: [float(M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2]), float(M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2])]
    esc = float(np.hypot(M[0, 0], M[1, 0]))
    D = {k: v for k, v in C.items() if k not in PONTOS + UM_PONTO}
    for k in PONTOS:
        if C.get(k) is None:
            continue
        if k in ("BRACO_A", "BRACO_B"):
            continue
        pts = [T(p) for p in C[k]]
        if k in ("COLARINHO", "BICO_BORDA"):     # linhas que precisam ir de ponta a ponta da imagem
            pts = sorted(pts)
            pts = [[-5000, pts[0][1]]] + pts + [[50000, pts[-1][1]]]
        D[k] = pts
    for k in UM_PONTO:
        if C.get(k) is not None:
            D[k] = T(C[k])
    D["K"] = C.get("K", 1.0) * esc
    D["LIMITE_CABECA_X"] = T((C["LIMITE_CABECA_X"], C["PIVO_CABECA"][1]))[0]
    D["BRACO_A"] = None
    D["escala_cabeca"] = esc
    return D


MARGEM = 160   # espaço em volta para a mão/cabeça não saírem da imagem ao girar


def com_margem(im):
    return cv2.copyMakeBorder(im, MARGEM, 0, MARGEM, MARGEM, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))


def deslocar(C, d):
    D = {}
    for k, v in C.items():
        if k in PONTOS and v is not None:
            D[k] = [[p[0] + d, p[1] + d] for p in v] if isinstance(v[0], (list, tuple)) else [v[0] + d, v[1] + d]
        elif k in UM_PONTO and v is not None:
            D[k] = [v[0] + d, v[1] + d]
        elif k in ("LIMITE_CABECA_X", "BRACO_Y_MAX", "BRACO_X_MIN", "BRACO_Y_MIN", "BRACO_PROTEGE_X"):
            D[k] = v + d
        elif k == "CAIXA_CABECA":
            D[k] = [x + d for x in v]
        else:
            D[k] = v
    return D


def main():
    cfgs = json.load(open(os.path.join(AQUI, "poses.json")))
    ref_nome = "apresenta"
    ref = com_margem(cv2.imread(os.path.join(HD, ref_nome + ".png"), cv2.IMREAD_UNCHANGED))
    C = deslocar(cfgs[ref_nome], MARGEM)
    preparar(ref_nome, ref, C, os.path.join(SAIDA, ref_nome))
    rj = os.path.join(SAIDA, ref_nome, "rig.json"); r_ = json.load(open(rj)); r_["M_de_apresenta"] = [[1, 0, 0], [0, 1, 0]]
    json.dump(r_, open(rj, "w"), indent=1)
    escalas = {ref_nome: 1.0}
    for nome, extra in cfgs.items():
        if nome == ref_nome:
            continue
        alvo = com_margem(cv2.imread(os.path.join(HD, nome + ".png"), cv2.IMREAD_UNCHANGED))
        M, n = sift_transform(ref, alvo, C["CAIXA_CABECA"])
        D = transportar(C, M)
        D.update({k: v for k, v in extra.items()})
        print(nome, "pontos casados:", n, "escala", round(D["escala_cabeca"], 3))
        preparar(nome, alvo, D, os.path.join(SAIDA, nome))
        escalas[nome] = D["escala_cabeca"]
        rj = os.path.join(SAIDA, nome, "rig.json"); r_ = json.load(open(rj)); r_["M_de_apresenta"] = M.tolist()
        json.dump(r_, open(rj, "w"), indent=1)
    json.dump(escalas, open(os.path.join(SAIDA, "escalas.json"), "w"), indent=1)
    sys.path.insert(0, AQUI)
    from preparar_poses import logo_bbox
    logos = {}
    for nome in ("microfone", "tablet"):
        im = com_margem(cv2.imread(os.path.join(HD, nome + ".png"), cv2.IMREAD_UNCHANGED))
        logos[nome] = logo_bbox(im)
    json.dump(logos, open(os.path.join(SAIDA, "logos.json"), "w"))


if __name__ == "__main__":
    main()
