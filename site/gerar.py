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
import privacidade

RAIZ = Path(__file__).parent
SAIDA = RAIZ.parent / "publico"
SITE = "ALOHA NOTÍCIAS"
# Nome no título da aba, no Google e nos dados para buscadores: o Google costuma trocar títulos só em maiúsculas por
# minúsculas ("aloha notícias"), então ali o nome vai com só as iniciais maiúsculas. No visual do site continua ALOHA NOTÍCIAS.
NOME_BUSCA = "Aloha Notícias"
# Endereços dos perfis oficiais (Instagram, YouTube, X, TikTok, etc.). Preencha quando existirem: o Google usa para ligar os perfis à marca.
# Redes sociais oficiais do site (a primeira aparece primeiro no rodapé). Para adicionar outra, inclua aqui.
ICONE_TELEGRAM = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><path fill="currentColor" '
                  'd="M21.9 4.3 18.6 19.8c-.2 1.1-.9 1.4-1.8.9l-5-3.7-2.4 2.3c-.3.3-.5.5-1 .5l.4-5.1 9.2-8.3c.4-.4-.1-.6-.6-.2'
                  'L6 13.4 1.1 11.9c-1.1-.3-1.1-1.1.2-1.6L20.5 2.9c.9-.3 1.7.2 1.4 1.4z"/></svg>')
ICONE_INSTAGRAM = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
                   'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="5"/>'
                   '<circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.6" fill="currentColor"/></svg>')
REDES_SITE = [("Instagram", "https://www.instagram.com/alohanoticiasbr/", ICONE_INSTAGRAM),
              ("Telegram", "https://t.me/alohanoticias", ICONE_TELEGRAM)]
SIGA = {"pt": "Siga o Aloha", "en": "Follow Aloha", "es": "Sigue a Aloha", "fr": "Suivez Aloha", "de": "Folge Aloha",
        "it": "Segui Aloha", "ja": "Aloha をフォロー", "zh": "关注 Aloha", "ar": "تابع Aloha"}
PERFIS = [u for _, u, _ in REDES_SITE]

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


AUTOR = "João Gabriel"
AUTOR_REDES = ["https://www.instagram.com/ladinzera/", "https://www.youtube.com/@ladinzando"]
AUTOR_FOTO = "assets/img/autor/joao-gabriel.jpg"


# Logos coloridos das redes do autor (página do autor)
LOGO_YOUTUBE = ('<svg viewBox="0 0 28 20" width="42" height="30" aria-hidden="true" focusable="false">'
                '<rect width="28" height="20" rx="5.5" fill="#FF0000"/><path d="M11.2 5.8v8.4l7.2-4.2z" fill="#fff"/></svg>')
LOGO_INSTAGRAM = ('<svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true" focusable="false">'
                  '<defs><radialGradient id="ig-grad" cx="0.3" cy="1.07" r="1.3"><stop offset="0" stop-color="#FFDD55"/>'
                  '<stop offset="0.1" stop-color="#FFDD55"/><stop offset="0.5" stop-color="#FF543E"/><stop offset="1" stop-color="#C837AB"/></radialGradient></defs>'
                  '<rect width="24" height="24" rx="6.5" fill="url(#ig-grad)"/>'
                  '<rect x="5" y="5" width="14" height="14" rx="4.2" fill="none" stroke="#fff" stroke-width="1.8"/>'
                  '<circle cx="12" cy="12" r="3.4" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="16.4" cy="7.6" r="1.05" fill="#fff"/></svg>')

REDES_SOCIAIS = {"pt": "Redes sociais", "en": "Social media", "es": "Redes sociales", "fr": "Réseaux sociaux", "de": "Soziale Netzwerke",
                 "it": "Social network", "ja": "SNS", "zh": "社交媒体", "ar": "وسائل التواصل الاجتماعي"}


def autor_cartao():
    """Foto e redes do autor, no topo da página do autor (todas as línguas)."""
    foto = f'<img src="{AUTOR_FOTO}" alt="{AUTOR}" width="120" height="120" loading="eager">' if (RAIZ / AUTOR_FOTO).exists() else ""
    redes = (f'<a class="rede-ig" href="https://www.instagram.com/ladinzera/" rel="me noopener" target="_blank" aria-label="Instagram" title="Instagram">{LOGO_INSTAGRAM}</a>'
             f'<a class="rede-yt" href="https://www.youtube.com/@ladinzando" rel="me noopener" target="_blank" aria-label="YouTube" title="YouTube">{LOGO_YOUTUBE}</a>')
    rot = REDES_SOCIAIS.get(LANG, REDES_SOCIAIS["pt"])
    return f'<div class="autor-cartao">{foto}<div class="autor-redes-bloco"><span class="autor-redes-titulo">{rot}</span><div class="autor-redes">{redes}</div></div></div>'


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
    "anime": ("#0F4C5C", "#9CC3C7", "#F4EDE4"),
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
    """Capa leve do vídeo (miniatura + botão). O player do YouTube, que é pesado, só carrega quando o leitor clica."""
    v = m.get("video")
    if not v:
        return ""
    vid, tit = esc(v["youtube"]), esc(v.get("titulo", "Video"))
    return (f'<div class="wrap video-materia"><div class="video"><a class="yt-capa" href="https://www.youtube.com/watch?v={vid}" data-yt="{vid}" data-titulo="{tit}" target="_blank" rel="noopener">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{tit}" width="480" height="360" loading="lazy" decoding="async">'
            f'<span class="yt-play" aria-hidden="true"></span><span class="sr">{tit}</span></a></div></div>')


_VARIANTES = {}
TAMANHOS_CAPA = (640, 960, 1280)


def variantes_capa(url):
    """Versões menores em WebP de uma capa local (assets/img/capas/<slug>.jpg), para celular e listas carregarem rápido.
    Ficam em assets/img/capas/v/<slug>-<hash>-<largura>.webp: o hash muda quando a capa é remontada, e a versão
    antiga é apagada. Sem a biblioteca Pillow (algumas automações), usa as versões que já existem ou só o .jpg."""
    if url in _VARIANTES:
        return _VARIANTES[url]
    res = []
    src = RAIZ / url
    if url.startswith("assets/img/") and url.endswith((".jpg", ".jpeg", ".png")) and src.exists():
        h = hashlib.md5(src.read_bytes()).hexdigest()[:8]
        dir_rel = str(Path(url).parent).replace("\\", "/")
        pasta = RAIZ / dir_rel / "v"
        for w in TAMANHOS_CAPA:
            rel = f"{dir_rel}/v/{src.stem}-{h}-{w}.webp"
            alvo = RAIZ / rel
            if not alvo.exists():
                try:
                    from PIL import Image
                except ImportError:
                    res = []
                    break
                pasta.mkdir(exist_ok=True)
                for velho in pasta.glob(f"{src.stem}-*-{w}.webp"):
                    if re.fullmatch(re.escape(src.stem) + r"-[0-9a-f]{8}-" + str(w) + r"\.webp", velho.name):
                        velho.unlink()
                with Image.open(src) as im:
                    im = im.convert("RGB")
                    im.resize((w, round(w * im.height / im.width)), Image.LANCZOS).save(alvo, "WEBP", quality=78, method=6)
            # a cópia de assets/ para o site publicado acontece antes das páginas; garante que a versão nova vá junto
            copia = SAIDA / rel
            if not copia.exists():
                copia.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(alvo, copia)
                for velho in copia.parent.glob(f"{src.stem}-*-{w}.webp"):
                    if velho.name != copia.name and re.fullmatch(re.escape(src.stem) + r"-[0-9a-f]{8}-" + str(w) + r"\.webp", velho.name):
                        velho.unlink()
            res.append((rel, w))
    _VARIANTES[url] = res
    return res


def capa(m, cls="capa", prioridade=False, sizes="(max-width: 760px) 100vw, 640px", responsivo=True):
    im = m.get("imagem")
    if im:
        v = variantes_capa(im["url"]) if responsivo else []
        srcset = (f' srcset="{", ".join(f"{u} {w}w" for u, w in v)}, {esc(im["url"])} 1920w" sizes="{sizes}"' if v else "")
        carga = 'loading="eager" fetchpriority="high"' if prioridade is True else ('loading="eager"' if prioridade == "eager" else 'loading="lazy"')
        return f'<img class="{cls}" src="{esc(im["url"])}"{srcset} alt="{esc(im.get("alt", m["titulo"]))}" {carga} decoding="async">'
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


def ed_visiveis():
    return [e for e in editorias if e["slug"] != "financas"]  # Finanças fica fora do menu por enquanto
ICONE_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
LOGO_IMG = '<picture><source type="image/webp" srcset="assets/img/aloha-logo-v3-700.webp"><img src="assets/img/aloha-logo-v3-700.png" alt="ALOHA NOTÍCIAS" width="290" height="101"></picture>'


def cabecalho(ativo):
    itens = [("index.html", t("Início"), "inicio")] + [(url_editoria(e["slug"]), e["nome"], e["slug"]) for e in ed_visiveis()]
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
# Código de editor do AdSense (ex.: "pub-1234567890123456"). Preenchido, já entra a meta tag "google-adsense-account"
# em todas as páginas: é assim que o Google confirma que o site é seu no pedido de análise, sem carregar anúncios antes da hora.
ADSENSE_PUB = ""
# Idiomas que o Google deve indexar. As outras versões continuam no ar para o visitante, mas com "noindex" e fora do
# sitemap, para o site não parecer conteúdo traduzido em massa na análise do AdSense. Para liberar um idioma depois
# da aprovação, acrescente aqui, por exemplo {"pt", "en", "es"}.
IDIOMAS_INDEXADOS = {"pt"}
# Páginas de assunto (tags) com menos matérias que isto ficam fora do Google ("noindex"): páginas com 1 ou 2 links
# contam como conteúdo raso. Elas continuam funcionando para quem navega.
MIN_MATERIAS_TAG = 3
NOINDEX = '<meta name="robots" content="noindex,follow">\n'
_PUSH_CFG = Path(__file__).resolve().parent / "conteudo" / "push.json"
ONESIGNAL_APP_ID = (json.loads(_PUSH_CFG.read_text(encoding="utf-8")).get("onesignal_app_id", "") if _PUSH_CFG.exists() else "").strip()


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
    eds = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a></li>' for e in ed_visiveis())
    redes_li = "".join(f'<li><a href="{u}" target="_blank" rel="noopener me">{ic}<span>{n}</span></a></li>' for n, u, ic in REDES_SITE)
    return f"""<footer class="rodape">
  <div class="wrap">
    <div><a class="rodape-logo" href="index.html" aria-label="{SITE}, {t('página inicial')}">{LOGO_IMG}</a>
      <p>{t('Cinema, games e tecnologia explicados com calma, de olho no que importa.')}</p>
      <h2 class="redes-titulo">{SIGA.get(LANG, SIGA["pt"])}</h2><ul class="redes-site">{redes_li}</ul></div>
    <div><h2>{t('Editorias')}</h2><ul>{eds}</ul></div>
    <div><h2>{t('Institucional')}</h2><ul>
      <li><a href="sobre.html">{t("Sobre nós")}</a></li>
      <li><a href="contato.html">{t("Contato e anúncios")}</a></li>
      <li><a href="busca.html">{t("Buscar")}</a></li>
      <li><a href="equipe.html">{t("Sobre o autor")}</a></li>
      <li><a href="politica-editorial.html">{t("Política editorial")}</a></li>
      <li><a href="termos.html">{t("Termos de uso")}</a></li>
      <li><a href="privacidade.html">{t("Privacidade")}</a></li>
      <li><a href="feed.xml">{t("RSS")}</a></li>
    </ul></div>
    {idiomas_rodape()}
    <div class="rodape-base"><span>© {HOJE.year} {SITE}</span> <a href="#" id="reabrir-consent">{PREFS_COOKIES.get(LANG, PREFS_COOKIES["pt"])}</a></div>
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
# Enquanto os anúncios não estão ligados, o aviso fala das estatísticas (Google Analytics).
CONSENT_TXT_SEM_ADS = {
    "pt": "Usamos cookies de estatística (Google Analytics) para saber quais páginas são lidas e de onde vêm as visitas. Você pode recusar.",
    "en": "We use statistics cookies (Google Analytics) to see which pages are read and where visits come from. You can decline.",
    "es": "Usamos cookies de estadística (Google Analytics) para saber qué páginas se leen y de dónde llegan las visitas. Puedes rechazarlas.",
    "fr": "Nous utilisons des cookies de mesure d’audience (Google Analytics) pour savoir quelles pages sont lues et d’où viennent les visites. Vous pouvez refuser.",
    "de": "Wir nutzen Statistik-Cookies (Google Analytics), um zu sehen, welche Seiten gelesen werden und woher Besuche kommen. Sie können ablehnen.",
    "it": "Usiamo cookie statistici (Google Analytics) per sapere quali pagine vengono lette e da dove arrivano le visite. Puoi rifiutarli.",
    "ja": "どのページが読まれ、どこから訪問があったかを知るため、統計用クッキー（Google アナリティクス）を使用しています。拒否することもできます。",
    "zh": "我们使用统计 Cookie（Google Analytics）来了解哪些页面被阅读以及访问来自哪里。您可以拒绝。",
    "ar": "نستخدم ملفات تعريف ارتباط إحصائية (Google Analytics) لمعرفة الصفحات المقروءة ومن أين تأتي الزيارات. يمكنك الرفض.",
}
PREFS_COOKIES = {"pt": "Preferências de cookies", "en": "Cookie preferences", "es": "Preferencias de cookies", "fr": "Préférences de cookies", "de": "Cookie-Einstellungen", "it": "Preferenze cookie", "ja": "クッキーの設定", "zh": "Cookie 偏好设置", "ar": "تفضيلات ملفات تعريف الارتباط"}


def consent_html():
    return (f'<div class="consent" id="consent" role="dialog" aria-label="{t("Aviso de cookies")}" hidden>\n'
            f'  <svg class="consent-ico" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5"/><path d="M8.5 8.5v.01M16 15.5v.01M12 12v.01M11 17v.01M7 14v.01"/></svg>\n'
            f'  <p>{(CONSENT_TXT if ANUNCIOS_ATIVOS else CONSENT_TXT_SEM_ADS)[LANG]} <a href="privacidade.html">{SABER_MAIS[LANG]}</a>.</p>\n'
            f'  <div><button class="botao" id="consent-sim" type="button">{t("Aceitar")}</button> <button class="botao sec" id="consent-nao" type="button">{t("Recusar")}</button></div>\n</div>\n')
CONSENT_JS = f'<script src="assets/js/consent.js" data-client="{("ca-" + ADSENSE_PUB) if ANUNCIOS_ATIVOS and ADSENSE_PUB else ""}"></script>'


def pagina(titulo, descricao, ativo, corpo, com_news=True, extra_head="", og_img="assets/img/og-padrao.png", og_tipo="website"):
    BASE = ""
    if '<base href="/">' in extra_head:
        BASE = '<base href="/">\n'
        extra_head = extra_head.replace('<base href="/">\n', "")
    tt = (f"{titulo} · {SITE}" if titulo != SITE else t("ALOHA NOTÍCIAS: notícias, cinema, games e tecnologia")).replace(SITE, NOME_BUSCA)
    # título da home com as iniciais maiúsculas (como aparece no Google)
    tt = {"pt": "Aloha Notícias: Notícias, Cinema, Games e Tecnologia", "en": "Aloha Notícias: News, Movies, Games and Technology"}.get(LANG, tt) if titulo == SITE else tt
    return f"""<!doctype html>
<html lang="{i18n.HTML_LANG[LANG]}"{' dir="rtl"' if LANG == "ar" else ''}>
<head>
<meta charset="utf-8">
{BASE}<script src="assets/js/analytics.js"></script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(tt)}</title>
<meta name="description" content="{esc(descricao)}">
<meta property="og:site_name" content="{NOME_BUSCA}">
<meta property="og:locale" content="{i18n.OG_LOCALE[LANG]}">
<meta property="og:type" content="{og_tipo}">
<meta property="og:url" content="https://alohanoticias.com/{{CANON}}">
<meta property="og:image" content="{og_url(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE}" href="feed.xml">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descricao)}">
<link rel="canonical" href="https://alohanoticias.com/{{CANON}}">
{f'<meta name="google-adsense-account" content="ca-{ADSENSE_PUB}">' + chr(10) if ADSENSE_PUB else ""}@@ALT@@
<meta name="theme-color" content="#0a0a0a">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="icon" href="assets/img/favicon-48.png" sizes="48x48">
<link rel="icon" href="assets/img/icone-app-192.png" sizes="192x192">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-title" content="ALOHA">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" id="fontes" media="print" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/css/site.css">
<script src="assets/js/tema.js"></script>
{extra_head}</head>
<body>
{cabecalho(ativo)}
<main id="conteudo">
{corpo}
</main>
{newsletter() if (com_news and NEWSLETTER_ATIVA) else ""}
{rodape()}
{consent_html()}<script src="assets/js/site.js"></script><script src="assets/js/contador.js" defer></script><script src="assets/js/em-alta.js" defer></script><script src="assets/js/novidades{'' if LANG == 'pt' else '-' + LANG}.js"></script><script src="assets/js/sino.js"></script>{CONSENT_JS}
</body>
</html>
"""


EM_ALTA = {"pt": "Em alta", "en": "Trending", "es": "Tendencia", "fr": "Tendance", "de": "Im Trend", "it": "Di tendenza", "ja": "話題", "zh": "热门", "ar": "رائج"}


# Ícone de foguinho só com contorno (cor do texto do selo)
FOGO = ('<svg class="fogo" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12'
        'c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3'
        'a2.5 2.5 0 0 0 2.5 2.5z"/></svg>')


def alta(m):
    """Selo "🔥 Em alta": escondido no HTML; assets/js/em-alta.js mostra nos artigos mais lidos dos últimos dias (contador próprio)."""
    return f'<span class="em-alta" data-alta="{esc(m["slug"])}" hidden>{FOGO} {EM_ALTA.get(LANG, EM_ALTA["pt"])}</span>'


def card(m, pequeno=False, mostrar_capa=True, chapeu=True):
    return f"""<a class="card{' pequeno' if pequeno else ''}" href="{url_materia(m)}">
  {capa(m) if mostrar_capa else ""}
  {f'<span class="chapeu">{esc(ED[m["editoria"]]["nome"])}</span>' if chapeu else ""}{alta(m)}
  <h3>{esc(m["titulo"])}</h3>
  <p class="meta"><time datetime="{m["data"]}">{data_curta(m["data"])}</time></p>
</a>"""


def mais_lidas(lista, cls=""):
    """Lista "Mais lidas": vai no HTML com até 40 matérias (5 visíveis, na ordem padrão). assets/js/em-alta.js reordena pelas
    leituras reais dos últimos 7 dias (contador próprio) e mostra as 5 primeiras; sem dados suficientes, fica a ordem padrão."""
    if len(lista) < 3:
        return ""
    itens = "".join(f'<li data-slug="{esc(m["slug"])}"{"" if i < 5 else " hidden"}><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for i, m in enumerate(lista))
    return f'<aside class="mais-lidas {cls}" aria-labelledby="ml-{cls or "x"}"><h2 id="ml-{cls or "x"}">{t("Mais lidas")}</h2><ol data-ml>{itens}</ol></aside>'


# Ordem de "mais lidas" de exemplo (troque pela sua métrica de audiência)
MAIS_LIDAS = materias[:40]


# ---------------------------------------------------------------- home











def tag_v(m):
    return f'<span class="tag-v">{esc(ED[m["editoria"]]["nome"])}</span>'


def hero_card(m, grande):
    fina = f'<p class="hero-fina">{esc(m["linha_fina"])}</p>' if grande else ""
    return f"""<a class="hero-card{' grande' if grande else ''}" href="{url_materia(m)}">
  {capa(m, "hero-img", prioridade=True if grande else "eager", sizes="(max-width: 760px) 100vw, 1100px" if grande else "(max-width: 760px) 100vw, 560px")}
  {tag_v(m)}
  <div class="hero-texto">
    {alta(m)}<time datetime="{m['data']}">{data_longa(m['data'])}</time>
    <h2>{esc(m['titulo'])}</h2>
    {fina}
  </div>
</a>"""


def item_lista(m, primeiro=False):
    return f"""<article class="item-lista">
  <a class="il-capa" href="{url_materia(m)}" tabindex="-1" aria-hidden="true">{capa(m, prioridade=True if primeiro else False)}{tag_v(m)}</a>
  <div class="il-texto">
    {alta(m)}<p class="meta-l"><span class="autor">{esc(autor_nome(m))}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time></p>
    <h3><a href="{url_materia(m)}">{esc(m['titulo'])}</a></h3>
    <p class="resumo">{esc(m['linha_fina'])}</p>
    <a class="leia-mais" href="{url_materia(m)}">{t("Leia mais")} »</a>
  </div>
</article>"""


def titulo_secao(texto, h="h2"):
    return f'<div class="tit-secao"><{h}>{esc(texto)}</{h}></div>'


def lateral():
    recentes = "".join(f'<li><a href="{url_materia(m)}">{esc(m["titulo"])}</a></li>' for m in materias[:6])
    cats = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a></li>' for e in ed_visiveis())
    mais = "".join(
        f'<li><a class="mini" href="{url_materia(m)}">{capa(m)}{tag_v(m)}<strong>{esc(m["titulo"])}</strong>'
        f'<time datetime="{m["data"]}">{data_longa(m["data"])}</time></a></li>' for m in materias[:4])
    return f"""<aside class="lateral-site" aria-label="{t('Barra lateral')}">
  <section>{titulo_secao(t("Mais recentes"))}<ul class="mini-lista">{mais}</ul></section>
  <section>{titulo_secao(t("Pesquisar"))}<form class="pesquisar" action="busca.html" role="search">
    <label class="sr-only" for="q-lateral">{t("Pesquisar")}</label><input id="q-lateral" name="q" type="search"><button type="submit">{t("Pesquisar")}</button></form></section>
  <section>{titulo_secao(t("Matérias recentes"))}<ul class="lista-links">{recentes}</ul></section>
  <section>{titulo_secao(t("Categorias"))}<ul class="lista-links">{cats}</ul></section>
</aside>"""


def gerar_home():
    manchete = next((m for m in materias if m.get("manchete")), materias[0])
    destaques = [manchete] + [m for m in materias if m is not manchete][:2]
    usados = {m["slug"] for m in destaques}
    hero = "".join(hero_card(m, i == 0) for i, m in enumerate(destaques))
    secoes = []
    for e in ed_visiveis():
        da_ed = [m for m in materias if m["editoria"] == e["slug"]][:5]
        if not da_ed:
            continue
        secoes.append(f"""<section class="secao-lista" aria-labelledby="sec-{e['slug']}">
  <div class="tit-secao"><h2 id="sec-{e['slug']}">{esc(e['nome'])}</h2></div>
  {"".join(item_lista(m, primeiro=(not secoes and i == 0)) for i, m in enumerate(da_ed))}
  <a class="ver-tudo" href="{url_editoria(e['slug'])}">{t("Ver tudo em")} {esc(e['nome'])} »</a>
</section>""")
    corpo = f"""<h1 class="sr-only">{SITE}: {t("notícias, cinema, games, tecnologia e curiosidades")}</h1>
<section class="hero hero-{len(destaques)}" aria-label="{t('Destaques')}"><div class="wrap hero-grade">{hero}</div></section>
<div class="wrap duas-colunas">
  <div class="coluna-principal">{"".join(secoes)}</div>
  {lateral()}
</div>"""
    marca = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": "https://alohanoticias.com/#site", "url": "https://alohanoticias.com/", "name": NOME_BUSCA,
         "alternateName": ["ALOHA NOTÍCIAS", "Aloha Noticias", "alohanoticias.com"], "inLanguage": "pt-BR",
         "publisher": {"@id": "https://alohanoticias.com/#org"}},
        {"@type": "NewsMediaOrganization", "@id": "https://alohanoticias.com/#org", "name": NOME_BUSCA,
         "alternateName": ["ALOHA NOTÍCIAS", "Aloha Noticias"], "url": "https://alohanoticias.com/",
         "logo": {"@type": "ImageObject", "url": "https://alohanoticias.com/assets/img/icone-app-512.png", "width": 512, "height": 512},
         "email": "contato@alohanoticias.com", "publishingPrinciples": "https://alohanoticias.com/politica-editorial.html",
         "ethicsPolicy": "https://alohanoticias.com/politica-editorial.html", "correctionsPolicy": "https://alohanoticias.com/politica-editorial.html",
         "sameAs": PERFIS}]}
    if not PERFIS:
        marca["@graph"][1].pop("sameAs")
    extra = '<script type="application/ld+json">' + json.dumps(marca, ensure_ascii=False) + '</script>\n'
    return pagina(SITE, t("Notícias, cinema, games e tecnologia, explicados com calma."), "inicio", corpo, extra_head=extra)


# ---------------------------------------------------------------- editoria
def card_cat(m, primeiro=False):
    return f"""<article class="card-cat">
  {alta(m)}<h2><a href="{url_materia(m)}">{esc(m['titulo'])}</a></h2>
  <p class="meta-l"><time datetime="{m['data']}">{data_longa(m['data'])}</time></p>
  <a class="cc-capa" href="{url_materia(m)}" tabindex="-1" aria-hidden="true">{capa(m, prioridade=True if primeiro else False)}</a>
  <p class="resumo">{esc(m['linha_fina'])}</p>
  <a class="leia-mais" href="{url_materia(m)}">{t("Leia mais")} »</a>
</article>"""


def gerar_editoria(e):
    da_ed = [m for m in materias if m["editoria"] == e["slug"]]
    lista = "".join(card_cat(m, primeiro=(i == 0)) for i, m in enumerate(da_ed)) if da_ed else f'<p class="resumo">{t("Ainda não publicamos matérias nesta editoria. Volte em breve.")}</p>'
    corpo = f"""<div class="wrap duas-colunas">
  <div class="coluna-principal">
    <nav class="migalhas-v" aria-label="{t('Você está em')}"><a href="index.html">{t("Início")}</a> &gt; <span>{esc(e['nome'])}</span></nav>
    <h1 class="titulo-cat">{esc(e['nome'])}</h1>
    <p class="desc-cat">{esc(e['descricao'])}</p>
    <div class="grade-cat">{lista}</div>
  </div>
  {lateral()}
</div>"""
    return pagina(e["nome"], e["descricao"], e["slug"], corpo, extra_head="" if da_ed else NOINDEX)


# ---------------------------------------------------------------- matéria
FONTES_RE = re.compile(r"^((?:Fontes|Fonte|Sources|Source|Fuentes|Fuente|Quellen|Quelle|Fonti|Fonte|情報源|出典|来源|المصادر)(?:\s*[(（][^)）]{1,40}[)）])?)\s*[:：]\s*")


def corpo_texto(paragrafos):
    out = []
    for p in paragrafos:
        if p.startswith("!img "):
            url, alt, cred = (p[5:].split("|") + ["", ""])[:3]
            v = variantes_capa(url) if url.startswith("assets/img/") else []
            mw = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons/thumb/.+/)(\d+)px-([^/]+)$", url)
            if mw and int(mw.group(2)) > 960:  # Wikimedia tem miniatura padrão de 960px: o celular baixa essa
                url_640 = f"{mw.group(1)}960px-{mw.group(3)}"
                _c = lambda u: esc(u.replace(",", "%2C"))  # vírgula no nome do arquivo quebraria a lista do srcset
                srcset_wm = f' srcset="{_c(url_640)} 960w, {_c(url)} {mw.group(2)}w" sizes="(max-width: 760px) 100vw, 720px"'
            else:
                srcset_wm = ""
            srcset = f' srcset="{", ".join(f"{u} {w}w" for u, w in v)}, {esc(url)} 1920w" sizes="(max-width: 760px) 100vw, 720px"' if v else "" or srcset_wm
            out.append(f'<figure class="foto-corpo"><img src="{esc(url)}"{srcset} alt="{esc(alt)}"{' width="1920" height="1080"' if v else ""} loading="lazy" decoding="async"><figcaption class="credito">{esc(cred)}</figcaption></figure>')
        elif p.startswith("## "):
            out.append(f"<h2>{esc(p[3:])}</h2>")
        elif FONTES_RE.match(p) and "](http" in p:
            # Linha "Fontes: [A](url); [B](url)" vira um bloco próprio, com uma fonte por linha
            rotulo = FONTES_RE.match(p).group(1)
            links = re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", p)
            itens = "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{esc(n)}</a></li>' for n, u in links)
            out.append(f'<aside class="fontes" aria-label="{esc(rotulo)}"><p class="fontes-tit">{esc(rotulo)}</p><ul>{itens}</ul></aside>')
        else:
            t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', esc(p))
            # link interno para outra matéria do Aloha: [texto](materia-<slug>.html) (vira o endereço certo em cada idioma)
            t = re.sub(r"\[([^\]]+)\]\((materia-[a-z0-9-]+\.html)\)", r'<a href="\2">\1</a>', t)
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
        quando = datetime.fromisoformat(m["data"]).strftime("%d/%m às %H:%M")
        rotulo, atual = f"Rascunho, ainda não publicado. Horário sugerido: {quando}.", f' value="{m["data"]}"'
        texto_ag, rot_agendar = "ou agendar para", "Agendar"
        rej = "Rejeitar"
    atalhos = " ".join(f'<button type="button" class="chip" data-hora="{h}">{h[:2]}h</button>' for h in HORARIOS_PADRAO)
    import agenda
    ocup = {dia: sorted(t.strftime("%H:%M") for t, _ in v) for dia, v in agenda.ocupacao(excluir=slug).items()}
    livre = agenda.proximo_livre(slug, agenda.ocupacao(excluir=slug)).strftime("%Y-%m-%dT%H:%M")
    dados_agenda = esc(json.dumps({"ocupacao": ocup, "livre": livre, "max": agenda.POR_DIA}, ensure_ascii=False))
    return (f'<div class="faixa-rascunho" data-slug="{esc(slug)}" data-repo="{REPO}" data-acao="{acao}" data-agenda="{dados_agenda}"><div class="wrap">'
            f'<strong>{rotulo}</strong> '
            f'<a class="botao" id="publicar-agora" href="{link_acao("Aprovar", slug)}" target="_blank" rel="noopener noreferrer">Publicar agora</a> '
            f'<label class="agendar">{texto_ag} <input type="datetime-local" id="quando"{atual} aria-label="Data e hora de publicação"></label> '
            f'<span class="atalhos">Atalhos: {atalhos}</span> '
            f'<a class="botao-sec" id="agendar" href="{link_acao(acao, slug)}" target="_blank" rel="noopener noreferrer">{rot_agendar}</a> '
            f'<a class="botao-sec" href="{link_acao("Rejeitar", slug)}" target="_blank" rel="noopener noreferrer">{rej}</a> '
            f'{prev_trad(m)}<a href="admin/rascunhos.html">Voltar ao painel</a>'
            f'<div class="aviso-agenda" id="aviso-agenda" role="alert" hidden></div></div></div>\n<script src="assets/js/admin.js"></script>')


NAV_PAINEL = [
    ("Visão geral", [("index", "admin/", "▦", "Painel"), ("metricas", "admin/metricas.html", "▤", "Métricas")]),
    ("Conteúdo", [("rascunhos", "admin/rascunhos.html", "✎", "Rascunhos"), ("agendados", "admin/agendados.html", "◷", "Agendados"),
                  ("publicados", "admin/publicados.html", "✔", "Publicados")]),
    ("Divulgação", [("links", "admin/links.html", "↗", "Links das redes"), ("parceiros", "admin/parceiros.html", "☺", "Links de parceiros")]),
]
CONTAGENS_PAINEL = {}


def painel_pagina(titulo, ativo, lede, conteudo, acao_topo=""):
    """Estrutura do painel administrativo: menu lateral, barra superior e área de conteúdo (separada do visual do site)."""
    menu = ""
    for grupo, itens in NAV_PAINEL:
        menu += f"<h6>{grupo}</h6>"
        for chave, href, icone, nome in itens:
            n = CONTAGENS_PAINEL.get(chave)
            badge = f'<span class="n{"" if chave == "rascunhos" else " cinza"}">{n}</span>' if n else ""
            menu += f'<a href="{href}" class="{"ativo" if chave == ativo else ""}"><span aria-hidden="true">{icone}</span> {nome}{badge}</a>'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"><base href="/">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{esc(titulo)} · Painel Aloha</title>
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="stylesheet" href="assets/css/aloha.css">
<link rel="stylesheet" href="assets/css/painel.css">
</head>
<body class="painel">
<aside class="p-lado">
<a class="p-marca" href="admin/"><i>A</i><span>ALOHA<small>Painel de controle</small></span></a>
<nav class="p-nav">{menu}
<h6>Atalhos</h6>
<a href="/" target="_blank" rel="noopener"><span aria-hidden="true">⌂</span> Ver o site</a>
<a href="https://github.com/{REPO}/actions" target="_blank" rel="noopener"><span aria-hidden="true">⚙</span> Automações</a>
</nav>
<div class="p-rodape-lado">ALOHA NOTÍCIAS · acesso restrito</div>
</aside>
<div class="p-main">
<header class="p-topo"><button class="p-menu" type="button" aria-label="Abrir menu">☰</button>
<div class="grow"><h1>{esc(titulo)}</h1><p class="lede">{lede}</p></div>
{acao_topo}<button class="p-btn" type="button" id="p-tema" title="Alternar claro/escuro">◐ Tema</button></header>
<main class="p-conteudo painel-main">
{conteudo}
</main></div>
<script src="assets/js/painel.js"></script>
</body></html>"""


def _linha_painel(d, tipo):
    ed = esc(ED[d["editoria"]]["nome"])
    if tipo == "agen":
        tag = f'<span class="p-tag agen">{datetime.fromisoformat(d["data"]).strftime("%d/%m %H:%M")}</span>'
        href, sub = f'admin/{esc(d["slug"])}.html', f"{ed} · {esc(d['autor'])}"
    elif tipo == "rasc":
        tag = '<span class="p-tag rasc">Aguardando</span>'
        href, sub = f'admin/{esc(d["slug"])}.html', f"{ed} · {esc(d['autor'])} · {data_curta(d['data'])}"
    else:
        tag = '<span class="p-tag pub">No ar</span>'
        href, sub = url_materia(d), f"{ed} · {data_curta(d['data'])}"
    busca = esc((d["titulo"] + " " + ed).lower())
    alvo = ' target="_blank" rel="noopener"' if tipo == "pub" else ""
    return (f'<li data-busca="{busca}"><a class="p-item" href="{href}"{alvo}><div class="t"><b>{esc(d["titulo"])}</b>'
            f'<small>{sub}</small></div>{tag}</a></li>')


def _lista_painel(itens, tipo, vazio):
    if not itens:
        return f'<div class="p-vazio">{vazio}</div>'
    return '<ul class="p-lista">' + "".join(_linha_painel(d, tipo) for d in itens) + "</ul>"


def gerar_metricas_admin(materias):
    """Métricas de visitas do contador próprio do site (worker/index.js), sem Google Analytics."""
    nomes = {"/": "Página inicial", "/busca.html": "Busca", "/404.html": "Página não encontrada"}
    for e in editorias:
        nomes["/" + url_editoria(e["slug"])] = "Editoria: " + e["nome"]
    for m in materias:
        nomes["/" + url_materia(m)] = m["titulo"]
        nomes["slug:" + m["slug"]] = m["titulo"]
    for n in ("sobre", "contato", "equipe", "politica-editorial", "privacidade", "termos"):
        nomes[f"/{n}.html"] = n.replace("-", " ").capitalize()
    acao = ('<select id="m-dias" class="p-btn" aria-label="Período"><option value="7">7 dias</option><option value="30" selected>30 dias</option>'
            '<option value="90">90 dias</option><option value="365">12 meses</option></select>')
    conteudo = f"""<section class="p-painel m-vivo"><header><h2><span class="m-ponto"></span>Ao vivo</h2><small id="v-hora"></small></header>
<div class="m-vivo-corpo"><div class="m-vivo-num"><b id="v-pessoas">…</b><span>pessoas no site agora</span><small>quem abriu uma página nos últimos 5 minutos · atualiza a cada 15 s</small></div>
<div class="m-vivo-lista"><h3>Lendo agora</h3><div id="v-paginas"></div></div>
<div class="m-vivo-lista"><h3>Chegaram por</h3><div id="v-origens"></div><h3>Aparelho</h3><div id="v-aparelhos"></div></div></div></section>
<div class="p-cards" id="m-cards"><div class="p-stat"><span>Carregando</span><b>…</b><small>buscando os números</small></div></div>
<p class="m-aviso" id="m-aviso" hidden></p>
<section class="p-painel"><header><h2>Visualizações por dia</h2><a href="#" id="m-tabela-dia">Ver tabela</a></header><div class="m-graf" id="m-serie"></div><div id="m-serie-tab" hidden></div></section>
<div class="m-duas">
<section class="p-painel"><header><h2>Artigos mais lidos (todos os idiomas)</h2></header><div id="m-artigos"></div></section>
<section class="p-painel"><header><h2>De onde vieram</h2></header><div id="m-origens"></div></section>
</div>
<section class="p-painel"><header><h2>Páginas mais vistas</h2></header><div id="m-paginas"></div></section>
<div class="m-duas">
<section class="p-painel"><header><h2>Links etiquetados (utm_source)</h2></header><div id="m-fontes"></div></section>
<section class="p-painel"><header><h2>Horário das visitas</h2></header><div class="m-graf" id="m-horas"></div></section>
</div>
<section class="p-painel"><header><h2>Parceiros</h2><a href="admin/parceiros.html">Criar links</a></header><div id="m-parceiros"></div></section>
<div class="m-tres">
<section class="p-painel"><header><h2>Países</h2></header><div id="m-paises"></div></section>
<section class="p-painel"><header><h2>Aparelhos</h2></header><div id="m-aparelhos"></div></section>
<section class="p-painel"><header><h2>Idioma do site</h2></header><div id="m-idiomas"></div></section>
</div>
<section class="p-painel"><header><h2>Como esta contagem funciona</h2></header><div class="m-sobre">
<p>Contador próprio do site, separado do Google Analytics: conta cada página aberta por uma pessoa (robôs e o painel ficam de fora), sem cookies. Visitantes únicos são contados por dia, com um código que muda todo dia; por isso, no período, a soma pode contar a mesma pessoa mais de uma vez. Horários em Brasília. O selo "Em alta" aparece no site para os até 3 artigos com 10 ou mais leitores nos últimos 7 dias, e a lista "Mais lidas" segue a mesma contagem (sem mostrar números ao público).</p>
<p><button type="button" class="p-btn" id="m-eu"></button> <span id="m-eu-txt"></span></p>
</div></section>
<script id="m-nomes" type="application/json">{json.dumps(nomes, ensure_ascii=False).replace("</", "<\\/")}</script>
<script src="assets/js/metricas-admin.js"></script>"""
    return painel_pagina("Métricas", "metricas", "Visitas contadas pelo próprio site, sem Google Analytics", conteudo, acao)


def gerar_admin(rascunhos, agendados=(), publicados=()):
    """Admin > Visão geral: números, o que espera aprovação, a fila de agendamentos e os últimos publicados."""
    pub = sorted(publicados, key=lambda d: d["data"], reverse=True)
    prox = agendados[0] if agendados else None
    cards = (f'<a class="p-stat{" destaque" if rascunhos else ""}" href="admin/rascunhos.html"><span>Aguardando aprovação</span><b>{len(rascunhos)}</b><small>rascunhos para revisar</small></a>'
             f'<a class="p-stat" href="admin/agendados.html"><span>Agendados</span><b>{len(agendados)}</b><small>{"próximo: " + datetime.fromisoformat(prox["data"]).strftime("%d/%m às %H:%M") if prox else "nenhum na fila"}</small></a>'
             f'<a class="p-stat" href="admin/publicados.html"><span>Publicados</span><b>{len(pub)}</b><small>{"último: " + data_curta(pub[0]["data"]) if pub else "ainda nenhum"}</small></a>'
             f'<a class="p-stat" href="admin/parceiros.html"><span>Parceiros</span><b>→</b><small>links por parceiro e jogo</small></a>')
    slots = "".join(f'<div class="p-slot"><b>{h}</b><span>horário padrão de publicação (Brasília)</span></div>' for h in HORARIOS_PADRAO)
    conteudo = f"""<div class="p-cards">{cards}</div>
<div class="p-grade"><div>
<section class="p-painel"><header><h2>Aguardando sua aprovação</h2><a href="admin/rascunhos.html">Ver todos</a></header>{_lista_painel(rascunhos[:6], "rasc", "Nenhum rascunho esperando aprovação.")}</section>
<section class="p-painel"><header><h2>Fila de agendamento</h2><a href="admin/agendados.html">Ver todos</a></header>{_lista_painel(agendados[:6], "agen", "Nada agendado no momento.")}</section>
<section class="p-painel"><header><h2>Publicados recentemente</h2><a href="admin/publicados.html">Ver todos</a></header>{_lista_painel(pub[:6], "pub", "Nada publicado ainda.")}</section>
</div><div>
<section class="p-painel"><header><h2>Atalhos</h2></header><div class="p-atalhos">
<a href="admin/rascunhos.html">Revisar rascunhos<small>Aprovar, agendar ou rejeitar</small></a>
<a href="admin/links.html">Links das redes<small>Etiquetados por rede</small></a>
<a href="admin/parceiros.html">Parceiros<small>Link por parceiro e jogo</small></a>
<a href="/" target="_blank" rel="noopener">Ver o site<small>Abre em outra aba</small></a>
<a href="https://github.com/{REPO}/actions" target="_blank" rel="noopener">Automações<small>Publicação e capas</small></a>
</div></section>
<section class="p-painel"><header><h2>Horários padrão</h2></header><div class="p-slots">{slots}</div></section>
</div></div>"""
    return painel_pagina("Visão geral", "index", "Resumo do site e do que precisa da sua atenção.", conteudo)


def gerar_lista_admin(chave, titulo, lede, itens, tipo, vazio):
    busca = '<input class="p-busca" id="p-busca" type="search" placeholder="Buscar por título ou editoria" aria-label="Buscar">'
    conteudo = (f'<p>{busca}</p><section class="p-painel"><header><h2>{len(itens)} {"item" if len(itens) == 1 else "itens"}</h2></header>'
                f'{_lista_painel(itens, tipo, vazio)}</section>')
    return painel_pagina(titulo, chave, lede, conteudo)


def atualizado_html(m):
    """Campo opcional "atualizado" (YYYY-MM-DDTHH:MM) na matéria: mostra "Atualizado em ..." ao lado da data."""
    a = m.get("atualizado")
    return f'<time datetime="{a}">{t("Atualizado em")} {data_longa(a)}</time>' if a else ""


def correcao_html(m):
    """Campo opcional "correcao": texto da nota de correção/atualização exibida ao fim da matéria."""
    c = m.get("correcao")
    return f'<aside class="nota-correcao"><strong>{t("Atualização:")}</strong> {esc(c)}</aside>' if c else ""


def autor_html(m):
    return f'<a href="equipe.html" rel="author">{esc(autor_nome(m))}</a>' if m["autor"] in ("Equipe Aloha", AUTOR) else esc(m["autor"])


REDES_LINKS = [("YouTube", "youtube"), ("TikTok", "tiktok"), ("Instagram", "instagram"), ("Facebook", "facebook"),
               ("X / Twitter", "x"), ("Threads", "threads"), ("WhatsApp", "whatsapp"), ("Telegram", "telegram"),
               ("Kwai", "kwai"), ("Pinterest", "pinterest"), ("Reddit", "reddit"), ("Discord", "discord"), ("LinkedIn", "linkedin")]


def gerar_links_admin(lista):
    """Admin > Links: link de cada matéria já etiquetado para cada rede social (para medir no Analytics)."""
    blocos = []
    for m in lista:
        base = "https://alohanoticias.com/" + url_materia(m)[:-5]
        linhas = "".join(
            f'<li class="link-rede"><span class="chapeu">{nome}</span>'
            f'<input readonly value="{esc(base)}?utm_source={cod}&amp;utm_medium=social&amp;utm_campaign=post_{cod}" aria-label="Link para {nome}">'
            f'<button class="botao-sec copiar" type="button">Copiar</button></li>'
            for nome, cod in REDES_LINKS)
        blocos.append(f'<details class="links-materia"><summary><strong>{esc(m["titulo"])}</strong> '
                      f'<span class="meta">{data_curta(m["data"])}</span></summary><ul class="lista-simples">{linhas}</ul></details>')
    corpo = f"""<div class="wrap editoria-corpo" style="max-width:820px">{"".join(blocos)}</div>
<style>.links-materia{{border-bottom:1px solid var(--linha,#ddd);padding:14px 0}}.links-materia summary{{cursor:pointer}}
.link-rede{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:6px 0}}.link-rede .chapeu{{min-width:110px}}
.link-rede input{{flex:1;min-width:200px;font-size:.85rem;padding:6px}}</style>
<script src="assets/js/links-admin.js"></script>"""
    return painel_pagina("Links das redes", "links", "Cada link já leva a etiqueta da rede, para medir no Analytics.", corpo)


def gerar_parceiros_admin(lista):
    """Admin > Parceiros: gera o link de um artigo com o nome do parceiro no final (para medir quem ele trouxe)."""
    opcoes = "".join(f'<option value="{esc(m["slug"])}">{esc(m["titulo"])}</option>' for m in lista)
    idiomas = "".join(f'<option value="{c}">{i18n.NOMES_IDIOMA[c]}</option>' for c in i18n.IDIOMAS_REAIS)
    corpo = f"""<div class="wrap editoria-corpo parceiros" style="max-width:820px">
<label for="p-artigo"><strong>Artigo</strong></label>
<select id="p-artigo"><option value="">Página inicial do site</option>{opcoes}</select>
<label for="p-idioma"><strong>Idioma em que o artigo será divulgado</strong></label>
<select id="p-idioma">{idiomas}</select>
<label for="p-nome"><strong>Nome do parceiro</strong></label>
<input id="p-nome" list="p-salvos" placeholder="ex.: Joao" autocomplete="off">
<datalist id="p-salvos"></datalist>
<label for="p-jogo"><strong>Jogo ou assunto do artigo (rótulo no link)</strong></label>
<input id="p-jogo" list="p-jogos" placeholder="ex.: roblox, freefire, stumble guys, fortnite" autocomplete="off">
<datalist id="p-jogos"><option value="roblox"><option value="freefire"><option value="stumble guys"><option value="fortnite"><option value="minecraft"><option value="gta"><option value="pokemon"></datalist>
<label for="p-rede"><strong>Onde o parceiro vai divulgar</strong></label>
<select id="p-rede"><option value="">Escolha a rede</option>{"".join(f'<option value="{cod}">{nome}</option>' for nome, cod in REDES_LINKS)}<option value="site">Site ou blog</option><option value="email">E-mail / newsletter</option><option value="outro">Outro</option></select>
<p class="meta" id="p-codigo"></p>
<p class="meta" id="p-aviso" style="color:var(--p-marca);font-weight:600"></p>
<label for="p-link"><strong>Link para enviar ao parceiro</strong></label>
<textarea id="p-link" readonly rows="3" placeholder="Escreva o nome do parceiro para gerar o link"></textarea>
<p><button class="botao" type="button" id="p-copiar">Copiar link</button></p>
<h2 style="margin-top:32px">Parceiros e seus links</h2>
<p class="meta">Cada parceiro tem um único link por artigo: gerar de novo o mesmo artigo para o mesmo parceiro atualiza o link, não cria outro. A lista fica salva neste navegador; use Exportar/Importar para levar a outro aparelho.</p>
<div id="p-registro"></div>
<p><button class="botao-sec" type="button" id="p-exportar">Exportar lista</button> <label class="botao-sec" style="display:inline-flex;margin:0!important;cursor:pointer">Importar lista<input type="file" id="p-importar" accept="application/json" hidden></label></p>
<h2 style="margin-top:32px">Como ver os resultados</h2>
<p><strong>Na hora:</strong> Analytics &gt; Visão geral em tempo real &gt; quadro de eventos: aparece <em>parceiro_nome_rede_idioma</em> (ex.: parceiro_joao_instagram_pt).</p>
<p><strong>No dia seguinte:</strong> Aquisição de tráfego (ou Páginas e telas) com <em>Origem/mídia da sessão</em>: cada linha mostra parceiro / rede (ex.: joao / instagram). O jogo/assunto aparece em <em>Termo da sessão</em>. Para ver só parceiros, filtre <em>Campanha da sessão</em> = <em>parceiro</em>; o idioma aparece na coluna <em>Conteúdo manual da sessão</em> (pt, en, es...).</p>
</div>
<style>.parceiros label{{display:block;margin:18px 0 6px}}.parceiros select,.parceiros input,.parceiros textarea{{width:100%;padding:10px;font-size:1rem;box-sizing:border-box}}</style>
<script src="assets/js/parceiros-admin.js"></script>"""
    return painel_pagina("Links de parceiros", "parceiros", "Link por artigo, idioma, parceiro, jogo e rede.", corpo)


def botoes_compartilhar(m):
    from urllib.parse import quote
    pre = "" if LANG == "pt" else LANG + "/"
    base = "https://alohanoticias.com/" + pre + url_materia(m)[:-5]  # endereço final, sem ".html"
    def com(rede):  # etiqueta: quem chega por um compartilhamento conta como vindo daquela rede
        return base + f"?utm_source={rede}&utm_medium=compartilhamento&utm_campaign=botao_compartilhar"
    tit = quote(m["titulo"], safe="")
    redes = [("WhatsApp", "https://wa.me/?text=" + quote(m["titulo"] + " " + com("whatsapp"), safe="")),
             ("X", f"https://twitter.com/intent/tweet?text={tit}&url={quote(com('x'), safe='')}"),
             ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={quote(com('facebook'), safe='')}"),
             ("Telegram", f"https://t.me/share/url?url={quote(com('telegram'), safe='')}&text={tit}")]
    return "".join(f'<a class="botao-sec" href="{h}" target="_blank" rel="noopener noreferrer" aria-label="{t('Compartilhar no')} {n}">{n}</a>' for n, h in redes)


def gerar_materia(m, preview=False, agendado=False):
    e = ED[m["editoria"]]
    # "Leia também": primeiro as matérias com mais assuntos (tags) em comum, depois a mesma editoria, depois as mais novas
    tags_m = {slug_tag(x) for x in m.get("tags", [])}
    candidatas = [x for x in materias if x["slug"] != m["slug"]]
    candidatas.sort(key=lambda x: x["data"], reverse=True)  # mais novas primeiro; o sort abaixo é estável
    candidatas.sort(key=lambda x: (-len(tags_m & {slug_tag(y) for y in x.get("tags", [])}), x["editoria"] != m["editoria"]))
    relacionadas = candidatas[:3]
    _eds = {e["slug"]: e["nome"] for e in editorias}
    tags = "".join(f'<a href="{url_editoria(slug_tag(t))}">{esc(_eds[slug_tag(t)])}</a>' if slug_tag(t) in _eds else f'<a href="{url_tag(t)}">{esc(t)}</a>'
                   for t in m.get("tags", []) if slug_tag(t))  # tag igual a uma editoria leva à editoria, com o mesmo nome do menu
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle", "headline": m["titulo"],
        "description": m["linha_fina"], "datePublished": m["data"], "dateModified": m.get("atualizado") or m["data"], "articleSection": e["nome"],
        "image": [og_url(og_da_capa(m))], "mainEntityOfPage": "https://alohanoticias.com/" + ("" if LANG == "pt" else LANG + "/") + url_materia(m), "inLanguage": i18n.HTML_LANG[LANG],
        "author": ({"@type": "Person", "name": AUTOR, "url": "https://alohanoticias.com/" + ("" if LANG == "pt" else LANG + "/") + "equipe.html", "sameAs": AUTOR_REDES}
                   if m["autor"] == AUTOR else {"@type": "Organization", "name": autor_nome(m), "url": "https://alohanoticias.com/" + ("" if LANG == "pt" else LANG + "/") + "equipe.html"}),
        "publisher": {"@type": "Organization", "name": NOME_BUSCA, "url": "https://alohanoticias.com/", "logo": {"@type": "ImageObject", "url": "https://alohanoticias.com/assets/img/icone-app-512.png"}},
    }, ensure_ascii=False)
    corpo = f"""<article class="wrap materia">
  <nav class="migalhas" aria-label="{t('Você está em')}"><a href="index.html">{t('Início')}</a><span aria-hidden="true">/</span><a href="{url_editoria(e['slug'])}">{esc(e['nome'])}</a></nav>
  <header class="materia-topo">
    <span class="chapeu">{esc(e['nome'])}</span>{alta(m)}
    <h1>{esc(m['titulo'])}</h1>
    <p class="linha-fina">{esc(m['linha_fina'])}</p>
    <p class="meta"><span>{t("Por")} {autor_html(m)}</span><time datetime="{m['data']}">{data_longa(m['data'])}</time></p>
  </header>
  <figure class="materia-capa" style="margin-inline:0">{capa(m, prioridade=True, sizes="(max-width: 1100px) 100vw, 1100px")}{legenda(m)}</figure>{video(m)}
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
    pre_abs = "https://alohanoticias.com/" + ("" if LANG == "pt" else LANG + "/")
    migalhas_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": t("Início"), "item": pre_abs},
        {"@type": "ListItem", "position": 2, "name": e["nome"], "item": pre_abs + url_editoria(e["slug"])},
        {"@type": "ListItem", "position": 3, "name": m["titulo"], "item": pre_abs + url_materia(m)}]}, ensure_ascii=False)
    head = f'<script type="application/ld+json">{ld}</script>\n<script type="application/ld+json">{migalhas_ld}</script>\n'
    head += f'<meta name="aloha-slug" content="{esc(m["slug"])}">\n'
    _im = m.get("imagem") or {}
    _v = variantes_capa(_im.get("url", "")) if _im.get("url", "").startswith("assets/") else []
    if _v:
        head += f'<link rel="preload" as="image" href="{esc(_im["url"])}" imagesrcset="{", ".join(f"{u} {w}w" for u, w in _v)}, {esc(_im["url"])} 1920w" imagesizes="(max-width: 1100px) 100vw, 1100px" fetchpriority="high">\n'
    if preview:
        corpo = faixa_rascunho(m, agendado) + corpo
        head = '<base href="/">\n<meta name="robots" content="noindex,nofollow">\n' + head
    return pagina(m["titulo"], m["linha_fina"], e["slug"], corpo, extra_head=head, og_img=og_da_capa(m), og_tipo="article")


# ---------------------------------------------------------------- busca e páginas simples
INDICES = {}
NOVID = {}


def gerar_novidades():
    """Feed leve (15 matérias mais recentes) para o sino de notificações."""
    pre = "" if LANG == "pt" else "../"
    itens = []
    for m in sorted(materias, key=lambda x: x["data"], reverse=True)[:15]:
        im = (m.get("imagem") or {}).get("url", "")
        if im and not im.startswith("http"):
            im = pre + im
        itens.append({"id": m["slug"], "titulo": m["titulo"], "editoria": ED[m["editoria"]]["nome"],
                      "data": data_curta(m["data"]), "url": url_materia(m), "capa": im})
    textos = {"titulo": t("Histórico de push"), "vazio": t("O histórico de notificações está vazio"),
              "ler": t("marcar tudo como lido"), "limpar": t("Limpar tudo"),
              "ativar": t("Ativar avisos no celular"), "ativado": t("Avisos ativados"), "bloqueado": t("Avisos bloqueados no navegador"),
              "ios": t("No iPhone, toque em Compartilhar e em “Adicionar à Tela de Início”; depois abra o ALOHA pelo ícone e ative os avisos."),
              "carregando": t("Ainda carregando. Tente de novo em alguns segundos (se persistir, desative bloqueadores de anúncio para este site)."),
              "erro": t("Não foi possível ativar os avisos neste aparelho.")}
    NOVID[LANG] = "window.ALOHA_NOVID = " + json.dumps({"t": textos, "itens": itens, "push": ONESIGNAL_APP_ID}, ensure_ascii=False) + ";\n"


def gerar_busca():
    indice = [{
        "titulo": m["titulo"], "linha_fina": m["linha_fina"], "editoria": ED[m["editoria"]]["nome"],
        "tags": m.get("tags", []), "url": url_materia(m), "data": data_longa(m["data"]), "capa": capa(m, responsivo=False),
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
    return pagina(t("Buscar"), t("Busque matérias da ALOHA NOTÍCIAS."), "", corpo, com_news=False, extra_head=NOINDEX)


def gerar_simples(titulo, descricao, conteudo):
    corpo = f'<div class="wrap"><div class="pagina-texto"><h1>{esc(titulo)}</h1>{conteudo}</div></div>'
    return pagina(titulo, descricao, "", corpo)


def gerar_404():
    corpo = f"""<div class="wrap erro"><div class="o">{O_SIMBOLO}</div><h1>{t("Essa onda passou")}</h1>
<p>{t("A página que você procurou não existe ou mudou de endereço.")}</p><a class="botao" href="index.html">{t("Voltar para a página inicial")}</a></div>"""
    return pagina(t("Página não encontrada"), t("Página não encontrada"), "", corpo, com_news=False, extra_head=NOINDEX)


# ---------------------------------------------------------------- saída
# Texto da política de privacidade (com a seção de anúncios): site/privacidade.py

CSP_BASE = ("default-src 'self'; script-src 'self' https://www.googletagmanager.com https://*.googletagmanager.com https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; "
            "frame-src https://www.youtube-nocookie.com; connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://www.google.com https://cloudflareinsights.com; object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests")
CSP_ADS = ("default-src 'self'; script-src 'self' https://www.googletagmanager.com https://*.googletagmanager.com 'unsafe-inline' https://static.cloudflareinsights.com https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.google.com https://*.doubleclick.net https://www.googletagservices.com https://adservice.google.com https://partner.googleadservices.com; "
           "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; "
           "frame-src https://www.youtube-nocookie.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; "
           "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://cloudflareinsights.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google; "
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
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400
"""


def montar_arquivos():
    for _m in (list(materias) if LANG == "pt" else []):
        _p = sum(len(b.split()) for b in _m["corpo"] if not b.startswith("!img"))
        if not 520 <= _p <= 880:
            print(f"AVISO tamanho: {_m['slug']} tem {_p} palavras (meta: 600 a 850, 3 a 4 min de leitura)")
    arquivos = {"index.html": gerar_home(), "busca.html": (gerar_novidades(), gerar_busca())[1], "404.html": gerar_404()}
    for e in editorias:
        arquivos[url_editoria(e["slug"])] = gerar_editoria(e)
    for m in materias:
        arquivos[url_materia(m)] = gerar_materia(m)

    arquivos["sobre.html"] = gerar_simples("Sobre nós", "Quem faz a ALOHA NOTÍCIAS.", """
<p>A ALOHA NOTÍCIAS é um site de notícias para quem quer entender o que está acontecendo sem pressa e sem barulho. Nosso foco é cinema, games e tecnologia: estreias, lançamentos e o que está em alta, com a informação conferida.</p>
<p>O site foi criado e é editado por <a href="equipe.html">João Gabriel</a>, criador de sites e de conteúdo digital.</p>
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
<p>Nenhuma matéria vai ao ar sem a revisão e a aprovação do editor, <a href="equipe.html">João Gabriel</a>.</p>
<h2>Uso de inteligência artificial</h2>
<p>Usamos ferramentas de inteligência artificial como apoio no trabalho: para pesquisar e organizar informações, preparar rascunhos e adaptar as matérias para outros idiomas. Nenhum texto vai ao ar direto da ferramenta. Toda matéria é conferida com as fontes, editada e aprovada por João Gabriel antes de ser publicada, e ele responde pelo que sai no site.</p>
<h2>Fato e opinião</h2>
<p>Separamos o que foi apurado do que é análise. Textos de opinião ou recomendação são identificados como tal.</p>
<h2>Como escolhemos os assuntos</h2>
<p>Priorizamos o que está em alta e é útil para quem lê: estreias, lançamentos, datas e novidades de cinema, games e tecnologia. Não publicamos só para repetir um comunicado. Em cada matéria buscamos reunir o que está confirmado, organizar o que ainda não se sabe e indicar de onde veio cada informação.</p>
<h2>Boatos e rumores</h2>
<p>Rumores, vazamentos e informações de bastidores só aparecem quando são relevantes, e sempre identificados como não confirmados, com a fonte indicada. Não tratamos boato como fato.</p>
<h2>Imagens e vídeos</h2>
<p>Na capa e no texto usamos imagens oficiais de divulgação do próprio assunto, de estúdios, plataformas, desenvolvedoras e fabricantes. Fotos de acervos livres, como o Wikimedia Commons, só entram quando mostram algo de que o texto fala. Toda imagem leva legenda com o crédito de quem a fez e, quando há, a licença. Não usamos imagens com marca d'água de terceiros. O vídeo de uma matéria, quando existe, é um conteúdo oficial incorporado do canal onde foi publicado, com o nome do canal indicado. Se você é autor ou dono de uma imagem e quer outro crédito ou a remoção, escreva para a gente pela página de <a href="contato.html">contato</a>.</p>
<h2>Correções</h2>
<p>Quando encontramos um erro, corrigimos a matéria e indicamos a correção no texto. Também atualizamos matérias quando datas ou fatos mudam, para que o conteúdo não fique desatualizado. Se você encontrou um erro, envie a matéria e o que está incorreto pela página de <a href="contato.html">contato</a>. Respondemos o quanto antes.</p>
<h2>Independência</h2>
<p>O conteúdo editorial é independente. Anúncios, quando existirem, ficam separados do texto e não influenciam o que publicamos. Se uma matéria tiver patrocínio ou parceria, isso será informado claramente ao leitor.</p>""")
    arquivos["equipe.html"] = gerar_simples('João Gabriel', 'Quem cria, escreve e edita a ALOHA NOTÍCIAS.', autor_cartao() + f"""
<p><strong>João Gabriel</strong> tem 21 anos, é brasileiro, criador de sites e criador de conteúdo digital em plataformas. Ele criou a ALOHA NOTÍCIAS e assina, revisa e aprova todas as matérias publicadas aqui.</p>
<h2>O site</h2>
<p>A ALOHA NOTÍCIAS é um projeto independente sobre cinema, games e tecnologia, sem vínculo com estúdios, produtoras ou fabricantes.</p>
<h2>O que você pode esperar</h2>
<p>Informação conferida em mais de uma fonte, fontes citadas no fim de cada texto, rumores identificados como tal e correções feitas às claras. Se algo estiver errado, eu quero saber. Os detalhes estão na <a href="politica-editorial.html">política editorial</a>.</p>
<h2>O que cobrimos</h2>
<ul>{"".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a>: {esc(e["descricao"])}</li>' for e in editorias)}</ul>
<h2>Contato</h2>
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
            f'<p class="meta"><time datetime="{x["data"]}">{data_curta(x["data"])}</time></p></div>{capa(x)}</a></li>' for x in lista)
        corpo = (f'<div class="topo-editoria"><div class="wrap"><h1>{esc(tg)}</h1><p>{len(lista)} {t("matéria") if len(lista) == 1 else t("matérias")} {t("sobre este assunto.")}</p></div></div>'
                 f'<div class="wrap editoria-corpo"><ul class="lista-simples" style="max-width:820px">{itens}</ul></div>')
        arquivos[url_tag(tg)] = pagina(tg, f"{t('Matérias da ALOHA NOTÍCIAS sobre')} {tg}.", "", corpo,
                                       extra_head=NOINDEX if len(lista) < MIN_MATERIAS_TAG else "")
    arquivos["contato.html"] = gerar_simples("Contato e anúncios", "Fale com a ALOHA NOTÍCIAS.", """
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
    arquivos["privacidade.html"] = gerar_simples(*privacidade.pagina("pt", ANUNCIOS_ATIVOS))

    if LANG != "pt":
        eds = "".join(f'<li><a href="{url_editoria(e["slug"])}">{esc(e["nome"])}</a>: {esc(e["descricao"])}</li>' for e in editorias)
        for nome, (tit, desc, corpo) in i18n.PAGINAS[LANG].items():
            corpo = corpo.replace("@@EDITORIAS@@", eds).replace("@@ANUNCIOS@@", i18n.PRIV_ANUNCIOS[LANG] if ANUNCIOS_ATIVOS else "")
            arquivos[nome] = gerar_simples(tit, desc, (autor_cartao() if nome == "equipe.html" else "") + corpo)
        arquivos["privacidade.html"] = gerar_simples(*privacidade.pagina(LANG, ANUNCIOS_ATIVOS))
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
                     for e in EDITORIAS_PT]  # todas as seções, para o menu não apontar para páginas inexistentes
    ED = {e["slug"]: e for e in editorias}
    MAIS_LIDAS = materias[:40]
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
    "anime": ["anime", "anime", "anime", "anime", "anime", "anime", "dongman", "anime"],
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


_RE_IDX = re.compile(r'(https://alohanoticias\.com/(?:[a-z]{2}/)?)index\.html')
_RE_HTML = re.compile(r'(https://alohanoticias\.com/[^"\'\s<>?#]*?)\.html')


def limpa_abs(s):
    """Endereços absolutos sem ".html": a Cloudflare redireciona /pagina.html para /pagina, e canonical, hreflang,
    og:url, sitemap e dados estruturados devem apontar para o endereço final, não para um redirecionamento."""
    return _RE_HTML.sub(r"\1", _RE_IDX.sub(r"\1", s))


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
    langs = [l for l in i18n.IDIOMAS_REAIS if nome in existe.get(l, ()) and l in IDIOMAS_INDEXADOS]
    alt = "" if lang in IDIOMAS_INDEXADOS or "noindex" in html_ else NOINDEX
    if len(langs) > 1:
        alt = "".join(f'<link rel="alternate" hreflang="{i18n.HTML_LANG[l]}" href="{url_abs(l, nome)}">\n' for l in langs)
        if "pt" in langs:
            alt += f'<link rel="alternate" hreflang="x-default" href="{url_abs("pt", nome)}">\n'
    html_ = html_.replace("@@ALT@@\n", alt).replace("@@ALT@@", alt)
    canon = prefixo(lang) + ("" if nome == "index.html" else nome_idioma(lang, nome))
    html_ = html_.replace("{CANON}", canon)
    if lang != "pt":
        html_ = re.sub(r'(href|src)="(assets/|feed\.xml|manifest\.webmanifest)', r'\1="../\2', html_)
        html_ = re.sub(r'srcset="([^"]*)"', lambda mo: 'srcset="' + re.sub(r'(^|, )assets/', r'\1../assets/', mo.group(1)) + '"', html_)
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
    # um só arquivo de estilo nas páginas do site (aloha.css + antigo.css): uma requisição a menos antes de mostrar a página
    (SAIDA / "assets/css/site.css").write_text((RAIZ / "assets/css/aloha.css").read_text(encoding="utf-8") + "\n" + (RAIZ / "assets/css/antigo.css").read_text(encoding="utf-8"), encoding="utf-8")

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
            (SAIDA / prefixo(lang) / nome_idioma(lang, nome)).write_text(limpa_abs(resolver(conteudo, lang, nome, existe)), encoding="utf-8")
        ind = INDICES[lang]
        if lang != "pt":
            ind = localizar(ind, lang).replace('src=\\"assets/', 'src=\\"../assets/')
        (SAIDA / "assets/js" / ("indice.js" if lang == "pt" else f"indice-{lang}.js")).write_text(ind, encoding="utf-8")
        (SAIDA / "assets/js" / ("novidades.js" if lang == "pt" else f"novidades-{lang}.js")).write_text(localizar(NOVID[lang], lang), encoding="utf-8")
    arquivos = por_idioma["pt"]
    csp = CSP_ADS if ANUNCIOS_ATIVOS else CSP_BASE
    if ONESIGNAL_APP_ID:  # avisos push (OneSignal): libera só o necessário
        csp = csp.replace("script-src 'self'", "script-src 'self' https://cdn.onesignal.com https://onesignal.com https://api.onesignal.com", 1)
        csp = csp.replace("connect-src 'self'", "connect-src 'self' https://onesignal.com https://*.onesignal.com", 1)
        csp = csp.replace("frame-src ", "frame-src https://onesignal.com https://*.onesignal.com ", 1)
        (SAIDA / "OneSignalSDKWorker.js").write_text('importScripts("https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.sw.js");\n', encoding="utf-8")
    (SAIDA / "_headers").write_text(HEADERS.replace("{CSP}", csp), encoding="utf-8")
    # endereços de cada matéria em cada idioma, para o aviso push abrir a página no idioma do aparelho
    (SAIDA / "push-urls.json").write_text(limpa_abs(json.dumps(
        {m["slug"]: {l: url_abs(l, f"materia-{m['slug']}.html") for l in i18n.IDIOMAS_REAIS} for m in materias}, ensure_ascii=False)), encoding="utf-8")
    if ANUNCIOS_ATIVOS and ADSENSE_PUB:
        (SAIDA / "ads.txt").write_text(f"google.com, {ADSENSE_PUB}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (SAIDA / ".well-known").mkdir(exist_ok=True)
    (SAIDA / ".well-known/security.txt").write_text(
        "Contact: mailto:contato@alohanoticias.com\nExpires: 2027-11-01T00:00:00.000Z\nPreferred-Languages: pt, en\nCanonical: https://alohanoticias.com/.well-known/security.txt\n", encoding="utf-8")
    (SAIDA / "manifest.webmanifest").write_text(json.dumps({
        "name": "ALOHA NOTÍCIAS", "short_name": "ALOHA", "description": "Cinema, games, anime e tecnologia explicados com calma.",
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
        f"<title>{SITE}</title><link>https://alohanoticias.com/</link><description>Cinema, games, anime e tecnologia explicados com calma.</description>"
        '<language>pt-BR</language><atom:link href="https://alohanoticias.com/feed.xml" rel="self" type="application/rss+xml"/>'
        + limpa_abs(itens) + "</channel></rss>", encoding="utf-8")
    import agenda
    agenda.ajustar_rascunhos()  # todo rascunho com data de um horário livre (máx. 3 por dia)
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
    CONTAGENS_PAINEL.update(rascunhos=len(rascunhos), agendados=len(agendados), publicados=len(materias))
    (SAIDA / "admin/index.html").write_text(resolver(gerar_admin(rascunhos, agendados, materias), "pt", "admin/index.html", existe), encoding="utf-8")
    for chave, tit, led, itens, tipo, vazio in [
            ("rascunhos", "Rascunhos", "Leia como ficará no site e aprove, agende ou rejeite.", rascunhos, "rasc", "Nenhum rascunho esperando aprovação."),
            ("agendados", "Agendados", "Artigos aprovados que saem no horário marcado.", agendados, "agen", "Nada agendado no momento."),
            ("publicados", "Publicados", "Artigos que já estão no ar (abrem o site em outra aba).", sorted(materias, key=lambda d: d["data"], reverse=True), "pub", "Nada publicado ainda.")]:
        (SAIDA / f"admin/{chave}.html").write_text(resolver(gerar_lista_admin(chave, tit, led, itens, tipo, vazio), "pt", f"admin/{chave}.html", existe), encoding="utf-8")
    (SAIDA / "admin/metricas.html").write_text(resolver(gerar_metricas_admin(materias), "pt", "admin/metricas.html", existe), encoding="utf-8")
    (SAIDA / "admin/links.html").write_text(resolver(gerar_links_admin(materias), "pt", "admin/links.html", existe), encoding="utf-8")
    (SAIDA / "admin/parceiros.html").write_text(resolver(gerar_parceiros_admin(materias), "pt", "admin/parceiros.html", existe), encoding="utf-8")
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
        t2 = re.sub(r'(assets/(?:css|js)/[\w.-]+\.(?:css|js)|assets/img/capas/[\w.-]+\.jpg)"', _v, t)
        if t2 != t:
            pg.write_text(t2, encoding="utf-8")
    # Sitemap: só idiomas indexados, sem páginas "noindex", com a data da última mudança de cada matéria
    def _lastmod(n):
        if n.startswith("materia-"):
            m = next((x for x in MATERIAS_PT if url_materia(x) == n), None)
            if m:
                return (m.get("atualizado") or m["data"]) + ":00-03:00"
        if n == "index.html" and MATERIAS_PT:
            return max(x.get("atualizado") or x["data"] for x in MATERIAS_PT) + ":00-03:00"
        return ""
    sm = "".join(f"<url><loc>{url_abs(l, n)}</loc>" + (f"<lastmod>{_lastmod(n)}</lastmod>" if _lastmod(n) else "") + "</url>"
                 for l, arqs in por_idioma.items() if l in IDIOMAS_INDEXADOS
                 for n, conteudo in arqs.items() if n not in ("404.html", "busca.html") and 'name="robots" content="noindex' not in conteudo)
    (SAIDA / "sitemap.xml").write_text(limpa_abs('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + "</urlset>"), encoding="utf-8")
    (SAIDA / "688dca8a511dd5a078482e96f25fecb8.txt").write_text("688dca8a511dd5a078482e96f25fecb8", encoding="utf-8")  # chave IndexNow
    # /favicon.ico na raiz: o Google e alguns navegadores procuram o ícone aqui antes de ler as tags da página
    shutil.copyfile(RAIZ / "assets/img/favicon.ico", SAIDA / "favicon.ico")
    # Endereços antigos do visual anterior que ainda aparecem no Google
    (SAIDA / "_redirects").write_text("/noticias /anime.html 301\n/noticias.html /anime.html 301\n", encoding="utf-8")
    (SAIDA / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: https://alohanoticias.com/sitemap.xml\n")
    print(f"{len(arquivos)} páginas geradas em {SAIDA}")


if __name__ == "__main__":
    main()
