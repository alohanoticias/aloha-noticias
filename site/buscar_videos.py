"""Busca vídeos no YouTube (id, título, canal, duração, views). Roda no GitHub: workflow 'Buscar vídeos YouTube'."""
import json, re, sys, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AlohaNoticiasBot/1.0", "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
def txt(o):
    if not o: return ""
    return o.get("simpleText") or "".join(r.get("text", "") for r in o.get("runs", []))
def achar(o, out):
    if isinstance(o, dict):
        if "videoRenderer" in o: out.append(o["videoRenderer"])
        for v in o.values(): achar(v, out)
    elif isinstance(o, list):
        for v in o: achar(v, out)
for q in [x.strip() for x in " ".join(sys.argv[1:]).split("|") if x.strip()]:
    print("##", q)
    try:
        h = urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q), headers=UA), timeout=40).read().decode("utf8", "ignore")
        m = re.search(r"ytInitialData\s*=\s*(\{.*?\});</script>", h, re.S)
        d = json.loads(m.group(1)); vs = []; achar(d, vs)
        for v in vs[:8]:
            print(v["videoId"], "|", txt(v.get("title"))[:90], "|", txt(v.get("ownerText")), "|", txt(v.get("lengthText")), "|", txt(v.get("viewCountText")), "|", txt(v.get("publishedTimeText")))
    except Exception as e:
        print("ERRO", e)
