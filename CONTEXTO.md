# Projeto ALOHA NOTÍCIAS — contexto para continuar

Responda sempre em português.

## O que é
Site de notícias com identidade inspirada na cultura havaiana, minimalista.
Editorias: Notícias, Cinema, Games, Tecnologia, Curiosidades, Finanças.

## Decisões tomadas
- Nome: ALOHA NOTÍCIAS. "ALOHA NEWS" foi descartado porque alohanews.com já existe.
- alohanoticias.com parece registrado por terceiros (não confirmado por WHOIS). alohanoticias.com.br não foi verificado.
- Cores: azul-oceano #0F4C5C, areia #F4EDE4, fundo claro #FBF7F1, coral #E76F51 (só destaque, nunca no logo).
  Apoio: tinta #1E2A2D, maré #5B6B6E, coral-texto #B4492F, linha #E6DDD0.
- Fontes: Outfit (ALOHA em Bold, NOTÍCIAS em SemiBold, interface). Newsreader no corpo das matérias (sugestão).
- Logo: o "O" de ALOHA é um anel grosso com mar preenchido (topo ondulado) e uma onda clara vazada. Sem ícone extra ao lado do nome.
  Ícone/favicon: o "O" sozinho sobre azul-oceano.

## Arquivos
- marca/svg, marca/png: logos (empilhado, em linha, positivo/negativo), símbolo O, ícone de app, favicons.
- marca/aloha-tokens.css: variáveis de cor e tipografia.
- marca/gerar-logo.py: gera os SVGs a partir da fonte Outfit (precisa de outfit700.ttf e outfit600.ttf instanciados do Outfit variável, via fontTools).
- marca/marca-aloha-noticias.html: folha de marca.
- site/: site estático. `python3 gerar.py` lê conteudo/*.json e gera a pasta publico/. Ver site/LEIAME.md.

## O que ainda é exemplo
18 matérias atemporais, autores fictícios, lista "Mais lidas" fixa, capas ilustradas no lugar de fotos,
newsletter sem serviço conectado, e-mails de contato e texto de privacidade.

## Próximos passos possíveis
Hospedar (Netlify/Cloudflare Pages a partir de publico/), registrar domínio, trocar o conteúdo de exemplo,
ou migrar o visual para WordPress se a redação for publicar com frequência.
