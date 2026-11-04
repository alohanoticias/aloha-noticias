"""Gera o site estático da ALOHA NOTÍCIAS a partir de conteudo/*.json.

Uso:  python3 gerar.py            -> gera em publico/
"""
import hashlib
import html
import json
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
            f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div></div>')


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
<div class="agora" aria-label="Últimas"><div class="wrap"><span class="agora-rotulo">Agora</span><ul class="agora-lista">{agora}</ul></div></div>
"""


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
      <li><a href="privacidade.html">Privacidade</a></li>
    </ul></div>
    <div class="rodape-base"><span>© {HOJE.year} {SITE}</span></div>
  </div>
</footer>"""


def pagina(titulo, descricao, ativo, corpo, com_news=True, extra_head=""):
    t = f"{titulo} · {SITE}" if titulo != SITE else f"{SITE}: notícias, cinema, games, tecnologia e finanças"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(t)}</title>
<meta name="description" content="{esc(descricao)}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<link rel="canonical" href="https://alohanoticias.com/{{CANON}}">
<meta name="theme-color" content="#0F4C5C">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
<link rel="stylesheet" href="assets/css/aloha.css">
<script>try{{var t=localStorage.getItem("aloha-tema");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
{extra_head}</head>
<body>
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{newsletter() if com_news else ""}
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
    itens = "".join(f'<li><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for m in lista)
    return f'<aside class="mais-lidas {cls}" aria-labelledby="ml-{cls or "x"}"><h2 id="ml-{cls or "x"}">Mais lidas</h2><ol>{itens}</ol></aside>'


# Ordem de "mais lidas" de exemplo (troque pela sua métrica de audiência)
MAIS_LIDAS = [m for m in materias if m["slug"] in {
    "reserva-de-emergencia-quanto-guardar", "por-que-o-mar-e-salgado", "senhas-fortes-e-dois-fatores",
    "console-pc-ou-nuvem", "como-checar-se-uma-noticia-e-verdadeira"}]


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
    manchete = next(m for m in materias if m.get("manchete"))
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
    niveis = ["grande", "grande", "medio", "medio", "largo"]
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
<section class="secao-home secao-mais-lidas">
  <div class="wrap">{mais_lidas(MAIS_LIDAS, "home")}</div>
</section>"""
    return pagina(SITE, "Notícias em geral, cinema, games, tecnologia, curiosidades e finanças, explicados com calma.", "inicio", corpo)


# ---------------------------------------------------------------- editoria
def gerar_editoria(e):
    da_ed = [m for m in materias if m["editoria"] == e["slug"]]
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
        if p.startswith("## "):
            out.append(f"<h2>{esc(p[3:])}</h2>")
        else:
            out.append(f"<p>{esc(p)}</p>")
    return "\n".join(out)


def gerar_materia(m):
    e = ED[m["editoria"]]
    relacionadas = [x for x in materias if x["editoria"] == m["editoria"] and x is not m][:3]
    if len(relacionadas) < 3:
        relacionadas += [x for x in materias if x is not m and x not in relacionadas][: 3 - len(relacionadas)]
    tags = "".join(f"<span>{esc(t)}</span>" for t in m.get("tags", []))
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": m["titulo"],
        "description": m["linha_fina"], "datePublished": m["data"], "articleSection": e["nome"],
        "author": {"@type": "Person" if m["autor"] != "Redação ALOHA" else "Organization", "name": m["autor"]},
        "publisher": {"@type": "Organization", "name": SITE},
    }, ensure_ascii=False)
    corpo = f"""<article class="wrap materia">
  <nav class="migalhas" aria-label="Você está em"><a href="index.html">Início</a><span aria-hidden="true">/</span><a href="{url_editoria(e['slug'])}">{esc(e['nome'])}</a></nav>
  <header class="materia-topo">
    <span class="chapeu">{esc(e['nome'])}</span>
    <h1>{esc(m['titulo'])}</h1>
    <p class="linha-fina">{esc(m['linha_fina'])}</p>
    <p class="meta"><span>Por {esc(m['autor'])}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time><span>{leitura(m)} min de leitura</span></p>
  </header>
  <figure class="materia-capa" style="margin-inline:0">{capa(m)}{legenda(m)}</figure>{video(m)}
  <div class="materia-grade">
    <div class="texto">
      <div class="compartilhar"><span>Compartilhe</span><button class="botao-sec" id="copiar-link" type="button">Copiar link</button></div>
      {corpo_texto(m['corpo'])}
      <div class="tags" aria-label="Assuntos">{tags}</div>
    </div>
    <div class="lateral">{mais_lidas(MAIS_LIDAS, "mat")}</div>
  </div>
</article>
<section class="leia-tambem" aria-labelledby="leia">
  <div class="wrap">
    <div class="secao-topo"><h2 id="leia">Leia também</h2><a class="ver-tudo" href="{url_editoria(e['slug'])}">Mais em {esc(e['nome'])} →</a></div>
    <div class="grade-3">{"".join(card(x) for x in relacionadas)}</div>
  </div>
</section>"""
    head = f'<meta property="og:type" content="article">\n<script type="application/ld+json">{ld}</script>\n'
    return pagina(m["titulo"], m["linha_fina"], e["slug"], corpo, extra_head=head)


# ---------------------------------------------------------------- busca e páginas simples
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
<script>window.ALOHA_INDICE = {json.dumps(indice, ensure_ascii=False)};</script>"""
    return pagina("Buscar", "Busque matérias da ALOHA NOTÍCIAS.", "", corpo, com_news=False)


def gerar_simples(titulo, descricao, conteudo):
    corpo = f'<div class="wrap"><div class="pagina-texto"><h1>{esc(titulo)}</h1>{conteudo}</div></div>'
    return pagina(titulo, descricao, "", corpo)


def gerar_404():
    corpo = f"""<div class="wrap erro"><div class="o">{O_SIMBOLO}</div><h1>Essa onda passou</h1>
<p>A página que você procurou não existe ou mudou de endereço.</p><a class="botao" href="index.html">Voltar para a página inicial</a></div>"""
    return pagina("Página não encontrada", "Página não encontrada.", "", corpo, com_news=False)


# ---------------------------------------------------------------- saída
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
<p>Cada matéria cita suas fontes, separa fato de opinião e é corrigida de forma transparente quando erramos.</p>
<h2>O nome</h2>
<p><em>Aloha</em> é a saudação havaiana que também significa afeto e respeito. É assim que queremos tratar quem nos lê.</p>""")
    arquivos["contato.html"] = gerar_simples("Contato e anúncios", "Fale com a redação da ALOHA NOTÍCIAS.", """
<p>Sugestões de pauta, correções e parcerias são bem-vindas.</p>
<h2>E-mail</h2><p><a href="mailto:alohanoticias@gmail.com">alohanoticias@gmail.com</a></p>""")
    arquivos["privacidade.html"] = gerar_simples("Privacidade", "Política de privacidade da ALOHA NOTÍCIAS.", """
<p>Este site guarda no seu navegador apenas a sua preferência de tema claro ou escuro.</p>
<p>Se você assinar a newsletter, o seu e-mail será usado só para o envio dela, e você poderá cancelar a qualquer momento.</p>""")

    for nome, conteudo in arquivos.items():
        c = "" if nome == "index.html" else nome
        conteudo = conteudo.replace("{CANON}", c)
        (SAIDA / nome).write_text(conteudo, encoding="utf-8")
    urls = [n for n in arquivos if n not in ("404.html", "busca.html")]
    sm = "".join(f"<url><loc>https://alohanoticias.com/{'' if n=='index.html' else n}</loc></url>" for n in urls)
    (SAIDA / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + "</urlset>", encoding="utf-8")
    (SAIDA / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://alohanoticias.com/sitemap.xml\n")
    print(f"{len(arquivos)} páginas geradas em {SAIDA}")


if __name__ == "__main__":
    main()
