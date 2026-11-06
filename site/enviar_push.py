"""Envia aviso push (OneSignal) das matérias que acabaram de ser publicadas.
Lê os slugs de publicados.txt (gravado por publicar_agendados.py). Precisa de site/conteudo/push.json com o App ID
e do segredo ONESIGNAL_REST_API_KEY. Sem isso, não faz nada."""
import json, os, sys, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
app = json.loads((RAIZ / "site/conteudo/push.json").read_text(encoding="utf-8")).get("onesignal_app_id", "").strip()
chave = os.environ.get("ONESIGNAL_REST_API_KEY", "").strip()
lista = RAIZ / "publicados.txt"
if not app or not chave or not lista.exists():
    print("Push desligado ou nada a enviar."); sys.exit(0)
mats = {m["slug"]: m for m in json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8"))}
CODIGOS = {"en": "en", "es": "es", "fr": "fr", "de": "de", "it": "it", "ja": "ja", "zh": "zh-Hans", "ar": "ar"}
for slug in lista.read_text().split():
    m = mats.get(slug)
    if not m:
        continue
    titulos = {"pt": m["titulo"]}; textos = {"pt": m["linha_fina"]}
    for l, c in CODIGOS.items():
        tr = (m.get("traducoes") or {}).get(l)
        if tr:
            titulos[c] = tr["titulo"]; textos[c] = tr["linha_fina"]
    titulos["en"] = titulos.get("en", titulos["pt"]); textos["en"] = textos.get("en", textos["pt"])
    corpo = {"app_id": app, "included_segments": ["Subscribed Users"], "headings": titulos, "contents": textos,
             "url": f"https://alohanoticias.com/materia-{slug}.html", "target_channel": "push"}
    img = (m.get("imagem") or {}).get("url", "")
    if img:
        corpo["big_picture"] = img if img.startswith("http") else "https://alohanoticias.com/" + img
        corpo["chrome_web_image"] = corpo["big_picture"]
    req = urllib.request.Request("https://api.onesignal.com/notifications", data=json.dumps(corpo).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Key " + chave}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print("Push enviado:", slug, r.read().decode()[:200])
    except Exception as e:
        print("Push FALHOU:", slug, e)
lista.unlink()
