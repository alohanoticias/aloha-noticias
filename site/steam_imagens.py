"""Lista imagens oficiais da loja Steam (capturas 1920x1080 e arte de capa) para escolher fotos dos artigos.
Roda no GitHub (workflow 'Imagens da Steam'). Uso: python3 site/steam_imagens.py "Nome do jogo" "Outro jogo" ...
Para cada termo: acha o app na busca da loja e imprime o appid, o nome, a arte larga e as capturas (path_full)."""
import json, sys, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (compatible; AlohaNoticiasBot/1.0)"}
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40))
for termo in sys.argv[1:]:
    print("##", termo)
    try:
        if termo.isdigit():
            ids = [termo]
        else:
            r = get("https://store.steampowered.com/api/storesearch/?" + urllib.parse.urlencode({"term": termo, "cc": "br", "l": "portuguese"}))
            ids = [str(i["id"]) for i in r.get("items", [])[:2]]
        for a in ids:
            d = get(f"https://store.steampowered.com/api/appdetails?appids={a}&cc=br&l=portuguese").get(a, {})
            if not d.get("success"):
                continue
            x = d["data"]
            print(f'  {a} | {x.get("name")} | lançamento {x.get("release_date", {}).get("date")} | preço {x.get("price_overview", {}).get("final_formatted", "-")} | dev {", ".join(x.get("developers", []))}')
            print("   capa:", x.get("header_image"), "|", x.get("background_raw") or "")
            for s in x.get("screenshots", [])[:8]:
                print("   ss:", s["path_full"])
    except Exception as e:
        print("  ERRO", e)
