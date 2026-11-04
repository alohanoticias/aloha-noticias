"""Confere os links externos dos artigos publicados. Escreve o relatório em stdout (vazio se tudo certo)."""
import json, re, sys, urllib.request, urllib.error
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (compatible; AlohaLinkCheck/1.0; +https://alohanoticias.com)"}
IGNORAR = {401, 403, 405, 406, 429, 451, 999}  # site recusa robô: não prova que o link quebrou


def links(m):
    urls = set()
    for p in m.get("corpo", []):
        urls |= set(re.findall(r"\]\((https?://[^)\s]+)\)", p))
        if p.startswith("!img ") and p[5:].startswith("http"):
            urls.add(p[5:].split("|")[0].strip())
    if m.get("imagem", {}).get("url", "").startswith("http"):
        urls.add(m["imagem"]["url"])
    return urls


def status(url):
    s = _status(url)
    return _status(url) if isinstance(s, str) else s  # tenta de novo se foi erro de conexão


def _status(url):
    for metodo in ("HEAD", "GET"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, method=metodo, headers=UA), timeout=20)
            return r.status
        except urllib.error.HTTPError as e:
            if metodo == "HEAD" and e.code in (400, 403, 404, 405, 501):
                continue
            return e.code
        except Exception as e:
            if metodo == "GET":
                return f"erro: {type(e).__name__}"
    return "erro"


quebrados = []
for m in json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8")):
    for u in sorted(links(m)):
        s = status(u)
        if s == 200 or (isinstance(s, int) and (s in IGNORAR or 200 <= s < 400)):
            continue
        quebrados.append(f"- `{m['slug']}`: {u} → {s}")
if quebrados:
    print("Estes links de artigos não responderam como esperado. Abra cada um e troque ou remova se realmente saiu do ar:\n")
    print("\n".join(quebrados))
