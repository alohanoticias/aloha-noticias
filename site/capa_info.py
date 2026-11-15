"""Capas "com informação": a foto do assunto continua visível e ganha por cima um dado-chave
(número, data, comparação) em texto centralizado. É um modelo a mais, convivendo com as colagens de montar_capa.py.

Lê site/capas_info/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1920x1080) usando como base
a foto do assunto em site/capas_base/<slug>.jpg (se não existir, copia a capa atual para lá antes).

Formato do .json (todos os textos são curtos; tudo fica centralizado e nunca é cortado):
  {"modelo": "faixa" | "data" | "numero" | "comparacao" | "topo" | "rodape",
   "largura_max": 760                      (opcional: estreita o texto para não encostar em logo ou rosto nas laterais),
   "logo_lado": "esquerda"                 (opcional: logo no canto superior esquerdo em vez do direito),
   "tema_cima": true                       (opcional: o selo do tema vai sozinho para o alto, quando embaixo ele cobriria algo),
   "posicao": "baixo" | "meio" | "cima"   (opcional; sem ela, a capa escolhe sozinha o lugar que não cobre rostos nem letreiros),
   "desfocar": true                        (opcional: desfoca a imagem só atrás do texto, quando ela tem letras miúdas),
   "logo": {"url": "logos/netflix.png" ou endereço de png oficial, "escala": 1.0, "canto": true (no canto superior direito, sem tirar o texto)}   (opcional: logo oficial no lugar do tema escrito; logos prontos em site/logos/),
   "tema": "NOME DO ASSUNTO (linha pequena em vermelho)",
   "titulo": "frase curta",
   "destaque": "26 NOV" | "26,35 mi"      (data, numero),
   "detalhe": "texto pequeno do selo"      (opcional),
   "barras": [["3º tri 2025", 152, "152 mi"], ["3º tri 2026", 138, "138 mi"]]   (comparacao),
   "selo": "−9%"                           (comparacao, opcional),
   "grafico": "barras" | "horizontal" | "duelo" | "seta"   (comparacao: varie o tipo de gráfico entre os artigos)}
Só monta o que ainda não existe (apague o .jpg para refazer). Uso: python3 site/capa_info.py [slug ...]"""
import hashlib, json, os, shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
VERM = (188, 49, 49, 255)
BRANCO = (255, 255, 255, 255)
CINZA = (228, 228, 228, 255)
FONTES = ["/usr/share/fonts/opentype/inter/Inter-{}.otf", "/usr/share/fonts/truetype/inter/Inter-{}.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def fonte(peso, tam):
    for c in FONTES:
        try:
            return ImageFont.truetype(c.format(peso), tam)
        except Exception:
            continue
    return ImageFont.load_default()


def caber(d, texto, peso, tam, maxw):
    """Diminui a fonte até o texto caber na largura (texto nunca é cortado)."""
    while tam > 24:
        f = fonte(peso, tam)
        if d.textlength(texto, font=f) <= maxw:
            return f
        tam -= 4
    return fonte(peso, tam)


def logo_da_colagem(slug):
    spec = RAIZ / f"site/capas_fotos/{slug}.json"
    return json.loads(spec.read_text(encoding="utf-8")).get("logo") if spec.exists() else None


def mc():
    sys.path.insert(0, str(RAIZ / "site"))
    import montar_capa
    return montar_capa


def base(slug):
    """Foto do assunto sem texto: guardada em site/capas_base/. Se o artigo tem colagem em capas_fotos/,
    remonta a colagem sem o título escrito (para não repetir texto); senão usa a capa atual."""
    pasta = RAIZ / "site/capas_base"
    pasta.mkdir(exist_ok=True)
    b = pasta / f"{slug}.jpg"
    if not b.exists():
        spec = RAIZ / f"site/capas_fotos/{slug}.json"
        sp = json.loads(spec.read_text(encoding="utf-8")) if spec.exists() else {}
        if sp:  # sempre remonta da colagem original (sem título): nunca parte de uma capa que já tem texto
            montar_capa = mc()
            if os.environ.get("CAPA_IA") == "1":  # regra de qualidade: fotos aprimoradas por IA antes de montar
                try:
                    import capa_ia
                except Exception as e:
                    print("   IA indisponível, montando sem:", e)
                    capa_ia = None
            if os.environ.get("CAPA_IA") == "1" and capa_ia:
                capa_ia.tipo_atual = "anime" if sp.get("editoria") == "anime" or sp.get("ia") == "anime" else "foto"
            for k in ("titulo", "titulo_y", "titulo_tam", "etiqueta", "logo"):
                sp.pop(k, None)
            montar_capa.montar(sp).save(b, "JPEG", quality=92)
        else:
            shutil.copy(RAIZ / f"site/assets/img/capas/{slug}.jpg", b)
    im = Image.open(b).convert("RGB")
    esc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")


def escurecer(im, topo=0.0, fundo=0.0, geral=0.0, inicio=0.4):
    """Degradê escuro (em cima e/ou embaixo) para o texto ler bem sem esconder a foto."""
    m = Image.new("L", (1, H))
    for y in range(H):
        t = y / (H - 1)
        a = geral + topo * max(0.0, 1 - t / 0.45) ** 1.6 + fundo * min(1.0, max(0.0, (t - inicio) / (0.92 - inicio))) ** 1.2
        m.putpixel((0, y), int(255 * min(a, 0.92)))
    m = m.resize((W, H))
    preto = Image.new("RGBA", (W, H), (6, 8, 12, 255))
    return Image.composite(preto, im, m)


def escurecer_banda(im, y0, y1, forca=0.88, folga=230):
    """Escurece só a faixa onde está o texto (e uma transição suave em volta): o resto da imagem fica intacto."""
    m = Image.new("L", (1, H))
    for y in range(H):
        if y0 <= y <= y1:
            a = 1.0
        elif y < y0:
            a = max(0.0, 1 - (y0 - y) / folga)
        else:
            a = max(0.0, 1 - (y - y1) / folga)
        m.putpixel((0, y), int(255 * forca * a ** 1.3))
    return Image.composite(Image.new("RGBA", (W, H), (6, 8, 12, 255)), im, m.resize((W, H)))


def ocupado(im):
    """Mapa do que o texto não pode cobrir: rostos (pesam muito) e áreas com letras/detalhes finos."""
    try:
        import cv2, numpy as np
    except Exception:
        return None
    g = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
    mapa = np.zeros(g.shape, np.float32)
    if not hasattr(cv2, "CascadeClassifier") or not hasattr(cv2, "data"):
        return mapa  # versão do OpenCV sem detector de rostos: segue sem ele (texto embaixo)
    for nome, peso in (("haarcascade_frontalface_default.xml", 40.0), ("haarcascade_frontalface_alt2.xml", 40.0), ("haarcascade_profileface.xml", 30.0)):
        cl = cv2.CascadeClassifier(cv2.data.haarcascades + nome)
        if cl.empty():
            continue
        for (x, y, w, h) in cl.detectMultiScale(g, 1.1, 6, minSize=(60, 60)):
            mapa[max(0, y - h // 3):y + h + h // 3, x:x + w] += peso  # rosto com testa e queixo
    # letras: muitas bordas finas e de alto contraste juntas
    bordas = cv2.Canny(g, 120, 240)
    letras = cv2.morphologyEx(bordas, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5)))
    mapa += (letras > 0).astype(np.float32) * 0.6
    return mapa


def melhor_posicao(im, caixa):
    """Embaixo é o padrão. Só muda se um rosto detectado ficar coberto embaixo (aí vai para o lugar sem rosto)."""
    mapa = ocupado(im)
    if mapa is None:
        return "baixo"
    alt = caixa[3] - caixa[1]
    opc = {"baixo": (H - 70 - alt, H - 70), "cima": (150, 150 + alt), "meio": ((H - alt) // 2, (H + alt) // 2)}
    rosto = {n: float((mapa[a:b, caixa[0]:caixa[2]] >= 30).sum()) for n, (a, b) in opc.items()}
    if rosto["baixo"] < 500:
        return "baixo"
    return min(rosto, key=lambda n: (rosto[n], list(opc).index(n)))

def com_sombra(fundo, camada, raio=14, forca=170):
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s.paste((0, 0, 0, forca), (0, 0), camada.split()[3])
    return Image.alpha_composite(Image.alpha_composite(fundo, s.filter(ImageFilter.GaussianBlur(raio))), camada)


def pilula(d, cx, cy, texto, f, cor=VERM, pad=(46, 22)):
    tw = d.textlength(texto, font=f)
    a = f.size
    d.rounded_rectangle((cx - tw / 2 - pad[0], cy - a / 2 - pad[1], cx + tw / 2 + pad[0], cy + a / 2 + pad[1] + 6),
                        radius=a, fill=cor)
    d.text((cx, cy + a * 0.36), texto, font=f, fill=BRANCO, anchor="ms")


LOGO_POS = {"faixa": (725, 120), "data": (730, 110), "numero": (300, 120), "comparacao": (90, 100), "topo": (85, 100), "rodape": (860, 120)}


def logo_img(logo, max_h, max_w=560, canto=False):
    if logo["url"].startswith("logos/"):
        lg = Image.open(RAIZ / "site" / logo["url"]).convert("RGBA")
        cx_ = lg.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        lg = lg.crop(cx_) if cx_ else lg
    else:
        lg = mc().logo_sem_fundo(logo)
    esc = 1.0 if canto else logo.get("escala", 1.0)
    e = min(max_w * esc / lg.width, max_h * esc / lg.height)
    return lg.resize((round(lg.width * e), round(lg.height * e)), Image.LANCZOS)


def pôr_logo(tela, logo, cy, max_h, max_w=560, canto=False):
    """Logo oficial centralizado, sem caixa nem borda, com sombra suave. site/logos/*.png ou endereço da web."""
    if logo["url"].startswith("logos/"):
        lg = Image.open(RAIZ / "site" / logo["url"]).convert("RGBA")
        cx_ = lg.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        lg = lg.crop(cx_) if cx_ else lg
    else:
        lg = mc().logo_sem_fundo(logo)
    esc = 1.0 if canto else logo.get("escala", 1.0)
    e = min(max_w * esc / lg.width, max_h * esc / lg.height)
    lg = lg.resize((round(lg.width * e), round(lg.height * e)), Image.LANCZOS)
    pos = ((60 if logo.get("lado") == "esquerda" else W - lg.width - 60), 50) if canto else (W // 2 - lg.width // 2, cy - lg.height // 2)
    base = tela.convert("RGBA")
    sa = Image.new("L", (W, H), 0)
    sa.paste(lg.getchannel("A").point(lambda v: round(v * 0.8)), pos)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra.putalpha(sa.filter(ImageFilter.GaussianBlur(16)))
    base = Image.alpha_composite(base, sombra)
    base.alpha_composite(lg, pos)
    return base.convert("RGB")


# estilo único: tema em selo pequeno, título grande, linha de apoio, selo de detalhe (iguais em todos os modelos e posições)
TEMA = (fonte("ExtraBold", 40), VERM, (30, 14))
SELO = (fonte("Bold", 40), VERM, (46, 22))
TITULO = ("ExtraBold", 96)
SUB = ("Bold", 62)


def montar(slug, s):
    im = base(slug)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, maxw = W // 2, W - 2 * 150
    mod = s["modelo"]
    tema_cima = s.get("tema") if s.get("tema_cima") else None  # selo do tema sozinho no alto (o resto fica embaixo)
    if tema_cima:
        s = {k: v for k, v in s.items() if k != "tema"}
    if mod == "topo":  # antigo "texto no alto": agora é a faixa com posição escolhida
        mod, s = "faixa", {**s, "posicao": s.get("posicao", "cima")}
    lg_ = s.get("logo") or logo_da_colagem(slug)  # logo oficial (plataforma, jogo, filme)
    logo_canto = {**lg_, "lado": s.get("logo_lado", lg_.get("lado"))} if lg_ and lg_.get("canto", True) else None  # padrão: no canto superior direito, sem cobrir nada
    logo = None if logo_canto else lg_  # "canto": false põe o logo no lugar do nome escrito

    if mod == "faixa":  # foto inteira; tema, título e selo na base
        if s.get("tema") and not logo:
            pilula(d, cx, 752, s["tema"].upper(), *TEMA)
        d.text((cx, 900), s["titulo"], font=caber(d, s["titulo"], *TITULO, maxw), fill=BRANCO, anchor="ms")
        if s.get("detalhe"):
            pilula(d, cx, 980, s["detalhe"], *SELO)

    elif mod == "data":  # foto inteira; data grande no centro do terço de baixo
        if s.get("tema") and not logo:
            pilula(d, cx, 700, s["tema"].upper(), *TEMA)
        pilula(d, cx, 840, s["destaque"], fonte("ExtraBold", 72), pad=(40, 18))
        d.text((cx, 985), s["titulo"], font=caber(d, s["titulo"], *SUB, maxw), fill=BRANCO, anchor="ms")

    elif mod == "numero":  # foto levemente escurecida; número enorme no meio
        if s.get("tema") and not logo:
            pilula(d, cx, 320, s["tema"].upper(), *TEMA)
        d.text((cx, 600), s["destaque"], font=caber(d, s["destaque"], "ExtraBold", 260, maxw), fill=BRANCO, anchor="ms")
        d.text((cx, 720), s["titulo"], font=caber(d, s["titulo"], *SUB, maxw), fill=BRANCO, anchor="ms")
        if s.get("detalhe"):
            pilula(d, cx, 830, s["detalhe"], *SELO)

    elif mod == "comparacao":  # foto do assunto aparece em cima; duas barras na metade de baixo
        im = escurecer(im, topo=0.75, fundo=0.97, geral=0.22, inicio=0.3)
        if not logo:
            d.text((cx, 95), s["tema"].upper(), font=caber(d, s["tema"].upper(), "ExtraBold", 56, maxw), fill=VERM, anchor="ms")
        d.text((cx, 270 if logo_canto else 215), s["titulo"], font=caber(d, s["titulo"], *TITULO, maxw), fill=BRANCO, anchor="ms")
        (r1, v1, t1), (r2, v2, t2) = s["barras"]
        g = s.get("grafico", "barras")
        if g == "barras":  # duas colunas verticais
            larg, gap, base_y, alto = 250, 120, 920, 330
            esc = alto / max(v1, v2)
            for i, (rot, v, txt) in enumerate(((r1, v1, t1), (r2, v2, t2))):
                x = cx - gap // 2 - larg if i == 0 else cx + gap // 2
                h = round(v * esc)
                cor = (235, 235, 235, 240) if i == 0 else VERM
                d.rounded_rectangle((x, base_y - h, x + larg, base_y), radius=16, fill=cor)
                d.rectangle((x, base_y - 16, x + larg, base_y), fill=cor)
                d.text((x + larg // 2, base_y - h - 24), txt, font=fonte("ExtraBold", 66), fill=BRANCO, anchor="ms")
                d.text((x + larg // 2, base_y + 62), rot, font=fonte("SemiBold", 40), fill=CINZA, anchor="ms")
            d.line((cx - gap // 2 - larg - 50, base_y, cx + gap // 2 + larg + 50, base_y), fill=(255, 255, 255, 120), width=4)
            selo_y = 380 if logo_canto else 340
        elif g == "horizontal":  # duas barras deitadas, uma sobre a outra, centralizadas
            maxl, alt, x0 = 1100, 110, cx - 550
            esc = maxl / max(v1, v2)
            for i, (rot, v, txt) in enumerate(((r1, v1, t1), (r2, v2, t2))):
                y = 600 + i * 190
                w = round(v * esc)
                cor = (235, 235, 235, 240) if i == 0 else VERM
                xa = cx - w // 2
                d.rounded_rectangle((xa, y, xa + w, y + alt), radius=alt // 2, fill=cor)
                d.text((cx, y - 18), f"{rot}: {txt}", font=fonte("ExtraBold", 54), fill=BRANCO, anchor="ms")
            selo_y = 360
        elif g == "duelo":  # dois números grandes frente a frente, com "x" no meio
            for i, (rot, v, txt) in enumerate(((r1, v1, t1), (r2, v2, t2))):
                x = cx - 430 if i == 0 else cx + 430
                d.text((x, 850), txt, font=caber(d, txt, "ExtraBold", 170, 720), fill=BRANCO if i == 0 else (235, 90, 90, 255), anchor="ms")
                d.text((x, 940), rot, font=fonte("Bold", 54), fill=CINZA, anchor="ms")
            d.ellipse((cx - 62, 710, cx + 62, 834), fill=VERM)
            d.text((cx, 798), "×", font=fonte("ExtraBold", 90), fill=BRANCO, anchor="ms")
            selo_y = 360
        elif g == "seta":  # antes -> depois, com seta no meio
            for i, (rot, v, txt) in enumerate(((r1, v1, t1), (r2, v2, t2))):
                x = cx - 450 if i == 0 else cx + 450
                cor = (215, 215, 215, 255) if i == 0 else BRANCO
                d.text((x, 905), txt, font=caber(d, txt, "ExtraBold", 140, 700), fill=cor, anchor="ms")
                d.text((x, 990), rot, font=fonte("Bold", 50), fill=CINZA, anchor="ms")
            ay = 855
            d.rectangle((cx - 90, ay - 14, cx + 40, ay + 14), fill=VERM)
            d.polygon([(cx + 30, ay - 50), (cx + 100, ay), (cx + 30, ay + 50)], fill=VERM)
            selo_y = 360
        else:
            raise SystemExit(f"grafico desconhecido: {g}")
        if s.get("selo"):
            pilula(d, cx, selo_y, s["selo"], *SELO)
    elif mod == "rodape":  # só um selo na base, para fotos que já trazem nome e arte oficial no meio
        pilula(d, cx, 1000, s["detalhe"], *SELO)

    else:
        raise SystemExit(f"modelo desconhecido: {mod}")

    if logo and mod in LOGO_POS:
        cy, mh = LOGO_POS[mod]
        lg = logo_img(logo, mh)
        lay.alpha_composite(lg, (W // 2 - lg.width // 2, cy - lg.height // 2))
        logo = None
    if mod in ("faixa", "data", "numero", "rodape"):
        caixa = lay.getchannel("A").point(lambda v: 255 if v > 30 else 0).getbbox()
        dy, pos = 0, "baixo"
        if caixa:
            pos = s.get("posicao") or melhor_posicao(im, caixa)
            topo_livre = 150
            if logo_canto:  # texto no alto nunca encosta no logo do canto
                topo_livre = max(150, 50 + logo_img(logo_canto, 150 * logo_canto.get("escala", 1.0), canto=True).height + 45)
            alvo = {"baixo": H - 70 - caixa[3], "cima": topo_livre - caixa[1],
                    "meio": (H - (caixa[3] - caixa[1])) // 2 - caixa[1]}[pos]
            dy = alvo if (pos != "baixo" or s.get("posicao") == "baixo" or caixa[3] > H - 70) else 0
            if dy:
                lay = lay.transform(lay.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy))
                caixa = (caixa[0], caixa[1] + dy, caixa[2], caixa[3] + dy)
        if caixa:  # degradê suave só na borda onde o texto está (o estilo aprovado), nunca faixa escura no meio
            if mod == "numero" and not dy:  # número no meio: leve escurecida geral, como antes
                im = escurecer(im, geral=0.3, topo=0.3, fundo=0.5)
            elif pos == "baixo":
                im = escurecer(im, fundo=0.95, inicio=max(0.2, (caixa[1] - 120) / H))
            elif pos == "cima":
                im = escurecer(im, topo=0.95 * min(1.0, (caixa[3] + 120) / (0.45 * H)))
    if tema_cima:
        dl = ImageDraw.Draw(lay)
        pilula(dl, W // 2, 95, tema_cima.upper(), *TEMA)
        im = escurecer(im, topo=0.5)
    if s.get("desfocar"):  # imagem com texto miúdo atrás (créditos, rótulos): desfoca só por trás do texto da capa
        m = lay.getchannel("A").filter(ImageFilter.MaxFilter(61)).filter(ImageFilter.GaussianBlur(30))
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(22)), im, m)
    fim = com_sombra(com_sombra(im, Image.new("RGBA", (W, H)), 1, 0), lay, raio=18, forca=215)  # sombra larga (sem faixa escura)
    s_ = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_.paste((0, 0, 0, 200), (0, 0), lay.getchannel("A").filter(ImageFilter.MaxFilter(5)))
    fim = Image.alpha_composite(fim.convert("RGBA"), s_.filter(ImageFilter.GaussianBlur(4)))  # contorno escuro justo: o texto se destaca da imagem
    fim = Image.alpha_composite(fim, lay).convert("RGB")
    if logo_canto:
        fim = pôr_logo(fim, logo_canto, 0, 150 * logo_canto.get("escala", 1.0), canto=True)
    if logo and mod in LOGO_POS:
        cy, mh = LOGO_POS[mod]
        fim = pôr_logo(fim, logo, cy, mh)
    return fim


if __name__ == "__main__":
    pasta = RAIZ / "site/capas_info"
    saida = RAIZ / "site/assets/img/capas"
    if sys.argv[1:] == ["--pendentes"]:  # quantas capas faltam (usado pelo workflow)
        marca = RAIZ / "site/capas_info/.feitas"
        feitas = dict(l.split(" ", 1) for l in marca.read_text().splitlines() if " " in l) if marca.exists() else {}
        print(sum(1 for f in pasta.glob("*.json") if feitas.get(f.stem) != hashlib.md5(f.read_bytes()).hexdigest()[:10]))
        sys.exit(0)
    so = set(sys.argv[1:])
    marca = RAIZ / "site/capas_info/.feitas"  # slug + assinatura do json: se o json mudar, a capa é refeita
    feitas = dict(l.split(" ", 1) for l in marca.read_text().splitlines() if " " in l) if marca.exists() else {}
    capa_ia = None
    falhou = False
    import time as _t
    limite = _t.time() + float(os.environ.get("CAPA_MINUTOS", "0") or 0) * 60
    def quando(f):  # primeiro as capas dos artigos que saem antes
        a = RAIZ / f"agendados/{f.stem}.json"
        return json.loads(a.read_text(encoding="utf-8")).get("data", "") if a.exists() else ""
    for f in sorted(pasta.glob("*.json"), key=quando):
        if so and f.stem not in so:
            continue
        assinatura = hashlib.md5(f.read_bytes()).hexdigest()[:10]
        if not so and feitas.get(f.stem) == assinatura:
            continue
        if limite > 1e9 and _t.time() > limite:
            print("Tempo da rodada esgotado; o resto continua na próxima.", flush=True)
            break
        try:
            montar(f.stem, json.loads(f.read_text(encoding="utf-8"))).save(saida / f"{f.stem}.jpg", "JPEG", quality=90, optimize=True, progressive=True)
        except Exception as e:
            falhou = True
            print(f"FALHOU {f.stem}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        feitas[f.stem] = assinatura
        marca.write_text("".join(f"{k} {v}\n" for k, v in sorted(feitas.items())))  # salva o progresso a cada capa
        print("Capa com informação:", f.stem, flush=True)
    marca.write_text("".join(f"{k} {v}\n" for k, v in sorted(feitas.items())))
    sys.exit(1 if falhou else 0)
