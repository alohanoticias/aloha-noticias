"""Animação do mascote por deformação contínua (sem camadas recortadas aparentes).

    b = Boneco("rig/apresenta", escala=0.8)
    img = b.quadro(boca=0.7, piscada=0.0, cabeca=2.0, braco=-5.0, sob_y=0, sob_rot=0, olho_esc=1)

boca: 1 = bico aberto como na arte, 0 = fechado. piscada: 0 aberto .. 1 fechado.
cabeca/braco: graus (positivo = anti-horário: bico para cima / mão para cima).
sob_y / sob_rot / olho_esc: expressão (sobrancelha sobe/desce e inclina, olho abre mais).
"""
import json, math, os
import cv2
import numpy as np
from PIL import Image


class Boneco:
    def __init__(self, pasta, escala=1.0):
        self.s = s = escala
        rig = json.load(open(os.path.join(pasta, "rig.json")))
        self.rig = rig
        W, H = int(rig["tamanho"][0] * s), int(rig["tamanho"][1] * s)
        self.W, self.H = W, H
        ld = lambda n: cv2.resize(cv2.imread(os.path.join(pasta, n), cv2.IMREAD_UNCHANGED), (W, H), interpolation=cv2.INTER_AREA)
        self.base, self.mand, self.bico_sup = ld("base.png"), ld("mandibula.png"), ld("bico_sup.png")
        p = np.load(os.path.join(pasta, "pesos.npz"))
        rs = lambda m: cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
        self.w_cab, self.w_bra, self.w_sob, self.w_olho = rs(p["cabeca"]), rs(p["braco"]), rs(p["sobrancelha"]), rs(p["olho"])
        sc = lambda v: [x * s for x in v]
        self.pc, self.pb, self.dob = sc(rig["pivo_cabeca"]), sc(rig["pivo_braco"]), sc(rig["dobradica"])
        self.ponta = sc(rig["ponta_bico"])
        self.rb = [int(v * s) for v in rig["regiao_boca"]]
        self.rbr = [int(v * s) for v in rig["regiao_braco"]]
        self.tem_boca, self.tem_braco = rig["boca"], rig["braco"]
        self.ang_fechado = rig["angulo_fechado"]
        self.piv_sob, self.c_olho = sc(rig["pivo_sobrancelha"]), sc(rig["centro_olho"])
        self.K = rig.get("K", 1.0) * s
        ol = np.load(os.path.join(pasta, "olhos.npz"))
        self.olhos = []
        for nome in ("esq", "dir"):
            d = {k: ol[f"{nome}_{k}"] for k in ("x0", "y0", "mask", "pele", "topo", "fundo")}
            hh, ww = d["mask"].shape
            nw, nh = max(2, int(ww * s)), max(2, int(hh * s))
            d["mask"] = cv2.resize(d["mask"], (nw, nh), interpolation=cv2.INTER_NEAREST)
            d["pele"] = cv2.resize(d["pele"], (nw, nh), interpolation=cv2.INTER_AREA)
            xs = np.linspace(0, ww - 1, nw)
            d["topo"] = np.where(np.interp(xs, np.arange(ww), d["topo"]) >= 0, np.interp(xs, np.arange(ww), d["topo"]) * s, -1)
            d["fundo"] = np.interp(xs, np.arange(ww), d["fundo"]) * s
            d["x0"], d["y0"] = int(round(float(d["x0"]) * s)), int(round(float(d["y0"]) * s))
            d["tras"] = nome == "dir"
            self.olhos.append(d)
        self.bocas = None
        bp = os.path.join(pasta, "bocas.npz")
        if os.path.exists(bp):
            bz = np.load(bp)
            bx0, by0 = int(bz["x0"]), int(bz["y0"])
            self.bocas = []
            for i in range(1, 9):
                b, m = bz[f"b{i}"], bz[f"m{i}"].astype(np.float32)
                nw, nh = max(2, int(b.shape[1] * s)), max(2, int(b.shape[0] * s))
                self.bocas.append((cv2.resize(b, (nw, nh), interpolation=cv2.INTER_AREA).astype(np.float32),
                                   cv2.resize(m, (nw, nh), interpolation=cv2.INTER_LINEAR)[..., None]))
            self.boca_xy = (int(round(bx0 * s)), int(round(by0 * s)))
        self.olhos_d = None
        op = os.path.join(pasta, "olhos_desenho.npz")
        if os.path.exists(op):
            oz = np.load(op)
            rs2 = lambda a: cv2.resize(a, (max(2, int(a.shape[1] * s)), max(2, int(a.shape[0] * s))), interpolation=cv2.INTER_AREA).astype(np.float32)
            self.olhos_d = dict(xy=(int(round(int(oz["x0"]) * s)), int(round(int(oz["y0"]) * s))),
                                limpo=rs2(oz["limpo"]), cam=[rs2(oz[f"o{i}"]) for i in range(1, 9)])
        self.gx, self.gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        ys = np.where(self.w_cab.max(axis=1) > 0.001)[0]
        self.lim_cab = int(ys.max()) + 2 if len(ys) else 0
        self.rb[3] = min(self.rb[3], H)

    # ------------------------------------------------------------------
    @staticmethod
    def _inverso(tx, ty, c, graus, peso, iters=4):
        h, w = peso.shape
        dx, dy = tx - c[0], ty - c[1]
        sx, sy = tx.copy(), ty.copy()
        k = math.radians(graus)
        for _ in range(iters):
            ix = np.clip(sx + 0.5, 0, w - 1).astype(np.int32)
            iy = np.clip(sy + 0.5, 0, h - 1).astype(np.int32)
            a = -k * peso[iy, ix]
            ca, sa = np.cos(a), np.sin(a)
            sx = c[0] + ca * dx + sa * dy
            sy = c[1] - sa * dx + ca * dy
        return sx, sy

    def _piscar(self, img, d, b):
        if b <= 0.02:
            return
        x0, y0, m, pele = d["x0"], d["y0"], d["mask"], d["pele"]
        h, w = m.shape
        h = min(h, img.shape[0] - y0); w = min(w, img.shape[1] - x0)
        m, pele = m[:h, :w], pele[:h, :w]
        topo, fundo = d["topo"][:w], d["fundo"][:w]
        cols = np.where(topo >= 0)[0]
        if not len(cols):
            return
        fech = topo + 0.66 * (fundo - topo)
        borda = topo + min(1, b) * (fech - topo)
        yy = np.arange(h, dtype=np.float32)[:, None]
        cobre = np.clip(borda[None, :] - yy + 0.5, 0, 1) * (topo[None, :] >= 0)
        if b > 0.85:
            cobre = np.maximum(cobre, (b - 0.85) / 0.15)
        mm = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
        k = (cobre * mm)[..., None]
        reg = img[y0:y0 + h, x0:x0 + w].astype(np.float32)
        reg[..., :3] = reg[..., :3] * (1 - k) + pele[..., :3].astype(np.float32) * k
        if not d["tras"]:
            S = 4
            cam = np.zeros((h * S, w * S), np.uint8)
            c0, c1 = cols.min() + 1, cols.max() - 1
            sup, inf = [], []
            for x in range(c0, c1 + 1):
                u = (x - c0) / max(1, c1 - c0)
                esp = (0.6 + 2.6 * math.sin(math.pi * u) ** 0.7) * max(0.6, self.K * 0.8) * (0.55 + 0.45 * min(1, b))
                y = borda[x]
                sup.append((x * S, (y - esp / 2) * S)); inf.append((x * S, (y + esp / 2) * S))
            cv2.fillPoly(cam, [np.array(sup + inf[::-1], np.int32)], 255, cv2.LINE_AA)
            cam = cv2.resize(cam, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            reg[..., :3] = reg[..., :3] * (1 - cam) + np.array([28, 22, 26], np.float32) * cam
        img[y0:y0 + h, x0:x0 + w] = reg.astype(np.uint8)

    def _bico(self, src, graus):
        """Mandíbula (peça do próprio desenho) gira na dobradiça; o bico de cima vai por cima."""
        x0, y0, x1, y1 = self.rb
        cx, cy = self.dob[0] - x0, self.dob[1] - y0
        M = cv2.getRotationMatrix2D((cx, cy), graus, 1.0)
        rot = cv2.warpAffine(self.mand[y0:y1, x0:x1], M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)).astype(np.float32)
        a = rot[..., 3:] / 255
        reg = src[y0:y1, x0:x1].astype(np.float32)
        reg[..., :3] = reg[..., :3] * (1 - a) + rot[..., :3] * a
        reg[..., 3:] = np.maximum(reg[..., 3:], a * 255)
        bs = self.bico_sup[y0:y1, x0:x1].astype(np.float32)
        ab = bs[..., 3:] / 255
        reg[..., :3] = reg[..., :3] * (1 - ab) + bs[..., :3] * ab
        reg[..., 3:] = np.maximum(reg[..., 3:], bs[..., 3:])
        src[y0:y1, x0:x1] = reg.astype(np.uint8)

    def _boca_desenho(self, src, v):
        """Troca o bico pelo desenho v (1..8), misturando a borda suavemente."""
        b, m = self.bocas[v - 1]
        x0, y0 = self.boca_xy
        h, w = m.shape[:2]
        h = min(h, src.shape[0] - y0); w = min(w, src.shape[1] - x0)
        b, m = b[:h, :w], m[:h, :w]
        reg = src[y0:y0 + h, x0:x0 + w].astype(np.float32)
        a_b = b[..., 3:] / 255.0
        a_r = reg[..., 3:] / 255.0
        # "over" com a máscara: dentro da região vale o desenho (inclusive o vazio em volta do bico)
        a_out = a_b * m + a_r * (1 - m)
        cor = (b[..., :3] * a_b * m + reg[..., :3] * a_r * (1 - m)) / np.maximum(a_out, 1e-4)
        reg[..., :3] = cor; reg[..., 3:] = a_out * 255
        src[y0:y0 + h, x0:x0 + w] = np.clip(reg, 0, 255).astype(np.uint8)

    def _olhos_desenho(self, src, v):
        d = self.olhos_d
        x0, y0 = d["xy"]; lim = d["limpo"]
        h, w = lim.shape[:2]; h = min(h, src.shape[0] - y0); w = min(w, src.shape[1] - x0)
        reg = lim[:h, :w].copy()
        c = d["cam"][v - 1][:h, :w]; a = c[..., 3:] / 255
        reg[..., :3] = reg[..., :3] * (1 - a) + c[..., :3] * a
        reg[..., 3:] = np.maximum(reg[..., 3:], c[..., 3:])
        src[y0:y0 + h, x0:x0 + w] = np.clip(reg, 0, 255).astype(np.uint8)

    def ponta_bico(self, cabeca=0.0):
        px, py = self.ponta
        c = self.pc; k = math.radians(cabeca)
        dx, dy = px - c[0], py - c[1]
        return c[0] + math.cos(k) * dx + math.sin(k) * dy, c[1] - math.sin(k) * dx + math.cos(k) * dy

    def _expressao(self, sx, sy, sob_y, sob_rot, olho_esc):
        if abs(sob_y) < 0.05 and abs(sob_rot) < 0.05 and abs(olho_esc - 1) < 0.003:
            return sx, sy
        h, w = self.w_sob.shape
        ix = np.clip(sx + 0.5, 0, w - 1).astype(np.int32); iy = np.clip(sy + 0.5, 0, h - 1).astype(np.int32)
        ws, wo = self.w_sob[iy, ix], self.w_olho[iy, ix]
        k = math.radians(sob_rot)
        dx, dy = sx - self.piv_sob[0], sy - self.piv_sob[1]
        rx = self.piv_sob[0] + math.cos(-k) * dx + math.sin(-k) * dy
        ry = self.piv_sob[1] - math.sin(-k) * dx + math.cos(-k) * dy
        nx = sx + ws * (rx - sx); ny = sy + ws * (ry - sy + sob_y * self.K / 1.5)
        ex = self.c_olho[0] + (nx - self.c_olho[0]) / olho_esc
        ey = self.c_olho[1] + (ny - self.c_olho[1]) / olho_esc
        return nx + wo * (ex - nx), ny + wo * (ey - ny)

    def quadro(self, boca=1.0, piscada=0.0, cabeca=0.0, braco=0.0, sob_y=0.0, sob_rot=0.0, olho_esc=1.0, visema=None,
               olhos=None):
        src = self.base.copy()
        if olhos and self.olhos_d:
            self._olhos_desenho(src, int(olhos))
            piscada, sob_y, sob_rot, olho_esc = 0.0, 0.0, 0.0, 1.0     # os desenhos já fazem isso
        if visema and self.bocas:
            self._boca_desenho(src, int(visema))       # desenho de bico pronto (sem a mandíbula girada)
        elif self.tem_boca:
            self._bico(src, self.ang_fechado * (1 - min(1.1, max(0, boca))))
        else:
            self._bico(src, 0.0)
        for d in self.olhos:
            self._piscar(src, d, min(1, max(0, piscada)))
        mx, my = self.gx.copy(), self.gy.copy()
        L = self.lim_cab
        tx, ty = self.gx[:L], self.gy[:L]
        if abs(cabeca) > 0.01:
            sx, sy = self._inverso(tx, ty, self.pc, cabeca, self.w_cab)
        else:
            sx, sy = tx.copy(), ty.copy()
        sx, sy = self._expressao(sx, sy, sob_y, sob_rot, olho_esc)
        mx[:L], my[:L] = sx, sy
        if self.tem_braco and abs(braco) > 0.01:
            x0, y0, x1, y1 = self.rbr
            nx, ny = self._inverso(self.gx[y0:y1, x0:x1], self.gy[y0:y1, x0:x1], self.pb, braco, self.w_bra)
            mx[y0:y1, x0:x1], my[y0:y1, x0:x1] = nx, ny
        out = cv2.remap(src, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGRA2RGBA))
