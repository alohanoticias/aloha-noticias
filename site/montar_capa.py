"""Monta capas em colagem a partir de fotos livres (Unsplash, Pexels, Wikimedia).
Lê site/capas_fotos/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1200x675).
Formato do .json:
  {"layout": "tres" | "dois" | "um" | "grade" | "grade_b" | "colunas" | "faixas" | "moldura" | "circulo" | "destaque",
   "fotos": [{"url": "...", "foco": [0.5, 0.5], "zoom": 1.0}, ...], "titulo": "texto opcional",
   "editoria": "cinema|games|tecnologia|noticias|curiosidades" (opcional: aplica o tom e a etiqueta da editoria)}   (zoom >= 1 aproxima)
Só monta o que ainda não existe (apague o .jpg para refazer). Uso: python3 site/montar_capa.py"""
import io, json, re, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
L, A = 1200, 675
UA = {"User-Agent": "Mozilla/5.0 (compatible; AlohaCapas/1.0; +https://alohanoticias.com)"}
def R(x0, y0, x1, y1, r=0, borda=0):
    """Retângulo (com cantos arredondados e borda branca opcionais)."""
    return {"rr": (x0, y0, x1, y1), "r": r, "borda": borda}


def O(cx, cy, raio, borda=0):
    """Círculo com borda branca opcional."""
    return {"elipse": (cx - raio, cy - raio, cx + raio, cy + raio), "borda": borda}


# Cada layout é uma lista de formas, uma por foto (a primeira é a principal). Forma = lista de pontos (polígono), R(...) ou O(...).
# Use um layout diferente do dos últimos artigos: a home fica variada.
LAYOUTS = {
    # painéis inclinados com divisórias brancas (padrão original)
    "tres": [[(0, 0), (660, 0), (525, 675), (0, 675)],
             [(678, 0), (1200, 0), (1200, 322), (618, 322)],
             [(600, 340), (1200, 340), (1200, 675), (543, 675)]],
    "dois": [[(0, 0), (700, 0), (560, 675), (0, 675)],
             [(718, 0), (1200, 0), (1200, 675), (578, 675)]],
    "um": [[(0, 0), (1200, 0), (1200, 675), (0, 675)]],
    # mosaico reto: uma foto grande e duas empilhadas
    "grade": [[(0, 0), (760, 0), (760, 675), (0, 675)],
              [(778, 0), (1200, 0), (1200, 328), (778, 328)],
              [(778, 346), (1200, 346), (1200, 675), (778, 675)]],
    # o mesmo mosaico espelhado: duas empilhadas à esquerda, a grande à direita
    "grade_b": [[(440, 0), (1200, 0), (1200, 675), (440, 675)],
                [(0, 0), (422, 0), (422, 328), (0, 328)],
                [(0, 346), (422, 346), (422, 675), (0, 675)]],
    # três colunas verticais
    "colunas": [[(0, 0), (392, 0), (392, 675), (0, 675)],
                [(404, 0), (796, 0), (796, 675), (404, 675)],
                [(808, 0), (1200, 0), (1200, 675), (808, 675)]],
    # três faixas horizontais (ótimo para paisagens)
    "faixas": [[(0, 0), (1200, 0), (1200, 217), (0, 217)],
               [(0, 229), (1200, 229), (1200, 446), (0, 446)],
               [(0, 458), (1200, 458), (1200, 675), (0, 675)]],
    # foto em tela cheia com uma moldura menor sobreposta no canto
    "moldura": [R(0, 0, 1200, 675), R(690, 340, 1140, 630, r=18, borda=12)],
    # foto em tela cheia com um círculo sobreposto
    "circulo": [R(0, 0, 1200, 675), O(920, 400, 190, borda=12)],
    # foto em tela cheia com duas molduras pequenas lado a lado
    "destaque": [R(0, 0, 1200, 675), R(560, 380, 850, 625, r=16, borda=10), R(880, 380, 1170, 625, r=16, borda=10)],
}


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
    with urllib.request.urlopen(req, timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


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
    f = fonte(150 if len(texto) <= 8 else 110)
    d = ImageDraw.Draw(base)
    x, y = 52, A - 52
    caixa = d.textbbox((x, y), texto, font=f, anchor="ls")
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((x + 3, y + 6), texto, font=f, fill=(0, 0, 0, 210), anchor="ls")
    base = Image.alpha_composite(base, sombra.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.text((x, y), texto, font=f, fill=(255, 255, 255, 255), anchor="ls")
    barra = d.rectangle((x, caixa[1] - 22, x + 96, caixa[1] - 14), fill=(255, 196, 61, 255))
    return base.convert("RGB")


TONS = {  # cor da etiqueta, tom de cor aplicado sobre as fotos (unifica fotos de fontes diferentes)
    "cinema": ((231, 111, 81), (22, 51, 60)),
    "games": ((231, 111, 81), (28, 89, 102)),
    "tecnologia": ((156, 195, 199), (10, 52, 64)),
    "noticias": ((231, 111, 81), (15, 76, 92)),
    "curiosidades": ((231, 111, 81), (15, 76, 92)),
}


def tom(tela, cor, forca=0.16):
    """Camada de cor da marca + vinheta suave + grão fino: deixa as fotos com cara de um conjunto só."""
    base = Image.blend(tela, Image.new("RGB", tela.size, cor), forca)
    vig = Image.new("L", tela.size, 0)
    d = ImageDraw.Draw(vig)
    for i in range(0, 140):
        d.rectangle((i, i, tela.width - i, tela.height - i), outline=int(70 * (1 - i / 140) ** 2))
    base = Image.composite(Image.new("RGB", tela.size, (8, 20, 24)), base, vig.filter(ImageFilter.GaussianBlur(30)))
    import random
    r = random.Random(7)
    g = Image.effect_noise(tela.size, 14).convert("RGB")
    return Image.blend(base, ImageChops.overlay(base, g), 0.10)


def etiqueta(tela, texto, cor):
    base = tela.convert("RGBA")
    f = fonte(26)
    d = ImageDraw.Draw(base)
    x, y = 40, 36
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
        tela = etiqueta(tela, {"games": "Games", "noticias": "Notícias"}.get(ed, ed.capitalize()), TONS[ed][0])
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
