"""Publica os artigos agendados cuja hora chegou (horário de Brasília)."""
import hashlib, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
agora = datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None)
mat = RAIZ / "site/conteudo/materias.json"
lista = json.loads(mat.read_text(encoding="utf-8"))
mudou = False
for f in sorted((RAIZ / "agendados").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    # Horário "quebrado": cada artigo espera um atraso fixo de 1 a 24 minutos depois da hora marcada
    # (calculado a partir do endereço do artigo) e sai com a hora real da publicação, sem minutos redondos.
    atraso = timedelta(minutes=1 + int(hashlib.md5(d["slug"].encode()).hexdigest(), 16) % 24)
    if datetime.fromisoformat(d["data"]) + atraso <= agora and not any(a["slug"] == d["slug"] for a in lista):
        d["data"] = agora.strftime("%Y-%m-%dT%H:%M")
        lista.append(d); f.unlink(); mudou = True; print("Publicado:", d["slug"])
if mudou:
    mat.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
