"""Aprova ou rejeita um rascunho. Uso: python3 site/aprovar.py "Aprovar: slug" """
import json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
titulo = sys.argv[1].strip()
m = re.fullmatch(r"(Aprovar|Rejeitar): ([a-z0-9-]{1,120})", titulo)
if not m:
    sys.exit("Título inválido")
acao, slug = m.groups()
arq = RAIZ / "rascunhos" / f"{slug}.json"
if not arq.exists():
    sys.exit(f"Rascunho não encontrado: {slug}")
if acao == "Aprovar":
    mat = RAIZ / "site/conteudo/materias.json"
    lista = json.loads(mat.read_text(encoding="utf-8"))
    if any(a["slug"] == slug for a in lista):
        sys.exit("Slug já publicado")
    d = json.loads(arq.read_text(encoding="utf-8"))
    d["data"] = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%dT%H:%M")
    lista.append(d)
    mat.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding="utf-8")
arq.unlink()
print(f"{acao} {slug}: ok")
