"""Capas "com informação": a foto do assunto continua visível e ganha por cima um dado-chave
(número, data, comparação) em texto centralizado. É um modelo a mais, convivendo com as colagens de montar_capa.py.

Lê site/capas_info/<slug>.json e grava site/assets/img/capas/<slug>.jpg (1920x1080) usando como base
a foto do assunto em site/capas_base/<slug>.jpg (se não existir, copia a capa atual para lá antes).

Formato do .json (todos os textos são curtos; tudo fica centralizado e nunca é cortado):
  {"modelo": "faixa" | "data" | "numero" | "comparacao" | "topo" | "rodape",
   "desfocar": true                        (opcional: desfoca a imagem só atrás do texto, quando ela tem letras miúdas),
   "logo": {"url": "logos/netflix.png" ou endereço de png oficial, "escala": 1.0}   (opcional: logo oficial no lugar do tema escrito; logos prontos em site/logos/),
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


LOGO_POS = {"faixa": (725, 120), "data": (110, 120), "numero": (300, 120), "comparacao": (90, 100), "topo": (85, 100), "rodape": (860, 120)}


def pôr_logo(tela, logo, cy, max_h, max_w=560):
    """Logo oficial centralizado, sem caixa nem borda, com sombra suave. site/logos/*.png ou endereço da web."""
    if logo["url"].startswith("logos/"):
        lg = Image.open(RAIZ / "site" / logo["url"]).convert("RGBA")
        cx_ = lg.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        lg = lg.crop(cx_) if cx_ else lg
    else:
        lg = mc().logo_sem_fundo(logo)
    e = min(max_w * logo.get("escala", 1.0) / lg.width, max_h * logo.get("escala", 1.0) / lg.height)
    lg = lg.resize((round(lg.width * e), round(lg.height * e)), Image.LANCZOS)
    pos = (W // 2 - lg.width // 2, cy - lg.height // 2)
    base = tela.convert("RGBA")
    sa = Image.new("L", (W, H), 0)
    sa.paste(lg.getchannel("A").point(lambda v: round(v * 0.8)), pos)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra.putalpha(sa.filter(ImageFilter.GaussianBlur(16)))
    base = Image.alpha_composite(base, sombra)
    base.alpha_composite(lg, pos)
    return base.convert("RGB")


def montar(slug, s):
    im = base(slug)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, maxw = W // 2, W - 2 * 150
    mod = s["modelo"]
    logo = s.get("logo") or logo_da_colagem(slug)  # logo oficial (filme, jogo, série): substitui o nome escrito

    if mod == "faixa":  # foto inteira; tema, título e selo na base
        im = escurecer(im, fundo=0.95, inicio=0.35)
        if s.get("tema") and not logo:
            pilula(d, cx, 760, s["tema"].upper(), fonte("ExtraBold", 40), pad=(30, 14))
        d.text((cx, 900), s["titulo"], font=caber(d, s["titulo"], "ExtraBold", 96, maxw), fill=BRANCO, anchor="ms")
        if s.get("detalhe"):
            pilula(d, cx, 975, s["detalhe"], fonte("Bold", 40))

    elif mod == "data":  # foto inteira; data grande no centro do terço de baixo
        im = escurecer(im, topo=0.55, fundo=0.95)
        if s.get("tema") and not logo:
            d.text((cx, 120), s["tema"].upper(), font=caber(d, s["tema"].upper(), "ExtraBold", 56, maxw), fill=BRANCO, anchor="ms")
        pilula(d, cx, 840, s["destaque"], fonte("ExtraBold", 72), pad=(40, 18))
        d.text((cx, 990), s["titulo"], font=caber(d, s["titulo"], "Bold", 62, maxw), fill=BRANCO, anchor="ms")

    elif mod == "numero":  # foto levemente escurecida; número enorme no meio
        im = escurecer(im, geral=0.35, topo=0.3, fundo=0.5)
        if s.get("tema") and not logo:
            pilula(d, cx, 320, s["tema"].upper(), fonte("ExtraBold", 44), pad=(30, 14))
        d.text((cx, 600), s["destaque"], font=caber(d, s["destaque"], "ExtraBold", 260, maxw), fill=BRANCO, anchor="ms")
        d.text((cx, 720), s["titulo"], font=caber(d, s["titulo"], "Bold", 64, maxw), fill=BRANCO, anchor="ms")
        if s.get("detalhe"):
            pilula(d, cx, 830, s["detalhe"], fonte("ExtraBold", 54))

    elif mod == "comparacao":  # foto do assunto aparece em cima; duas barras na metade de baixo
        im = escurecer(im, topo=0.75, fundo=0.97, geral=0.22, inicio=0.3)
        if not logo:
            d.text((cx, 95), s["tema"].upper(), font=caber(d, s["tema"].upper(), "ExtraBold", 56, maxw), fill=VERM, anchor="ms")
        d.text((cx, 215), s["titulo"], font=caber(d, s["titulo"], "ExtraBold", 80, maxw), fill=BRANCO, anchor="ms")
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
            selo_y = 340
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
            pilula(d, cx, selo_y, s["selo"], fonte("ExtraBold", 54))
    elif mod == "rodape":  # só um selo na base, para fotos que já trazem nome e arte oficial no meio
        im = escurecer(im, fundo=0.85, inicio=0.6)
        pilula(d, cx, 1000, s["detalhe"], fonte("ExtraBold", 50), pad=(40, 16))

    elif mod == "topo":  # texto no alto, para fotos com logo ou letreiro na metade de baixo
        im = escurecer(im, topo=0.97)
        if s.get("tema") and not logo:
            pilula(d, cx, 95, s["tema"].upper(), fonte("ExtraBold", 40), pad=(30, 14))
        d.text((cx, 230), s["titulo"], font=caber(d, s["titulo"], "ExtraBold", 96, maxw), fill=BRANCO, anchor="ms")
        if s.get("detalhe"):
            pilula(d, cx, 315, s["detalhe"], fonte("Bold", 40))

    else:
        raise SystemExit(f"modelo desconhecido: {mod}")

    if s.get("desfocar"):  # imagem com texto miúdo atrás (créditos, rótulos): desfoca só por trás do texto da capa
        m = lay.getchannel("A").filter(ImageFilter.MaxFilter(61)).filter(ImageFilter.GaussianBlur(30))
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(22)), im, m)
    fim = com_sombra(im, lay).convert("RGB")
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
    def quando(f):  # primeiro as capas dos artigos que saem antes
        a = RAIZ / f"agendados/{f.stem}.json"
        return json.loads(a.read_text(encoding="utf-8")).get("data", "") if a.exists() else ""
    for f in sorted(pasta.glob("*.json"), key=quando):
        if so and f.stem not in so:
            continue
        assinatura = hashlib.md5(f.read_bytes()).hexdigest()[:10]
        if not so and feitas.get(f.stem) == assinatura:
            continue
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
