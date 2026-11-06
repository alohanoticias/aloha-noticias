"""Aprova, agenda ou rejeita um rascunho.
Uso: python3 site/aprovar.py "Aprovar: slug"  |  "Aprovar: slug | 2026-11-06T08:00"  |  "Reagendar: slug | 2026-11-07T09:00"  |  "Rejeitar: slug" """
import hashlib, json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BRT = timezone(timedelta(hours=-3))
RAIZ = Path(__file__).resolve().parent.parent
titulo = sys.argv[1].strip()
m = re.fullmatch(r"(Aprovar|Reagendar|Rejeitar): ([a-z0-9-]{1,120})(?: \| (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}))?", titulo)
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

origem = rasc if rasc.exists() else (agen if agen.exists() else None)
if origem is None:
    sys.exit(f"Rascunho não encontrado: {slug}")
mat = RAIZ / "site/conteudo/materias.json"
lista = json.loads(mat.read_text(encoding="utf-8"))
if any(a["slug"] == slug for a in lista):
    sys.exit("Slug já publicado")
d = json.loads(origem.read_text(encoding="utf-8"))
if acao == "Reagendar" and not quando:
    sys.exit("Reagendar exige data")
def quebrar(iso, slug):
    """Horário "quebrado": se o minuto for redondo (múltiplo de 5), soma de 1 a 24 minutos (fixo para cada artigo), sem cair em outro múltiplo de 5."""
    t = datetime.fromisoformat(iso)
    if t.minute % 5:
        return iso
    off = 1 + int(hashlib.md5(slug.encode()).hexdigest(), 16) % 24
    while (t.minute + off) % 5 == 0:
        off += 1
    return (t + timedelta(minutes=off)).strftime("%Y-%m-%dT%H:%M")


if quando and datetime.fromisoformat(quando) > agora:
    quando = quebrar(quando, slug)
    d["data"] = quando
    agen.parent.mkdir(exist_ok=True)
    agen.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    if origem != agen:
        origem.unlink()
    print(f"Agendado {slug} para {quando}")
else:
    d["data"] = agora.strftime("%Y-%m-%dT%H:%M")
    lista.append(d)
    mat.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
    origem.unlink(); print(f"Publicado {slug}")
