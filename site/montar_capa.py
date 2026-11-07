"""Monta capas em colagem a partir de fotos livres (Unsplash, Pexels, Wikimedia).
Lê site/capas_fotos/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1920x1080).
Formato do .json:
  {"layout": "tres" | "dois" | "um" | "grade" | "grade_b" | "colunas" | "faixas" | "moldura" | "circulo" | "destaque",
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


def baixar(url):
    url = resolver(url)
    if url.startswith("/"):
        return Image.open(url).convert("RGB")
    req = urllib.request.Request(url, headers=UA)
    for tentativa in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return Image.open(io.BytesIO(r.read())).convert("RGB")
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504, 520, 522, 524) or tentativa == 4:
                raise
            time.sleep(10 * (tentativa + 1))  # o Wikimedia pede calma: espera e tenta de novo


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


def titulo(tela, texto):
    """Escreve o nome do assunto (texto simples, nunca logotipo) no canto inferior esquerdo."""
    base = tela.convert("RGBA")
    d = ImageDraw.Draw(base)
    x, y = round(52 * S), A - round(52 * S)
    maxw = base.width - 2 * x  # margens iguais dos dois lados: texto nunca corta e fica centralizado
    tam = 150 if len(texto) <= 8 else 110
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


def montar(spec):
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
    if spec.get("titulo"):
        tela = titulo(tela, spec["titulo"])
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
