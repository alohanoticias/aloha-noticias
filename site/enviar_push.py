"""Envia aviso push (OneSignal) das matérias que acabaram de ser publicadas, uma mensagem por idioma:
cada pessoa recebe no idioma do aparelho e, ao tocar, abre a matéria nesse mesmo idioma.
Lê os slugs de publicados.txt (gravado por publicar_agendados.py) e os endereços de publico/push-urls.json.
Precisa de site/conteudo/push.json (App ID) e do segredo ONESIGNAL_REST_API_KEY. Sem isso, não faz nada."""
import json, os, sys, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
app = json.loads((RAIZ / "site/conteudo/push.json").read_text(encoding="utf-8")).get("onesignal_app_id", "").strip()
chave = os.environ.get("ONESIGNAL_REST_API_KEY", "").strip()
lista = RAIZ / "publicados.txt"
if not app or not chave or not lista.exists():
    print("Push desligado ou nada a enviar."); sys.exit(0)
mats = {m["slug"]: m for m in json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8"))}
urls = json.loads((RAIZ / "publico/push-urls.json").read_text(encoding="utf-8"))
OS = {"pt": "pt", "en": "en", "es": "es", "fr": "fr", "de": "de", "it": "it", "ja": "ja", "zh": "zh-Hans", "ar": "ar"}


def enviar(corpo):
    req = urllib.request.Request("https://api.onesignal.com/notifications", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Key " + chave}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode()[:120]
    except Exception as e:
        return f"FALHOU: {e}"


for slug in lista.read_text().split():
    m = mats.get(slug)
    if not m:
        continue
    img = (m.get("imagem") or {}).get("url", "")
    if img and not img.startswith("http"):
        img = "https://alohanoticias.com/" + img
    for l, cod in OS.items():
        tr = m if l == "pt" else (m.get("traducoes") or {}).get(l)
        if not tr:
            continue
        corpo = {"app_id": app, "target_channel": "push", "headings": {"en": tr["titulo"]}, "contents": {"en": tr["linha_fina"]},
                 "url": urls[slug][l], "filters": [{"field": "language", "relation": "=", "value": cod}]}
        if img:
            corpo["chrome_web_image"] = img
        print(slug, l, enviar(corpo))
    # idiomas que o site não tem (ex.: coreano): recebem em inglês
    en = (m.get("traducoes") or {}).get("en") or m
    filtros = [{"field": "language", "relation": "!=", "value": c} for c in OS.values()]
    corpo = {"app_id": app, "target_channel": "push", "headings": {"en": en["titulo"]}, "contents": {"en": en["linha_fina"]},
             "url": urls[slug].get("en", urls[slug]["pt"]), "filters": filtros}
    if img:
        corpo["chrome_web_image"] = img
    print(slug, "outros", enviar(corpo))
lista.unlink()
