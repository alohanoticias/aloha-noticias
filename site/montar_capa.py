"""Monta capas em colagem a partir de fotos livres (Unsplash, Pexels, Wikimedia).
Lê site/capas_fotos/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1920x1080).
Formato do .json:
  {"layout": "tres" | "dois" | "um" | "grade" | "grade_b" | "colunas" | "faixas" | "canto" | "cantos" | "circulo",
   "fotos": [{"url": "...", "foco": [0.5, 0.5], "zoom": 1.0}, ...], "titulo": "texto opcional",
   "editoria": "cinema|games|tecnologia|anime|curiosidades" (opcional: aplica o tom e a etiqueta da editoria)}   (zoom >= 1 aproxima)
Só monta o que ainda não existe (apague o .jpg para refazer). Uso: python3 site/montar_capa.py"""
import io, time, json, re, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
S = 1.6  # os layouts abaixo foram desenhados em 1200x675; tudo é multiplicado por S para sair em 1920x1080
L, A = 1920, 1080
UA = {"User-Agent": "AlohaNoticiasBot/1.0 (https://alohanoticias.com; alohanoticias@gmail.com)"}
def R(x0, y0, x1, y1, r=0, borda=0):
    """Retângulo (com cantos arredondados e borda branca opcionais)."""
    return {"rr": (x0, y0, x1, y1), "r": r, "borda": borda}


def O(cx, cy, raio, borda=0):
    """Círculo com borda branca opcional."""
    return {"elipse": (cx - raio, cy - raio, cx + raio, cy + raio), "borda": borda}


# Cada layout é uma lista de formas, uma por foto (a primeira é a principal). Forma = lista de pontos (polígono), R(...) ou O(...).
# Use um layout diferente do dos últimos artigos: a home fica variada.
LAYOUTS = {
    # Todos os layouts são simétricos (iguais dos dois lados ou do centro para fora) para a capa ficar centralizada.
    # três painéis inclinados, do mesmo tamanho, com divisórias paralelas
    "tres": [[(0, 0), (442, 0), (342, 675), (0, 675)],
             [(458, 0), (842, 0), (742, 675), (358, 675)],
             [(858, 0), (1200, 0), (1200, 675), (758, 675)]],
    # dois painéis inclinados do mesmo tamanho (divisória no centro da capa)
    "dois": [[(0, 0), (641, 0), (541, 675), (0, 675)],
             [(659, 0), (1200, 0), (1200, 675), (559, 675)]],
    "um": [[(0, 0), (1200, 0), (1200, 675), (0, 675)]],
    # duas faixas largas empilhadas, do mesmo tamanho (boas para imagens largas, como letreiros)
    "duplo": [[(0, 0), (1200, 0), (1200, 328), (0, 328)],
              [(0, 347), (1200, 347), (1200, 675), (0, 675)]],
    # mosaico reto: foto principal no centro e uma coluna de cada lado, do mesmo tamanho
    "grade": [[(270, 0), (930, 0), (930, 675), (270, 675)],
              [(0, 0), (252, 0), (252, 675), (0, 675)],
              [(948, 0), (1200, 0), (1200, 675), (948, 675)]],
    # foto principal larga em cima e duas do mesmo tamanho embaixo
    "grade_b": [[(0, 0), (1200, 0), (1200, 396), (0, 396)],
                [(0, 414), (591, 414), (591, 675), (0, 675)],
                [(609, 414), (1200, 414), (1200, 675), (609, 675)]],
    # três colunas verticais
    "colunas": [[(0, 0), (388, 0), (388, 675), (0, 675)],
                [(406, 0), (794, 0), (794, 675), (406, 675)],
                [(812, 0), (1200, 0), (1200, 675), (812, 675)]],
    # três faixas horizontais (ótimo para paisagens)
    "faixas": [[(0, 0), (1200, 0), (1200, 213), (0, 213)],
               [(0, 231), (1200, 231), (1200, 444), (0, 444)],
               [(0, 462), (1200, 462), (1200, 675), (0, 675)]],
    # foto principal ocupando a capa e a segunda no canto superior direito, separada por divisa branca (18 px)
    "canto": [[(0, 0), (726, 0), (726, 275), (1200, 275), (1200, 675), (0, 675)],
              [(744, 0), (1200, 0), (1200, 257), (744, 257)]],
    # foto principal ocupando a capa e uma foto em cada canto de cima, separadas por divisas brancas (simétrico)
    "cantos": [[(474, 0), (726, 0), (726, 275), (1200, 275), (1200, 675), (0, 675), (0, 275), (474, 275)],
               [(0, 0), (456, 0), (456, 257), (0, 257)],
               [(744, 0), (1200, 0), (1200, 257), (744, 257)]],
    # (antigos, não usar: quadrado com borda branca sobre a foto)
    # foto em tela cheia com uma moldura menor centralizada embaixo
    "moldura": [R(0, 0, 1200, 675), R(400, 390, 800, 640, r=18, borda=12)],
    # foto em tela cheia com um círculo centralizado embaixo
    "circulo": [R(0, 0, 1200, 675), O(600, 520, 150, borda=12)],
    # foto em tela cheia com duas molduras pequenas centralizadas embaixo
    "destaque": [R(0, 0, 1200, 675), R(295, 400, 585, 640, r=16, borda=12), R(615, 400, 905, 640, r=16, borda=12)],
}


def _esc(forma):
    if isinstance(forma, dict):
        d = dict(forma)
        k = "rr" if "rr" in d else "elipse"
        d[k] = tuple(round(v * S) for v in d[k])
        d["r"] = round(d.get("r", 0) * S) if "r" in d else 0
        d["borda"] = round(d.get("borda", 0) * S)
        return d
    return [(round(x * S), round(y * S)) for x, y in forma]


LAYOUTS = {k: [_esc(f) for f in v] for k, v in LAYOUTS.items()}


def resolver(url):
    """Página de foto do Unsplash (unsplash.com/photos/<id>) -> endereço da imagem (og:image) em boa resolução."""
    if re.match(r"https://unsplash\.com/photos/[\w-]+/?$", url):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            html = r.read().decode("utf-8", "ignore")
        m = re.search(r'property="og:image"\s+content="([^"]+)"', html) or re.search(r'content="([^"]+)"\s+property="og:image"', html)
        if not m:
            raise RuntimeError("og:image não encontrada em " + url)
        img = m.group(1).replace("&amp;", "&")
        return re.sub(r"([?&])w=\d+", r"\g<1>w=1800", img)
    return url


def sem_transparencia(img):
    """Foto recortada (PNG com fundo transparente): coloca sobre um fundo de estúdio claro, em degradê,
    em vez de deixar a transparência virar preto."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        if img.getchannel("A").getextrema()[0] < 255:
            w, h = img.size
            topo, base = (238, 240, 243), (196, 202, 210)
            faixa = Image.new("RGB", (1, 256))
            for y in range(256):
                faixa.putpixel((0, y), tuple(round(topo[i] + (base[i] - topo[i]) * y / 255) for i in range(3)))
            fundo = faixa.resize((w, h), Image.BILINEAR)
            fundo.paste(img, (0, 0), img)
            return fundo
    return img.convert("RGB")


def baixar(url):
    url = resolver(url)
    if url.startswith("/"):
        return sem_transparencia(Image.open(url))
    req = urllib.request.Request(url, headers=UA)
    for tentativa in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return sem_transparencia(Image.open(io.BytesIO(r.read())))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504, 520, 522, 524) or tentativa == 4:
                raise
            time.sleep(10 * (tentativa + 1))  # o Wikimedia pede calma: espera e tenta de novo


def logo_sem_fundo(spec_logo):
    """Logo oficial sem caixa e sem borda: se a imagem tiver fundo preto, o preto vira transparente; recorta nas bordas do desenho."""
    url = resolver(spec_logo["url"])
    if url.startswith("/"):
        bruto = open(url, "rb").read()
    else:
        req = urllib.request.Request(url, headers=UA)
        bruto = urllib.request.urlopen(req, timeout=60).read()
    im = Image.open(io.BytesIO(bruto)).convert("RGBA")
    a = im.getchannel("A")
    if a.getextrema()[0] > 250:  # sem transparência própria: tira o fundo escuro
        rgb = im.convert("RGB")
        mx = ImageChops.lighter(ImageChops.lighter(rgb.getchannel("R"), rgb.getchannel("G")), rgb.getchannel("B"))
        a = mx.point(lambda v: 0 if v < 14 else min(255, round((v - 14) * 255 / 60)))
        im.putalpha(a)
    caixa = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    if caixa:
        im = im.crop(caixa)
    return im


def pôr_logo(tela, spec_logo):
    lg = logo_sem_fundo(spec_logo)
    w = round(L * spec_logo.get("largura", 0.36))
    lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    cx, cy = spec_logo.get("x", 0.5), spec_logo.get("y", 0.80)
    pos = (round(L * cx - lg.width / 2), round(A * cy - lg.height / 2))
    base = tela.convert("RGBA")
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sa = Image.new("L", base.size, 0)
    sa.paste(lg.getchannel("A").point(lambda v: round(v * 0.85)), pos)
    sombra.putalpha(sa.filter(ImageFilter.GaussianBlur(14)))
    base = Image.alpha_composite(base, sombra)
    base.alpha_composite(lg, pos)
    return base.convert("RGB")


def recorte(img, w, h, foco, zoom=1.0):
    esc = max(w / img.width, h / img.height) * zoom
    img = img.resize((max(w, round(img.width * esc)), max(h, round(img.height * esc))), Image.LANCZOS)
    x = round((img.width - w) * foco[0]); y = round((img.height - h) * foco[1])
    return img.crop((x, y, x + w, y + h))


def fonte(tam):
    """Inter Bold se existir no sistema; senão DejaVu Bold."""
    candidatos = []
    try:
        candidatos.append(subprocess.check_output(["fc-match", "-f", "%{file}", "Inter:bold"], text=True, timeout=10))
    except Exception:
        pass
    candidatos.append("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    for c in candidatos:
        try:
            return ImageFont.truetype(c, tam)
        except Exception:
            continue
    return ImageFont.load_default()


def titulo(tela, texto, y_rel=None, tam_ini=None):
    """Escreve o nome do assunto (texto simples, nunca logotipo) no canto inferior esquerdo."""
    base = tela.convert("RGBA")
    d = ImageDraw.Draw(base)
    x, y = round(52 * S), A - round(52 * S)
    if y_rel is not None:  # posição vertical da linha de base (fração da altura)
        y = round(y_rel * base.height)
    maxw = base.width - 2 * x  # margens iguais dos dois lados: texto nunca corta e fica centralizado
    tam = tam_ini or (150 if len(texto) <= 8 else 110)
    linhas = [texto]
    while True:
        f = fonte(round(tam * S))
        if max(d.textlength(l, font=f) for l in linhas) <= maxw:
            break
        if tam > 70:
            tam -= 4
            continue
        pal = texto.split()
        if len(linhas) == 1 and len(pal) > 1:
            melhor = min(range(1, len(pal)), key=lambda i: max(d.textlength(" ".join(pal[:i]), font=f), d.textlength(" ".join(pal[i:]), font=f)))
            linhas = [" ".join(pal[:melhor]), " ".join(pal[melhor:])]
            tam = 110
            continue
        tam -= 4
        if tam < 30:
            break
    ent = round(tam * S * 1.12)
    topo = y - ent * (len(linhas) - 1)
    cx = base.width // 2
    caixa = d.textbbox((cx, topo), linhas[0], font=f, anchor="ms")
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    for i, l in enumerate(linhas):
        sd.text((cx + 5, topo + ent * i + 10), l, font=f, fill=(0, 0, 0, 210), anchor="ms")
    base = Image.alpha_composite(base, sombra.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(base)
    for i, l in enumerate(linhas):
        d.text((cx, topo + ent * i), l, font=f, fill=(255, 255, 255, 255), anchor="ms")
    barra = d.rectangle((cx - 77, caixa[1] - 35, cx + 77, caixa[1] - 22), fill=(255, 196, 61, 255))
    return base.convert("RGB")


TONS = {  # cor da etiqueta, tom de cor aplicado sobre as fotos (unifica fotos de fontes diferentes)
    "cinema": ((231, 111, 81), (22, 51, 60)),
    "games": ((231, 111, 81), (28, 89, 102)),
    "tecnologia": ((156, 195, 199), (10, 52, 64)),
    "anime": ((231, 111, 81), (15, 76, 92)),
    "curiosidades": ((231, 111, 81), (15, 76, 92)),
}


def tom(tela, cor, forca=0.16):
    """Camada de cor da marca + vinheta suave + grão fino: deixa as fotos com cara de um conjunto só."""
    base = Image.blend(tela, Image.new("RGB", tela.size, cor), forca)
    vig = Image.new("L", tela.size, 0)
    d = ImageDraw.Draw(vig)
    for i in range(0, 224):
        d.rectangle((i, i, tela.width - i, tela.height - i), outline=int(70 * (1 - i / 224) ** 2))
    base = Image.composite(Image.new("RGB", tela.size, (8, 20, 24)), base, vig.filter(ImageFilter.GaussianBlur(48)))
    import random
    r = random.Random(7)
    g = Image.effect_noise(tela.size, 14).convert("RGB")
    return Image.blend(base, ImageChops.overlay(base, g), 0.10)


def etiqueta(tela, texto, cor):
    base = tela.convert("RGBA")
    f = fonte(42)
    d = ImageDraw.Draw(base)
    x, y = 64, 58
    c = d.textbbox((x, y), texto.upper(), font=f, anchor="la")
    d.rounded_rectangle((c[0] - 18, c[1] - 12, c[2] + 18, c[3] + 14), radius=8, fill=cor + (255,))
    d.text((x, y), texto.upper(), font=f, fill=(255, 255, 255, 255), anchor="la")
    return base.convert("RGB")


def lado_a_lado(spec):
    """Duas fotos inteiras (sem cortar), lado a lado e centralizadas, sobre fundo escuro neutro."""
    from PIL import ImageFilter
    tela = Image.new("RGB", (L, A), (18, 18, 22))
    fotos = spec["fotos"]
    if spec.get("cobrir"):  # metade da capa para cada foto, preenchendo todo o quadro
        meio = L // 2
        for i, f in enumerate(fotos):
            im = recorte(baixar(f["url"]), meio, A, f.get("foco", [.5, .5]), f.get("zoom", 1.0))
            tela.paste(ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.04), (i * meio, 0))
        return tela
    gap, margem = 36, 40
    pw = (L - 2 * margem - gap) // 2
    ph = A - 2 * margem
    imgs = [baixar(f["url"]) for f in fotos]
    # as duas com a mesma altura quando couber; senão reduz o necessário
    esc = min(min(ph / im.height, pw / im.width) for im in imgs)
    tamanhos = [(round(im.width * esc), round(im.height * esc)) for im in imgs]
    total = sum(w for w, _ in tamanhos) + gap
    x = (L - total) // 2
    for im, (w, h) in zip(imgs, tamanhos):
        im = im.resize((w, h), Image.LANCZOS)
        tela.paste(im, (x, (A - h) // 2))
        x += w + gap
    return tela


def montar(spec):
    if spec["layout"] == "lado_a_lado":
        return lado_a_lado(spec)
    poligonos = LAYOUTS[spec["layout"]]
    fotos = spec["fotos"]
    if len(fotos) != len(poligonos):
        raise SystemExit(f"layout {spec['layout']} pede {len(poligonos)} fotos")
    tela = Image.new("RGB", (L, A), "white")

    def mascara(forma, grow=0):
        """Máscara suavizada (3x) da forma, opcionalmente alargada em 'grow' pixels."""
        m = Image.new("L", (L * 3, A * 3), 0)
        d = ImageDraw.Draw(m)
        if isinstance(forma, dict):
            x0, y0, x1, y1 = [v * 3 for v in (forma.get("rr") or forma["elipse"])]
            g = grow * 3
            if "elipse" in forma:
                d.ellipse((x0 - g, y0 - g, x1 + g, y1 + g), fill=255)
            else:
                d.rounded_rectangle((x0 - g, y0 - g, x1 + g, y1 + g), radius=forma["r"] * 3 + g, fill=255)
        else:
            d.polygon([(x * 3, y * 3) for x, y in forma], fill=255)
        return m.resize((L, A), Image.LANCZOS)

    for forma, f in zip(poligonos, fotos):
        if isinstance(forma, dict):
            x0, y0, x1, y1 = forma.get("rr") or forma["elipse"]
            if forma.get("borda"):  # moldura branca ao redor da foto
                tela.paste(Image.new("RGB", (L, A), "white"), (0, 0), mascara(forma, forma["borda"]))
        else:
            xs, ys = [p[0] for p in forma], [p[1] for p in forma]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        img = recorte(baixar(f["url"]), x1 - x0, y1 - y0, f.get("foco", [.5, .5]), f.get("zoom", 1.0))
        img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.08)).enhance(1.04)
        tela.paste(img, (x0, y0), mascara(forma).crop((x0, y0, x1, y1)))
    ed = spec.get("editoria")
    if ed in TONS:
        tela = tom(tela, TONS[ed][1])
    if spec.get("logo"):  # logo oficial por cima da colagem, sem caixa nem borda (depois do tom, para manter as cores)
        tela = pôr_logo(tela, spec["logo"])
    if spec.get("titulo"):
        tela = titulo(tela, spec["titulo"], spec.get("titulo_y"), spec.get("titulo_tam"))
    if spec.get("etiqueta") and ed in TONS:  # opcional; por padrão a capa não leva o nome da editoria
        tela = etiqueta(tela, {"games": "Games", "anime": "Anime"}.get(ed, ed.capitalize()), TONS[ed][0])
    return tela


if __name__ == "__main__":
    pasta = RAIZ / "site/capas_fotos"
    saida = RAIZ / "site/assets/img/capas"
    saida.mkdir(parents=True, exist_ok=True)
    falhou = False
    for f in sorted(pasta.glob("*.json")):
        destino = saida / f"{f.stem}.jpg"
        if destino.exists():
            continue
        try:
            montar(json.loads(f.read_text(encoding="utf-8"))).save(destino, "JPEG", quality=88, optimize=True, progressive=True)
            print("Capa montada:", destino.name)
        except Exception as e:
            falhou = True
            print(f"FALHOU {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(1 if falhou else 0)
