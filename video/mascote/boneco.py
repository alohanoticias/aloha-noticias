"""Animação do mascote por deformação contínua (sem camadas recortadas).

    b = Boneco(pasta_rig, escala=0.95)
    img = b.quadro(boca=0.7, piscada=0.0, cabeca=2.0, braco=-5.0)   # PIL RGBA

boca: 1 = bico aberto como na arte, 0 = fechado. piscada: 0 aberto .. 1 fechado.
cabeca/braco: graus (positivo = anti-horário: bico para cima / mão para cima).
"""
import json, math, os
import cv2
import numpy as np
from PIL import Image


class Boneco:
    def __init__(self, pasta, escala=1.0):
        self.s = s = escala
        rig = json.load(open(os.path.join(pasta, "rig.json")))
        base = cv2.imread(os.path.join(pasta, "base.png"), cv2.IMREAD_UNCHANGED)
        W, H = int(rig["tamanho"][0] * s), int(rig["tamanho"][1] * s)
        self.W, self.H = W, H
        self.base = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)
        p = np.load(os.path.join(pasta, "pesos.npz"))
        rs = lambda m: cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        self.w_cab, self.w_bra = rs(p["cabeca"]), rs(p["braco"])
        self.mand = cv2.resize(cv2.imread(os.path.join(pasta, "mandibula.png"), cv2.IMREAD_UNCHANGED), (W, H),
                               interpolation=cv2.INTER_AREA)
        self.acima = rs(p["acima_bico"])
        sc = lambda v: [x * s for x in v]
        self.pc, self.pb, self.dob = sc(rig["pivo_cabeca"]), sc(rig["pivo_braco"]), sc(rig["dobradica"])
        self.rb = [int(v * s) for v in rig["regiao_boca"]]
        self.rbr = [int(v * s) for v in rig["regiao_braco"]]
        self.ang_fechado = rig["angulo_fechado"]
        self.olhos = []
        for k in ("olho_esq", "olho_dir"):
            o = rig[k]
            self.olhos.append(dict(c=sc(o["c"]), r=sc(o["r"]), ang=o["ang"], cor=o["cor"]))
        self.gx, self.gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        ys = np.where(self.w_cab.max(axis=1) > 0.001)[0]
        self.lim_cab = int(ys.max()) + 2 if len(ys) else 0
        self.rb[3] = min(self.rb[3], self.lim_cab)

    # ------------------------------------------------------------------
    @staticmethod
    def _inverso(tx, ty, c, graus, peso, iters=4):
        """Acha a origem s de cada ponto t para F(s) = c + R(graus*peso(s))(s - c)."""
        h, w = peso.shape
        dx, dy = tx - c[0], ty - c[1]
        sx, sy = tx.copy(), ty.copy()
        k = math.radians(graus)
        for _ in range(iters):
            ix = np.clip(sx + 0.5, 0, w - 1).astype(np.int32)
            iy = np.clip(sy + 0.5, 0, h - 1).astype(np.int32)
            a = -k * peso[iy, ix]
            ca, sa = np.cos(a), np.sin(a)
            # rotação anti-horária na tela (y para baixo)
            sx = c[0] + ca * dx + sa * dy
            sy = c[1] - sa * dx + ca * dy
        return sx, sy

    def _palpebra(self, img, o, b):
        """Pálpebra que desce pela curva do olho; fechada vira um arco (olho fechado sorrindo)."""
        if b <= 0.02:
            return
        cx, cy = o["c"]; rx, ry = o["r"]; ang = math.radians(o["ang"])
        rx2, ry2 = rx + 5 * self.s, ry + 6 * self.s
        x0, x1 = int(cx - rx2 - 4), int(cx + rx2 + 5)
        y0, y1 = int(cy - ry2 - 4), int(cy + ry2 + 5)
        gx, gy = self.gx[y0:y1, x0:x1] - cx, self.gy[y0:y1, x0:x1] - cy
        u = gx * math.cos(ang) + gy * math.sin(ang)
        v = -gx * math.sin(ang) + gy * math.cos(ang)
        q = np.sqrt(np.clip(1 - (u / rx2) ** 2, 0, 1))
        dist_el = (u / rx2) ** 2 + (v / ry2) ** 2
        dentro = np.clip((1 - dist_el) * ry2 / 2.0, 0, 1)            # borda suave da elipse
        e_linha = 2 * (b * 0.8) - 1                                   # onde fica o cílio
        e_cobre = e_linha if b < 0.9 else e_linha + (1 - e_linha) * (b - 0.9) / 0.1
        borda = e_cobre * ry2 * q
        suav = np.clip((borda - v) / 1.5 + 0.5, 0, 1) * dentro
        reg = img[y0:y1, x0:x1].astype(np.float32)
        cor = np.array(o["cor"][::-1] + [255], np.float32)
        reg = reg * (1 - suav[..., None]) + cor * suav[..., None]
        img[y0:y1, x0:x1] = reg.astype(np.uint8)
        pts = []
        for i in range(29):
            uu = -rx * 1.02 + 2 * rx * 1.02 * i / 28
            vv = e_linha * ry2 * math.sqrt(max(0, 1 - (uu / rx2) ** 2))
            pts.append((cx + uu * math.cos(ang) - vv * math.sin(ang), cy + uu * math.sin(ang) + vv * math.cos(ang)))
        pts = (np.array(pts) * 16).astype(np.int32)
        cv2.polylines(img, [pts], False, (29, 23, 26, 255), max(2, int(round(5 * self.s))), cv2.LINE_AA, shift=4)

    def _bico(self, src, graus):
        """Gira a mandíbula (peça com contorno próprio) na dobradiça e encaixa sob o bico de cima."""
        x0, y0, x1, y1 = self.rb
        cx, cy = self.dob[0] - x0, self.dob[1] - y0
        M = cv2.getRotationMatrix2D((cx, cy), graus, 1.0)
        reg_m = self.mand[y0:y1, x0:x1]
        rot = cv2.warpAffine(reg_m, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)).astype(np.float32)
        visivel = (1 - self.acima[y0:y1, x0:x1])[..., None]
        a = rot[..., 3:] / 255 * visivel
        reg = src[y0:y1, x0:x1].astype(np.float32)
        # sombra suave da mandíbula sobre o queixo
        sh = cv2.GaussianBlur(a[..., 0], (0, 0), 3 * self.s)
        sh = np.roll(sh, int(4 * self.s), axis=0)[..., None] * 0.28 * visivel * (reg[..., 3:] / 255)
        reg[..., :3] *= (1 - sh)
        reg[..., :3] = reg[..., :3] * (1 - a) + rot[..., :3] * a
        reg[..., 3:] = np.maximum(reg[..., 3:], a * 255)
        src[y0:y1, x0:x1] = reg.astype(np.uint8)

    def ponta_bico(self, cabeca=0.0):
        """Ponta do bico (coordenadas do quadro) para a cabeça girada 'cabeca' graus."""
        px, py = 548 * self.s, 352 * self.s
        c = self.pc; k = math.radians(cabeca)
        dx, dy = px - c[0], py - c[1]
        return c[0] + math.cos(k) * dx + math.sin(k) * dy, c[1] - math.sin(k) * dx + math.cos(k) * dy

    def quadro(self, boca=1.0, piscada=0.0, cabeca=0.0, braco=0.0):
        src = self.base.copy()
        self._bico(src, self.ang_fechado * (1 - min(1.15, max(0, boca))))
        for o in self.olhos:
            self._palpebra(src, o, min(1, max(0, piscada)))
        mx, my = self.gx.copy(), self.gy.copy()
        # cabeça (+ bico dentro dela)
        L = self.lim_cab
        tx, ty = self.gx[:L], self.gy[:L]
        if abs(cabeca) > 0.01:
            sx, sy = self._inverso(tx, ty, self.pc, cabeca, self.w_cab)
        else:
            sx, sy = tx.copy(), ty.copy()
        mx[:L], my[:L] = sx, sy
        # antebraço
        if abs(braco) > 0.01:
            x0, y0, x1, y1 = self.rbr
            nx, ny = self._inverso(self.gx[y0:y1, x0:x1], self.gy[y0:y1, x0:x1], self.pb, braco, self.w_bra)
            mx[y0:y1, x0:x1], my[y0:y1, x0:x1] = nx, ny
        out = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

        return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGRA2RGBA))
