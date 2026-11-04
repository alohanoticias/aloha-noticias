import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SRC = sys.argv[1]  # dir with outfit700.ttf / outfit600.ttf
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

OCEANO, AREIA, FUNDO, CORAL = "#0F4C5C", "#F4EDE4", "#FBF7F1", "#E76F51"
_tt = {w: TTFont(f"{SRC}/outfit{w}.ttf") for w in (700, 600)}
fonts = {w: t.getGlyphSet() for w, t in _tt.items()}
cmap = _tt[700].getBestCmap()
NOME = "ALOHA NOTÍCIAS"


def glyph(w, ch, x, y, s):
    gs = fonts[w]
    pen = SVGPathPen(gs, lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    g = cmap[ord(ch)]
    gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
    return pen.getCommands(), gs[g].width * s


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def o_mark(cx, cy, R, uid, ink, small=False):
    """O: anel grosso, mar preenchido com topo ondulado, onda clara recortada."""
    t = R * (0.35 if small else 0.32)       # espessura do anel
    r = R - t
    s, d = R * 0.10, R * 0.13                 # nível do mar e amplitude
    s2, ww = R * (0.46 if small else 0.44), R * (0.17 if small else 0.13)
    X = lambda k: f(cx + k * R)
    Y = lambda k: f(cy + k)

    def wave(y0):
        return (f"M{X(-1.1)},{Y(y0)} C{X(-0.7)},{Y(y0-d)} {X(-0.37)},{Y(y0-d)} {X(0)},{Y(y0)} "
                f"S{X(0.7)},{Y(y0+d)} {X(1.1)},{Y(y0)}")

    sky = wave(s) + f" L{X(1.1)},{Y(-R*1.2)} L{X(-1.1)},{Y(-R*1.2)} Z"
    return f"""<defs>
    <clipPath id="{uid}-ceu"><path d="{sky}"/></clipPath>
    <mask id="{uid}-m" maskUnits="userSpaceOnUse" x="{f(cx-R-2)}" y="{f(cy-R-2)}" width="{f(2*R+4)}" height="{f(2*R+4)}">
      <circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R)}" fill="#fff"/>
      <circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="#000" clip-path="url(#{uid}-ceu)"/>
      <path d="{wave(s2)}" fill="none" stroke="#000" stroke-width="{f(ww)}"/>
    </mask>
  </defs>
  <circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R)}" fill="{ink}" mask="url(#{uid}-m)"/>"""


def word(text, w, x, base, s, track, ink, o_uid=None):
    out, pen_x = [], x
    for ch in text:
        if ch == " ":
            pen_x += 230 * s
            continue
        if ch == "O" and o_uid:
            adv = fonts[w]["O"].width * s
            R = 365 * s
            out.append(o_mark(pen_x + adv / 2, base - 353 * s, R, o_uid, ink))
        else:
            d, adv = glyph(w, ch, pen_x, base, s)
            out.append(f'<path d="{d}" fill="{ink}"/>')
        pen_x += adv + track * s
    return "\n  ".join(out), pen_x - track * s - x


def measure(text, w, s, track):
    tot = 0
    for ch in text:
        tot += (230 if ch == " " else fonts[w][cmap[ord(ch)]].width) * s + track * s
    return tot - track * s


def svg(wd, ht, body, title, bg=None, rx=0):
    rect = f'<rect width="{f(wd)}" height="{f(ht)}" rx="{f(rx)}" fill="{bg}"/>\n  ' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(wd)} {f(ht)}" '
            f'width="{f(wd)}" height="{f(ht)}" role="img" aria-label="{title}">\n'
            f'  <title>{title}</title>\n  {rect}{body}\n</svg>\n')


def write(name, content):
    open(f"{OUT}/{name}", "w").write(content)


# ---- Logo empilhado ----
def stacked(ink, uid):
    pad, s = 40, 0.2
    track = 10
    aw = measure("ALOHA", 700, s, track)
    ns, ntrack = 0.062, 575                   # NOTÍCIAS pequeno e bem espaçado
    nw = measure("NOTÍCIAS", 600, ns, ntrack)
    W = aw + 2 * pad
    base1 = pad + 718 * s
    base2 = base1 + 706 * s * 0.5 + 703 * ns
    a, _ = word("ALOHA", 700, pad, base1, s, track, ink, uid)
    n, _ = word("NOTÍCIAS", 600, (W - nw) / 2, base2, ns, ntrack, ink)
    return W, base2 + pad, a + "\n  " + n


for name, ink, bg in [("aloha-noticias-logo-empilhado", OCEANO, None),
                      ("aloha-noticias-logo-empilhado-negativo", AREIA, None)]:
    W, H, body = stacked(ink, "o" + str(len(name)))
    write(name + ".svg", svg(W, H, body, NOME))


# ---- Versão em linha (cabeçalho) ----
def inline(ink, uid):
    pad, s, track = 12, 0.06, 10
    base = pad + 983 * s                      # topo do acento do Í
    a, aw = word("ALOHA", 700, pad, base, s, track, ink, uid)
    n, nw = word("NOTÍCIAS", 600, pad + aw + 230 * s, base, s, track, ink)
    return pad * 2 + aw + 230 * s + nw, base + 12 * s + pad, a + "\n  " + n


for name, ink in [("aloha-noticias-logo-linha", OCEANO), ("aloha-noticias-logo-linha-negativo", AREIA)]:
    W, H, body = inline(ink, "o" + str(len(name)))
    write(name + ".svg", svg(W, H, body, NOME))

# ---- Símbolo O isolado ----
write("aloha-o-simbolo.svg", svg(200, 200, o_mark(100, 100, 96, "os", OCEANO), "ALOHA"))
write("aloha-o-simbolo-negativo.svg", svg(200, 200, o_mark(100, 100, 96, "osn", AREIA), "ALOHA"))

# ---- Ícone de app (quadrado arredondado) e favicon ----
write("aloha-icone-app.svg", svg(512, 512, o_mark(256, 256, 168, "ic", AREIA), NOME, OCEANO, rx=112))
write("favicon.svg", svg(64, 64, o_mark(32, 32, 24, "fv", AREIA, small=True), NOME, OCEANO, rx=14))
print("ok")
write("aloha-icone-app-quadrado.svg", svg(512, 512, o_mark(256, 256, 168, "iq", AREIA), NOME, OCEANO, rx=0))
