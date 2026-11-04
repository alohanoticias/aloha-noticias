"""Publica os artigos agendados cuja hora chegou (horário de Brasília)."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
agora = datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None)
mat = RAIZ / "site/conteudo/materias.json"
lista = json.loads(mat.read_text(encoding="utf-8"))
mudou = False
for f in sorted((RAIZ / "agendados").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    if datetime.fromisoformat(d["data"]) <= agora and not any(a["slug"] == d["slug"] for a in lista):
        lista.append(d); f.unlink(); mudou = True; print("Publicado:", d["slug"])
if mudou:
    mat.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
