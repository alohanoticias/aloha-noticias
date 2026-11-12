"""Busca imagens no Wikimedia Commons (URL direta, tamanho, licença). Roda no GitHub: workflow 'Buscar imagens Commons'."""
import json, sys, urllib.parse, urllib.request
QUERIES = ['ClassInd classificação indicativa', 'Classificação Indicativa Brasil símbolo', 'video game shelf store', 'PEGI rating', 'dubbing studio', 'voice recording booth microphone', 'estúdio de dublagem', 'recording studio mixing console', 'Akihabara anime billboard', 'anime production studio Tokyo', 'anime cel animation', 'Kyoto Animation studio', 'phishing email screen', 'gift card rack', 'computer keyboard password', 'two-factor authentication', 'foley studio', 'foley stage props', 'sound effects recording', 'film sound mixing stage', 'Horizon Chase Turbo', 'Brasil Game Show', 'Brazil Game Show 2019', 'indie game booth', 'cinema multiplex Brazil', 'movie theater auditorium', 'streaming television remote', 'Blu-ray disc case', 'manga shelf bookstore', 'light novel books', 'manga volumes', 'Jump magazine', 'HDMI 2.1 cable', 'television gaming setup', 'OLED TV', 'HDMI port television', 'speedrun Games Done Quick', 'Games Done Quick', 'stopwatch timer', 'Summer Games Done Quick', 'Atari Adventure easter egg', 'video game cartridge collection', 'arcade cabinets', 'retro game console collection', 'movie theater ticket booth', 'cinema ticket', 'film premiere marquee', 'box office cinema', 'gaming mouse', 'mechanical keyboard', 'gaming headset', 'PC gaming setup', 'handheld game console', 'video game controller', 'indie games', 'Steam Deck', 'Netflix logo screen', 'São Paulo film set', 'film shooting Brazil', 'television production set', 'film credits screen', 'film crew camera', 'clapperboard', 'film set lighting crew', 'Toei Animation building', 'Studio Ghibli Museum', 'MAPPA studio', 'Sunrise studio Gundam statue', 'solid state drive', 'hard disk drive internal', 'microSD card', 'NVMe SSD M.2']
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
