"""Gera o site estático da ALOHA NOTÍCIAS a partir de conteudo/*.json.

Uso:  python3 gerar.py            -> gera em publico/
"""
import hashlib
import html
import json, re
import re
import shutil
from datetime import datetime
from pathlib import Path

import i18n

RAIZ = Path(__file__).parent
SAIDA = RAIZ.parent / "publico"
SITE = "ALOHA NOTÍCIAS"

editorias = json.loads((RAIZ / "conteudo/editorias.json").read_text(encoding="utf-8"))
materias = json.loads((RAIZ / "conteudo/materias.json").read_text(encoding="utf-8"))
ED = {e["slug"]: e for e in editorias}
materias.sort(key=lambda m: m["data"], reverse=True)

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

esc = html.escape

LANG = "pt"  # idioma da passada de geração em curso


def t(s):
    """Texto de interface no idioma atual; a chave é o texto em português."""
    return s if LANG == "pt" else i18n.UI[LANG].get(s, s)


def autor_nome(m):
    return t(m["autor"])


def _data(d, dia_semana=False):
    mes = i18n.MESES[LANG][d.month - 1]
    dia = i18n.DIAS[LANG][d.weekday()] if dia_semana else ""
    if LANG == "en":
        return f"{dia}, {mes} {d.day}, {d.year}" if dia else f"{mes} {d.day}, {d.year}"
    if LANG == "de":
        return f"{dia}, {d.day}. {mes} {d.year}" if dia else f"{d.day}. {mes} {d.year}"
    if LANG in ("fr", "it"):
        return f"{dia} {d.day} {mes} {d.year}" if dia else f"{d.day} {mes} {d.year}"
    if LANG == "ja":
        return f"{d.year}年{d.month}月{d.day}日{dia}"
    if LANG == "zh":
        return f"{d.year}年{d.month}月{d.day}日 {dia}".strip()
    if LANG == "ar":
        return f"{dia}، {d.day} {mes} {d.year}" if dia else f"{d.day} {mes} {d.year}"
    return f"{dia}, {d.day} de {mes} de {d.year}" if dia else f"{d.day} de {mes} de {d.year}"


def data_extenso(d):
    return _data(d, True)


def data_longa(iso):
    d = datetime.fromisoformat(iso)
    return f"{_data(d)}, {d:%H:%M}"


def data_curta(iso):
    d = datetime.fromisoformat(iso)
    if LANG == "en":
        return f"{d.month:02d}/{d.day:02d}"
    if LANG in ("ja", "zh"):
        return f"{d.month}/{d.day}"
    if LANG == "de":
        return f"{d.day:02d}.{d.month:02d}."
    return f"{d.day:02d}/{d.month:02d}"


def hora(iso):
    return datetime.fromisoformat(iso).strftime("%H:%M")


def leitura(m):
    palavras = sum(len(p.split()) for p in m["corpo"])
    return max(1, round(palavras / 200))


def slug_tag(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def url_tag(t):
    return f"assunto-{slug_tag(t)}.html"


def url_materia(m):
    return f"materia-{m['slug']}.html"


def url_editoria(slug):
    return f"{slug}.html"


# ---------------------------------------------------------------- logos
def svg_logo(nome, uid):
    s = (RAIZ / f"assets/img/{nome}.svg").read_text(encoding="utf-8")
    s = re.sub(r"<title>.*?</title>\s*", "", s)
    s = re.sub(r' width="[\d.]+" height="[\d.]+" role="img" aria-label="[^"]*"', ' aria-hidden="true" focusable="false"', s, count=1)
    s = s.replace('fill="#0F4C5C"', 'fill="currentColor"').replace('fill="#F4EDE4"', 'fill="currentColor"')
    for i in set(re.findall(r'id="([^"]+)"', s)):
        s = s.replace(f'id="{i}"', f'id="{uid}-{i}"').replace(f"#{i})", f"#{uid}-{i})")
    return s


O_SIMBOLO = svg_logo("aloha-o-simbolo", "erro")

# ---------------------------------------------------------------- capas
# Ilustrações de capa provisórias (substituir por fotos reais).
TONS = {
    "noticias": ("#0F4C5C", "#9CC3C7", "#F4EDE4"),
    "cinema": ("#16333C", "#E76F51", "#F4EDE4"),
    "games": ("#1C5966", "#8DB8BC", "#E76F51"),
    "tecnologia": ("#0A3440", "#9CC3C7", "#F4EDE4"),
    "curiosidades": ("#E9DFD1", "#0F4C5C", "#E76F51"),
    "financas": ("#24605F", "#8FBFB0", "#F4EDE4"),
}


def legenda(m):
    im = m.get("imagem")
    if im and im.get("credito"):
        return f'<figcaption class="credito">{esc(im["credito"])}</figcaption>'
    return ""


def video(m):
    v = m.get("video")
    if not v:
        return ""
    return (f'<div class="wrap video-materia"><div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{esc(v["youtube"])}" '
            f'title="{esc(v.get("titulo", "Video"))}" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" '
            f'allowfullscreen sandbox="allow-scripts allow-same-origin allow-presentation allow-popups" referrerpolicy="strict-origin-when-cross-origin"></iframe></div></div>')


def capa(m, cls="capa"):
    im = m.get("imagem")
    if im:
        return f'<img class="{cls}" src="{esc(im["url"])}" alt="{esc(im.get("alt", m["titulo"]))}" loading="lazy" decoding="async">'
    fundo, onda, sol = TONS[m["editoria"]]
    h = int(hashlib.md5(m["slug"].encode()).hexdigest(), 16)
    sx = 260 + (h % 360)
    sy = 120 + (h >> 8) % 90
    r = 46 + (h >> 16) % 40
    ondas = []
    for i in range(3):
        y = 250 + i * 46 + ((h >> (20 + i * 4)) % 20)
        a = 14 + ((h >> (32 + i * 3)) % 14)
        op = (0.9, 0.55, 0.3)[i]
        ondas.append(
            f'<path d="M-20 {y} C 120 {y - a}, 240 {y - a}, 400 {y} S 680 {y + a}, 820 {y} L 820 460 L -20 460 Z" '
            f'fill="{onda}" fill-opacity="{op}"/>'
        )
    return (f'<svg class="{cls}" viewBox="0 0 800 450" preserveAspectRatio="xMidYMid slice" role="img" '
            f'aria-label="{t('Ilustração')}: {esc(ED[m["editoria"]]["nome"])}">'
            f'<rect width="800" height="450" fill="{fundo}"/>'
            f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{sol}" fill-opacity="0.85"/>'
            + "".join(reversed(ondas)) + "</svg>")


# ---------------------------------------------------------------- partes
ICONE_BUSCA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICONE_TEMA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'

HOJE = datetime.fromisoformat(materias[0]["data"])


ICONE_IDIOMA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18"/></svg>'
def _bandeira(corpo):
    return f'<svg class="bandeira" viewBox="0 0 30 20" width="22" height="15" aria-hidden="true" focusable="false">{corpo}</svg>'


def _faixas_v(*cores):
    return "".join(f'<rect x="{i * 30 / len(cores)}" width="{30 / len(cores) + .1}" height="20" fill="{c}"/>' for i, c in enumerate(cores))


def _faixas_h(*cores):
    return "".join(f'<rect y="{i * 20 / len(cores)}" width="30" height="{20 / len(cores) + .1}" fill="{c}"/>' for i, c in enumerate(cores))


BANDEIRAS = {
    "pt": _bandeira('<rect width="30" height="20" fill="#009C3B"/><polygon points="15,2 27.5,10 15,18 2.5,10" fill="#FFDF00"/><circle cx="15" cy="10" r="4.4" fill="#002776"/>'),
    "en": _bandeira('<rect width="30" height="20" fill="#fff"/>' + "".join(f'<rect y="{i * 20 / 7 * 2}" width="30" height="{20 / 13 * 1.0 + 1.1}" fill="#B22234"/>' for i in range(4)) + '<rect width="13" height="10.8" fill="#3C3B6E"/>'),
    "es": _bandeira('<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>'),
    "fr": _bandeira(_faixas_v("#0055A4", "#fff", "#EF4135")),
    "de": _bandeira(_faixas_h("#000", "#DD0000", "#FFCE00")),
    "it": _bandeira(_faixas_v("#009246", "#fff", "#CE2B37")),
    "ja": _bandeira('<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="6" fill="#BC002D"/>'),
    "zh": _bandeira('<rect width="30" height="20" fill="#DE2910"/><polygon points="6,2.5 7.3,6.4 11.4,6.4 8.1,8.8 9.3,12.7 6,10.3 2.7,12.7 3.9,8.8 0.6,6.4 4.7,6.4" fill="#FFDE00"/>'),
    "ar": _bandeira('<rect width="30" height="20" fill="#fff"/><rect y="0" width="30" height="6.7" fill="#00732F"/><rect y="13.3" width="30" height="6.7" fill="#000"/><rect width="8" height="20" fill="#FF0000"/>'),
}
IDIOMAS_GOOGLE = []  # todos os idiomas agora são páginas reais
BANDEIRAS_EXTRA = {}


def _item_idioma(code, nome, flag=True):
    bd = BANDEIRAS.get(code, "") if flag else ""
    if code in i18n.IDIOMAS_REAIS:
        atual = ' aria-current="true"' if code == LANG else ""
        return f'<li><a href="@@L:{code}@@" hreflang="{i18n.HTML_LANG[code]}" lang="{i18n.HTML_LANG[code]}"{atual}>{bd}<span>{nome}</span></a></li>'
    return f'<li><a data-l="{code}" href="#" rel="noopener">{bd}<span>{nome}</span></a></li>'


def seletor_idioma():
    lista = "".join(_item_idioma(c, i18n.NOMES_IDIOMA[c]) for c in i18n.IDIOMAS_REAIS) + "".join(_item_idioma(c, n) for c, n in IDIOMAS_GOOGLE)
    return (f'<details class="idioma-menu" id="idioma-menu"><summary class="botao-icone" aria-label="{t("Traduzir esta página / Translate")}">'
            f'{BANDEIRAS[LANG]}<span class="idioma-rotulo">{i18n.SIGLA[LANG]}</span></summary>'
            f'<ul class="idioma-lista"><li class="idioma-tit">{t("Traduzir / Translate")}</li>{lista}</ul></details>')


def idiomas_rodape():
    links = "".join(
        (f'<a href="@@L:{c}@@" hreflang="{i18n.HTML_LANG[c]}" lang="{i18n.HTML_LANG[c]}">{i18n.NOMES_IDIOMA[c]}</a>' if c in i18n.IDIOMAS_REAIS else f'<a data-l="{c}" href="#" rel="noopener">{n}</a>')
        for c, n in [(c, i18n.NOMES_IDIOMA[c]) for c in i18n.IDIOMAS_REAIS] + IDIOMAS_GOOGLE)
    return f'<div class="idiomas" aria-label="{t("Traduzir esta página / Translate")}"><span>{t("Traduzir / Translate:")}</span> {links}</div>'


ED_VISIVEIS = [e for e in editorias if e["slug"] != "financas"]  # Finanças fica fora do menu por enquanto
ICONE_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
LOGO_IMG = '<img src="assets/img/aloha-logo-prancha.svg" alt="ALOHA NOTÍCIAS" width="290" height="92">'


def cabecalho(ativo):
    itens = [("index.html", t("Início"), "inicio")] + [(url_editoria(e["slug"]), e["nome"], e["slug"]) for e in ED_VISIVEIS]
    li = "".join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if s == ativo else ""}>{esc(n)}</a></li>' for u, n, s in itens
    )
    return f"""<a class="pular" href="#conteudo">{t('Pular para o conteúdo')}</a>
<header class="cabecalho">
  <div class="barra-m"><div class="wrap">
    <button class="menu-m" id="botao-menu" type="button" aria-expanded="false" aria-controls="gaveta">{ICONE_MENU}<span>{t('Menu')}</span></button>
    <a class="logo-m" href="index.html" aria-label="{SITE}, {t('página inicial')}">{LOGO_IMG}</a>
    <a class="busca-m" href="busca.html" aria-label="{t('Buscar')}">{ICONE_BUSCA}</a>
  </div></div>
  <div class="logo-area"><div class="wrap">
    <a class="cab-logo" href="index.html" aria-label="{SITE}, {t('página inicial')}">{LOGO_IMG}</a>
  </div></div>
  <nav class="nav" aria-label="{t('Editorias')}"><div class="wrap"><ul>{li}</ul><div class="nav-ferr">{seletor_idioma()}<button class="botao-icone" id="botao-tema" type="button" aria-label="{t('Alternar tema')}">{ICONE_TEMA}</button><a class="nav-busca" href="busca.html" aria-label="{t('Buscar')}">{ICONE_BUSCA}</a></div></div></nav>
  <nav class="gaveta" id="gaveta" aria-label="{t('Editorias')}" hidden><div class="wrap">
    <form class="gaveta-busca" action="busca.html" role="search"><label class="sr-only" for="q-gaveta">{t('Pesquisar')}</label><input id="q-gaveta" name="q" type="search" placeholder="{t('Pesquisar')} ..."><button type="submit" aria-label="{t('Buscar')}">{ICONE_BUSCA}</button></form>
    <ul>{li}</ul>
    <div class="gaveta-ferr">{seletor_idioma().replace(' id="idioma-menu"', '')}<button class="botao-icone botao-tema-m" type="button" aria-label="{t('Alternar tema')}">{ICONE_TEMA}</button></div>
  </div></nav>
</header>
"""


NEWSLETTER_ATIVA = False  # ligue quando houver um serviço de e-mail conectado
# Anúncios: depois da aprovação do AdSense, preencha ADSENSE_PUB (ex.: "pub-1234567890123456") e ligue ANUNCIOS_ATIVOS.
# Ligado, o site passa a: gerar o ads.txt, liberar o Google no CSP, mostrar o aviso de cookies (os anúncios só carregam
# depois do "Aceitar") e acrescentar a seção de anúncios à política de privacidade.
ANUNCIOS_ATIVOS = False
ADSENSE_PUB = ""


def newsletter():
    return """<section class="newsletter" aria-labelledby="titulo-news">
  <div class="wrap">
    <div><h2 id="titulo-news">O essencial do dia, toda manhã</h2><p>Um e-mail curto com as notícias que importam, de segunda a sexta.</p></div>
    <form class="form-news" novalidate>
      <label class="sr-only" for="email-news">Seu e-mail</label>
      <input id="email-news" type="email" name="email" placeholder="seu@email.com" autocomplete="email" required>
      <button class="botao" type="submit">Assinar</button>
      <p class="form-aviso" role="status"></p>
    </form>
  </div>
</section>"""


def rodape():
    eds = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a></li>' for e in ED_VISIVEIS)
    return f"""<footer class="rodape">
  <div class="wrap">
    <div><a class="rodape-logo" href="index.html" aria-label="{SITE}, {t('página inicial')}">{LOGO_IMG}</a>
      <p>{t('Cinema, games e tecnologia explicados com calma, de olho no que importa.')}</p></div>
    <div><h2>{t('Editorias')}</h2><ul>{eds}</ul></div>
    <div><h2>{t('Institucional')}</h2><ul>
      <li><a href="sobre.html">{t("Sobre nós")}</a></li>
      <li><a href="contato.html">{t("Contato e anúncios")}</a></li>
      <li><a href="busca.html">{t("Buscar")}</a></li>
      <li><a href="equipe.html">{t("Equipe Aloha")}</a></li>
      <li><a href="politica-editorial.html">{t("Política editorial")}</a></li>
      <li><a href="termos.html">{t("Termos de uso")}</a></li>
      <li><a href="privacidade.html">{t("Privacidade")}</a></li>
      <li><a href="feed.xml">{t("RSS")}</a></li>
    </ul></div>
    {idiomas_rodape()}
    <div class="rodape-base"><span>© {HOJE.year} {SITE}</span></div>
  </div>
</footer>"""


def og_url(u):
    return u if u.startswith("http") else "https://alohanoticias.com/" + u.lstrip("/")


def og_da_capa(m):
    """Imagem de compartilhamento: redes sociais não leem SVG, então usa o PNG de mesmo nome quando existir."""
    u = (m.get("imagem") or {}).get("url", "")
    if not u:
        return "assets/img/og-padrao.png"
    if u.endswith(".svg") and (RAIZ / u.replace(".svg", ".png")).exists():
        return u.replace(".svg", ".png")
    return u


CONSENT_TXT = {"pt": "Usamos cookies para exibir anúncios e manter o site gratuito. Você escolhe: sem aceitar, não carregamos anúncios.", **i18n.CONSENT}
SABER_MAIS = {"pt": "Saiba mais", **i18n.SABER}


def consent_html():
    return (f'<div class="consent" id="consent" role="dialog" aria-label="{t("Aviso de cookies")}" hidden>\n'
            f'  <p>{CONSENT_TXT[LANG]} <a href="privacidade.html">{SABER_MAIS[LANG]}</a>.</p>\n'
            f'  <div><button class="botao" id="consent-sim" type="button">{t("Aceitar")}</button> <button class="botao sec" id="consent-nao" type="button">{t("Recusar")}</button></div>\n</div>\n')
CONSENT_JS = f'<script src="assets/js/consent.js" data-client="ca-{ADSENSE_PUB}"></script>'


def pagina(titulo, descricao, ativo, corpo, com_news=True, extra_head="", og_img="assets/img/og-padrao.png", og_tipo="website"):
    BASE = ""
    if '<base href="/">' in extra_head:
        BASE = '<base href="/">\n'
        extra_head = extra_head.replace('<base href="/">\n', "")
    tt = f"{titulo} · {SITE}" if titulo != SITE else t("ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia")
    return f"""<!doctype html>
<html lang="{i18n.HTML_LANG[LANG]}"{' dir="rtl"' if LANG == "ar" else ''}>
<head>
<meta charset="utf-8">
{BASE}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(tt)}</title>
<meta name="description" content="{esc(descricao)}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="{i18n.OG_LOCALE[LANG]}">
<meta property="og:type" content="{og_tipo}">
<meta property="og:url" content="https://alohanoticias.com/{{CANON}}">
<meta property="og:image" content="{og_url(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE}" href="feed.xml">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<link rel="canonical" href="https://alohanoticias.com/{{CANON}}">
@@ALT@@
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-title" content="ALOHA">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/aloha.css">
<link rel="stylesheet" href="assets/css/antigo.css">
<script src="assets/js/tema.js"></script>
{extra_head}</head>
<body>
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{newsletter() if (com_news and NEWSLETTER_ATIVA) else ""}
{rodape()}
{consent_html() if ANUNCIOS_ATIVOS else ""}<script src="assets/js/site.js"></script>{CONSENT_JS if ANUNCIOS_ATIVOS else ""}
</body>
</html>
"""


def card(m, pequeno=False, mostrar_capa=True, chapeu=True):
    return f"""<a class="card{' pequeno' if pequeno else ''}" href="{url_materia(m)}">
  {capa(m) if mostrar_capa else ""}
  {f'<span class="chapeu">{esc(ED[m["editoria"]]["nome"])}</span>' if chapeu else ""}
  <h3>{esc(m["titulo"])}</h3>
  <p class="meta"><time datetime="{m["data"]}">{data_curta(m["data"])}</time><span>{leitura(m)} {t("min de leitura")}</span></p>
</a>"""


def mais_lidas(lista, cls=""):
    if len(lista) < 3:
        return ""
    itens = "".join(f'<li><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for m in lista)
    return f'<aside class="mais-lidas {cls}" aria-labelledby="ml-{cls or "x"}"><h2 id="ml-{cls or "x"}">{t("Mais lidas")}</h2><ol>{itens}</ol></aside>'


# Ordem de "mais lidas" de exemplo (troque pela sua métrica de audiência)
MAIS_LIDAS = materias[:5]


# ---------------------------------------------------------------- home











def tag_v(m):
    return f'<span class="tag-v">{esc(ED[m["editoria"]]["nome"])}</span>'


def hero_card(m, grande):
    fina = f'<p class="hero-fina">{esc(m["linha_fina"])}</p>' if grande else ""
    return f"""<a class="hero-card{' grande' if grande else ''}" href="{url_materia(m)}">
  {capa(m, "hero-img")}
  {tag_v(m)}
  <div class="hero-texto">
    <time datetime="{m['data']}">{data_longa(m['data'])}</time>
    <h2>{esc(m['titulo'])}</h2>
    {fina}
  </div>
</a>"""


def item_lista(m):
    return f"""<article class="item-lista">
  <a class="il-capa" href="{url_materia(m)}" tabindex="-1" aria-hidden="true">{capa(m)}{tag_v(m)}</a>
  <div class="il-texto">
    <p class="meta-l"><span class="autor">{esc(autor_nome(m))}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time></p>
    <h3><a href="{url_materia(m)}">{esc(m['titulo'])}</a></h3>
    <p class="resumo">{esc(m['linha_fina'])}</p>
    <a class="leia-mais" href="{url_materia(m)}">{t("Leia mais")} »</a>
  </div>
</article>"""


def titulo_secao(texto, h="h2"):
    return f'<div class="tit-secao"><{h}>{esc(texto)}</{h}></div>'


def lateral():
    recentes = "".join(f'<li><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for m in materias[:6])
    cats = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a></li>' for e in ED_VISIVEIS)
    mais = "".join(
        f'<li><a class="mini" href="{url_materia(m)}">{capa(m)}{tag_v(m)}<strong>{esc(m["titulo"])}</strong>'
        f'<time datetime="{m["data"]}">{data_longa(m["data"])}</time></a></li>' for m in materias[:4])
    return f"""<aside class="lateral-site" aria-label="{t('Barra lateral')}">
  <section>{titulo_secao(t("Mais recentes"))}<ul class="mini-lista">{mais}</ul></section>
  <section>{titulo_secao(t("Pesquisar"))}<form class="pesquisar" action="busca.html" role="search">
    <label class="sr-only" for="q-lateral">Pesquisar</label><input id="q-lateral" name="q" type="search"><button type="submit">{t("Pesquisar")}</button></form></section>
  <section>{titulo_secao(t("Matérias recentes"))}<ul class="lista-links">{recentes}</ul></section>
  <section>{titulo_secao(t("Categorias"))}<ul class="lista-links">{cats}</ul></section>
</aside>"""


def gerar_home():
    manchete = next((m for m in materias if m.get("manchete")), materias[0])
    destaques = [manchete] + [m for m in materias if m is not manchete][:2]
    usados = {m["slug"] for m in destaques}
    hero = "".join(hero_card(m, i == 0) for i, m in enumerate(destaques))
    secoes = []
    for e in ED_VISIVEIS:
        da_ed = [m for m in materias if m["editoria"] == e["slug"]][:5]
        if not da_ed:
            continue
        secoes.append(f"""<section class="secao-lista" aria-labelledby="sec-{e['slug']}">
  <div class="tit-secao"><h2 id="sec-{e['slug']}">{esc(e['nome'])}</h2></div>
  {"".join(item_lista(m) for m in da_ed)}
  <a class="ver-tudo" href="{url_editoria(e['slug'])}">{t("Ver tudo em")} {esc(e['nome'])} »</a>
</section>""")
    corpo = f"""<h1 class="sr-only">{SITE}: notícias, cinema, games, tecnologia e finanças</h1>
<section class="hero hero-{len(destaques)}" aria-label="{t('Destaques')}"><div class="wrap hero-grade">{hero}</div></section>
<div class="wrap duas-colunas">
  <div class="coluna-principal">{"".join(secoes)}</div>
  {lateral()}
</div>"""
    return pagina(SITE, t("Notícias, cinema, games e tecnologia, explicados com calma."), "inicio", corpo)


# ---------------------------------------------------------------- editoria
def card_cat(m):
    return f"""<article class="card-cat">
  <h2><a href="{url_materia(m)}">{esc(m['titulo'])}</a></h2>
  <p class="meta-l"><time datetime="{m['data']}">{data_longa(m['data'])}</time><span>{leitura(m)} {t("min")}</span></p>
  <a class="cc-capa" href="{url_materia(m)}" tabindex="-1" aria-hidden="true">{capa(m)}</a>
  <p class="resumo">{esc(m['linha_fina'])}</p>
  <a class="leia-mais" href="{url_materia(m)}">{t("Leia mais")} »</a>
</article>"""


def gerar_editoria(e):
    da_ed = [m for m in materias if m["editoria"] == e["slug"]]
    lista = "".join(card_cat(m) for m in da_ed) if da_ed else '<p class="resumo">{t("Ainda não publicamos matérias nesta editoria. Volte em breve.")}</p>'
    corpo = f"""<div class="wrap duas-colunas">
  <div class="coluna-principal">
    <nav class="migalhas-v" aria-label="{t('Você está em')}"><a href="index.html">{t("Início")}</a> &gt; <span>{esc(e['nome'])}</span></nav>
    <h1 class="titulo-cat">{esc(e['nome'])}</h1>
    <p class="desc-cat">{esc(e['descricao'])}</p>
    <div class="grade-cat">{lista}</div>
  </div>
  {lateral()}
</div>"""
    return pagina(e["nome"], e["descricao"], e["slug"], corpo)


# ---------------------------------------------------------------- matéria
def corpo_texto(paragrafos):
    out = []
    for p in paragrafos:
        if p.startswith("!img "):
            url, alt, cred = (p[5:].split("|") + ["", ""])[:3]
            out.append(f'<figure class="foto-corpo"><img src="{esc(url)}" alt="{esc(alt)}" loading="lazy" decoding="async"><figcaption class="credito">{esc(cred)}</figcaption></figure>')
        elif p.startswith("## "):
            out.append(f"<h2>{esc(p[3:])}</h2>")
        else:
            t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', esc(p))
            t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
            out.append(f"<p>{t}</p>")
    return "\n".join(out)


REPO = "alohanoticias/aloha-noticias"
HORARIOS_PADRAO = ["09:00", "13:00", "19:00"]  # atalhos de horário no admin (Brasília)


def link_acao(acao, slug):
    from urllib.parse import quote
    return (f"https://github.com/{REPO}/issues/new?title={quote(acao + ': ' + slug)}"
            f"&body={quote('Clique em Submit new issue para confirmar. O site é atualizado em cerca de 1 minuto.')}")


def prev_trad(m):
    """Links para a prévia das versões em outros idiomas (só no admin)."""
    trs = m.get("traducoes") or {}
    if not trs:
        return '<span>Sem traduções neste rascunho.</span> '
    nomes = i18n.NOMES_IDIOMA
    return "<span>Prévia das traduções:</span> " + " ".join(f'<a href="admin/{l}/{esc(m["slug"])}.html">{nomes.get(l, l)}</a>' for l in i18n.IDIOMAS_REAIS[1:] if l in trs) + " "


def faixa_rascunho(m, agendado=False):
    slug = m["slug"]
    acao = "Reagendar" if agendado else "Aprovar"
    if agendado:
        quando = datetime.fromisoformat(m["data"]).strftime("%d/%m/%Y às %H:%M")
        rotulo, atual = f"Agendado para {quando}.", f' value="{m["data"]}"'
        texto_ag, rot_agendar = "ou mudar para", "Reagendar"
        rej = "Cancelar agendamento"
    else:
        rotulo, atual = "Rascunho, ainda não publicado.", ""
        texto_ag, rot_agendar = "ou agendar para", "Agendar"
        rej = "Rejeitar"
    atalhos = " ".join(f'<button type="button" class="chip" data-hora="{h}">{h[:2]}h</button>' for h in HORARIOS_PADRAO)
    return (f'<div class="faixa-rascunho" data-slug="{esc(slug)}" data-repo="{REPO}" data-acao="{acao}"><div class="wrap">'
            f'<strong>{rotulo}</strong> '
            f'<a class="botao" href="{link_acao("Aprovar", slug)}" target="_blank" rel="noopener noreferrer">Publicar agora</a> '
            f'<label class="agendar">{texto_ag} <input type="datetime-local" id="quando"{atual} aria-label="Data e hora de publicação"></label> '
            f'<span class="atalhos">Atalhos: {atalhos}</span> '
            f'<a class="botao-sec" id="agendar" href="{link_acao(acao, slug)}" target="_blank" rel="noopener noreferrer">{rot_agendar}</a> '
            f'<a class="botao-sec" href="{link_acao("Rejeitar", slug)}" target="_blank" rel="noopener noreferrer">{rej}</a> '
            f'{prev_trad(m)}<a href="admin/">Voltar à lista</a></div></div>\n<script src="assets/js/admin.js"></script>')


def gerar_admin(rascunhos, agendados=()):
    if rascunhos:
        itens = "".join(
            f'<li><a href="admin/{esc(d["slug"])}.html"><div class="dupla" style="gap:6px"><span class="chapeu">{esc(ED[d["editoria"]]["nome"])}</span>'
            f'<h3>{esc(d["titulo"])}</h3><p class="linha-fina" style="font-size:1rem">{esc(d["linha_fina"])}</p>'
            f'<p class="meta"><span>{esc(d["autor"])}</span><time datetime="{d["data"]}">{data_curta(d["data"])}</time><span>{leitura(d)} min de leitura</span></p></div></a></li>'
            for d in rascunhos)
        lista = f'<ul class="lista-simples" style="max-width:820px">{itens}</ul>'
    else:
        lista = '<p class="linha-fina">Nenhum rascunho esperando aprovação no momento.</p>'
    if agendados:
        itens2 = "".join(
            f'<li><a href="admin/{esc(d["slug"])}.html"><div class="dupla" style="gap:6px"><span class="chapeu">Agendado: {datetime.fromisoformat(d["data"]).strftime("%d/%m %H:%M")}</span>'
            f'<h3>{esc(d["titulo"])}</h3><p class="meta"><span>{esc(ED[d["editoria"]]["nome"])}</span></p></div></a></li>'
            for d in agendados)
        lista += f'<h2 style="margin-top:40px">Agendados</h2><ul class="lista-simples" style="max-width:820px">{itens2}</ul>'
    corpo = f"""<div class="topo-editoria"><div class="wrap"><h1>Admin: rascunhos</h1><p>Abra o rascunho, leia como ficará no site e clique em Aprovar e publicar ou em Rejeitar.</p></div></div>
<div class="wrap editoria-corpo">{lista}</div>"""
    return pagina("Admin", "Rascunhos para aprovação", "", corpo, com_news=False, extra_head='<base href="/">\n<meta name="robots" content="noindex,nofollow">\n')


def atualizado_html(m):
    """Campo opcional "atualizado" (YYYY-MM-DDTHH:MM) na matéria: mostra "Atualizado em ..." ao lado da data."""
    a = m.get("atualizado")
    return f'<time datetime="{a}">{t("Atualizado em")} {data_longa(a)}</time>' if a else ""


def correcao_html(m):
    """Campo opcional "correcao": texto da nota de correção/atualização exibida ao fim da matéria."""
    c = m.get("correcao")
    return f'<aside class="nota-correcao"><strong>{t("Atualização:")}</strong> {esc(c)}</aside>' if c else ""


def autor_html(m):
    return f'<a href="equipe.html">{esc(autor_nome(m))}</a>' if m["autor"] == "Equipe Aloha" else esc(m["autor"])


def botoes_compartilhar(m):
    from urllib.parse import quote
    pre = "" if LANG == "pt" else LANG + "/"
    u = quote("https://alohanoticias.com/" + pre + url_materia(m), safe="")
    tit = quote(m["titulo"], safe="")
    tt = quote(m["titulo"] + " https://alohanoticias.com/" + pre + url_materia(m), safe="")
    redes = [("WhatsApp", f"https://wa.me/?text={tt}"), ("X", f"https://twitter.com/intent/tweet?text={tit}&url={u}"),
             ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}"), ("Telegram", f"https://t.me/share/url?url={u}&text={tit}")]
    return "".join(f'<a class="botao-sec" href="{h}" target="_blank" rel="noopener noreferrer" aria-label="{t('Compartilhar no')} {n}">{n}</a>' for n, h in redes)


def gerar_materia(m, preview=False, agendado=False):
    e = ED[m["editoria"]]
    relacionadas = [x for x in materias if x["editoria"] == m["editoria"] and x is not m][:3]
    if len(relacionadas) < 3:
        relacionadas += [x for x in materias if x is not m and x not in relacionadas][: 3 - len(relacionadas)]
    tags = "".join(f'<a href="{url_tag(t)}">{esc(t)}</a>' for t in m.get("tags", []) if slug_tag(t))
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": m["titulo"],
        "description": m["linha_fina"], "datePublished": m["data"], "dateModified": m.get("atualizado") or m["data"], "articleSection": e["nome"],
        "image": [og_url(og_da_capa(m))], "mainEntityOfPage": "https://alohanoticias.com/" + ("" if LANG == "pt" else LANG + "/") + url_materia(m), "inLanguage": i18n.HTML_LANG[LANG],
        "author": {"@type": "Person" if m["autor"] != "Equipe Aloha" else "Organization", "name": autor_nome(m)},
        "publisher": {"@type": "Organization", "name": SITE},
    }, ensure_ascii=False)
    corpo = f"""<article class="wrap materia">
  <nav class="migalhas" aria-label="{t('Você está em')}"><a href="index.html">{t('Início')}</a><span aria-hidden="true">/</span><a href="{url_editoria(e['slug'])}">{esc(e['nome'])}</a></nav>
  <header class="materia-topo">
    <span class="chapeu">{esc(e['nome'])}</span>
    <h1>{esc(m['titulo'])}</h1>
    <p class="linha-fina">{esc(m['linha_fina'])}</p>
    <p class="meta"><span>{t("Por")} {autor_html(m)}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time>{atualizado_html(m)}<span>{leitura(m)} {t("min de leitura")}</span></p>
  </header>
  <figure class="materia-capa" style="margin-inline:0">{capa(m)}{legenda(m)}</figure>{video(m)}
  <div class="materia-grade">
    <div class="texto">
      <div class="compartilhar"><span>{t("Compartilhe")}</span>{botoes_compartilhar(m)}<button class="botao-sec" id="copiar-link" type="button" data-rotulo="{t('Copiar link')}" data-ok="{t('Link copiado')}" data-erro="{t('Copie o endereço na barra do navegador')}">{t("Copiar link")}</button></div>
      {corpo_texto(m['corpo'])}{correcao_html(m)}
      <div class="tags" aria-label="{t('Assuntos')}">{tags}</div>
      {'' if LANG == 'pt' else f'<p class="nota-traducao">{t("Esta matéria foi escrita em português e adaptada para o inglês pela equipe.")} <a href="@@L:pt@@" hreflang="pt">{t("Original em português")}</a></p>'}
    </div>
    <div class="lateral">{mais_lidas(MAIS_LIDAS, "mat")}</div>
  </div>
</article>
{"" if not relacionadas else f'''<section class="leia-tambem" aria-labelledby="leia">
  <div class="wrap">
    <div class="secao-topo"><h2 id="leia">{t("Leia também")}</h2><a class="ver-tudo" href="{url_editoria(e['slug'])}">{t("Mais em")} {esc(e['nome'])} →</a></div>
    <div class="grade-3">{"".join(card(x) for x in relacionadas)}</div>
  </div>
</section>'''}"""
    head = f'<script type="application/ld+json">{ld}</script>\n'
    if preview:
        corpo = faixa_rascunho(m, agendado) + corpo
        head = '<base href="/">\n<meta name="robots" content="noindex,nofollow">\n' + head
    return pagina(m["titulo"], m["linha_fina"], e["slug"], corpo, extra_head=head, og_img=og_da_capa(m), og_tipo="article")


# ---------------------------------------------------------------- busca e páginas simples
INDICES = {}


def gerar_busca():
    indice = [{
        "titulo": m["titulo"], "linha_fina": m["linha_fina"], "editoria": ED[m["editoria"]]["nome"],
        "tags": m.get("tags", []), "url": url_materia(m), "data": data_longa(m["data"]), "capa": capa(m),
    } for m in materias]
    corpo = f"""<div class="topo-editoria"><div class="wrap"><h1>{t("Buscar")}</h1>
  <form class="busca-form" id="form-busca" role="search">
    <label class="sr-only" for="campo-busca">{t("Buscar matérias")}</label>
    <input id="campo-busca" type="search" placeholder="{t('Ex.: GTA 6, Vingadores, Switch 2')}" autocomplete="off">
    <button class="botao" type="submit">{t("Buscar")}</button>
  </form></div></div>
<div class="wrap editoria-corpo">
  <p class="busca-resultado" id="info-busca" role="status"></p>
  <ul class="lista-simples" id="resultados" style="max-width:820px"></ul>
</div>
<script src="assets/js/indice{'' if LANG == 'pt' else '-' + LANG}.js"></script>"""
    textos = {k: t(k) for k in ["Digite um assunto, por exemplo: GTA 6, Marvel ou cinema.", "Nada encontrado para", "Tente outra palavra.", "matéria encontrada", "matérias encontradas"]}
    INDICES[LANG] = ("window.ALOHA_T = " + json.dumps(textos, ensure_ascii=False) + ";\nwindow.ALOHA_INDICE = " + json.dumps(indice, ensure_ascii=False) + ";\n")
    return pagina(t("Buscar"), t("Busque matérias da ALOHA NOTÍCIAS."), "", corpo, com_news=False)


def gerar_simples(titulo, descricao, conteudo):
    corpo = f'<div class="wrap"><div class="pagina-texto"><h1>{esc(titulo)}</h1>{conteudo}</div></div>'
    return pagina(titulo, descricao, "", corpo)


def gerar_404():
    corpo = f"""<div class="wrap erro"><div class="o">{O_SIMBOLO}</div><h1>{t("Essa onda passou")}</h1>
<p>{t("A página que você procurou não existe ou mudou de endereço.")}</p><a class="botao" href="index.html">{t("Voltar para a página inicial")}</a></div>"""
    return pagina(t("Página não encontrada"), t("Página não encontrada"), "", corpo, com_news=False)


# ---------------------------------------------------------------- saída
PRIV_ANUNCIOS = """<h2>Anúncios e cookies</h2>
<p>Este site exibe anúncios do Google AdSense. Com a sua permissão, o Google e seus parceiros podem usar cookies e identificadores do aparelho para mostrar anúncios e medir o desempenho deles. Os anúncios só são carregados depois que você clica em &ldquo;Aceitar&rdquo; no aviso de cookies; se recusar, o site continua funcionando normalmente, sem anúncios. Você pode mudar de ideia a qualquer momento em <a href="#" id="reabrir-consent">preferências de cookies</a>.</p>
<p>Saiba como o Google usa dados de sites parceiros em <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com/technologies/partner-sites</a>. Você também pode gerenciar anúncios personalizados em <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.</p>
"""

CSP_BASE = ("default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; "
            "frame-src https://www.youtube-nocookie.com; connect-src 'self' https://cloudflareinsights.com; object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests")
CSP_ADS = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.doubleclick.net https://www.googletagservices.com https://adservice.google.com https://partner.googleadservices.com; "
           "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; "
           "frame-src https://www.youtube-nocookie.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; "
           "connect-src 'self' https://cloudflareinsights.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google; "
           "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests")

HEADERS = """/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: {CSP}

/admin/*
  X-Robots-Tag: noindex, nofollow
  Cache-Control: no-store

/assets/*
  Cache-Control: public, max-age=3600, must-revalidate
"""


def montar_arquivos():
    for _m in (list(materias) if LANG == "pt" else []):
        _p = sum(len(b.split()) for b in _m["corpo"] if not b.startswith("!img"))
        if not 520 <= _p <= 880:
            print(f"AVISO tamanho: {_m['slug']} tem {_p} palavras (meta: 600 a 850, 3 a 4 min de leitura)")
    arquivos = {"index.html": gerar_home(), "busca.html": gerar_busca(), "404.html": gerar_404()}
    for e in editorias:
        arquivos[url_editoria(e["slug"])] = gerar_editoria(e)
    for m in materias:
        arquivos[url_materia(m)] = gerar_materia(m)

    arquivos["sobre.html"] = gerar_simples("Sobre nós", "Quem faz a ALOHA NOTÍCIAS.", """
<p>A ALOHA NOTÍCIAS é um site de notícias para quem quer entender o que está acontecendo sem pressa e sem barulho. Nosso foco é cinema, games e tecnologia: estreias, lançamentos e o que está em alta, com a informação conferida.</p>
<h2>Como trabalhamos</h2>
<p>Cada matéria cita suas fontes, separa fato de opinião e é corrigida de forma transparente quando erramos. Os detalhes estão na nossa <a href="politica-editorial.html">política editorial</a>.</p>
<h2>O nome</h2>
<p><em>Aloha</em> é a saudação havaiana que também significa afeto e respeito. É assim que queremos tratar quem nos lê.</p>
<h2>Fale com a gente</h2>
<p>Sugestões, correções e parcerias na página de <a href="contato.html">contato</a>.</p>""")
    arquivos["politica-editorial.html"] = gerar_simples("Política editorial e de correções", "Como a ALOHA NOTÍCIAS apura, escreve, ilustra e corrige suas matérias.", """
<p>Esta página explica, em linguagem simples, como o conteúdo da ALOHA NOTÍCIAS é feito. Se algo aqui não for cumprido, queremos saber.</p>
<h2>Como apuramos</h2>
<p>Procuramos confirmar cada informação importante em mais de uma fonte antes de publicar. Datas, preços e números só entram no texto quando aparecem nas fontes consultadas, que listamos no fim de cada matéria. Quando uma informação vem de uma fonte só, ou ainda não foi confirmada, dizemos isso no texto.</p>
<h2>Revisão antes de publicar</h2>
<p>Nenhuma matéria vai ao ar sem a revisão e a aprovação de uma pessoa da equipe.</p>
<h2>Fato e opinião</h2>
<p>Separamos o que foi apurado do que é análise. Textos de opinião ou recomendação são identificados como tal.</p>
<h2>Como escolhemos os assuntos</h2>
<p>Priorizamos o que está em alta e é útil para quem lê: estreias, lançamentos, datas e novidades de cinema, games e tecnologia. Não publicamos só para repetir um comunicado. Em cada matéria buscamos reunir o que está confirmado, organizar o que ainda não se sabe e indicar de onde veio cada informação.</p>
<h2>Boatos e rumores</h2>
<p>Rumores, vazamentos e informações de bastidores só aparecem quando são relevantes, e sempre identificados como não confirmados, com a fonte indicada. Não tratamos boato como fato.</p>
<h2>Imagens e vídeos</h2>
<p>As capas são montadas pela nossa equipe com fotos de bancos de imagens de uso livre, como o Unsplash, com o crédito do autor na matéria, e com elementos gráficos próprios. Não usamos cartazes, capas ou imagens protegidas de filmes, jogos ou personagens. O vídeo de uma matéria, quando existe, é um conteúdo oficial incorporado do canal onde foi publicado, com o nome do canal indicado. Se você é autor ou dono de uma imagem e quer outro crédito ou a remoção, escreva para a gente.</p>
<h2>Correções</h2>
<p>Quando encontramos um erro, corrigimos a matéria e indicamos a correção no texto. Também atualizamos matérias quando datas ou fatos mudam, para que o conteúdo não fique desatualizado. Se você encontrou um erro, envie a matéria e o que está incorreto pela página de <a href="contato.html">contato</a>. Respondemos o quanto antes.</p>
<h2>Independência</h2>
<p>O conteúdo editorial é independente. Anúncios, quando existirem, ficam separados do texto e não influenciam o que publicamos. Se uma matéria tiver patrocínio ou parceria, isso será informado claramente ao leitor.</p>""")
    arquivos["equipe.html"] = gerar_simples("Equipe Aloha", "Quem assina as matérias da ALOHA NOTÍCIAS e o que cobrimos.", f"""
<p>Equipe Aloha é a assinatura da redação do ALOHA NOTÍCIAS, um site independente em português sobre cinema, games e tecnologia. Reúne quem pesquisa, escreve, monta as capas e revisa as matérias publicadas aqui.</p>
<h2>Quem está por trás</h2>
<p>O ALOHA NOTÍCIAS é um projeto editorial independente, mantido por uma equipe e sem vínculo com estúdios, produtoras ou fabricantes. Toda matéria passa por revisão e aprovação de uma pessoa antes de ir ao ar.</p>
<h2>O que você pode esperar</h2>
<p>Informação conferida em mais de uma fonte, fontes citadas no fim de cada texto, rumores identificados como tal e correções feitas às claras. Se algo estiver errado, a gente quer saber.</p>
<h2>O que cobrimos</h2>
<ul>{"".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a>: {esc(e["descricao"])}</li>' for e in editorias)}</ul>
<h2>Como trabalhamos</h2>
<p>Confirmamos os fatos em mais de uma fonte, citamos as fontes no fim de cada matéria e corrigimos os erros de forma aberta. Veja a <a href="politica-editorial.html">política editorial</a>.</p>
<h2>Fale com a gente</h2>
<p>Pautas, correções e parcerias: <a href="contato.html">página de contato</a>.</p>""")
    por_tag = {}
    for m in materias:
        for tg in m.get("tags", []):
            if slug_tag(tg):
                por_tag.setdefault(tg, []).append(m)
    for tg, lista in por_tag.items():
        itens = "".join(
            f'<li><a href="{url_materia(x)}"><div class="dupla" style="gap:6px"><span class="chapeu">{esc(ED[x["editoria"]]["nome"])}</span><h3>{esc(x["titulo"])}</h3>'
            f'<p class="linha-fina" style="font-size:1rem">{esc(x["linha_fina"])}</p>'
            f'<p class="meta"><time datetime="{x["data"]}">{data_curta(x["data"])}</time><span>{leitura(x)} {t("min")}</span></p></div>{capa(x)}</a></li>' for x in lista)
        corpo = (f'<div class="topo-editoria"><div class="wrap"><h1>{esc(tg)}</h1><p>{len(lista)} {t("matéria") if len(lista) == 1 else t("matérias")} {t("sobre este assunto.")}</p></div></div>'
                 f'<div class="wrap editoria-corpo"><ul class="lista-simples" style="max-width:820px">{itens}</ul></div>')
        arquivos[url_tag(tg)] = pagina(tg, f"{t('Matérias da ALOHA NOTÍCIAS sobre')} {tg}.", "", corpo)
    arquivos["contato.html"] = gerar_simples("Contato e anúncios", "Fale com a redação da ALOHA NOTÍCIAS.", """
<p>Fale com a gente pelo e-mail <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>. Para agilizar, coloque no assunto o motivo do contato:</p>
<h2>Sugestão de pauta</h2><p>Viu algo que merece uma matéria? Mande o assunto e, se tiver, o link da fonte.</p>
<h2>Correções</h2><p>Encontrou um erro? Envie o endereço da matéria e o que está incorreto, com a fonte, se possível. Veja como tratamos correções na <a href="politica-editorial.html">política editorial</a>.</p>
<h2>Direitos autorais e imagens</h2><p>Se você é autor ou dono de uma imagem, texto ou vídeo e quer corrigir o crédito ou pedir a retirada, escreva com o endereço da página e a comprovação de autoria.</p>
<h2>Publicidade e parcerias</h2><p>Para anunciar ou propor parcerias, escreva para o mesmo e-mail. Conteúdo patrocinado será sempre identificado como tal.</p>
<h2>Privacidade</h2><p>Pedidos sobre dados pessoais seguem o que está na <a href="privacidade.html">política de privacidade</a>.</p>""")
    arquivos["termos.html"] = gerar_simples("Termos de uso", "Termos de uso do site ALOHA NOTÍCIAS.", """
<p>Última atualização: novembro de 2026. Ao acessar o ALOHA NOTÍCIAS (alohanoticias.com), você concorda com estes termos. Se não concordar, pedimos que não use o site.</p>
<h2>O que é o site</h2>
<p>O ALOHA NOTÍCIAS publica matérias sobre cinema, games, tecnologia, notícias e curiosidades. O conteúdo é oferecido para informação e entretenimento.</p>
<h2>Conteúdo informativo, sem aconselhamento</h2>
<p>As matérias têm caráter informativo e de entretenimento e não substituem a orientação de um profissional. Fazemos o possível para publicar informações corretas e atuais, mas dados, preços e datas podem mudar depois da publicação.</p>
<h2>Propriedade intelectual</h2>
<p>Os textos e as ilustrações originais do site pertencem ao ALOHA NOTÍCIAS. Você pode compartilhar links e citar trechos curtos, com o crédito e o link para a matéria original. Não é permitido copiar matérias inteiras, republicá-las ou usá-las para treinar sistemas automáticos sem autorização por escrito.</p>
<p>Marcas, nomes, imagens e vídeos de terceiros citados nas matérias pertencem aos seus donos e aparecem com finalidade informativa e crédito. Se você é dono de um conteúdo e quer corrigir o crédito ou pedir a retirada, fale conosco pela página de <a href="contato.html">contato</a>.</p>
<h2>Links e serviços de terceiros</h2>
<p>O site pode ter links para outros sites e conteúdos incorporados de serviços como o YouTube. Não controlamos esses endereços e não nos responsabilizamos pelo que publicam ou pelas regras deles.</p>
<h2>Publicidade</h2>
<p>O site poderá exibir anúncios. Quando houver, eles serão identificados como publicidade e separados do conteúdo editorial. A existência de um anúncio não significa que apoiamos o produto ou o serviço anunciado.</p>
<h2>Uso adequado</h2>
<p>Você concorda em não tentar prejudicar o funcionamento do site, acessar áreas restritas, enviar códigos maliciosos ou usar o site para fins ilegais.</p>
<h2>Limitação de responsabilidade</h2>
<p>O site é oferecido como está. Não garantimos que ele esteja sempre disponível ou livre de erros e não nos responsabilizamos por perdas decorrentes do uso das informações publicadas, dentro do que a lei permitir.</p>
<h2>Privacidade</h2>
<p>O tratamento de dados está descrito na <a href="privacidade.html">política de privacidade</a>.</p>
<h2>Mudanças e lei aplicável</h2>
<p>Podemos alterar estes termos, e a versão em vigor é a publicada nesta página, com a data de atualização. Estes termos seguem as leis do Brasil.</p>
<h2>Contato</h2>
<p>Dúvidas sobre estes termos: <a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a>.</p>""")
    arquivos["privacidade.html"] = gerar_simples("Privacidade", "Política de privacidade da ALOHA NOTÍCIAS.", """
<p>Última atualização: novembro de 2026. Respeitamos a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018). Aqui está, de forma direta, o que acontece com os seus dados quando você visita este site.</p>
<h2>O que coletamos</h2>
<p>Não pedimos cadastro e não usamos cookies de publicidade ou de rastreamento. Guardamos no seu próprio navegador apenas a sua preferência de tema claro ou escuro.</p>
<p>Medimos o número de acessos com um serviço de estatísticas que não usa cookies e não identifica você pessoalmente (Cloudflare Web Analytics). Os dados vistos por nós são agregados, como páginas mais lidas, país e tipo de aparelho.</p>
<h2>Serviços de terceiros</h2>
<p>As fontes de letra vêm do Google Fonts. Fotos podem vir do Unsplash e vídeos são incorporados do YouTube, em modo de privacidade aprimorada (youtube-nocookie.com). Ao carregar esses conteúdos, esses serviços recebem o seu endereço de IP e podem ter regras próprias de privacidade. O site é hospedado pela Cloudflare.</p>
""" + (PRIV_ANUNCIOS if ANUNCIOS_ATIVOS else "") + """<h2>E-mail de contato</h2>
<p>Se você nos escrever, usaremos o seu e-mail apenas para responder. Não vendemos nem repassamos os seus dados.</p>
<h2>Seus direitos</h2>
<p>Você pode pedir informações sobre os dados que temos sobre você, a correção ou a exclusão deles, escrevendo pela página de <a href="contato.html">contato</a>.</p>
<h2>Mudanças</h2>
<p>Se esta política mudar, a data acima será atualizada. Se passarmos a usar cookies, anúncios ou newsletter, vamos avisar aqui antes.</p>""")

    if LANG != "pt":
        eds = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a>: {esc(e["descricao"])}</li>' for e in editorias)
        for nome, (tit, desc, corpo) in i18n.PAGINAS[LANG].items():
            corpo = corpo.replace("@@EDITORIAS@@", eds).replace("@@ANUNCIOS@@", i18n.PRIV_ANUNCIOS[LANG] if ANUNCIOS_ATIVOS else "")
            arquivos[nome] = gerar_simples(tit, desc, corpo)
        arquivos.pop("404.html", None)
    return arquivos


# ---------------------------------------------------------------- idiomas
MATERIAS_PT, EDITORIAS_PT = materias, editorias


def traduzir(m, tr, lang):
    d = dict(m)
    d["titulo"], d["linha_fina"], d["corpo"] = tr["titulo"], tr["linha_fina"], tr["corpo"]
    d["tags"] = tr.get("tags", m.get("tags", []))
    d["correcao"] = tr.get("correcao")
    if m.get("imagem"):
        d["imagem"] = {**m["imagem"], "alt": tr.get("alt", m["imagem"].get("alt", "")), "credito": tr.get("credito", m["imagem"].get("credito", ""))}
    if m.get("video"):
        d["video"] = {**m["video"], "titulo": tr.get("video_titulo", m["video"].get("titulo", ""))}
    return d


def aplicar_idioma(lang):
    global LANG, materias, editorias, ED, MAIS_LIDAS
    LANG = lang
    if lang == "pt":
        materias, editorias = MATERIAS_PT, EDITORIAS_PT
    else:
        ms = [traduzir(m, m["traducoes"][lang], lang) for m in MATERIAS_PT if (m.get("traducoes") or {}).get(lang)]
        if not ms:
            return False
        usados = {m["editoria"] for m in ms}
        materias = ms
        editorias = [{"slug": e["slug"], "nome": i18n.EDITORIAS[lang][e["slug"]][0], "descricao": i18n.EDITORIAS[lang][e["slug"]][1]}
                     for e in EDITORIAS_PT if e["slug"] in usados]
    ED = {e["slug"]: e for e in editorias}
    MAIS_LIDAS = materias[:5]
    return True


def prefixo(lang):
    return "" if lang == "pt" else lang + "/"


# Endereços traduzidos. Internamente cada página tem um nome em português (a "chave");
# o nome final de cada idioma sai de nome_idioma(). Os links são reescritos em localizar().
_L = ["en", "es", "fr", "de", "it", "ja", "zh", "ar"]
PREF_MAT = dict(zip(_L, ["article", "articulo", "article", "artikel", "articolo", "kiji", "wenzhang", "maqal"]))
PREF_TAG = dict(zip(_L, ["topic", "tema", "sujet", "thema", "argomento", "tag", "huati", "mawdu"]))
_F = {  # em ordem: en, es, fr, de, it, ja, zh, ar
    "sobre": ["about", "quienes-somos", "a-propos", "ueber-uns", "chi-siamo", "about", "about", "about"],
    "contato": ["contact", "contacto", "contact", "kontakt", "contatti", "contact", "contact", "contact"],
    "busca": ["search", "buscar", "recherche", "suche", "cerca", "search", "search", "search"],
    "equipe": ["team", "equipo", "equipe", "team", "team", "team", "team", "team"],
    "politica-editorial": ["editorial-policy", "politica-editorial", "politique-editoriale", "redaktionelle-richtlinien", "linea-editoriale", "editorial-policy", "editorial-policy", "editorial-policy"],
    "termos": ["terms", "terminos", "conditions", "nutzungsbedingungen", "termini", "terms", "terms", "terms"],
    "privacidade": ["privacy", "privacidad", "confidentialite", "datenschutz", "privacy", "privacy", "privacy", "privacy"],
    "games": ["games", "juegos", "jeux", "spiele", "giochi", "games", "games", "games"],
    "cinema": ["movies", "cine", "cinema", "kino", "cinema", "eiga", "dianying", "cinema"],
    "tecnologia": ["technology", "tecnologia", "technologie", "technik", "tecnologia", "tech", "keji", "tech"],
    "noticias": ["news", "noticias", "actualites", "nachrichten", "notizie", "news", "xinwen", "news"],
    "curiosidades": ["curiosities", "curiosidades", "curiosites", "kurioses", "curiosita", "trivia", "qushi", "curiosities"],
}
FIXOS = {k: dict(zip(_L, v)) for k, v in _F.items()}
SLUGS_IDIOMA = {}  # {lang: {slug_pt: slug_no_idioma}}


def _slug_ok(x):
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", x or ""))


def preparar_slugs():
    for lang in _L:
        SLUGS_IDIOMA[lang] = {}
        for m in MATERIAS_PT:
            sl = ((m.get("traducoes") or {}).get(lang) or {}).get("slug")
            SLUGS_IDIOMA[lang][m["slug"]] = sl if _slug_ok(sl) else m["slug"]


def nome_idioma(lang, nome):
    """Nome do arquivo no idioma, a partir do nome em português."""
    if lang == "pt" or not nome.endswith(".html"):
        return nome
    base = nome[:-5]
    if base in FIXOS:
        return FIXOS[base][lang] + ".html"
    if base.startswith("materia-"):
        return f"{PREF_MAT[lang]}-{SLUGS_IDIOMA[lang].get(base[8:], base[8:])}.html"
    if base.startswith("assunto-"):
        return f"{PREF_TAG[lang]}-{base[8:]}.html"
    return nome


def localizar(html_, lang):
    """Troca, no HTML do idioma, os nomes de página em português pelos nomes do idioma."""
    if lang == "pt":
        return html_
    return re.sub(r'(?:(?<=["\'/])|(?<=%2F))([A-Za-z0-9_-]+\.html)(?=["\'#?%&])',
                  lambda mo: nome_idioma(lang, mo.group(1)), html_)


def url_abs(lang, nome):
    nome = nome_idioma(lang, nome)
    return "https://alohanoticias.com/" + prefixo(lang) + ("" if nome == "index.html" else nome)


def rel_url(src, dst, nome, existe):
    destino = nome_idioma(dst, nome) if nome in existe.get(dst, ()) else "index.html"
    if src == dst:
        return destino
    if src == "pt":
        return f"{dst}/{destino}"
    return f"../{destino}" if dst == "pt" else f"../{dst}/{destino}"


def resolver(html_, lang, nome, existe):
    """Troca os marcadores de idioma, canonical e hreflang e ajusta os caminhos dos arquivos compartilhados."""
    html_ = localizar(html_, lang)
    html_ = re.sub(r"@@L:([\w-]+)@@", lambda mo: rel_url(lang, mo.group(1), nome, existe), html_)
    langs = [l for l in i18n.IDIOMAS_REAIS if nome in existe.get(l, ())]
    alt = ""
    if len(langs) > 1:
        alt = "".join(f'<link rel="alternate" hreflang="{i18n.HTML_LANG[l]}" href="{url_abs(l, nome)}">\n' for l in langs)
        if "pt" in langs:
            alt += f'<link rel="alternate" hreflang="x-default" href="{url_abs("pt", nome)}">\n'
    html_ = html_.replace("@@ALT@@\n", alt).replace("@@ALT@@", alt)
    canon = prefixo(lang) + ("" if nome == "index.html" else nome_idioma(lang, nome))
    html_ = html_.replace("{CANON}", canon)
    if lang != "pt":
        html_ = re.sub(r'(href|src)="(assets/|feed\.xml|manifest\.webmanifest)', r'\1="../\2', html_)
    return html_


def main():
    global LANG, editorias, ED, materias
    import checar_fotos
    if not checar_fotos.main():
        raise SystemExit('Há foto com endereço incompleto; corrija antes de gerar o site.')
    if SAIDA.exists():
        # Limpa o conteúdo; em alguns discos não é possível apagar a própria pasta.
        for item in SAIDA.iterdir():
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    (SAIDA / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copytree(RAIZ / "assets", SAIDA / "assets", dirs_exist_ok=True)

    preparar_slugs()
    por_idioma = {}
    for lang in i18n.IDIOMAS_REAIS:
        if aplicar_idioma(lang):
            por_idioma[lang] = montar_arquivos()
    aplicar_idioma("pt")

    existe = {l: set(a) for l, a in por_idioma.items()}
    for lang, arqs in por_idioma.items():
        (SAIDA / prefixo(lang)).mkdir(exist_ok=True)
        for nome, conteudo in arqs.items():
            (SAIDA / prefixo(lang) / nome_idioma(lang, nome)).write_text(resolver(conteudo, lang, nome, existe), encoding="utf-8")
        ind = INDICES[lang]
        if lang != "pt":
            ind = localizar(ind, lang).replace('src=\\"assets/', 'src=\\"../assets/')
        (SAIDA / "assets/js" / ("indice.js" if lang == "pt" else f"indice-{lang}.js")).write_text(ind, encoding="utf-8")
    arquivos = por_idioma["pt"]
    (SAIDA / "_headers").write_text(HEADERS.replace("{CSP}", CSP_ADS if ANUNCIOS_ATIVOS else CSP_BASE), encoding="utf-8")
    if ANUNCIOS_ATIVOS and ADSENSE_PUB:
        (SAIDA / "ads.txt").write_text(f"google.com, {ADSENSE_PUB}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (SAIDA / ".well-known").mkdir(exist_ok=True)
    (SAIDA / ".well-known/security.txt").write_text(
        "Contact: mailto:contato@alohanoticias.com\nExpires: 2027-11-01T00:00:00.000Z\nPreferred-Languages: pt, en\nCanonical: https://alohanoticias.com/.well-known/security.txt\n", encoding="utf-8")
    (SAIDA / "manifest.webmanifest").write_text(json.dumps({
        "name": "ALOHA NOTÍCIAS", "short_name": "ALOHA", "description": "Notícias, cinema, games, tecnologia, curiosidades e finanças.",
        "start_url": "/", "scope": "/", "display": "standalone", "lang": "pt-BR",
        "background_color": "#FFFFFF", "theme_color": "#0a0a0a",
        "icons": [{"src": "assets/img/icone-app-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "assets/img/icone-app-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "assets/img/icone-app-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
        ensure_ascii=False), encoding="utf-8")
    from email.utils import format_datetime
    from xml.sax.saxutils import escape as xe
    from datetime import timezone, timedelta
    br = timezone(timedelta(hours=-3))
    itens = "".join(
        f"<item><title>{xe(m['titulo'])}</title><link>https://alohanoticias.com/{url_materia(m)}</link>"
        f"<guid isPermaLink=\"true\">https://alohanoticias.com/{url_materia(m)}</guid>"
        f"<pubDate>{format_datetime(datetime.fromisoformat(m['data']).replace(tzinfo=br))}</pubDate>"
        f"<category>{xe(ED[m['editoria']]['nome'])}</category><description>{xe(m['linha_fina'])}</description></item>"
        for m in materias[:30])
    (SAIDA / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"<title>{SITE}</title><link>https://alohanoticias.com/</link><description>Notícias, cinema, games, tecnologia, curiosidades e finanças.</description>"
        '<language>pt-BR</language><atom:link href="https://alohanoticias.com/feed.xml" rel="self" type="application/rss+xml"/>'
        + itens + "</channel></rss>", encoding="utf-8")
    rascunhos = []
    for f in sorted((RAIZ.parent / "rascunhos").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("slug") == f.stem and d.get("editoria") in ED:
            rascunhos.append(d)
    rascunhos.sort(key=lambda d: d["data"], reverse=True)
    agendados = []
    for f in sorted((RAIZ.parent / "agendados").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("slug") == f.stem and d.get("editoria") in ED:
            agendados.append(d)
    agendados.sort(key=lambda d: d["data"])
    (SAIDA / "admin").mkdir(exist_ok=True)
    (SAIDA / "admin/index.html").write_text(resolver(gerar_admin(rascunhos, agendados), "pt", "admin/index.html", existe), encoding="utf-8")
    for d in rascunhos:
        (SAIDA / f"admin/{d['slug']}.html").write_text(resolver(gerar_materia(d, preview=True), "pt", f"admin/{d['slug']}.html", existe), encoding="utf-8")
    # prévias das traduções de rascunhos e agendados (admin/en/<slug>.html, admin/es/<slug>.html)
    for lang in i18n.IDIOMAS_REAIS[1:]:
        (SAIDA / "admin" / lang).mkdir(exist_ok=True)
        for d in list(rascunhos) + list(agendados):
            tr = (d.get("traducoes") or {}).get(lang)
            if not tr:
                continue
            LANG = lang
            editorias = [{"slug": sl, "nome": n, "descricao": ds} for sl, (n, ds) in i18n.EDITORIAS[lang].items()]
            ED = {e["slug"]: e for e in editorias}
            materias = [traduzir(m, m["traducoes"][lang], lang) for m in MATERIAS_PT if (m.get("traducoes") or {}).get(lang)]
            pg = gerar_materia(traduzir(d, tr, lang), preview=True, agendado=d in agendados)
            pg = localizar(pg, lang)
            pg = re.sub(r'href="([A-Za-z0-9_-]+\.html)"', lambda mo: f'href="{lang}/{mo.group(1)}"' if mo.group(1) != "index.html" else mo.group(0), pg)
            pg = pg.replace("{CANON}", f"admin/{lang}/{d['slug']}.html")
            pg = re.sub(r"@@L:[\w-]+@@", "index.html", pg).replace("@@ALT@@", "")
            (SAIDA / "admin" / lang / f"{d['slug']}.html").write_text(pg, encoding="utf-8")
    aplicar_idioma("pt")
    for d in agendados:
        (SAIDA / f"admin/{d['slug']}.html").write_text(resolver(gerar_materia(d, preview=True, agendado=True), "pt", f"admin/{d['slug']}.html", existe), encoding="utf-8")
    # versão no endereço de CSS/JS: o navegador baixa de novo sempre que o arquivo muda
    import hashlib as _h
    def _v(m):
        f = SAIDA / m.group(1)
        return f'{m.group(1)}?v={_h.md5(f.read_bytes()).hexdigest()[:8]}"' if f.exists() else m.group(0)
    for pg in SAIDA.rglob("*.html"):
        t = pg.read_text(encoding="utf-8")
        t2 = re.sub(r'(assets/(?:css|js)/[\w.-]+\.(?:css|js))"', _v, t)
        if t2 != t:
            pg.write_text(t2, encoding="utf-8")
    sm = "".join(f"<url><loc>{url_abs(l, n)}</loc></url>" for l, arqs in por_idioma.items() for n in arqs if n not in ("404.html", "busca.html"))
    (SAIDA / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + "</urlset>", encoding="utf-8")
    (SAIDA / "688dca8a511dd5a078482e96f25fecb8.txt").write_text("688dca8a511dd5a078482e96f25fecb8", encoding="utf-8")  # chave IndexNow
    (SAIDA / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: https://alohanoticias.com/sitemap.xml\n")
    print(f"{len(arquivos)} páginas geradas em {SAIDA}")


if __name__ == "__main__":
    main()
