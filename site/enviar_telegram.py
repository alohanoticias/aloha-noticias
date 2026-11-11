"""Posta no canal do Telegram as matérias que acabaram de ser publicadas (em português).
Uso: python3 site/enviar_telegram.py               -> lê os slugs de publicados.txt
     python3 site/enviar_telegram.py slug1 slug2   -> posta essas matérias (ex.: as que já estavam no ar)
Precisa dos segredos TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (@ do canal ou ID numérico). Sem eles, não faz nada.
Se site/conteudo/telegram.json tiver "rascunho_id", o post vai primeiro para o canal privado de rascunho,
com botões Aprovar/Descartar (quem trata os botões é site/telegram_aprovar.py).
Não apaga publicados.txt (o enviar_push.py usa o mesmo arquivo depois)."""
import html, json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UTM = "?utm_source=telegram&utm_medium=social&utm_campaign=canal_aloha"
token = "".join(os.environ.get("TELEGRAM_BOT_TOKEN", "").split()).strip("'\"")  # tira espaços/aspas coladas por engano
if token.lower().startswith("bot"):
    token = token[3:]
canal = "".join(os.environ.get("TELEGRAM_CHAT_ID", "").split()).strip("'\"")
if canal and not canal.startswith("@") and not canal.lstrip("-").isdigit():
    canal = "@" + canal.split("/")[-1]  # aceita "alohanoticias" ou "t.me/alohanoticias"
if not token or not canal:
    print("Telegram desligado (faltam TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID)."); sys.exit(0)

try:
    rascunho = str(json.loads((RAIZ / "site/conteudo/telegram.json").read_text(encoding="utf-8")).get("rascunho_id", "")).strip()
except FileNotFoundError:
    rascunho = ""
destino = rascunho or canal
AUTOMATICO = True  # posta no canal oficial na hora, junto com a cópia no rascunho (sem esperar botão)
APROVAR = [{"text": "✅ Aprovar", "callback_data": "ok"}, {"text": "❌ Descartar", "callback_data": "no"}]
print("Destino:", "rascunho + canal oficial" if rascunho else "canal oficial")

slugs = sys.argv[1:]
previa_oficial = "--como-oficial" in slugs  # manda no rascunho exatamente como sairia no canal oficial, sem botões de aprovação
slugs = [x for x in slugs if x != "--como-oficial"]
if not slugs:
    arq = RAIZ / "publicados.txt"
    slugs = arq.read_text(encoding="utf-8").split() if arq.exists() else []
if not slugs:
    print("Nada a postar."); sys.exit(0)

mats = {m["slug"]: m for m in json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8"))}
eds = {e["slug"]: e["nome"] for e in json.loads((RAIZ / "site/conteudo/editorias.json").read_text(encoding="utf-8"))}
try:
    urls = json.loads((RAIZ / "publico/push-urls.json").read_text(encoding="utf-8"))
except FileNotFoundError:
    urls = {}


def api(metodo, dados):
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}",
                                 data=urllib.parse.urlencode(dados).encode())
    for tentativa in range(4):  # a conexão com o Telegram às vezes cai: tenta de novo
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read() or b"{}")
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            print("Conexão falhou, tentando de novo:", e)
            time.sleep(5 * (tentativa + 1))
    return {}


def hashtag(nome):
    return "#" + "".join(p for p in nome.replace("&", " ").split() if p.isalnum())


falhas = 0
for i, slug in enumerate(slugs):
    m = mats.get(slug)
    if not m:
        print("Não achei a matéria:", slug); falhas += 1; continue
    link = (urls.get(slug) or {}).get("pt") or f"https://alohanoticias.com/materia-{slug}.html"
    if link.endswith(".html"):
        link = link[:-5]  # endereço final: a Cloudflare redireciona ".html" e o salto pode perder a etiqueta
    link += UTM  # etiqueta para medir os cliques vindos do Telegram
    titulo = html.escape(m["titulo"])
    resumo = html.escape(m.get("linha_fina", "").strip())
    rodape = "\n\nA matéria está completa em nosso site <b>Aloha Notícias</b>."  # o link vai no botão (sem hashtag)
    texto = f"<b>{titulo}</b>\n\n{resumo}"
    if len(texto) + len(rodape) > 1000:  # legenda de foto tem limite de 1024 caracteres
        texto = texto[:999 - len(rodape)].rsplit(" ", 1)[0] + "…"
    texto += rodape
    img = (m.get("imagem") or {}).get("url", "")
    if img and not img.startswith("http"):
        local = RAIZ / "site" / img.lstrip("/")
        img = "https://alohanoticias.com/" + img.lstrip("/")
        if local.exists():  # versão no link: o Telegram baixa a capa atual, não uma antiga guardada
            import hashlib
            img += "?v=" + hashlib.md5(local.read_bytes()).hexdigest()[:8]
    r = {}
    teclado = [[{"text": "👉🏻 Clique para ver COMPLETO 🚨", "url": link}]]
    extra = {"reply_markup": json.dumps({"inline_keyboard": teclado})}
    alvos = [canal] if not rascunho else ([rascunho] if previa_oficial else [rascunho, canal] if AUTOMATICO else [rascunho])
    for alvo in alvos:
        r = {}
        if img:
            r = api("sendPhoto", {"chat_id": alvo, "photo": img, "caption": texto, "parse_mode": "HTML", **extra})
        if not r.get("ok"):
            if img:
                print("Foto não foi aceita, mandando com prévia do link:", r.get("description"))
            r = api("sendMessage", {"chat_id": alvo, "text": texto, "parse_mode": "HTML", **extra})
        print("  mensagem", (r.get("result") or {}).get("message_id"), "em", "rascunho" if alvo == rascunho else "canal oficial")
        if len(alvos) > 1 and alvo != alvos[-1]:
            time.sleep(1)
    print(slug, "->", "ok" if r.get("ok") else r.get("description"))
    falhas += 0 if r.get("ok") else 1
    if i < len(slugs) - 1:
        time.sleep(3)
sys.exit(1 if falhas else 0)
