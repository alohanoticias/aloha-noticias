"""Confere as fotos do Unsplash usadas nos artigos e nas capas.
  python3 site/checar_fotos.py          -> só o formato (offline, usado pelo gerar.py)
  python3 site/checar_fotos.py --rede   -> também abre cada endereço e confere que a imagem carrega (roda no GitHub)
Erro típico que isto evita: endereço sem o código final, como photo-1751823886813 (o certo é photo-1751823886813-0cfc86cb9478)."""
import glob, json, re, sys, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS = ["site/conteudo/materias.json"] + sorted(glob.glob(str(RAIZ / "rascunhos/*.json"))) + \
    sorted(glob.glob(str(RAIZ / "agendados/*.json"))) + sorted(glob.glob(str(RAIZ / "site/capas_fotos/*.json")))
FOTO = re.compile(r"https://images\.unsplash\.com/photo-[0-9a-z-]+")
CERTO = re.compile(r"^https://images\.unsplash\.com/photo-\d{10,}-[0-9a-f]{12}$")


def enderecos():
    achados = {}
    for f in ARQUIVOS:
        p = Path(f) if Path(f).is_absolute() else RAIZ / f
        if p.exists():
            for u in FOTO.findall(p.read_text(encoding="utf-8")):
                achados.setdefault(u, []).append(p.name)
    return achados


def poucas_fotos():
    """Regra fixa: todo artigo tem pelo menos 2 fotos dentro do texto (linhas !img), em português e em todas as traduções."""
    ruins = []
    for f in ["site/conteudo/materias.json"] + sorted(glob.glob(str(RAIZ / "rascunhos/*.json"))) + sorted(glob.glob(str(RAIZ / "agendados/*.json"))):
        p = Path(f) if Path(f).is_absolute() else RAIZ / f
        if not p.exists():
            continue
        dados = json.loads(p.read_text(encoding="utf-8"))
        for m in (dados if isinstance(dados, list) else [dados]):
            conta = lambda corpo: sum(1 for b in corpo if b.startswith("!img "))
            n = conta(m.get("corpo", []))
            if n < 2:
                ruins.append(f"{m.get('slug')}: só {n} foto(s) no texto (mínimo 2)")
            for lg, t in (m.get("traducoes") or {}).items():
                if conta(t.get("corpo", [])) != n:
                    ruins.append(f"{m.get('slug')}: tradução {lg} tem {conta(t.get('corpo', []))} fotos e o português tem {n}")
    return ruins


def main(rede=False):
    ruins = poucas_fotos()
    ach = enderecos()
    for u, onde in ach.items():
        if not CERTO.match(u):
            ruins.append(f"endereço incompleto (falta o código final): {u} em {sorted(set(onde))}")
    if rede and not ruins:
        for u, onde in ach.items():
            try:
                req = urllib.request.Request(u + "?fm=jpg&q=40&w=200", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    if not r.headers.get("Content-Type", "").startswith("image/"):
                        ruins.append(f"não é imagem: {u} em {sorted(set(onde))}")
            except Exception as e:
                ruins.append(f"não carrega ({e}): {u} em {sorted(set(onde))}")
    for r in ruins:
        print("FOTO COM PROBLEMA:", r, file=sys.stderr)
    print(f"{len(ach)} fotos conferidas, {len(ruins)} com problema")
    return not ruins


if __name__ == "__main__":
    sys.exit(0 if main("--rede" in sys.argv) else 1)
