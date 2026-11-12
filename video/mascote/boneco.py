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
        self.w_sob = rs(p["sobrancelha"]) if "sobrancelha" in p else None
        self.w_olho = rs(p["olho"]) if "olho" in p else None
        self.bico_sup = cv2.resize(cv2.imread(os.path.join(pasta, "bico_sup.png"), cv2.IMREAD_UNCHANGED), (W, H),
                                   interpolation=cv2.INTER_AREA)
        ol = np.load(os.path.join(pasta, "olhos.npz"))
        self.olhos_rec = []
        for nome in ("esq", "dir"):
            d = {k: ol[f"{nome}_{k}"] for k in ("x0", "y0", "mask", "pele", "topo", "fundo")}
            if s != 1.0:
                hh, ww = d["mask"].shape
                nw, nh = max(2, int(ww * s)), max(2, int(hh * s))
                d["mask"] = cv2.resize(d["mask"], (nw, nh), interpolation=cv2.INTER_NEAREST)
                d["pele"] = cv2.resize(d["pele"], (nw, nh), interpolation=cv2.INTER_AREA)
                xs = np.linspace(0, ww - 1, nw)
                d["topo"] = np.interp(xs, np.arange(ww), d["topo"]) * s
                d["fundo"] = np.interp(xs, np.arange(ww), d["fundo"]) * s
                d["x0"], d["y0"] = d["x0"] * s, d["y0"] * s
            d["x0"], d["y0"] = int(round(float(d["x0"]))), int(round(float(d["y0"])))
            self.olhos_rec.append(d)
        self.mand = cv2.resize(cv2.imread(os.path.join(pasta, "mandibula.png"), cv2.IMREAD_UNCHANGED), (W, H),
                               interpolation=cv2.INTER_AREA)
        self.acima = rs(p["acima_bico"])
        sc = lambda v: [x * s for x in v]
        self.pc, self.pb, self.dob = sc(rig["pivo_cabeca"]), sc(rig["pivo_braco"]), sc(rig["dobradica"])
        self.rb = [int(v * s) for v in rig["regiao_boca"]]
        self.rbr = [int(v * s) for v in rig["regiao_braco"]]
        self.ang_fechado = rig["angulo_fechado"]
        self.piv_sob = [v * s for v in rig.get("pivo_sobrancelha", [300, 168])]
        self.c_olho = [v * s for v in rig.get("centro_olho", [355, 213])]
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

    def _piscar(self, img, d, b):
        """Pálpebra: a pele reconstruída desce do topo do olho até a linha de olho fechado,
        com um cílio que afina nas pontas. Em b=1 o olho inteiro vira pele + cílio curvo."""
        if b <= 0.02:
            return
        x0, y0, m, pele = d["x0"], d["y0"], d["mask"], d["pele"]
        h, w = m.shape
        topo, fundo = d["topo"], d["fundo"]
        cols = np.where(topo >= 0)[0]
        if not len(cols):
            return
        fech = topo + 0.66 * (fundo - topo)          # onde fica o cílio com o olho fechado
        borda = topo + min(1, b) * (fech - topo)     # borda da pálpebra agora
        yy = np.arange(h, dtype=np.float32)[:, None]
        cobre = np.clip(borda[None, :] - yy + 0.5, 0, 1) * (topo[None, :] >= 0)
        if b > 0.85:                                  # no fim cobre também o resto do olho
            cobre = np.maximum(cobre, (b - 0.85) / 0.15 * np.ones_like(cobre))
        mm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.7)
        k = (cobre * mm)[..., None]
        reg = img[y0:y0 + h, x0:x0 + w].astype(np.float32)
        p = pele.astype(np.float32)
        reg[..., :3] = reg[..., :3] * (1 - k) + p[..., :3] * k
        # cílio: curva da borda, mais grosso no meio, fino nas pontas (desenhado em 4x)
        S = 4
        cam = np.zeros((h * S, w * S), np.uint8)
        c0, c1 = cols.min() + 1, cols.max() - 1
        sup, inf = [], []
        for x in range(c0, c1 + 1):
            u = (x - c0) / max(1, c1 - c0)
            esp = (0.6 + 2.6 * math.sin(math.pi * u) ** 0.7) * max(0.6, self.s) * (0.55 + 0.45 * min(1, b))
            y = borda[x]
            sup.append((x * S, (y - esp / 2) * S)); inf.append((x * S, (y + esp / 2) * S))
        poli = np.array(sup + inf[::-1], np.int32)
        cv2.fillPoly(cam, [poli], 255, cv2.LINE_AA)
        cam = cv2.resize(cam, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
        cor = np.array([28, 22, 26], np.float32)
        reg[..., :3] = reg[..., :3] * (1 - cam) + cor * cam
        img[y0:y0 + h, x0:x0 + w] = reg.astype(np.uint8)

    def _bico(self, src, graus):
        """Gira a mandíbula na dobradiça; o bico de cima (recorte exato) vai por cima."""
        x0, y0, x1, y1 = self.rb
        cx, cy = self.dob[0] - x0, self.dob[1] - y0
        M = cv2.getRotationMatrix2D((cx, cy), graus, 1.0)
        rot = cv2.warpAffine(self.mand[y0:y1, x0:x1], M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)).astype(np.float32)
        a = rot[..., 3:] / 255
        reg = src[y0:y1, x0:x1].astype(np.float32)
        if graus > 0.5:   # sombra suave da mandíbula sobre o queixo
            sh = cv2.GaussianBlur(a[..., 0], (0, 0), 3 * self.s)
            sh = np.roll(sh, int(4 * self.s), axis=0)[..., None] * 0.25 * (reg[..., 3:] / 255) * min(1, graus / 6)
            reg[..., :3] *= (1 - sh)
        reg[..., :3] = reg[..., :3] * (1 - a) + rot[..., :3] * a
        reg[..., 3:] = np.maximum(reg[..., 3:], a * 255)
        bs = self.bico_sup[y0:y1, x0:x1].astype(np.float32)
        ab = bs[..., 3:] / 255
        reg[..., :3] = reg[..., :3] * (1 - ab) + bs[..., :3] * ab
        reg[..., 3:] = np.maximum(reg[..., 3:], bs[..., 3:])
        src[y0:y1, x0:x1] = reg.astype(np.uint8)

    def ponta_bico(self, cabeca=0.0):
        """Ponta do bico (coordenadas do quadro) para a cabeça girada 'cabeca' graus."""
        px, py = 548 * self.s, 352 * self.s
        c = self.pc; k = math.radians(cabeca)
        dx, dy = px - c[0], py - c[1]
        return c[0] + math.cos(k) * dx + math.sin(k) * dy, c[1] - math.sin(k) * dx + math.cos(k) * dy

    def _expressao(self, sx, sy, sob_y=0.0, sob_rot=0.0, olho_esc=1.0):
        """Desloca a sobrancelha (sobe/desce e inclina) e aumenta o olho — deformação suave do
        próprio desenho, sem colagem. Recebe/devolve as coordenadas de origem (mapa inverso)."""
        if self.w_sob is None or (abs(sob_y) < 0.05 and abs(sob_rot) < 0.05 and abs(olho_esc - 1) < 0.003):
            return sx, sy
        h, w = self.w_sob.shape
        ix = np.clip(sx + 0.5, 0, w - 1).astype(np.int32); iy = np.clip(sy + 0.5, 0, h - 1).astype(np.int32)
        ws, wo = self.w_sob[iy, ix], self.w_olho[iy, ix]
        k = math.radians(sob_rot)
        dx, dy = sx - self.piv_sob[0], sy - self.piv_sob[1]
        rx = self.piv_sob[0] + math.cos(-k) * dx + math.sin(-k) * dy
        ry = self.piv_sob[1] - math.sin(-k) * dx + math.cos(-k) * dy
        nx = sx + ws * (rx - sx); ny = sy + ws * (ry - sy + sob_y * self.s)
        ex = self.c_olho[0] + (nx - self.c_olho[0]) / olho_esc
        ey = self.c_olho[1] + (ny - self.c_olho[1]) / olho_esc
        nx = nx + wo * (ex - nx); ny = ny + wo * (ey - ny)
        return nx, ny

    def quadro(self, boca=1.0, piscada=0.0, cabeca=0.0, braco=0.0, sob_y=0.0, sob_rot=0.0, olho_esc=1.0):
        src = self.base.copy()
        self._bico(src, self.ang_fechado * (1 - min(1.15, max(0, boca))))
        for d in self.olhos_rec:
            self._piscar(src, d, min(1, max(0, piscada)))
        mx, my = self.gx.copy(), self.gy.copy()
        # cabeça (+ bico dentro dela)
        L = self.lim_cab
        tx, ty = self.gx[:L], self.gy[:L]
        if abs(cabeca) > 0.01:
            sx, sy = self._inverso(tx, ty, self.pc, cabeca, self.w_cab)
        else:
            sx, sy = tx.copy(), ty.copy()
        sx, sy = self._expressao(sx, sy, sob_y, sob_rot, olho_esc)
        mx[:L], my[:L] = sx, sy
        # antebraço
        if abs(braco) > 0.01:
            x0, y0, x1, y1 = self.rbr
            nx, ny = self._inverso(self.gx[y0:y1, x0:x1], self.gy[y0:y1, x0:x1], self.pb, braco, self.w_bra)
            mx[y0:y1, x0:x1], my[y0:y1, x0:x1] = nx, ny
        out = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

        return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGRA2RGBA))
