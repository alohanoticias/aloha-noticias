# ALOHA NOTÍCIAS — site

Site de notícias estático (HTML + CSS + um pouco de JavaScript), gerado a partir de arquivos JSON.
Não precisa de banco de dados nem de servidor especial: funciona em qualquer hospedagem de arquivos.

## Estrutura

```
site/
├── conteudo/
│   ├── editorias.json   ← as 6 editorias (nome, endereço, descrição)
│   └── materias.json    ← todas as matérias
├── assets/
│   ├── css/aloha.css    ← todo o visual (cores, tipografia, layout, tema escuro)
│   ├── js/site.js       ← menu no celular, tema claro/escuro, busca, copiar link
│   └── img/             ← logos, ícone de app e favicons
├── gerar.py             ← monta as páginas
└── publico/             ← site pronto para publicar (gerado)
```

## Páginas geradas

- `index.html`: manchete, destaques, mais lidas, um bloco por editoria e newsletter
- `noticias.html`, `cinema.html`, `games.html`, `tecnologia.html`, `curiosidades.html`, `financas.html`
- `materia-<endereço>.html`: uma por matéria, com migalhas, autor, data, tempo de leitura, tags, "Leia também" e dados estruturados para o Google (NewsArticle)
- `busca.html` (busca no próprio navegador), `sobre.html`, `contato.html`, `privacidade.html`, `404.html`

## Como publicar uma matéria nova

1. Abra `conteudo/materias.json` e copie um bloco existente.
2. Troque `slug` (endereço, sem acentos e com hífens), `editoria`, `titulo`, `linha_fina`, `autor`, `data` e `corpo`.
   Cada item de `corpo` é um parágrafo. Comece com `## ` para virar intertítulo.
3. Para colocar a matéria como manchete da home, use `"manchete": true` (só uma por vez).
4. Rode `python3 gerar.py` e publique a pasta `publico/`.

## Como colocar no ar

Qualquer hospedagem estática serve. As mais simples e gratuitas: Netlify (arrastar a pasta `publico/`),
Cloudflare Pages, Vercel ou GitHub Pages. Depois, aponte o domínio para lá.

## O que ainda é de exemplo

- As matérias, autores e a lista de "Mais lidas" (no `gerar.py`, variável `MAIS_LIDAS`).
- As capas são ilustrações provisórias geradas pelo `gerar.py` (função `capa`). Troque por fotos reais.
- A newsletter não envia nada: conecte a um serviço como Mailchimp, Brevo ou Substack.
- E-mails de contato e o texto de privacidade.

## Próximo passo sugerido

Quando o volume de matérias crescer, este visual pode ser levado para um CMS (WordPress com tema próprio,
ou Next.js com um painel como Sanity/Strapi), para a redação publicar sem editar arquivos.

## Avisos push com o site fechado (OneSignal)
1. Criar conta grátis em onesignal.com, app "Web", site https://alohanoticias.com (Typical Site, Custom Code), service worker em /OneSignalSDKWorker.js.
2. Colocar o App ID em `site/conteudo/push.json` ({"onesignal_app_id": "..."}).
3. Criar o segredo `ONESIGNAL_REST_API_KEY` (Settings > Secrets and variables > Actions) com a REST API Key do app.
4. Pronto: cada artigo agendado publicado dispara o push (títulos nos 8 idiomas conforme o idioma do aparelho).
