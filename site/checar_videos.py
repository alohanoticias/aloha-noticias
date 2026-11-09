"""Mostra título, canal e data de envio de vídeos do YouTube. Uso: python3 site/checar_videos.py ID [ID ...]"""
import json, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
for vid in sys.argv[1:]:
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        data = "?"
        try:
            html = urllib.request.urlopen(urllib.request.Request(f"https://www.youtube.com/watch?v={vid}", headers=UA), timeout=30).read().decode("utf-8", "ignore")
            m = re.search(r'"uploadDate":"([^"]+)"', html) or re.search(r'itemprop="uploadDate" content="([^"]+)"', html) or re.search(r'"publishDate":"([^"]+)"', html)
            data = m.group(1) if m else "?"
        except Exception:
            pass
        print(f"OK  {vid} | canal: {d.get('author_name')} | data: {data} | título: {d.get('title')}")
    except Exception as e:
        print(f"ERRO {vid} | {type(e).__name__}: {e}")
