"""Motor do vídeo vertical do Aloha Notícias (1080x1920, 30 fps) — versão 2.

- Fundo em tela cheia: fotos (zoom e deslize lentos) e trechos de vídeo, trocando por fala.
- Título no topo; legenda grande palavra a palavra; selo de destaque; balão nas piadas.
- Mascote grande num canto; troca de lado (espelhado) e chega mais perto nos comentários.
- Movimento com molas (cabeça, braço, corpo), piscadas naturais, bico pelo volume da voz.
"""
import math, os, random, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "mascote"))
from boneco import Boneco  # noqa: E402

W, H, FPS = 1080, 1920, 30
VERMELHO = (188, 49, 49)
PRETO = (10, 10, 12)
AMARELO = (255, 214, 0)
BRANCO = (255, 255, 255)
# Fonte da legenda: se existir video/fontes/Gotham-Black.otf (com licença), ela é usada.
_cands = ["Gotham-Black.otf", "Gotham-Black.ttf", "legenda.otf"]
FONTE_LEG = next(os.path.join(AQUI, "fontes", f) for f in _cands if os.path.exists(os.path.join(AQUI, "fontes", f)))
_t = os.path.join(AQUI, "fontes", "texto.otf")
FONTE_TXT = _t if os.path.exists(_t) else FONTE_LEG
FINAL = 2.6
ESCALA = 1.0

_f = {}
def fonte(t, arq=None):
    k = (t, arq or FONTE_LEG)
    if k not in _f:
        _f[k] = ImageFont.truetype(k[1], t)
    return _f[k]


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def ease_out_back(x, c=1.7):
    x = min(1, max(0, x)); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def quebrar(texto, f, largura):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if f.getlength(t.replace("*", "")) <= largura or not atual:
            atual = t
        else:
            linhas.append(atual); atual = p
    if atual:
        linhas.append(atual)
    return linhas

def com_sombra(im, raio=10, opac=0.5, desl=7):
    sh = im.split()[3].filter(ImageFilter.GaussianBlur(raio)).point(lambda v: int(v * opac))
    s = Image.new("RGBA", im.size, (0, 0, 0, 255)); s.putalpha(sh)
    o = Image.new("RGBA", (im.width, im.height + desl), (0, 0, 0, 0))
    o.alpha_composite(s, (0, desl)); o.alpha_composite(im)
    return o


# ============================================================ fundo
class Plano:
    """Um trecho do fundo: foto (zoom/deslize lentos) ou vídeo."""
    def __init__(self, midia, t0, t1, semente):
        self.t0, self.t1, self.m = t0, t1, midia
        rnd = random.Random(semente)
        self.zoom0, self.zoom1 = (1.0, 1.1) if rnd.random() < 0.5 else (1.1, 1.0)
        self.dir = rnd.choice([-1, 1])
        self.video = midia["tipo"] == "video"
        self.proc = None
        if midia is None or midia.get("tipo") == "cor":
            y = np.linspace(0, 1, H)[:, None, None]
            arr = (np.array([40, 14, 16]) * (1 - y) + np.array([8, 8, 10]) * y).repeat(W, axis=1).astype(np.uint8)
            midia = {"tipo": "imagem", "inteira": False}
            self.m = midia; self.video = False; self.proc = None; self.inteira = False
            self.im = Image.fromarray(arr).resize((int(W * 1.12), int(H * 1.12)))
            return
        self.inteira = bool(midia.get("inteira"))
        if not self.video and self.inteira:
            # foto de produto: aparece inteira (largura da tela) sobre ela mesma desfocada
            im0 = Image.open(midia["caminho"])
            if im0.mode in ("RGBA", "LA", "P"):
                im0 = im0.convert("RGBA")
                fundo_t = Image.new("RGBA", im0.size, (24, 20, 26, 255)); fundo_t.alpha_composite(im0); im0 = fundo_t
            im = im0.convert("RGB")
            r = max(W / im.width, H / im.height)
            fundo = im.resize((int(im.width * r) // 8, int(im.height * r) // 8), Image.BILINEAR)
            fundo = fundo.filter(ImageFilter.GaussianBlur(6)).resize((int(im.width * r), int(im.height * r)), Image.BILINEAR)
            fx, fy = (fundo.width - W) // 2, (fundo.height - H) // 2
            self.fundo = Image.blend(fundo.crop((fx, fy, fx + W, fy + H)), Image.new("RGB", (W, H), PRETO), 0.35)
            k = W / im.width
            self.foto = im.resize((W, int(im.height * k)), Image.LANCZOS)
            return
        if not self.video:
            im = Image.open(midia["caminho"]).convert("RGB")
            folga = 1.03 if midia.get("foco") else 1.12
            r = max(W * folga / im.width, H * folga / im.height)
            if midia.get("foco"):
                self.zoom0, self.zoom1 = (1.0, 1.05)
            self.im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

    def quadro(self, t):
        p = min(1, max(0, (t - self.t0) / max(0.01, self.t1 - self.t0)))
        if self.video:
            if self.proc is None:
                vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
                cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(self.m.get("inicio", 0)),
                       "-t", f"{self.t1 - self.t0 + 0.5:.2f}", "-i", self.m["caminho"], "-an", "-vf", vf,
                       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                self.ultimo = Image.new("RGB", (W, H), PRETO)
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) == W * H * 3:
                self.ultimo = Image.frombytes("RGB", (W, H), buf)
            return self.ultimo
        if self.inteira:
            z = 1.0 + 0.06 * ease(p)
            fo = self.foto.resize((int(W * z), int(self.foto.height * z)), Image.BILINEAR)
            out = self.fundo.copy()
            out.paste(fo, ((W - fo.width) // 2, int(H * 0.47 - fo.height / 2)))
            return out
        z = self.zoom0 + (self.zoom1 - self.zoom0) * ease(p)
        ww, hh = W / z, H / z
        mx, my = self.im.width - ww, self.im.height - hh
        foco = self.m.get("foco")
        if foco:   # foto de produto: fica centrada no objeto, só um respiro de movimento
            fx = min(1, max(0, foco[0] + self.dir * 0.06 * (p - 0.5) * 2)); fy = foco[1]
        else:
            fx = 0.5 + self.dir * 0.42 * (p - 0.5) * 2; fy = 0.45
        x, y = mx * fx, my * fy
        return self.im.crop((int(x), int(y), int(x + ww), int(y + hh))).resize((W, H), Image.BILINEAR)

    def fechar(self):
        if self.proc:
            self.proc.stdout.close(); self.proc.wait()


def degrades():
    y = np.arange(H, dtype=np.float32)[:, None]
    topo = np.clip(1 - y / 620, 0, 1) ** 1.5 * 190
    base = np.clip((y - 1100) / 820, 0, 1) ** 1.3 * 160
    a = np.repeat(np.maximum(topo, base), W, axis=1).astype(np.uint8)
    g = np.zeros((H, W, 4), np.uint8); g[..., 3] = a
    return Image.fromarray(g, "RGBA")


# ============================================================ textos
def titulo_img(texto):
    """Título da notícia no topo: caixa preta arredondada, faixa vermelha à esquerda, texto branco."""
    texto = texto.replace("*", "")
    arq = os.path.join(AQUI, "fontes", "titulo.ttf")
    f = fonte(58, arq if os.path.exists(arq) else FONTE_TXT)
    linhas = quebrar(texto, f, 900)[:3]
    alt = 30 + 74 * len(linhas) + 18
    larg = int(max(f.getlength(l) for l in linhas) + 96)
    im = Image.new("RGBA", (W, alt), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = (W - larg) // 2
    d.rounded_rectangle((x0, 0, x0 + larg, alt), 24, fill=(14, 14, 16, 238))
    d.rounded_rectangle((x0, 0, x0 + 13, alt), 6, fill=VERMELHO)
    d.rectangle((x0 + 7, 0, x0 + 13, alt), fill=VERMELHO)
    for i, l in enumerate(linhas):
        d.text((W / 2 + 7, 30 + 37 + 74 * i - 2), l, font=f, fill=BRANCO, anchor="mm")
    return com_sombra(im, 14, 0.45, 8)


class Legendas:
    """Legenda palavra a palavra; a palavra falada ganha uma faixa vermelha do Aloha."""
    def __init__(self):
        self.cache = {}

    def img(self, palavras, ativa):
        k = (tuple(palavras), ativa)
        if k not in self.cache:
            txt = [p.upper() for p in palavras]
            tam = 70
            while tam > 40 and fonte(tam).getlength(" ".join(txt)) > 930:   # sempre uma linha só
                tam -= 2
            f = fonte(tam)
            linhas = [" ".join(txt)]
            LH = 92
            im = Image.new("RGBA", (W, LH * len(linhas) + 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(im); esp = f.getlength(" "); idx = 0
            for li, l in enumerate(linhas):
                ws = l.split()
                larg = sum(f.getlength(w) for w in ws) + esp * (len(ws) - 1)
                x = (W - larg) / 2; y = 82 + li * LH
                for w in ws:
                    if idx == ativa:
                        bb = d.textbbox((x, y), w, font=f, anchor="ls")
                        d.rounded_rectangle((bb[0] - 14, bb[1] - 10, bb[2] + 14, bb[3] + 12), 14, fill=VERMELHO)
                        d.text((x, y), w, font=f, fill=BRANCO, stroke_width=4, stroke_fill=(90, 18, 18), anchor="ls")
                    else:
                        d.text((x, y), w, font=f, fill=BRANCO, stroke_width=10, stroke_fill=PRETO, anchor="ls")
                    x += f.getlength(w) + esp; idx += 1
            self.cache[k] = com_sombra(im, 9, 0.5, 6)
        return self.cache[k]


def selo_img(texto):
    f = fonte(64)
    tw = f.getlength(texto)
    bw, bh = int(tw + 72), 104
    im = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + bw, 20 + bh), 24, fill=VERMELHO, outline=BRANCO, width=7)
    d.text((20 + bw / 2, 20 + bh / 2 + 2), texto, font=f, fill=BRANCO, anchor="mm")
    return com_sombra(im.rotate(-3, Image.BICUBIC, expand=True), 12, 0.55, 10)


class Balao:
    """Balão de fala: branco, contorno grosso, rabicho curvo até o bico. As palavras escurecem
    conforme são ditas (as que faltam ficam em cinza claro)."""
    R = 36; BORDA = 5; RAB = 58

    def __init__(self, palavras, espelhar):
        self.palavras, self.esp = palavras, espelhar
        self.f = fonte(40, FONTE_TXT)
        self.linhas = quebrar(" ".join(p[0] for p in palavras), self.f, 400)
        tw = max(self.f.getlength(l) for l in self.linhas)
        self.LH = 50
        self.bw, self.bh = int(tw + 64), 30 + self.LH * len(self.linhas) + 18
        self.cache = {}
        self.forma = self._forma()

    def _forma(self):
        M = 34; bw, bh, R, B, RAB = self.bw, self.bh, self.R, self.BORDA, self.RAB
        S = 2  # desenha em 2x para borda lisa
        im = Image.new("RGBA", ((bw + 2 * M) * S, (bh + 2 * M + RAB) * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = M * S, M * S, (M + bw) * S, (M + bh) * S
        bx = x0 + 48 * S
        def rabicho(enc):
            # triângulo de lados curvos: base no balão, ponta para baixo/esquerda
            pts = []
            for i in range(21):
                u = i / 20
                pts.append((bx + (52 * S - enc) * (1 - u) + (-26 * S + enc * 0.3) * u + 10 * S * math.sin(math.pi * u),
                            y1 - 6 * S + (RAB * S - enc) * u ** 1.15))
            for i in range(21):
                u = 1 - i / 20
                pts.append((bx + enc * (1 - u) + (-26 * S + enc * 0.3) * u + 4 * S * math.sin(math.pi * u),
                            y1 - 6 * S + (RAB * S - enc) * u ** 1.3))
            return pts
        d.rounded_rectangle((x0, y0, x1, y1), R * S, fill=PRETO)
        d.polygon(rabicho(0), fill=PRETO)
        d.rounded_rectangle((x0 + B * S, y0 + B * S, x1 - B * S, y1 - B * S), (R - B) * S, fill=BRANCO)
        d.polygon(rabicho(B * S * 1.6), fill=BRANCO)
        d.rectangle((bx + B * S, y1 - 12 * S, bx + 44 * S, y1 - B * S), fill=BRANCO)
        im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
        if self.esp:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        self.M = M
        return com_sombra(im, 12, 0.45, 9)

    def img(self, n_vis):
        if n_vis in self.cache:
            return self.cache[n_vis]
        im = self.forma.copy(); d = ImageDraw.Draw(im)
        M = self.M; esp = self.f.getlength(" "); k = 0
        for li, l in enumerate(self.linhas):
            ws = l.split()
            larg = sum(self.f.getlength(w) for w in ws) + esp * (len(ws) - 1)
            x = M + (self.bw - larg) / 2; y = M + 30 + 36 + self.LH * li - 4
            for w in ws:
                d.text((x, y), w, font=self.f, fill=(18, 18, 22) if k < n_vis else (190, 190, 196), anchor="ls")
                x += self.f.getlength(w) + esp; k += 1
        self.cache[n_vis] = im
        return im


def cartao_final():
    im = Image.new("RGBA", (W, 460), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 78), "MATÉRIA COMPLETA NO", font=fonte(50), fill=BRANCO, anchor="ms", stroke_width=9, stroke_fill=PRETO)
    ft = fonte(118)
    t1, t2 = "ALOHA ", "NOTÍCIAS"
    l1, l2 = ft.getlength(t1), ft.getlength(t2)
    x = W / 2 - (l1 + l2) / 2
    d.text((x, 205), t1, font=ft, fill=BRANCO, anchor="ls", stroke_width=13, stroke_fill=PRETO)
    d.text((x + l1, 205), t2, font=ft, fill=VERMELHO, anchor="ls", stroke_width=13, stroke_fill=PRETO)
    # botão "seguir": pílula branca, bolinha vermelha com +, texto escuro
    f = fonte(46, FONTE_TXT); t = "Siga @alohanoticiasbr"; tw = f.getlength(t)
    bw = int(tw + 150); bx0 = int(W / 2 - bw / 2); by0 = 262; bh = 100
    d.rounded_rectangle((bx0, by0, bx0 + bw, by0 + bh), 50, fill=BRANCO, outline=PRETO, width=6)
    cx, cy, r = bx0 + 56, by0 + bh // 2, 30
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=VERMELHO)
    d.rounded_rectangle((cx - 15, cy - 4, cx + 15, cy + 4), 3, fill=BRANCO)
    d.rounded_rectangle((cx - 4, cy - 15, cx + 4, cy + 15), 3, fill=BRANCO)
    d.text((bx0 + 104, cy + 2), t, font=f, fill=(18, 18, 22), anchor="lm")
    return com_sombra(im, 12, 0.5, 8)


# ============================================================ poses
LOGO_POSES = {"microfone": (395, 470, 600, 628), "tablet": (520, 594, 712, 757)}   # emblema "e" (px da pose, altura 900)


def espelhar_pose(ps, nome, esc):
    """Espelha a pose, mas recoloca o emblema do Aloha no sentido certo (para ler direito)."""
    out = ps.transpose(Image.FLIP_LEFT_RIGHT)
    if nome in LOGO_POSES:
        k = esc * 900 / 955 if False else esc
        x0, y0, x1, y1 = [int(v * k * POSE_K.get(nome, 1)) for v in LOGO_POSES[nome]]
        reg = ps.crop((x0, y0, x1, y1))
        arr = np.array(reg).astype(np.int16)
        r_, g_, b_ = arr[..., 0], arr[..., 1], arr[..., 2]
        emb = (((r_ > 150) & (g_ < 90) & (b_ < 90)) | ((r_ > 200) & (g_ > 200) & (b_ > 200))).astype(np.uint8) * 255
        m = Image.fromarray(emb).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
        m2 = m.transpose(Image.FLIP_LEFT_RIGHT)
        mm = Image.fromarray(np.minimum(np.array(m), np.array(m2)))   # só onde o emblema existe nos dois sentidos
        out.paste(reg, (ps.width - x1, y0), mm)
    return out


POSE_K = {}


# ============================================================ animação
class Mola:
    def __init__(self, k, c, x0=0.0):
        self.k, self.c, self.x, self.v = k, c, x0, 0.0
    def passo(self, alvo, dt=1 / FPS):
        for _ in range(2):  # 2 subpassos: estável
            a = self.k * (alvo - self.x) - self.c * self.v
            self.v += a * dt / 2; self.x += self.v * dt / 2
        return self.x


def envelope_estimado(falas, total):
    n = int(total * FPS) + 2
    env = np.zeros(n); rnd = random.Random(7)
    for f in falas:
        for txt, a, b in f["palavras"]:
            sil = max(1, len(re.findall(r"[aeiouáéíóúâêôãõà]+", txt.lower())))
            i0, i1 = int(a * FPS), max(int(a * FPS) + 2, int(b * FPS))
            amp = [0.6 + 0.4 * rnd.random() for _ in range(sil)]
            for i in range(i0, min(i1, n)):
                fase = (i - i0) / max(1, i1 - i0) * sil
                s = min(int(fase), sil - 1)
                env[i] = max(env[i], amp[s] * math.sin(math.pi * (fase - s)) ** 0.7)
    return env


def envelope_do_audio(wav, total):
    with wave.open(wav) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    n = int(total * FPS) + 2; hop = sr / FPS
    env = np.array([np.sqrt(np.mean(x[int(i * hop):int((i + 1) * hop)] ** 2)) if int((i + 1) * hop) <= len(x) else 0
                    for i in range(n)])
    ref = np.percentile(env[env > 0], 92) if (env > 0).any() else 1
    env = np.clip(env / (ref + 1e-6), 0, 1.1); env[env < 0.07] = 0
    return env


def planejar(falas, total, dur_voz, env):
    """Simula quadro a quadro os parâmetros do mascote."""
    n = int(total * FPS)
    rnd = random.Random(11)
    pisc = np.zeros(n + 2)
    t = 0.9
    while t < total:
        for t_ in ([t, t + 0.3] if rnd.random() < 0.2 else [t]):
            for i in range(int(t_ * FPS), min(n, int((t_ + 0.2) * FPS) + 1)):
                pisc[i] = max(pisc[i], math.sin(math.pi * min(1, (i / FPS - t_) / 0.2)))
        t += rnd.uniform(2.2, 4.6)
    acento = np.zeros(n + 2)
    for f in falas:
        for w, a, b in f["palavras"]:
            if len(w.strip(",.!?:")) >= 6 or w[-1] in "!?":
                i = int(a * FPS)
                if i < n:
                    acento[i] = 1.0 + 0.06 * len(w)
    m_cab, m_bra = Mola(110, 12), Mola(55, 9)
    m_x, m_esc, m_bob = Mola(60, 12), Mola(70, 11, 1.0), Mola(140, 16)
    boca = 0.0
    lado_ant = falas[0].get("lado", "esq")
    P = []
    for k in range(n):
        t = k / FPS
        fala = next((f for f in falas if f["inicio"] - 0.05 <= t < f["fim"] + 0.3), None)
        prox = next((f for f in falas if f["inicio"] - 0.5 <= t < f["fim"] + 0.3), fala)
        fim = t >= dur_voz + 0.1
        g = dict(aponta=0.0, risada=0.0, pensativo=0.0, surpreso=0.0, tchau=0.0)
        for f in falas:
            ge = f.get("gesto")
            if ge in g:
                g[ge] = max(g[ge], ease((t - f["inicio"] + 0.15) / 0.3) * ease((f["fim"] + 0.25 - t) / 0.3))
        if fim:
            g["tchau"] = max(g["tchau"], ease((t - dur_voz) / 0.3))
        e = env[min(k, len(env) - 1)]
        alvo = min(1.1, e * 1.15)
        if g["risada"] > 0.4 and e > 0.05:
            alvo = max(alvo, 0.65 + 0.4 * abs(math.sin(2 * math.pi * 4.4 * t)))
        boca += (alvo - boca) * (0.72 if alvo > boca else 0.4)
        idle = 1.3 * math.sin(2 * math.pi * 0.29 * t) + 0.8 * math.sin(2 * math.pi * 0.13 * t + 1.3)
        if acento[k]:
            m_cab.v -= 26 * acento[k]
        cab = m_cab.passo(idle + 1.5 * (e - 0.3) + 7 * g["pensativo"] + 6 * g["surpreso"] - 1.5 * g["aponta"]
                          + 3.4 * g["risada"] * math.sin(2 * math.pi * 5.0 * t))
        if acento[k] and g["pensativo"] < 0.3:
            m_bra.v += 34 * acento[k]
        bra = m_bra.passo(2.4 * math.sin(2 * math.pi * 0.21 * t + 0.6) + 16 * g["aponta"] - 12 * g["pensativo"]
                          + g["tchau"] * (9 + 15 * math.sin(2 * math.pi * 2.3 * t))
                          + 5 * g["risada"] * math.sin(2 * math.pi * 5.0 * t))
        p = pisc[k]
        if fala and fala.get("gesto") == "risada":
            dtf = t - fala["inicio"]
            p = max(p, ease(dtf / 0.12) * ease((0.95 - dtf) / 0.15))      # ri de olho fechado e abre
        elif fala and fala.get("gesto") == "pensativo":
            dtf = t - fala["inicio"]
            p = max(p, 0.45 * ease(dtf / 0.2) * ease((1.4 - dtf) / 0.25))
        lado = (prox or {}).get("lado", lado_ant) if not fim else lado_ant
        P.append(dict(t=t, fala=fala, fim=fim, boca=boca, pisc=p, cab=cab, bra=bra, e=e, g=g, lado=lado,
                      coment=1.0 if (fala and fala.get("tipo") == "comentario" and not fim) else 0.0))
        lado_ant = lado
    # poses da folha (microfone, aponta_tela, tablet, braco_cruzado, apresenta, joinha):
    # aparecem no começo da fala por até 1,6 s e no encerramento (joinha)
    for k in range(n):
        q = P[k]; q["pose"], q["pose_mix"] = None, 0.0
        f = q["fala"]
        if f and f.get("pose"):
            dtf = q["t"] - f["inicio"]
            dur = min(1.6, f["fim"] - f["inicio"])
            if -0.1 <= dtf <= dur + 0.15:
                q["pose"] = f["pose"]; q["pose_mix"] = ease((dtf + 0.1) / 0.12) * ease((dur + 0.15 - dtf) / 0.12)
        if q["fim"] and q["t"] > dur_voz + 0.5:
            q["pose"] = "joinha"; q["pose_mix"] = ease((q["t"] - dur_voz - 0.5) / 0.12)
    trocas = [k for k in range(1, n) if P[k]["lado"] != P[k - 1]["lado"]]
    for k in range(n):
        P[k]["saida"] = 0.0
    for tk in trocas:
        velho = P[tk - 1]["lado"]
        for k in range(max(0, tk - 9), tk):                 # sai em 0,3 s
            P[k]["saida"] = ease((k - (tk - 9)) / 9); P[k]["lado"] = velho
        for k in range(tk, min(n, tk + 14)):                # entra em 0,45 s
            P[k]["saida"] = 1 - ease_out_back((k - tk) / 13, 1.3)
    for q in P:
        q["esc"] = m_esc.passo(1.0 + 0.13 * q["coment"])
        q["dx"] = m_x.passo(80 * q["coment"])
        q["bob"] = m_bob.passo(9 * q["e"] + 4 * math.sin(2 * math.pi * 0.25 * q["t"])
                               + 8 * q["g"]["risada"] * abs(math.sin(2 * math.pi * 5.0 * q["t"])))
    return P


# ============================================================ render
def renderizar(roteiro, falas_tempos, dur_voz, midias, saida, wav=None, pasta_rig=None, amostras=None,
               midia_final=None):
    """midias: uma lista por fala, de {'tipo': 'imagem'|'video', 'caminho', 'inicio'}."""
    bon = Boneco(pasta_rig or os.path.join(AQUI, "mascote", "rig"), ESCALA)
    poses = {}
    pdir = os.path.join(AQUI, "mascote", "poses")
    if os.path.isdir(pdir):
        for fn in os.listdir(pdir):
            if fn.endswith(".png"):
                im = Image.open(os.path.join(pdir, fn)).convert("RGBA")
                k = 900 / im.height                     # mesma altura de tronco do mascote
                POSE_K[fn[:-4]] = k
                poses[fn[:-4]] = im.resize((int(im.width * k), 900), Image.LANCZOS)
    falas = [{**f, **tt} for f, tt in zip(roteiro["falas"], falas_tempos)]
    total = dur_voz + FINAL
    n = int(total * FPS)
    env = envelope_do_audio(wav, total) if wav else envelope_estimado(falas, total)
    P = planejar(falas, total, dur_voz, env)

    planos, ult = [], None
    for i, f in enumerate(falas):
        ms = [m for m in (midias[i] or []) if m] or ([ult] if ult else [])
        t0 = 0.0 if i == 0 else f["inicio"] - 0.1
        t1 = (falas[i + 1]["inicio"] - 0.1) if i + 1 < len(falas) else dur_voz + 0.1
        for j, m in enumerate(ms):
            planos.append(Plano(m, t0 + j * (t1 - t0) / len(ms), t0 + (j + 1) * (t1 - t0) / len(ms), len(planos)))
        if ms:
            ult = ms[-1]
    if not planos:
        planos.append(Plano(None, 0, dur_voz + 0.1, 0))
    mf = midia_final or ult
    planos.append(Plano(mf, dur_voz + 0.1, total + 1, len(planos)))

    grad = degrades()
    tit = titulo_img(roteiro.get("titulo_curto", ""))
    leg = Legendas()
    selos = {i: selo_img(f["destaque"]) for i, f in enumerate(falas) if f.get("destaque")}
    baloes = {}
    fin = cartao_final()
    for f in falas:
        bl, at = [], []
        for p in f["palavras"]:
            txt = " ".join(x[0] for x in at + [p])
            if at and (len(at) >= 3 or len(txt) > 17 or at[-1][0][-1] in ".!?:,"):
                bl.append(at); at = []
            at.append(p)
        if at:
            bl.append(at)
        f["blocos"] = bl

    def desenhar(k):
        q = P[k]; t = q["t"]
        p = next((p for p in planos if p.t0 <= t < p.t1), planos[-1])
        fr = p.quadro(t).convert("RGBA")
        dt = t - p.t0
        if dt < 0.25 and p.t0 > 0:                   # corte com leve "soco" de zoom
            z = 1 + 0.06 * (1 - ease(dt / 0.25))
            big = fr.resize((int(W * z), int(H * z)), Image.BILINEAR)
            ox, oy = (big.width - W) // 2, (big.height - H) // 2
            fr = big.crop((ox, oy, ox + W, oy + H))
        if q["fim"]:
            fr.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(110 * ease((t - dur_voz) / 0.4)))))
        fr.alpha_composite(grad)
        f = q["fala"]; i = falas.index(f) if f else None
        if not q["fim"]:
            fr.alpha_composite(tit, (0, 150))
        else:
            a = ease((t - dur_voz - 0.1) / 0.35)
            c = fin.copy(); c.putalpha(c.split()[3].point(lambda v: int(v * a)))
            fr.alpha_composite(c, (0, int(330 - 40 * (1 - a))))
        ytopo = 150 + tit.height
        if False:  # selo de destaque desligado (pedido do João)
            s = selos[i]
            e2 = ease_out_back((t - f["inicio"] - 0.05) / 0.32) * ease((f["fim"] + 0.25 - t) / 0.2)
            if e2 > 0.02:
                im = s.resize((max(1, int(s.width * e2)), max(1, int(s.height * e2))), Image.BILINEAR)
                fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(ytopo + 70 - im.height / 2)))
        if f and f.get("tipo", "noticia") != "comentario" and not q["fim"]:
            bl = f["blocos"]
            for bi, b in enumerate(bl):
                ini = b[0][1]
                prox = bl[bi + 1][0][1] if bi + 1 < len(bl) else f["fim"] + 0.3
                if ini - 0.04 <= t < prox:
                    ativa = max([j for j, pp in enumerate(b) if pp[1] <= t + 0.03] or [0])
                    im = leg.img([pp[0] for pp in b], ativa)
                    e2 = 0.85 + 0.15 * ease_out_back((t - ini + 0.04) / 0.16, 2.2)
                    if abs(e2 - 1) > 0.005:
                        im = im.resize((int(im.width * e2), int(im.height * e2)), Image.BILINEAR)
                    fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(ytopo + 130 - im.height / 2)))
                    break
        # ---- mascote (rig animado) ou pose da folha
        mq = bon.quadro(q["boca"], q["pisc"], q["cab"], q["bra"])
        es = q["esc"]
        esq = q["lado"] == "esq"
        pm = q["pose_mix"] if q["pose"] in poses else 0.0

        def posicionar(img_m, larg_ref):
            xx = (-130 + q["dx"]) if esq else (W - larg_ref + 130 - q["dx"])
            xx += (-1 if esq else 1) * q["saida"] * 760
            yy = H - img_m.height + 60 - q["bob"] + q["saida"] * 120
            return xx, yy
        if abs(es - 1) > 0.003:
            mq = mq.resize((int(mq.width * es), int(mq.height * es)), Image.BILINEAR)
        if not esq:
            mq = mq.transpose(Image.FLIP_LEFT_RIGHT)
        x, y = posicionar(mq, mq.width)
        desenho = mq; dx_ = x; dy_ = y
        if pm > 0.5:
            ps = poses[q["pose"]]
            pop = 0.96 + 0.04 * ease_out_back(min(1, pm), 2.0)
            e3 = es * pop
            ps = ps.resize((int(ps.width * e3), int(ps.height * e3)), Image.BILINEAR)
            if not esq:
                ps = espelhar_pose(ps, q["pose"], e3)
            # alinha pela base e pelo lado de dentro do mascote
            px_ = (x + 60 * es) if esq else (x + mq.width - 60 * es - ps.width)
            py_ = H - ps.height + 40 - q["bob"] + q["saida"] * 120
            desenho, dx_, dy_ = ps, px_, py_
        a = desenho.split()[3].resize((max(1, desenho.width // 8), max(1, desenho.height // 8))).filter(ImageFilter.GaussianBlur(3))
        sh = Image.new("RGBA", desenho.size, (0, 0, 0, 255)); sh.putalpha(a.resize(desenho.size, Image.BILINEAR).point(lambda v: int(v * 0.5)))
        fr.alpha_composite(sh, (int(dx_ + (14 if esq else -14)), int(dy_ + 18)))
        fr.alpha_composite(desenho, (int(dx_), int(dy_)))
        ocupado = desenho.split()[3].point(lambda v: 255 if v > 20 else 0)
        # ---- balão
        if f and f.get("tipo") == "comentario" and q["saida"] < 0.02 and not q["fim"]:
            if i not in baloes:
                baloes[i] = Balao(f["palavras"], not esq)
            b = baloes[i]
            nvis = sum(1 for pp in f["palavras"] if pp[1] <= t + 0.05)
            im = b.img(nvis)
            e2 = ease_out_back((t - f["inicio"] + 0.1) / 0.3, 1.9) * ease((f["fim"] + 0.3 - t) / 0.18)
            if e2 > 0.02:
                im2 = im.resize((max(1, int(im.width * e2)), max(1, int(im.height * e2))), Image.BILINEAR)
                ponta_x = (b.M + 48 - 26) * e2           # ponta do rabicho dentro da imagem
                ponta_y = (b.M + b.bh + b.RAB) * e2
                # ponta do bico no rig (cabeça girada) -> tela, acompanhando tamanho e lado do mascote
                bpx, bpy = bon.ponta_bico(q["cab"])
                bico_x = x + bpx * es if esq else x + mq.width - bpx * es
                bico_y = y + bpy * es
                if esq:
                    bx = bico_x + 18 - ponta_x
                else:
                    bx = bico_x - 18 - (im2.width - ponta_x)
                by = bico_y - 18 * es - ponta_y
                bx = min(max(bx, 16), W - im2.width - 16)
                # nunca em cima do personagem: sobe até sair do desenho
                for _ in range(40):
                    cx0, cy0 = int(bx - dx_), int(by - dy_)
                    caixa = (max(0, cx0), max(0, cy0), min(ocupado.width, cx0 + im2.width), min(ocupado.height, cy0 + im2.height - 20))
                    if caixa[2] <= caixa[0] or caixa[3] <= caixa[1] or not ocupado.crop(caixa).getbbox():
                        break
                    by -= 12
                fr.alpha_composite(im2, (int(bx), int(by)))
        return fr.convert("RGB")

    if amostras:
        for ts in amostras:
            desenhar(int(ts * FPS)).save(f"{saida}.{ts:05.2f}s.jpg", quality=90)
        return None
    tmp = saida + ".parcial.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if wav:
        cmd += ["-i", wav]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    if wav:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += [tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        proc.stdin.write(desenhar(k).tobytes())
    proc.stdin.close()
    for p in planos:
        p.fechar()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    os.replace(tmp, saida)
    return saida


def tempos_estimados(roteiro, inicio=0.35, pausa=0.22):
    t = inicio; out = []
    for f in roteiro["falas"]:
        pal = []; ini = t
        for w in f["texto"].split():
            dur = 0.052 * len(w) + 0.07
            pal.append((w, t, t + dur)); t += dur
            if w[-1] in ",;:": t += 0.12
            if w[-1] in ".!?": t += 0.18
        out.append({"inicio": ini, "fim": t, "palavras": pal}); t += pausa
    return out, t
