"""Busca imagens no Wikimedia Commons (URL direta, tamanho, licença). Roda no GitHub: workflow 'Buscar imagens Commons'."""
import json, sys, urllib.parse, urllib.request
QUERIES = ["Sony headquarters Tokyo", "Sony City Tokyo Minato", "PlayStation 5 console white", "PS5 Slim console", "PlayStation 5 living room"]
TITULOS = ["Hand-painted hanafuda - late Edo period.jpg", "Mushibana by Nintendo (early Shōwa era).jpg", "Nintendo Hanafuda.jpg", "Filmprojektor mit Handkurbel,Heimprojektor für 35mm Stummfilm.Malteserkreuzgetriebe.JPG", "AGFA Vista 200 35 mm film strip.jpg", "Color print film strip 02 - positive.jpg", "-Man with a movie projector in a projection booth at a movie theater- (LOC) (55384266832).jpg", "35mmProjectorUnknown.jpg"]
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
        if ii["width"] >= 1000:
            print(f'{ii["width"]}x{ii["height"]} | {m.get("LicenseShortName",{}).get("value")} | {pg["title"]} | {ii["url"]}')

print("#### AUTORES")
for t in TITULOS:
    p = urllib.parse.urlencode({"action": "query", "format": "json", "titles": "File:" + t, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiextmetadatafilter": "LicenseShortName|Artist|Credit"})
    d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + p, headers=UA), timeout=40))
    for pg in d["query"]["pages"].values():
        ii = pg.get("imageinfo", [{}])[0]; m = ii.get("extmetadata", {})
        print(t[:40], "|", m.get("Artist", {}).get("value", "")[:150], "|", m.get("Credit", {}).get("value", "")[:100])
