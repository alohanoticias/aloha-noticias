"""Busca imagens no Wikimedia Commons (URL direta, tamanho, licença). Roda no GitHub: workflow 'Buscar imagens Commons'."""
import json, sys, urllib.parse, urllib.request
QUERIES = ['empty cinema auditorium seats', 'digital cinema projector booth', 'cinema ticket box office', 'television remote control streaming', 'manga volumes bookstore shelf', 'light novel bunko books', 'Akihabara anime advertising building', 'Weekly Shonen Jump magazines', 'HDMI cable connector', 'PlayStation 5 console', 'Xbox Series X console', 'television rear panel HDMI ports', 'speedrun timer LiveSplit', 'Games Done Quick stage setup', 'Super Mario 64 cartridge', 'Super Mario Bros NES cartridge', 'mechanical keyboard switches', 'gaming mouse', 'gaming headset', 'computer monitor desk setup', 'film set lighting equipment', 'clapperboard film', 'film camera dolly track', 'Kyoto Animation studio building', 'Toei Animation Oizumi studio', 'anime production cels', 'M.2 NVMe SSD', 'hard disk drive platters open', 'microSD card', 'SATA SSD 2.5 inch', 'cinema marquee Brazil', 'Cine Odeon Rio de Janeiro', 'movie theater lobby posters', 'Netflix headquarters Los Gatos', 'Pinewood studios sound stage', 'film credits screen']
TITULOS = []
UA = {"User-Agent": "AlohaNoticiasBot/1.0 (alohanoticias@gmail.com)"}
for q in QUERIES:
    p = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 10, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiextmetadatafilter": "LicenseShortName|Artist"})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + p, headers=UA), timeout=40))
    except Exception as e:
        print("##", q, "ERRO", e); continue
    print("##", q)
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
        if ii["width"] >= 1000 and ii["width"] >= 1.2 * ii["height"]:
            import re as _r
            print(f'{ii["width"]}x{ii["height"]} | {m.get("LicenseShortName",{}).get("value")} | {_r.sub("<[^>]+>","",m.get("Artist",{}).get("value",""))[:40]} | {pg["title"]} | {ii["url"]}')

print("#### AUTORES")
for t in TITULOS:
    p = urllib.parse.urlencode({"action": "query", "format": "json", "titles": "File:" + t, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiextmetadatafilter": "LicenseShortName|Artist|Credit"})
    d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + p, headers=UA), timeout=40))
    for pg in d["query"]["pages"].values():
        ii = pg.get("imageinfo", [{}])[0]; m = ii.get("extmetadata", {})
        print(t[:40], "|", m.get("Artist", {}).get("value", "")[:150], "|", m.get("Credit", {}).get("value", "")[:100])
