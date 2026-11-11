"""Agenda de publicação: no máximo 3 artigos por dia, um em cada janela (9h–11h, 13h–15h, 18h–20h, Brasília),
em minutos quebrados.

- proximo_livre(): o próximo horário livre, contando publicados, agendados e rascunhos.
- ajustar_rascunhos(): todo rascunho fica com a data de um horário livre. Se a data dele já passou,
  cai fora das janelas, cai num dia que já tem 3 artigos ou numa janela já ocupada, muda para o
  próximo horário livre. Roda sozinho no gerar.py.
- ocupacao(): artigos por dia (publicados + agendados), usada pelo aviso do admin.

Uso: python3 site/agenda.py              (mostra os próximos horários livres)
     python3 site/agenda.py ajustar      (ajusta as datas dos rascunhos)
"""
import hashlib, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BRT = timezone(timedelta(hours=-3))
RAIZ = Path(__file__).resolve().parent.parent
JANELAS = [(9, 11), (13, 15), (18, 20)]  # início inclusive, fim exclusivo
POR_DIA = 3
FOLGA = timedelta(minutes=30)  # rascunho novo não sai a menos de 30 min de agora


def agora():
    return datetime.now(BRT).replace(tzinfo=None)


def _ler(pasta):
    out = []
    for f in sorted((RAIZ / pasta).glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("data"):
            out.append((f, d))
    return out


def _publicados():
    try:
        return json.loads((RAIZ / "site/conteudo/materias.json").read_text(encoding="utf-8"))
    except Exception:
        return []


def janela(dt):
    for i, (a, b) in enumerate(JANELAS):
        if a <= dt.hour < b:
            return i
    return None


def ocupacao(excluir=None, incluir_rascunhos=False):
    """{'2026-11-17': [(datetime, slug), ...]} com publicados e agendados (e rascunhos, se pedido)."""
    itens = [(d["data"], d["slug"]) for d in _publicados()]
    itens += [(d["data"], d["slug"]) for _, d in _ler("agendados")]
    if incluir_rascunhos:
        itens += [(d["data"], d["slug"]) for _, d in _ler("rascunhos")]
    dias = {}
    for data, slug in itens:
        if slug == excluir:
            continue
        try:
            t = datetime.fromisoformat(str(data)[:16])
        except ValueError:
            continue
        dias.setdefault(t.strftime("%Y-%m-%d"), []).append((t, slug))
    return dias


def minuto_quebrado(slug, dia, j):
    """Minuto fixo para o artigo, dentro da janela, nunca múltiplo de 5."""
    a, b = JANELAS[j]
    total = (b - a) * 60
    n = int(hashlib.md5(f"{slug}|{dia}|{j}".encode()).hexdigest(), 16)
    m = 7 + n % (total - 20)
    while m % 5 == 0:
        m += 1
    return datetime.fromisoformat(dia) + timedelta(hours=a, minutes=m)


def _livre(dias, dt):
    """O horário dt cabe? (dia com menos de 3 e janela ainda sem artigo)."""
    j = janela(dt)
    if j is None:
        return False
    usados = dias.get(dt.strftime("%Y-%m-%d"), [])
    if len(usados) >= POR_DIA:
        return False
    return all(janela(t) != j for t, _ in usados)


def proximo_livre(slug="novo", dias=None, depois=None):
    dias = ocupacao(incluir_rascunhos=True) if dias is None else dias
    inicio = max(depois or agora(), agora() + FOLGA)
    d = inicio.date()
    for _ in range(400):
        dia = d.isoformat()
        for j in range(len(JANELAS)):
            dt = minuto_quebrado(slug, dia, j)
            if dt < inicio:
                # a janela de hoje pode ainda estar aberta: tenta um minuto quebrado depois de agora
                a, b = JANELAS[j]
                fim = datetime.fromisoformat(dia) + timedelta(hours=b)
                cand = inicio + timedelta(minutes=1)
                while cand.minute % 5 == 0:
                    cand += timedelta(minutes=1)
                if not (cand < fim and janela(cand) == j):
                    continue
                dt = cand.replace(second=0, microsecond=0)
            if _livre(dias, dt):
                return dt
        d += timedelta(days=1)
    raise RuntimeError("Sem horário livre nos próximos 400 dias")


def ajustar_rascunhos(verbose=True):
    """Garante que cada rascunho tem um horário livre só dele. Os rascunhos mais antigos (pela data)
    escolhem primeiro; quem não cabe vai para o próximo horário livre. Devolve a lista de mudanças."""
    dias = ocupacao()
    mudancas = []
    lim = agora() + FOLGA
    for f, d in sorted(_ler("rascunhos"), key=lambda x: str(x[1]["data"])):
        try:
            t = datetime.fromisoformat(str(d["data"])[:16])
        except ValueError:
            t = None
        if t is None or t < lim or not _livre(dias, t):
            novo = proximo_livre(d.get("slug", f.stem), dias)
            antigo = d.get("data")
            d["data"] = novo.strftime("%Y-%m-%dT%H:%M")
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            mudancas.append((d.get("slug", f.stem), antigo, d["data"]))
            t = novo
        dias.setdefault(t.strftime("%Y-%m-%d"), []).append((t, d.get("slug", f.stem)))
    if verbose:
        for slug, a, n in mudancas:
            print(f"Rascunho {slug[:60]}: {a} -> {n} (próximo horário livre)")
    return mudancas


if __name__ == "__main__":
    if sys.argv[1:] == ["ajustar"]:
        ajustar_rascunhos()
    else:
        dias = ocupacao(incluir_rascunhos=True)
        t = agora()
        for i in range(6):
            t = proximo_livre(f"exemplo{i}", dias, t)
            print("Próximo livre:", t.strftime("%d/%m/%Y %H:%M"))
            dias.setdefault(t.strftime("%Y-%m-%d"), []).append((t, f"exemplo{i}"))
