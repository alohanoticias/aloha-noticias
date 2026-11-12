"""Busca imagens no Wikimedia Commons (URL direta, tamanho, licença). Roda no GitHub: workflow 'Buscar imagens Commons'."""
import json, sys, urllib.parse, urllib.request
QUERIES = ['Autodromo Jose Carlos Pace Interlagos aerial', 'Interlagos circuit grandstand', 'Goiania skyline', 'Goiania aerial view', 'Sao Bernardo do Campo', 'Ayrton Senna helmet museum']
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
