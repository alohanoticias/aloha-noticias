"""Aprova, agenda ou rejeita um rascunho.
Uso: python3 site/aprovar.py "Aprovar: slug"  |  "Aprovar: slug | 2026-11-06T08:00"  |  "Rejeitar: slug" """
import json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BRT = timezone(timedelta(hours=-3))
RAIZ = Path(__file__).resolve().parent.parent
titulo = sys.argv[1].strip()
m = re.fullmatch(r"(Aprovar|Rejeitar): ([a-z0-9-]{1,120})(?: \| (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}))?", titulo)
if not m:
    sys.exit("Título inválido")
acao, slug, quando = m.groups()
rasc = RAIZ / "rascunhos" / f"{slug}.json"
agen = RAIZ / "agendados" / f"{slug}.json"
agora = datetime.now(BRT).replace(tzinfo=None)

if acao == "Rejeitar":
    for a in (rasc, agen):
        if a.exists():
            a.unlink(); print(f"Rejeitado {slug}"); sys.exit(0)
    sys.exit("Nada encontrado para rejeitar")

if not rasc.exists():
    sys.exit(f"Rascunho não encontrado: {slug}")
mat = RAIZ / "site/conteudo/materias.json"
if any(a["slug"] == slug for a in json.loads(mat.read_text(encoding="utf-8"))):
    sys.exit("Slug já publicado")
d = json.loads(rasc.read_text(encoding="utf-8"))
if quando and datetime.fromisoformat(quando) > agora:
    d["data"] = quando
    agen.parent.mkdir(exist_ok=True)
    agen.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    rasc.unlink(); print(f"Agendado {slug} para {quando}")
else:
    d["data"] = agora.strftime("%Y-%m-%dT%H:%M")
    lista = json.loads(mat.read_text(encoding="utf-8")); lista.append(d)
    mat.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    rasc.unlink(); print(f"Publicado {slug}")
