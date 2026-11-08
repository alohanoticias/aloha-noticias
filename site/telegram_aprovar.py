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
limpar = sys.argv[1:] == ["limpar"]  # apaga todas as mensagens do canal de rascunho (o canal oficial não é tocado)
if not token or not canal or not (rascunho or descobrir):
    print("Aprovação pelo Telegram desligada."); sys.exit(0)


TIPOS = json.dumps(["callback_query", "my_chat_member", "channel_post"])  # sempre a mesma lista, para nenhum botão se perder


def api(metodo, dados):
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}", data=urllib.parse.urlencode(dados).encode())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b"{}")


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

if sys.argv[1:] == ["limpar"]:
    # apaga todas as prévias do canal de rascunho (o Telegram não deixa listar, então vai por número de mensagem)
    t = api("sendMessage", {"chat_id": rascunho, "text": "limpando…", "disable_notification": "true"})
    ultimo_id = t.get("result", {}).get("message_id", 0)
    ids = list(range(1, ultimo_id + 1))
    apagou = True
    for i in range(0, len(ids), 100):
        r = api("deleteMessages", {"chat_id": rascunho, "message_ids": json.dumps(ids[i:i + 100])})
        apagou = apagou and r.get("ok", False)
        if not r.get("ok"):
            print("Sem permissão para apagar:", r.get("description"))
    if not apagou:  # sem permissão de apagar: marca como descartadas
        for m in ids[:-1]:
            api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": m, "reply_markup": json.dumps(
                {"inline_keyboard": [[{"text": "❌ Descartado", "callback_data": "x"}]]})})
        api("deleteMessage", {"chat_id": rascunho, "message_id": ultimo_id})
    print("Rascunhos", "apagados" if apagou else "marcados como descartados", f"(até a mensagem {ultimo_id}).")
    sys.exit(0)

oficial = api("getChat", {"chat_id": canal}).get("result", {})
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
            if b["text"].startswith("🚨"):
                b["text"] = "🚨Clique para ver COMPLETO 🚨"
    if acao == "ok":
        # tira os botões antes de copiar, para o post oficial sair limpo
        api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"]})
        c = api("copyMessage", {"chat_id": canal, "from_chat_id": rascunho, "message_id": msg["message_id"],
                                **({"reply_markup": json.dumps({"inline_keyboard": links})} if links else {})})
        if c.get("ok"):
            mid = c["result"]["message_id"]
            un = oficial.get("username")
            link = f"https://t.me/{un}/{mid}" if un else f"https://t.me/c/{str(oficial.get('id', ''))[4:]}/{mid}"
            api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"],
                                           "reply_markup": json.dumps({"inline_keyboard": links + [[{"text": "✅ Postado no canal — ver", "url": link}]]})})
            api("answerCallbackQuery", {"callback_query_id": q["id"], "text": "Postado no canal!"})
            print("Aprovado:", msg["message_id"], "->", link)
        else:
            api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"], "reply_markup": json.dumps(
                {"inline_keyboard": links + [[{"text": "⚠️ Falhou — tocar para tentar de novo", "callback_data": "ok"}]]})})
            print("Falhou ao copiar:", c.get("description"))
    elif acao == "no":
        api("editMessageReplyMarkup", {"chat_id": rascunho, "message_id": msg["message_id"], "reply_markup": json.dumps(
            {"inline_keyboard": links + [[{"text": "❌ Descartado (tocar para aprovar mesmo assim)", "callback_data": "ok"}]]})})
        api("answerCallbackQuery", {"callback_query_id": q["id"], "text": "Descartado."})
        print("Descartado:", msg["message_id"])
    else:
        api("answerCallbackQuery", {"callback_query_id": q["id"]})
if ultimo is not None:
    api("getUpdates", {"offset": ultimo + 1, "timeout": 0})  # confirma o que já foi tratado
print("Botões tratados." if ultimo is not None else "Nenhum botão tocado.")
