"""Mostra título e canal de vídeos do YouTube (oEmbed). Uso: python3 site/checar_videos.py ID [ID ...]"""
import json, sys, urllib.parse, urllib.request

for vid in sys.argv[1:]:
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe="")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30))
        print(f"OK  {vid} | canal: {d.get('author_name')} | título: {d.get('title')}")
    except Exception as e:
        print(f"ERRO {vid} | {type(e).__name__}: {e}")
