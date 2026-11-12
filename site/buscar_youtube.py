"""Lista vídeos do YouTube para termos de busca (ID, canal, duração, título).
Uso: python3 site/buscar_youtube.py "termo 1" "termo 2" ..."""
import json, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}

def texto(x):
    if not x: return ""
    if "simpleText" in x: return x["simpleText"]
    return "".join(r.get("text", "") for r in x.get("runs", []))

def achar(o, out):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            out.append(o["videoRenderer"])
        for v in o.values(): achar(v, out)
    elif isinstance(o, list):
        for v in o: achar(v, out)

for termo in sys.argv[1:]:
    termo = termo.strip()
    if not termo: continue
    print(f"\n=== {termo}")
    url = "https://www.youtube.com/results?hl=pt&gl=BR&search_query=" + urllib.parse.quote(termo)
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
        vids = []
        achar(json.loads(m.group(1)), vids)
        for v in vids[:12]:
            canal = texto(v.get("ownerText"))
            print(f"{v.get('videoId')} | {canal} | {texto(v.get('lengthText'))} | {texto(v.get('publishedTimeText'))} | {texto(v.get('title'))}")
    except Exception as e:
        print("ERRO", type(e).__name__, e)
