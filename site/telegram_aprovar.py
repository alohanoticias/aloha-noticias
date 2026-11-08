"""Trata os botões do canal de rascunho do Telegram.
✅ Aprovar  -> copia o post para o canal oficial e troca o botão por um link para o post publicado.
❌ Descartar -> só marca a prévia como descartada.
Uso: python3 site/telegram_aprovar.py            -> processa os botões tocados
     python3 site/telegram_aprovar.py descobrir  -> lista os canais onde o bot está (para achar o ID do rascunho)
Roda junto com a publicação dos agendados (a cada ~10 min). Precisa de TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID."""
import json, os, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
token = "".join(os.environ.get("TELEGRAM_BOT_TOKEN", "").split()).strip("'\"")
if token.lower().startswith("bot"):
    token = token[3:]
canal = "".join(os.environ.get("TELEGRAM_CHAT_ID", "").split()).strip("'\"")
if canal and not canal.startswith("@") and not canal.lstrip("-").isdigit():
    canal = "@" + canal.split("/")[-1]
try:
    rascunho = str(json.loads((RAIZ / "site/conteudo/telegram.json").read_text(encoding="utf-8")).get("rascunho_id", "")).strip()
except FileNotFoundError:
    rascunho = ""
descobrir = sys.argv[1:] == ["descobrir"]
limpar = sys.argv[1:2] == ["limpar"]  # "limpar 83" apaga só até a mensagem 83  # apaga todas as mensagens do canal de rascunho (o canal oficial não é tocado)
if not token or not canal or not (rascunho or descobrir):
    print("Aprovação pelo Telegram desligada."); sys.exit(0)


TIPOS = json.dumps(["callback_query", "my_chat_member", "channel_post"])  # sempre a mesma lista, para nenhum botão se perder


def api(metodo, dados):
    import time
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}", data=urllib.parse.urlencode(dados).encode())
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


if descobrir:
    # não confirma as atualizações: os botões tocados continuam na fila
    r = api("getUpdates", {"allowed_updates": TIPOS})
    vistos = {}
    for u in r.get("result", []):
        c = (u.get("my_chat_member") or u.get("channel_post") or {}).get("chat") or {}
        if c.get("id"):
            vistos[c["id"]] = (c.get("title"), c.get("username"), c.get("type"))
    for i, (t, un, tp) in vistos.items():
        print(f"ID {i} | {t} | @{un or '-'} | {tp}")
    if not vistos:
        print("Nenhum canal visto. Mande uma mensagem qualquer no canal de rascunho e rode de novo.")
    sys.exit(0)

if limpar:
    if len(sys.argv) > 2:
        ate = int(sys.argv[2])
    else:
        marca = api("sendMessage", {"chat_id": rascunho, "text": "Limpando…"})
        ate = marca.get("result", {}).get("message_id", 0)
    apagadas = 0
    for ini in range(1, ate + 1, 100):
        ids = list(range(ini, min(ini + 100, ate + 1)))
        r = api("deleteMessages", {"chat_id": rascunho, "message_ids": json.dumps(ids)})
        apagadas += len(ids) if r.get("ok") else 0
        if not r.get("ok"):  # alguma não pode ser apagada (ex.: aviso de criação do canal): vai uma por uma
            for i in ids:
                apagadas += 1 if api("deleteMessage", {"chat_id": rascunho, "message_id": i}).get("ok") else 0
    print(f"Canal de rascunho limpo: {apagadas} mensagens apagadas.")
    sys.exit(0)

FILA = RAIZ / "site/conteudo/telegram_fila.json"
BOTAO = "👉🏻 Clique para ver COMPLETO 🚨"
UTM = "?utm_source=telegram&utm_medium=social&utm_campaign=canal_aloha"  # etiqueta para medir os cliques vindos do Telegram


def com_utm(url):
    return url if "utm_source=" in url else url.split("?")[0] + UTM
import datetime as _dt
agora = _dt.datetime.now(_dt.timezone.utc)


def ler_fila():
    try:
        return json.loads(FILA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"itens": [], "intervalo_min": 30, "proximo": ""}


def gravar_fila(f):
    FILA.write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")


if sys.argv[1:2] == ["fila"]:
    # põe na fila as últimas N prévias do rascunho (as N matérias mais recentes, na ordem em que foram enviadas)
    mats = sorted(json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8")), key=lambda m: m["data"])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else len(mats)
    intervalo = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    marca = api("sendMessage", {"chat_id": rascunho, "text": "…", "disable_notification": "true"})
    m_id = marca.get("result", {}).get("message_id", 0)
    api("deleteMessage", {"chat_id": rascunho, "message_id": m_id})
    ids = list(range(m_id - n, m_id))
    itens = [{"msg": i, "slug": m["slug"]} for i, m in zip(ids, mats[-n:])]
    inicio = sys.argv[4] if len(sys.argv) > 4 else agora.isoformat(timespec="seconds")
    gravar_fila({"itens": itens, "intervalo_min": intervalo, "proximo": inicio})
    for it in itens:
        print("Na fila:", it["msg"], it["slug"][:60])
    sys.exit(0)

if sys.argv[1:2] == ["corrigir-botao"]:
    # atualiza o texto do botão num post que já está no canal oficial: corrigir-botao <id_no_canal> <slug>
    mid, slug = sys.argv[2], sys.argv[3]
    urls = json.loads((RAIZ / "publico/push-urls.json").read_text(encoding="utf-8"))
    url = (urls.get(slug) or {}).get("pt") or f"https://alohanoticias.com/materia-{slug}.html"
    r = api("editMessageReplyMarkup", {"chat_id": canal, "message_id": mid,
                                       "reply_markup": json.dumps({"inline_keyboard": [[{"text": BOTAO, "url": com_utm(url)}]]})})
    print("Botão corrigido:" if r.get("ok") else "Falhou:", mid, r.get("description", ""))
    sys.exit(0)

oficial = api("getChat", {"chat_id": canal}).get("result", {})


def postar(mid, links):
    """Copia a prévia para o canal oficial e marca a prévia como postada. Devolve o link ou None."""
    api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": mid})
    c = api("copyMessage", {"chat_id": canal, "from_chat_id": rascunho, "message_id": mid,
                            **({"reply_markup": json.dumps({"inline_keyboard": links})} if links else {})})
    if not c.get("ok"):
        print("Falhou ao copiar:", mid, c.get("description"))
        return None
    novo = c["result"]["message_id"]
    un = oficial.get("username")
    link = f"https://t.me/{un}/{novo}" if un else f"https://t.me/c/{str(oficial.get('id', ''))[4:]}/{novo}"
    api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": mid,
                                   "reply_markup": json.dumps({"inline_keyboard": links + [[{"text": "✅ Postado no canal — ver", "url": link}]]})})
    return link


fila = ler_fila()
tratados = set()
r = api("getUpdates", {"allowed_updates": TIPOS, "timeout": 0})
ultimo = None
for u in r.get("result", []):
    ultimo = u["update_id"]
    q = u.get("callback_query")
    if not q or not q.get("message"):
        continue
    msg = q["message"]
    if str(msg["chat"]["id"]) != rascunho:
        api("answerCallbackQuery", {"callback_query_id": q["id"]}); continue
    acao = q.get("data")
    # botões de link da prévia (ex.: "Leia no Aloha Notícias") vão junto para o post oficial
    links = [[b for b in linha if b.get("url")] for linha in (msg.get("reply_markup") or {}).get("inline_keyboard", [])]
    links = [l for l in links if l and not l[0]["text"].startswith("✅ Postado")]
    for linha in links:  # usa sempre o texto atual do botão, mesmo em prévias antigas
        for b in linha:
            if "COMPLETO" in b["text"] or b["text"].startswith("🚨"):
                b["text"] = BOTAO
                b["url"] = com_utm(b["url"])
    if acao == "ok":
        link = postar(msg["message_id"], links)
        tratados.add(msg["message_id"])
        if link:
            api("answerCallbackQuery", {"callback_query_id": q["id"], "text": "Postado no canal!"})
            print("Aprovado:", msg["message_id"], "->", link)
        else:
            api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"], "reply_markup": json.dumps(
                {"inline_keyboard": links + [[{"text": "⚠️ Falhou — tocar para tentar de novo", "callback_data": "ok"}]]})})
    elif acao == "no":
        api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"], "reply_markup": json.dumps(
            {"inline_keyboard": links + [[{"text": "❌ Descartado (tocar para aprovar mesmo assim)", "callback_data": "ok"}]]})})
        api("answerCallbackQuery", {"callback_query_id": q["id"], "text": "Descartado."})
        tratados.add(msg["message_id"])
        print("Descartado:", msg["message_id"])
    else:
        api("answerCallbackQuery", {"callback_query_id": q["id"]})
if ultimo is not None:
    api("getUpdates", {"offset": ultimo + 1, "timeout": 0})  # confirma o que já foi tratado
print("Botões tratados." if ultimo is not None else "Nenhum botão tocado.")

# fila: solta uma prévia por vez no canal oficial, no intervalo combinado
if fila["itens"]:
    antes = len(fila["itens"])
    fila["itens"] = [it for it in fila["itens"] if it["msg"] not in tratados]  # aprovadas/descartadas à mão saem da fila
    hora = _dt.datetime.fromisoformat(fila["proximo"]) if fila.get("proximo") else agora
    if agora >= hora - _dt.timedelta(minutes=2):
        it = fila["itens"].pop(0)
        try:
            urls = json.loads((RAIZ / "publico/push-urls.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            urls = {}
        url = (urls.get(it["slug"]) or {}).get("pt") or f"https://alohanoticias.com/materia-{it['slug']}.html"
        link = postar(it["msg"], [[{"text": BOTAO, "url": com_utm(url)}]])
        print("Fila: postado", it["slug"][:60], "->", link)
        fila["proximo"] = (agora + _dt.timedelta(minutes=fila.get("intervalo_min", 30))).isoformat(timespec="seconds")
    if fila["itens"] or antes:
        print(f"Fila: faltam {len(fila['itens'])}; próximo às {fila.get('proximo')}")
        gravar_fila(fila)
