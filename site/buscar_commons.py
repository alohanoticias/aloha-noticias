"""Busca imagens no Wikimedia Commons (URL direta, tamanho, licença). Roda no GitHub: workflow 'Buscar imagens Commons'."""
import json, sys, urllib.parse, urllib.request
QUERIES = ["hanafuda cards", "hanafuda deck", "Nintendo Koppai Kyoto", "Nintendo Marufukuro Kyoto", "35 mm film strip", "35mm film frames close up", "Todd-AO 70 mm projector", "The Jazz Singer 1927 Vitaphone", "hand crank movie camera", "movie projector 35mm", "PlayStation 5 console", "PlayStation 5 DualSense"]
UA = {"User-Agent": "AlohaNoticiasBot/1.0 (alohanoticias@gmail.com)"}
for q in QUERIES:
    p = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 12, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiextmetadatafilter": "LicenseShortName|Artist"})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + p, headers=UA), timeout=40))
    except Exception as e:
        print("##", q, "ERRO", e); continue
    print("##", q)
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata", {})
        if ii["width"] >= 1000 and ii["width"] > ii["height"]:
            print(f'{ii["width"]}x{ii["height"]} | {m.get("LicenseShortName",{}).get("value")} | {pg["title"]} | {ii["url"]}')
