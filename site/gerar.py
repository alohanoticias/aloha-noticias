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


def data_longa(iso):
    d = datetime.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}, {d:%H:%M}"


def data_curta(iso):
    d = datetime.fromisoformat(iso)
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


LOGO_LINHA = svg_logo("aloha-noticias-logo-linha", "cab")
LOGO_EMP = svg_logo("aloha-noticias-logo-empilhado-negativo", "rod")
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
            f'title="{esc(v.get("titulo", "Vídeo"))}" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" '
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
            f'aria-label="Ilustração: {esc(ED[m["editoria"]]["nome"])}">'
            f'<rect width="800" height="450" fill="{fundo}"/>'
            f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{sol}" fill-opacity="0.85"/>'
            + "".join(reversed(ondas)) + "</svg>")


# ---------------------------------------------------------------- partes
ICONE_BUSCA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICONE_TEMA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
ICONE_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

HOJE = datetime.fromisoformat(materias[0]["data"])


def cabecalho(ativo):
    itens = [("index.html", "Início", "inicio")] + [(url_editoria(e["slug"]), e["nome"], e["slug"]) for e in editorias]
    li = "".join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if s == ativo else ""}>{esc(n)}</a></li>' for u, n, s in itens
    )
    agora = "".join(
        f'<li><a href="{url_materia(m)}"><time datetime="{m["data"]}">{hora(m["data"])}</time>{esc(m["titulo"])}</a></li>'
        for m in materias[:6]
    )
    data_hoje = f"{DIAS[HOJE.weekday()]}, {HOJE.day} de {MESES[HOJE.month - 1]} de {HOJE.year}"
    return f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="cabecalho">
  <div class="wrap cab-linha">
    <a class="cab-logo" href="index.html" aria-label="{SITE}, página inicial">{LOGO_LINHA}</a>
    <span class="cab-data">{data_hoje}</span>
    <div class="cab-acoes">
      <a class="botao-icone" href="busca.html" aria-label="Buscar">{ICONE_BUSCA}</a>
      <button class="botao-icone" id="botao-tema" type="button" aria-label="Alternar tema">{ICONE_TEMA}</button>
      <button class="botao-icone menu-botao" id="botao-menu" type="button" aria-expanded="false" aria-controls="gaveta" aria-label="Abrir menu">{ICONE_MENU}</button>
    </div>
  </div>
  <nav class="nav" aria-label="Editorias"><div class="wrap"><ul>{li}</ul></div></nav>
  <nav class="gaveta" id="gaveta" aria-label="Editorias" hidden><div class="wrap"><ul>{li}</ul></div></nav>
</header>
"""


NEWSLETTER_ATIVA = False  # ligue quando houver um serviço de e-mail conectado


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
    eds = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a></li>' for e in editorias)
    return f"""<footer class="rodape">
  <div class="wrap">
    <div><a class="rodape-logo" href="index.html" aria-label="{SITE}, página inicial">{LOGO_EMP}</a>
      <p>Notícias, cultura e ciência explicadas com calma, de olho no mundo inteiro.</p></div>
    <div><h2>Editorias</h2><ul>{eds}</ul></div>
    <div><h2>Institucional</h2><ul>
      <li><a href="sobre.html">Sobre nós</a></li>
      <li><a href="contato.html">Contato e anúncios</a></li>
      <li><a href="busca.html">Buscar</a></li>
      <li><a href="equipe.html">Equipe Aloha</a></li>
      <li><a href="politica-editorial.html">Política editorial</a></li>
      <li><a href="privacidade.html">Privacidade</a></li>
      <li><a href="feed.xml">RSS</a></li>
    </ul></div>
    <div class="rodape-base"><span>© {HOJE.year} {SITE}</span></div>
  </div>
</footer>"""


def og_url(u):
    return u if u.startswith("http") else "https://alohanoticias.com/" + u.lstrip("/")


def pagina(titulo, descricao, ativo, corpo, com_news=True, extra_head="", og_img="assets/img/og-padrao.png", og_tipo="website"):
    BASE = ""
    if '<base href="/">' in extra_head:
        BASE = '<base href="/">\n'
        extra_head = extra_head.replace('<base href="/">\n', "")
    t = f"{titulo} · {SITE}" if titulo != SITE else f"{SITE}: notícias, cinema, games, tecnologia e finanças"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
{BASE}<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(t)}</title>
<meta name="description" content="{esc(descricao)}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:locale" content="pt_BR">
<meta property="og:type" content="{og_tipo}">
<meta property="og:url" content="https://alohanoticias.com/{{CANON}}">
<meta property="og:image" content="{og_url(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE}" href="feed.xml">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<link rel="canonical" href="https://alohanoticias.com/{{CANON}}">
<meta name="theme-color" content="#0F4C5C">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-title" content="ALOHA">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/aloha.css">
<script src="assets/js/tema.js"></script>
{extra_head}</head>
<body>
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{newsletter() if (com_news and NEWSLETTER_ATIVA) else ""}
{rodape()}
<script src="assets/js/site.js"></script>
</body>
</html>
"""


def card(m, pequeno=False, mostrar_capa=True, chapeu=True):
    return f"""<a class="card{' pequeno' if pequeno else ''}" href="{url_materia(m)}">
  {capa(m) if mostrar_capa else ""}
  {f'<span class="chapeu">{esc(ED[m["editoria"]]["nome"])}</span>' if chapeu else ""}
  <h3>{esc(m["titulo"])}</h3>
  <p class="meta"><time datetime="{m["data"]}">{data_curta(m["data"])}</time><span>{leitura(m)} min de leitura</span></p>
</a>"""


def mais_lidas(lista, cls=""):
    if len(lista) < 3:
        return ""
    itens = "".join(f'<li><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for m in lista)
    return f'<aside class="mais-lidas {cls}" aria-labelledby="ml-{cls or "x"}"><h2 id="ml-{cls or "x"}">Mais lidas</h2><ol>{itens}</ol></aside>'


# Ordem de "mais lidas" de exemplo (troque pela sua métrica de audiência)
MAIS_LIDAS = materias[:5]


# ---------------------------------------------------------------- home
def card_dest(m, nivel):
    """nivel: 'grande' (linha 1), 'medio' (linha 2) ou 'largo' (linha 3, horizontal)."""
    fina = f'<p class="linha-fina">{esc(m["linha_fina"])}</p>' if nivel != "medio" else ""
    return f"""<a class="card-dest {nivel}" href="{url_materia(m)}">
  <div class="cd-capa">{capa(m)}</div>
  <div class="cd-texto">
    <span class="chapeu">{esc(ED[m['editoria']]['nome'])}</span>
    <h2>{esc(m['titulo'])}</h2>
    {fina}
    <p class="meta"><span>{esc(m['autor'])}</span><time datetime="{m['data']}">{data_curta(m['data'])}</time><span>{leitura(m)} min</span></p>
  </div>
</a>"""


SETA_D = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
SETA_E = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>'
POR_PAGINA = 4


def card_linha(m):
    return f"""<a class="card-linha" href="{url_materia(m)}">
  <div class="cl-capa">{capa(m)}</div>
  <div class="cl-texto">
    <h3>{esc(m['titulo'])}</h3>
    <p class="linha-fina">{esc(m['linha_fina'])}</p>
    <p class="meta"><span>{esc(m['autor'])}</span><time datetime="{m['data']}">{data_curta(m['data'])}</time><span>{leitura(m)} min de leitura</span></p>
  </div>
</a>"""


def carrossel(lista, nome):
    paginas = [lista[i:i + POR_PAGINA] for i in range(0, len(lista), POR_PAGINA)]
    html_pag = "".join(
        f'<div class="pagina-lista" data-pagina="{i}">{"".join(card_linha(m) for m in p)}</div>'
        for i, p in enumerate(paginas)
    )
    pager = ""
    if len(paginas) > 1:
        pager = f"""<div class="pager" hidden>
    <button class="pager-btn pager-ant" type="button" aria-label="Voltar às notícias anteriores de {esc(nome)}" hidden>{SETA_E}</button>
    <span class="pager-info" aria-live="polite">1 / {len(paginas)}</span>
    <button class="pager-btn pager-prox" type="button" aria-label="Ver mais notícias de {esc(nome)}">{SETA_D}</button>
  </div>"""
    return f'<div class="carrossel" data-carrossel>{html_pag}{pager}</div>'


def gerar_home():
    manchete = next((m for m in materias if m.get("manchete")), materias[0])
    # 5 destaques: a manchete + 4 matérias de editorias diferentes (as mais recentes de cada uma).
    destaques = [manchete]
    vistas = {manchete["editoria"]}
    for m in materias:
        if len(destaques) == 5:
            break
        if m is not manchete and m["editoria"] not in vistas:
            destaques.append(m)
            vistas.add(m["editoria"])
    for m in materias:
        if len(destaques) == 5:
            break
        if m not in destaques:
            destaques.append(m)
    usados = {m["slug"] for m in destaques}
    niveis = ["largo"] if len(destaques) == 1 else ["grande", "grande", "medio", "medio", "largo"]
    cards_dest = "".join(card_dest(m, n) for m, n in zip(destaques, niveis))

    blocos = []
    for e in editorias:
        todas = [m for m in materias if m["editoria"] == e["slug"]]
        # Não repete o que já aparece nos destaques do topo; o resto entra em páginas de 4.
        da_ed = [m for m in todas if m["slug"] not in usados]
        if not da_ed:
            continue
        blocos.append(f"""<section class="secao-home" aria-labelledby="sec-{e['slug']}">
  <div class="wrap">
    <div class="secao-topo"><h2 id="sec-{e['slug']}">{esc(e['nome'])}</h2><a class="ver-tudo" href="{url_editoria(e['slug'])}">Ver tudo em {esc(e['nome'])} →</a></div>
    {carrossel(da_ed, e['nome'])}
  </div>
</section>""")

    corpo = f"""<section class="principal" aria-label="Destaques">
  <div class="wrap destaques">
    <div class="dest-grade">{cards_dest}</div>
  </div>
</section>
{"".join(blocos)}
{('<section class="secao-home secao-mais-lidas"><div class="wrap">' + mais_lidas(MAIS_LIDAS, "home") + '</div></section>') if len(MAIS_LIDAS) >= 3 else ""}"""
    return pagina(SITE, "Notícias em geral, cinema, games, tecnologia, curiosidades e finanças, explicados com calma.", "inicio", corpo)


# ---------------------------------------------------------------- editoria
def gerar_editoria(e):
    da_ed = [m for m in materias if m["editoria"] == e["slug"]]
    if not da_ed:
        corpo = f"""<div class="topo-editoria"><div class="wrap"><h1>{esc(e['nome'])}</h1><p>{esc(e['descricao'])}</p></div></div>
<div class="wrap editoria-corpo"><p class="linha-fina">Ainda não publicamos matérias nesta editoria. Volte em breve.</p></div>"""
        return pagina(e["nome"], e["descricao"], e["slug"], corpo)
    lead, resto = da_ed[0], da_ed[1:]
    itens = "".join(
        f'<li><a href="{url_materia(m)}"><div class="dupla" style="gap:6px"><h3>{esc(m["titulo"])}</h3>'
        f'<p class="linha-fina" style="font-size:1rem">{esc(m["linha_fina"])}</p>'
        f'<p class="meta"><time datetime="{m["data"]}">{data_curta(m["data"])}</time><span>{leitura(m)} min</span></p></div>{capa(m)}</a></li>'
        for m in resto
    )
    corpo = f"""<div class="topo-editoria"><div class="wrap"><h1>{esc(e['nome'])}</h1><p>{esc(e['descricao'])}</p></div></div>
<div class="wrap editoria-corpo">
  <a class="editoria-lead" href="{url_materia(lead)}">
    {capa(lead)}
    <div class="card"><h2>{esc(lead['titulo'])}</h2><p class="linha-fina">{esc(lead['linha_fina'])}</p>
      <p class="meta"><span>{esc(lead['autor'])}</span><time datetime="{lead['data']}">{data_longa(lead['data'])}</time></p></div>
  </a>
  <div class="grade-2">
    <ul class="lista-simples" aria-label="Mais em {esc(e['nome'])}">{itens}</ul>
    {mais_lidas(MAIS_LIDAS, "ed")}
  </div>
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


def link_acao(acao, slug):
    from urllib.parse import quote
    return (f"https://github.com/{REPO}/issues/new?title={quote(acao + ': ' + slug)}"
            f"&body={quote('Clique em Submit new issue para confirmar. O site é atualizado em cerca de 1 minuto.')}")


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
    return (f'<div class="faixa-rascunho" data-slug="{esc(slug)}" data-repo="{REPO}" data-acao="{acao}"><div class="wrap">'
            f'<strong>{rotulo}</strong> '
            f'<a class="botao" href="{link_acao("Aprovar", slug)}" target="_blank" rel="noopener noreferrer">Publicar agora</a> '
            f'<label class="agendar">{texto_ag} <input type="datetime-local" id="quando"{atual} aria-label="Data e hora de publicação"></label> '
            f'<a class="botao-sec" id="agendar" href="{link_acao(acao, slug)}" target="_blank" rel="noopener noreferrer">{rot_agendar}</a> '
            f'<a class="botao-sec" href="{link_acao("Rejeitar", slug)}" target="_blank" rel="noopener noreferrer">{rej}</a> '
            f'<a href="admin/">Voltar à lista</a></div></div>\n<script src="assets/js/admin.js"></script>')


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


def autor_html(m):
    return f'<a href="equipe.html">{esc(m["autor"])}</a>' if m["autor"] == "Equipe Aloha" else esc(m["autor"])


def botoes_compartilhar(m):
    from urllib.parse import quote
    u = quote("https://alohanoticias.com/" + url_materia(m), safe="")
    t = quote(m["titulo"], safe="")
    tt = quote(m["titulo"] + " https://alohanoticias.com/" + url_materia(m), safe="")
    redes = [("WhatsApp", f"https://wa.me/?text={tt}"), ("X", f"https://twitter.com/intent/tweet?text={t}&url={u}"),
             ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}"), ("Telegram", f"https://t.me/share/url?url={u}&text={t}")]
    return "".join(f'<a class="botao-sec" href="{h}" target="_blank" rel="noopener noreferrer" aria-label="Compartilhar no {n}">{n}</a>' for n, h in redes)


def gerar_materia(m, preview=False, agendado=False):
    e = ED[m["editoria"]]
    relacionadas = [x for x in materias if x["editoria"] == m["editoria"] and x is not m][:3]
    if len(relacionadas) < 3:
        relacionadas += [x for x in materias if x is not m and x not in relacionadas][: 3 - len(relacionadas)]
    tags = "".join(f'<a href="{url_tag(t)}">{esc(t)}</a>' for t in m.get("tags", []) if slug_tag(t))
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": m["titulo"],
        "description": m["linha_fina"], "datePublished": m["data"], "articleSection": e["nome"],
        "author": {"@type": "Person" if m["autor"] != "Equipe Aloha" else "Organization", "name": m["autor"]},
        "publisher": {"@type": "Organization", "name": SITE},
    }, ensure_ascii=False)
    corpo = f"""<article class="wrap materia">
  <nav class="migalhas" aria-label="Você está em"><a href="index.html">Início</a><span aria-hidden="true">/</span><a href="{url_editoria(e['slug'])}">{esc(e['nome'])}</a></nav>
  <header class="materia-topo">
    <span class="chapeu">{esc(e['nome'])}</span>
    <h1>{esc(m['titulo'])}</h1>
    <p class="linha-fina">{esc(m['linha_fina'])}</p>
    <p class="meta"><span>Por {autor_html(m)}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time><span>{leitura(m)} min de leitura</span></p>
  </header>
  <figure class="materia-capa" style="margin-inline:0">{capa(m)}{legenda(m)}</figure>{video(m)}
  <div class="materia-grade">
    <div class="texto">
      <div class="compartilhar"><span>Compartilhe</span>{botoes_compartilhar(m)}<button class="botao-sec" id="copiar-link" type="button">Copiar link</button></div>
      {corpo_texto(m['corpo'])}
      <div class="tags" aria-label="Assuntos">{tags}</div>
    </div>
    <div class="lateral">{mais_lidas(MAIS_LIDAS, "mat")}</div>
  </div>
</article>
{"" if not relacionadas else f'''<section class="leia-tambem" aria-labelledby="leia">
  <div class="wrap">
    <div class="secao-topo"><h2 id="leia">Leia também</h2><a class="ver-tudo" href="{url_editoria(e['slug'])}">Mais em {esc(e['nome'])} →</a></div>
    <div class="grade-3">{"".join(card(x) for x in relacionadas)}</div>
  </div>
</section>'''}"""
    head = f'<script type="application/ld+json">{ld}</script>\n'
    if preview:
        corpo = faixa_rascunho(m, agendado) + corpo
        head = '<base href="/">\n<meta name="robots" content="noindex,nofollow">\n' + head
    return pagina(m["titulo"], m["linha_fina"], e["slug"], corpo, extra_head=head, og_img=(m.get("imagem") or {}).get("url", "assets/img/og-padrao.png"), og_tipo="article")


# ---------------------------------------------------------------- busca e páginas simples
INDICE_JS = ""


def gerar_busca():
    indice = [{
        "titulo": m["titulo"], "linha_fina": m["linha_fina"], "editoria": ED[m["editoria"]]["nome"],
        "tags": m.get("tags", []), "url": url_materia(m), "data": data_longa(m["data"]), "capa": capa(m),
    } for m in materias]
    corpo = f"""<div class="topo-editoria"><div class="wrap"><h1>Buscar</h1>
  <form class="busca-form" id="form-busca" role="search">
    <label class="sr-only" for="campo-busca">Buscar matérias</label>
    <input id="campo-busca" type="search" placeholder="Ex.: juros, bateria, cinema" autocomplete="off">
    <button class="botao" type="submit">Buscar</button>
  </form></div></div>
<div class="wrap editoria-corpo">
  <p class="busca-resultado" id="info-busca" role="status"></p>
  <ul class="lista-simples" id="resultados" style="max-width:820px"></ul>
</div>
<script src="assets/js/indice.js"></script>"""
    global INDICE_JS
    INDICE_JS = "window.ALOHA_INDICE = " + json.dumps(indice, ensure_ascii=False) + ";\n"
    return pagina("Buscar", "Busque matérias da ALOHA NOTÍCIAS.", "", corpo, com_news=False)


def gerar_simples(titulo, descricao, conteudo):
    corpo = f'<div class="wrap"><div class="pagina-texto"><h1>{esc(titulo)}</h1>{conteudo}</div></div>'
    return pagina(titulo, descricao, "", corpo)


def gerar_404():
    corpo = f"""<div class="wrap erro"><div class="o">{O_SIMBOLO}</div><h1>Essa onda passou</h1>
<p>A página que você procurou não existe ou mudou de endereço.</p><a class="botao" href="index.html">Voltar para a página inicial</a></div>"""
    return pagina("Página não encontrada", "Página não encontrada.", "", corpo, com_news=False)


# ---------------------------------------------------------------- saída
HEADERS = """/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: default-src 'self'; script-src 'self' https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://img.youtube.com https://i.ytimg.com https://images.unsplash.com; frame-src https://www.youtube-nocookie.com; connect-src 'self' https://cloudflareinsights.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests

/admin/*
  X-Robots-Tag: noindex, nofollow
  Cache-Control: no-store

/assets/*
  Cache-Control: public, max-age=3600, must-revalidate
"""


def main():
    if SAIDA.exists():
        # Limpa o conteúdo; em alguns discos não é possível apagar a própria pasta.
        for item in SAIDA.iterdir():
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    (SAIDA / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copytree(RAIZ / "assets", SAIDA / "assets", dirs_exist_ok=True)

    arquivos = {"index.html": gerar_home(), "busca.html": gerar_busca(), "404.html": gerar_404()}
    for e in editorias:
        arquivos[url_editoria(e["slug"])] = gerar_editoria(e)
    for m in materias:
        arquivos[url_materia(m)] = gerar_materia(m)

    arquivos["sobre.html"] = gerar_simples("Sobre nós", "Quem faz a ALOHA NOTÍCIAS.", """
<p>A ALOHA NOTÍCIAS é um site de notícias para quem quer entender o que está acontecendo sem pressa e sem barulho. Cobrimos notícias em geral, cinema, games, tecnologia, curiosidades e finanças.</p>
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
<h2>Uso de inteligência artificial</h2>
<p>Usamos ferramentas de inteligência artificial como apoio à pesquisa e à redação. Nenhuma matéria é publicada sem a revisão e a aprovação de uma pessoa da equipe.</p>
<h2>Fato e opinião</h2>
<p>Separamos o que foi apurado do que é análise. Textos de opinião ou recomendação são identificados como tal.</p>
<h2>Imagens e vídeos</h2>
<p>Usamos fotos de bancos gratuitos, com o crédito do autor na legenda, ilustrações feitas para o site e, quando necessário, imagens de divulgação oficial ligadas ao assunto da matéria, também com crédito. O vídeo que aparece em uma matéria é incorporado do canal onde foi publicado. Se você é o autor ou o dono de uma imagem e quer que ela seja creditada de outra forma ou removida, escreva para a gente.</p>
<h2>Correções</h2>
<p>Quando encontramos um erro, corrigimos a matéria e indicamos a correção no texto. Se você encontrou um erro, envie a matéria e o que está incorreto pela página de <a href="contato.html">contato</a>. Respondemos o quanto antes.</p>
<h2>Independência</h2>
<p>Se uma matéria tiver publicidade, patrocínio ou parceria envolvida, isso será informado claramente ao leitor.</p>""")
    arquivos["equipe.html"] = gerar_simples("Equipe Aloha", "Quem assina as matérias da ALOHA NOTÍCIAS e o que cobrimos.", f"""
<p>Equipe Aloha é a assinatura da redação do ALOHA NOTÍCIAS. Reúne quem pesquisa, escreve, ilustra e revisa as matérias publicadas aqui.</p>
<h2>O que cobrimos</h2>
<ul>{"".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a>: {esc(e["descricao"])}</li>' for e in editorias)}</ul>
<h2>Como trabalhamos</h2>
<p>Confirmamos os fatos em mais de uma fonte, citamos as fontes no fim de cada matéria e corrigimos os erros de forma aberta. Veja a <a href="politica-editorial.html">política editorial</a>.</p>
<h2>Fale com a gente</h2>
<p>Pautas, correções e parcerias: <a href="contato.html">página de contato</a>.</p>""")
    por_tag = {}
    for m in materias:
        for t in m.get("tags", []):
            if slug_tag(t):
                por_tag.setdefault(t, []).append(m)
    for t, lista in por_tag.items():
        itens = "".join(
            f'<li><a href="{url_materia(x)}"><div class="dupla" style="gap:6px"><span class="chapeu">{esc(ED[x["editoria"]]["nome"])}</span><h3>{esc(x["titulo"])}</h3>'
            f'<p class="linha-fina" style="font-size:1rem">{esc(x["linha_fina"])}</p>'
            f'<p class="meta"><time datetime="{x["data"]}">{data_curta(x["data"])}</time><span>{leitura(x)} min</span></p></div>{capa(x)}</a></li>' for x in lista)
        corpo = (f'<div class="topo-editoria"><div class="wrap"><h1>{esc(t)}</h1><p>{len(lista)} {"matéria" if len(lista) == 1 else "matérias"} sobre este assunto.</p></div></div>'
                 f'<div class="wrap editoria-corpo"><ul class="lista-simples" style="max-width:820px">{itens}</ul></div>')
        arquivos[url_tag(t)] = pagina(t, f"Matérias da ALOHA NOTÍCIAS sobre {t}.", "", corpo)
    arquivos["contato.html"] = gerar_simples("Contato e anúncios", "Fale com a redação da ALOHA NOTÍCIAS.", """
<p>Sugestões de pauta, correções e parcerias são bem-vindas.</p>
<h2>E-mail</h2><p><a href="mailto:contato@alohanoticias.com">contato@alohanoticias.com</a></p>""")
    arquivos["privacidade.html"] = gerar_simples("Privacidade", "Política de privacidade da ALOHA NOTÍCIAS.", """
<p>Última atualização: novembro de 2026. Respeitamos a Lei Geral de Proteção de Dados (LGPD, Lei 13.709/2018). Aqui está, de forma direta, o que acontece com os seus dados quando você visita este site.</p>
<h2>O que coletamos</h2>
<p>Não pedimos cadastro e não usamos cookies de publicidade ou de rastreamento. Guardamos no seu próprio navegador apenas a sua preferência de tema claro ou escuro.</p>
<p>Medimos o número de acessos com um serviço de estatísticas que não usa cookies e não identifica você pessoalmente (Cloudflare Web Analytics). Os dados vistos por nós são agregados, como páginas mais lidas, país e tipo de aparelho.</p>
<h2>Serviços de terceiros</h2>
<p>As fontes de letra vêm do Google Fonts. Fotos podem vir do Unsplash e vídeos são incorporados do YouTube, em modo de privacidade aprimorada (youtube-nocookie.com). Ao carregar esses conteúdos, esses serviços recebem o seu endereço de IP e podem ter regras próprias de privacidade. O site é hospedado pela Cloudflare.</p>
<h2>E-mail de contato</h2>
<p>Se você nos escrever, usaremos o seu e-mail apenas para responder. Não vendemos nem repassamos os seus dados.</p>
<h2>Seus direitos</h2>
<p>Você pode pedir informações sobre os dados que temos sobre você, a correção ou a exclusão deles, escrevendo pela página de <a href="contato.html">contato</a>.</p>
<h2>Mudanças</h2>
<p>Se esta política mudar, a data acima será atualizada. Se passarmos a usar cookies, anúncios ou newsletter, vamos avisar aqui antes.</p>""")

    for nome, conteudo in arquivos.items():
        c = "" if nome == "index.html" else nome
        conteudo = conteudo.replace("{CANON}", c)
        (SAIDA / nome).write_text(conteudo, encoding="utf-8")
    (SAIDA / "assets/js/indice.js").write_text(INDICE_JS, encoding="utf-8")
    (SAIDA / "_headers").write_text(HEADERS, encoding="utf-8")
    (SAIDA / ".well-known").mkdir(exist_ok=True)
    (SAIDA / ".well-known/security.txt").write_text(
        "Contact: mailto:contato@alohanoticias.com\nExpires: 2027-11-01T00:00:00.000Z\nPreferred-Languages: pt, en\nCanonical: https://alohanoticias.com/.well-known/security.txt\n", encoding="utf-8")
    (SAIDA / "manifest.webmanifest").write_text(json.dumps({
        "name": "ALOHA NOTÍCIAS", "short_name": "ALOHA", "description": "Notícias, cinema, games, tecnologia, curiosidades e finanças.",
        "start_url": "/", "scope": "/", "display": "standalone", "lang": "pt-BR",
        "background_color": "#FFFFFF", "theme_color": "#0F4C5C",
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
    (SAIDA / "admin/index.html").write_text(gerar_admin(rascunhos, agendados).replace("{CANON}", "admin/"), encoding="utf-8")
    for d in rascunhos:
        (SAIDA / f"admin/{d['slug']}.html").write_text(gerar_materia(d, preview=True).replace("{CANON}", f"admin/{d['slug']}.html"), encoding="utf-8")
    for d in agendados:
        (SAIDA / f"admin/{d['slug']}.html").write_text(gerar_materia(d, preview=True, agendado=True).replace("{CANON}", f"admin/{d['slug']}.html"), encoding="utf-8")
    urls = [n for n in arquivos if n not in ("404.html", "busca.html")]
    sm = "".join(f"<url><loc>https://alohanoticias.com/{'' if n=='index.html' else n}</loc></url>" for n in urls)
    (SAIDA / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + "</urlset>", encoding="utf-8")
    (SAIDA / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: https://alohanoticias.com/sitemap.xml\n")
    print(f"{len(arquivos)} páginas geradas em {SAIDA}")


if __name__ == "__main__":
    main()
