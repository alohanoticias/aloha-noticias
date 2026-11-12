"""Recorta as posições de ação da folha de personagem e prepara para o vídeo.

Gera poses/<nome>.png (fundo transparente, ampliadas para o tamanho do mascote).
Na pose de braços cruzados as mãos vêm amarelas na folha: aqui viram luva preta,
como nas outras referências.
Uso: python3 preparar_poses.py [folha-de-personagem.png]
"""
import os, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "poses")
REGIOES = {   # na folha 1536x1024
    "microfone": (240, 830, 445, 1024),
    "aponta_tela": (430, 830, 600, 1024),
    "tablet": (580, 830, 770, 1024),
    "braco_cruzado": (750, 830, 925, 1024),
    "apresenta": (900, 830, 1095, 1024),
    "joinha": (1050, 830, 1235, 1024),
}
AMPLIA = 5.0


def recortar(folha, caixa):
    x0, y0, x1, y1 = caixa
    c = folha[y0:y1, x0:x1].copy()
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    fundo = ((hsv[..., 2] > 200) & (hsv[..., 1] < 40)).astype(np.uint8)
    h, w = fundo.shape
    ff = np.pad(fundo, 1, constant_values=1)
    cv2.floodFill(ff, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 2)
    fg = (ff[1:-1, 1:-1] != 2).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    fg = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
    return c, fg


def luvas_pretas(c, fg):
    """Mãos amarelas (só na metade de baixo, longe do bico) -> luva preta com o mesmo sombreado."""
    h, w = fg.shape
    hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
    amarelo = (hsv[..., 0] >= 8) & (hsv[..., 0] <= 38) & (hsv[..., 1] > 80) & (hsv[..., 2] > 90)
    yy = np.arange(h)[:, None]
    mao = amarelo & (yy > h * 0.52) & (fg > 0)
    mao = cv2.dilate(mao.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (fg > 0)
    lum = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY).astype(np.float32)
    v = 18 + (lum / 255.0) ** 1.6 * 95
    luva = np.dstack([v * 1.04, v * 0.96, v * 1.02]).clip(0, 255).astype(np.uint8)
    out = c.copy(); out[mao] = luva[mao]
    return out


def ampliar(c, fg):
    big = cv2.resize(c, None, fx=AMPLIA, fy=AMPLIA, interpolation=cv2.INTER_LANCZOS4)
    big = cv2.bilateralFilter(big, 7, 28, 7)                       # chapa as cores como desenho
    borr = cv2.GaussianBlur(big, (0, 0), 2.2)
    big = cv2.addWeighted(big, 1.7, borr, -0.7, 0)                  # devolve nitidez ao contorno
    a = cv2.resize(cv2.erode(fg * 255, np.ones((2, 2), np.uint8)), None, fx=AMPLIA, fy=AMPLIA,
                   interpolation=cv2.INTER_CUBIC)
    a = cv2.GaussianBlur(a, (0, 0), 1.2)
    a = np.clip((a.astype(np.float32) - 60) * 1.5, 0, 255).astype(np.uint8)
    # borda escura (sem halo claro do fundo branco da folha)
    dentro = cv2.erode((a > 128).astype(np.uint8), np.ones((7, 7), np.uint8))
    faixa = ((a > 0) & (dentro == 0))[..., None]
    lum = big.astype(np.float32).mean(axis=2, keepdims=True)
    k = np.clip((lum - 60) / 110, 0, 1) * faixa
    big = (big * (1 - k) + np.array([29, 23, 26]) * k).astype(np.uint8)
    return np.dstack([big, a])


def logo_bbox(rgba):
    """Caixa do emblema "e" (vermelho com branco dentro) — para desespelhar quando a pose vira."""
    hsv = cv2.cvtColor(rgba[..., :3], cv2.COLOR_BGR2HSV)
    red = (((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 120) & (hsv[..., 2] > 90)).astype(np.uint8)
    white = (hsv[..., 2] > 200) & (hsv[..., 1] < 40)
    n, lab, st, _ = cv2.connectedComponentsWithStats(red)
    melhor, nota = None, 0
    h = rgba.shape[0]
    for i in range(1, n):
        x, y, w, hh, a = st[i]
        if a < 400 or y < h * 0.4:
            continue
        wi = white[y:y + hh, x:x + w].mean()
        if wi > nota:
            melhor, nota = (int(x), int(y), int(x + w), int(y + hh)), wi
    return melhor


def main(folha_p):
    import json
    os.makedirs(SAIDA, exist_ok=True)
    hd = os.path.join(AQUI, "referencias", "poses-hd")
    logos = {}
    for nome in REGIOES:
        p = os.path.join(hd, nome + ".png")
        if os.path.exists(p):           # arte em alta (preferida)
            im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            ys, xs = np.where(im[..., 3] > 10)
            im = im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            cv2.imwrite(os.path.join(SAIDA, nome + ".png"), im)
            if nome in ("microfone", "tablet"):
                logos[nome] = logo_bbox(im)
            print("pose HD", nome, im.shape[:2])
    json.dump(logos, open(os.path.join(SAIDA, "logos.json"), "w"))
    folha = cv2.imread(folha_p)
    for nome, caixa in REGIOES.items():
        if os.path.exists(os.path.join(hd, nome + ".png")):
            continue
        c, fg = recortar(folha, caixa)
        if nome == "braco_cruzado":
            c = luvas_pretas(c, fg)
        ys, xs = np.where(fg)
        c, fg = c[ys.min():, xs.min():xs.max() + 1], fg[ys.min():, xs.min():xs.max() + 1]
        cv2.imwrite(os.path.join(SAIDA, nome + ".png"), ampliar(c, fg))
        print("pose", nome)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "referencias", "folha-de-personagem.png"))
