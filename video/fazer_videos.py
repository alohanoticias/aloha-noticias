"""Gera os vídeos verticais do dia (um por matéria, ~30 s) com o mascote narrando.

Uso (na raiz do repositório):
  python3 video/fazer_videos.py                  # matérias publicadas hoje (horário de Brasília)
  python3 video/fazer_videos.py --data 2026-11-11
  python3 video/fazer_videos.py --slug gta-6-...  # uma matéria só
  python3 video/fazer_videos.py --sem-voz        # teste sem narração (tempo estimado)

Para cada matéria:
  1. roteiro: video/roteiros/<slug>.json (escrito junto com o rascunho);
     se não existir e houver ANTHROPIC_API_KEY, é escrito pela API seguindo video/GUIA-VIDEOS.md;
  2. voz: edge-tts (vozes neurais pt-BR), uma fala por vez, com o tempo de cada palavra;
  3. imagens: capa + fotos do meio do artigo;
  4. render: video/saida/<data>-<slug>.mp4
"""
import argparse, asyncio, datetime, json, os, re, subprocess, sys, urllib.parse, urllib.request, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SITE = os.path.join(RAIZ, "site")
sys.path.insert(0, AQUI)
import render  # noqa: E402

VOZ_PADRAO = {"nome": "pt-BR-AntonioNeural", "rate": "+10%", "pitch": "+5Hz"}
SR = 24000
PAUSA = 0.2
UA = "Mozilla/5.0 (AlohaNoticias video bot)"


# ------------------------------------------------------------ matérias
def materias_do_dia(data, slug=None):
    mats = json.load(open(os.path.join(SITE, "conteudo", "materias.json")))
    if slug:
        return [m for m in mats if m["slug"] == slug]
    return sorted([m for m in mats if m.get("data", "").startswith(data)], key=lambda m: m["data"])


def imagens_da_materia(m, pasta_cache):
    os.makedirs(pasta_cache, exist_ok=True)
    fontes = [m["imagem"]["url"]] if m.get("imagem") else []
    for b in m.get("corpo", []):
        if isinstance(b, str) and b.startswith("!img "):
            fontes.append(b[5:].split("|")[0].strip())
    saida = []
    for i, u in enumerate(fontes):
        if u.startswith("http"):
            destino = os.path.join(pasta_cache, f"{m['slug'][:40]}-{i}" + os.path.splitext(u.split("?")[0])[1][:5])
            if not os.path.exists(destino):
                try:
                    req = urllib.request.Request(u, headers={"User-Agent": UA})
                    open(destino, "wb").write(urllib.request.urlopen(req, timeout=30).read())
                except Exception as e:
                    print("  imagem não baixou:", u, e); continue
            saida.append(destino)
        else:
            p = os.path.join(SITE, u.lstrip("/"))
            if os.path.exists(p):
                saida.append(p)
    ok = []
    from PIL import Image
    for p in saida:
        try:
            Image.open(p).verify(); ok.append(p)
        except Exception:
            print("  imagem inválida:", p)
    return ok


# ------------------------------------------------------------ mídia de cada fala
def _baixar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    open(destino, "wb").write(urllib.request.urlopen(req, timeout=60).read())


def _commons(busca, tipo, pasta):
    """Procura no Wikimedia Commons (licenças livres) e baixa o primeiro arquivo bom."""
    filtro = "filetype:video" if tipo == "video" else "filetype:bitmap"
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                "gsrsearch": f"{busca} {filtro}", "gsrlimit": 8, "prop": "imageinfo",
                                "iiprop": "url|size|mime", "iiurlwidth": 1600})
    req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers={"User-Agent": UA})
    dados = json.load(urllib.request.urlopen(req, timeout=30))
    for pg in sorted(dados.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99)):
        ii = (pg.get("imageinfo") or [{}])[0]
        url = ii.get("url", "")
        if tipo == "video" and not ii.get("mime", "").startswith("video"):
            continue
        if tipo != "video" and ii.get("width", 0) < 900:
            continue
        if tipo != "video":
            url = ii.get("thumburl") or url
        ext = os.path.splitext(url.split("?")[0])[1] or ".bin"
        destino = os.path.join(pasta, "commons-" + re.sub(r"\W+", "-", busca)[:40] + ext)
        if not os.path.exists(destino):
            _baixar(url, destino)
        return destino
    return None


def _youtube(vid, inicio, dur, pasta):
    destino = os.path.join(pasta, f"yt-{vid}-{inicio}.mp4")
    if not os.path.exists(destino):
        r = subprocess.run(["yt-dlp", "--no-warnings", "-f", "bv*[height<=1080][ext=mp4]/bv*[height<=1080]/b",
                        "--download-sections", f"*{inicio}-{inicio + dur + 1}", "--force-keyframes-at-cuts",
                        "-o", destino, f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not os.path.exists(destino):
            raise RuntimeError("yt-dlp: " + (r.stderr or r.stdout)[-400:])
    return destino


def resolver_midia(m, pasta):
    """Item do roteiro -> {'tipo','caminho','inicio','inteira'} ou None se não deu."""
    os.makedirs(pasta, exist_ok=True)
    try:
        if "arquivo" in m:
            c = os.path.join(RAIZ, m["arquivo"]); tipo = "video" if c.lower().endswith((".mp4", ".webm", ".mov")) else "imagem"
            if not os.path.exists(c):
                return None
            return {"tipo": tipo, "caminho": c, "inicio": m.get("inicio", 0), "inteira": m.get("inteira")}
        if "youtube" in m:
            c = _youtube(m["youtube"], m.get("inicio", 0), m.get("dur", 4), pasta)
            return {"tipo": "video", "caminho": c, "inicio": 0}
        if "commons" in m:
            c = _commons(m["commons"], m.get("tipo", "imagem"), pasta)
            if c:
                tipo = "video" if m.get("tipo") == "video" else "imagem"
                return {"tipo": tipo, "caminho": c, "inicio": m.get("inicio", 0), "inteira": m.get("inteira")}
        if "url" in m:
            ext = os.path.splitext(m["url"].split("?")[0])[1] or ".jpg"
            c = os.path.join(pasta, "url-" + str(abs(hash(m["url"])))[:10] + ext)
            if not os.path.exists(c):
                _baixar(m["url"], c)
            tipo = "video" if ext.lower() in (".mp4", ".webm", ".mov") else "imagem"
            return {"tipo": tipo, "caminho": c, "inicio": m.get("inicio", 0), "inteira": m.get("inteira")}
    except Exception as e:
        print("  mídia falhou:", m, e)
        with open(os.path.join(AQUI, "saida", "log-midia.txt"), "a") as lg:
            lg.write(f"FALHOU {m}: {e}\n")
    return None


# ------------------------------------------------------------ roteiro
def texto_da_materia(m):
    partes = [m["titulo"], m.get("linha_fina", "")]
    for b in m.get("corpo", []):
        if isinstance(b, str) and not b.startswith("!"):
            partes.append(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b).replace("**", "").lstrip("# "))
    return "\n".join(partes)[:7000]


def roteiro_pela_api(m, n_imagens):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        return None
    guia = open(os.path.join(AQUI, "GUIA-VIDEOS.md")).read()
    pedido = (f"Escreva o roteiro do vídeo desta matéria. Há {n_imagens} imagens (índices 0 a {n_imagens - 1}; 0 é a capa). "
              "Responda só com o JSON, sem comentários.\n\n" + texto_da_materia(m))
    corpo = json.dumps({"model": os.environ.get("MODELO_ROTEIRO", "claude-sonnet-5-5"), "max_tokens": 1500,
                        "system": guia, "messages": [{"role": "user", "content": pedido}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=corpo, headers={
        "x-api-key": chave, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    txt = "".join(c.get("text", "") for c in r.get("content", []))
    txt = txt[txt.find("{"): txt.rfind("}") + 1]
    rot = json.loads(txt)
    rot["slug"] = m["slug"]
    return rot


def roteiro_simples(m):
    """Último recurso (sem roteiro e sem API): título + linha fina, sem piada."""
    return {"slug": m["slug"], "titulo_curto": m["titulo"][:48], "falas": [
        {"texto": m["titulo"], "tipo": "noticia", "imagem": 0, "gesto": "aponta"},
        {"texto": m.get("linha_fina", ""), "tipo": "noticia", "imagem": 1},
        {"texto": "Tem tudo no Aloha Notícias!", "tipo": "noticia", "imagem": 0, "gesto": "tchau"}]}


def obter_roteiro(m, n_imagens):
    p = os.path.join(AQUI, "roteiros", m["slug"] + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    try:
        rot = roteiro_pela_api(m, n_imagens)
    except Exception as e:
        print("  API do roteiro falhou:", e); rot = None
    if rot:
        json.dump(rot, open(p, "w"), ensure_ascii=False, indent=1)
        return rot
    print("  sem roteiro: usando título e linha fina")
    return roteiro_simples(m)


# ------------------------------------------------------------ voz
async def _falar(texto, voz, mp3):
    import edge_tts
    try:
        com = edge_tts.Communicate(texto, voz["nome"], rate=voz["rate"], pitch=voz["pitch"], boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(texto, voz["nome"], rate=voz["rate"], pitch=voz["pitch"])
    palavras = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                palavras.append((ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7))
    return palavras


def ler_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def alinhar(texto, fronteiras, dur):
    """Usa as palavras do roteiro (com pontuação) e o tempo que a voz deu a cada uma."""
    ws = texto.split()
    if fronteiras and len(fronteiras) == len(ws):
        return [(w, a, b) for w, (_, a, b) in zip(ws, fronteiras)]
    a0 = fronteiras[0][1] if fronteiras else 0.05
    a1 = fronteiras[-1][2] if fronteiras else dur - 0.05
    pesos = np.array([len(w) + 2 for w in ws], float); pesos /= pesos.sum()
    bordas = a0 + np.concatenate([[0], np.cumsum(pesos)]) * (a1 - a0)
    return [(w, bordas[i], bordas[i + 1]) for i, w in enumerate(ws)]


def efeito_pop(sr=SR):
    t = np.arange(int(0.09 * sr)) / sr
    return 0.22 * np.sin(2 * np.pi * (520 + 2600 * t) * t) * np.exp(-t * 38)


def narrar(rot, pasta):
    voz = {**VOZ_PADRAO, **rot.get("voz", {})}
    os.makedirs(pasta, exist_ok=True)
    trilha = [np.zeros(int(0.3 * SR), np.float32)]
    t = 0.3; tempos = []
    for i, f in enumerate(rot["falas"]):
        mp3, wav = os.path.join(pasta, f"f{i}.mp3"), os.path.join(pasta, f"f{i}.wav")
        fr = asyncio.run(_falar(f["texto"], voz, mp3))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
        x = ler_wav(wav)
        nz = np.where(np.abs(x) > 0.01)[0]                 # corta silêncio do começo/fim
        ini, fim = (nz[0], nz[-1] + int(0.05 * SR)) if len(nz) else (0, len(x))
        x = x[max(0, ini - int(0.03 * SR)):fim]
        desloc = max(0, ini - int(0.03 * SR)) / SR
        dur = len(x) / SR
        pal = [(w, t + a - desloc, t + b - desloc) for w, a, b in alinhar(f["texto"], fr, dur + desloc)]
        tempos.append({"inicio": t, "fim": t + dur, "palavras": pal})
        trilha.append(x); trilha.append(np.zeros(int(PAUSA * SR), np.float32))
        t += dur + PAUSA
    voz_total = np.concatenate(trilha)
    total = np.zeros(int((t + render.FINAL + 0.5) * SR), np.float32)
    total[:len(voz_total)] += voz_total
    pop = efeito_pop()
    for f, tt in zip(rot["falas"], tempos):          # "pop" quando entra adesivo ou balão
        if f.get("destaque") or f.get("tipo") == "comentario":
            k = int((tt["inicio"] + 0.1) * SR); total[k:k + len(pop)] += pop[:len(total) - k]
    total = np.clip(total, -1, 1)
    saida = os.path.join(pasta, "narracao.wav")
    with wave.open(saida, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((total * 32767).astype(np.int16).tobytes())
    return tempos, t, saida


# ------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser()
    hoje = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")
    ap.add_argument("--data", default=hoje)
    ap.add_argument("--slug")
    ap.add_argument("--sem-voz", action="store_true")
    a = ap.parse_args()
    mats = materias_do_dia(a.data, a.slug)
    print(f"{len(mats)} matéria(s) para {a.slug or a.data}")
    pasta_saida = os.path.join(AQUI, "saida"); os.makedirs(pasta_saida, exist_ok=True)
    feitos = []
    for m in mats:
        print("-", m["slug"])
        cache = os.path.join(AQUI, "cache", m["slug"][:40])
        rot = obter_roteiro(m, 1)
        midias = []
        for i, f in enumerate(rot["falas"]):
            itens = [x for x in (resolver_midia(it, cache) for it in f.get("midia", [])) if x]
            # sem mídia própria, repete a anterior (as fotos dos artigos não entram nos vídeos)
            print(f"  fala {i}: " + ", ".join(os.path.basename(x["caminho"]) for x in itens))
            with open(os.path.join(pasta_saida, "log-midia.txt"), "a") as lg:
                lg.write(f"fala {i}: " + ", ".join(os.path.basename(x["caminho"]) for x in itens) + "\n")
            midias.append(itens)
        mf = resolver_midia(rot["fundo_final"], cache) if rot.get("fundo_final") else None
        if a.sem_voz:
            tempos, dur = render.tempos_estimados(rot); wav = None
        else:
            tempos, dur, wav = narrar(rot, os.path.join(cache, "voz"))
        destino = os.path.join(pasta_saida, f"{m['data'][:10]}-{m['slug'][:60]}.mp4")
        render.renderizar(rot, tempos, dur, midias, destino, wav=wav, midia_final=mf)
        print("  pronto:", destino, f"({dur + render.FINAL:.1f} s)")
        feitos.append(destino)
    json.dump(feitos, open(os.path.join(pasta_saida, "lista.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
