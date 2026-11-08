"""Posta no canal do Telegram as matérias que acabaram de ser publicadas (em português).
Uso: python3 site/enviar_telegram.py               -> lê os slugs de publicados.txt
     python3 site/enviar_telegram.py slug1 slug2   -> posta essas matérias (ex.: as que já estavam no ar)
Precisa dos segredos TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (@ do canal ou ID numérico). Sem eles, não faz nada.
Não apaga publicados.txt (o enviar_push.py usa o mesmo arquivo depois)."""
import html, json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
token = "".join(os.environ.get("TELEGRAM_BOT_TOKEN", "").split()).strip("'\"")  # tira espaços/aspas coladas por engano
if token.lower().startswith("bot"):
    token = token[3:]
canal = "".join(os.environ.get("TELEGRAM_CHAT_ID", "").split()).strip("'\"")
if canal and not canal.startswith("@") and not canal.lstrip("-").isdigit():
    canal = "@" + canal.split("/")[-1]  # aceita "alohanoticias" ou "t.me/alohanoticias"
if not token or not canal:
    print("Telegram desligado (faltam TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID)."); sys.exit(0)

slugs = sys.argv[1:]
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
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


def hashtag(nome):
    return "#" + "".join(p for p in nome.replace("&", " ").split() if p.isalnum())


falhas = 0
for i, slug in enumerate(slugs):
    m = mats.get(slug)
    if not m:
        print("Não achei a matéria:", slug); falhas += 1; continue
    link = (urls.get(slug) or {}).get("pt") or f"https://alohanoticias.com/materia-{slug}.html"
    titulo = html.escape(m["titulo"])
    resumo = html.escape(m.get("linha_fina", "").strip())
    tag = hashtag(eds.get(m.get("editoria", ""), "")) if m.get("editoria") else ""
    rodape = f'\n\n👉 <a href="{link}">Leia no Aloha Notícias</a>' + (f"\n\n{tag}" if len(tag) > 1 else "")
    texto = f"<b>{titulo}</b>\n\n{resumo}"
    if len(texto) + len(rodape) > 1000:  # legenda de foto tem limite de 1024 caracteres
        texto = texto[:1000 - len(rodape) - 1].rsplit(" ", 1)[0] + "…"
    texto += rodape
    img = (m.get("imagem") or {}).get("url", "")
    if img and not img.startswith("http"):
        img = "https://alohanoticias.com/" + img.lstrip("/")
    r = {}
    if img:
        r = api("sendPhoto", {"chat_id": canal, "photo": img, "caption": texto, "parse_mode": "HTML"})
    if not r.get("ok"):
        if img:
            print("Foto não foi aceita, mandando com prévia do link:", r.get("description"))
        r = api("sendMessage", {"chat_id": canal, "text": texto, "parse_mode": "HTML"})
    print(slug, "->", "ok" if r.get("ok") else r.get("description"))
    falhas += 0 if r.get("ok") else 1
    if i < len(slugs) - 1:
        time.sleep(3)
sys.exit(1 if falhas else 0)
