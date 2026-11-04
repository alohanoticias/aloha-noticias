# Guia para publicar artigos no ALOHA NOTÍCIAS

Responda sempre em português do Brasil.

## Passo a passo
1. Pesquise na web (busca atual) um assunto em alta e **confirme fatos em pelo menos duas fontes**. Datas, preços e números só entram se aparecerem nas fontes.
2. Escolha a editoria (noticias, cinema, games, tecnologia, curiosidades, financas), alternando em relação aos últimos artigos de `site/conteudo/materias.json`.
3. Adicione um objeto ao `materias.json` com: `slug`, `editoria`, `titulo`, `linha_fina`, `autor` (use "Redação ALOHA"), `data` (formato `2026-11-04T08:00`, horário de Brasília), `tags`, `corpo` (lista de parágrafos).
   - Subtítulo: parágrafo começando com `## `.
   - Foto no meio do texto: `!img URL|texto alternativo|crédito`.
   - Link: `[texto](https://...)` dentro do parágrafo.
   - Capa: campo `imagem` `{url, alt, credito}`. Prefira foto gratuita do Unsplash (https://images.unsplash.com/..., licença gratuita, nunca Unsplash+) ou uma ilustração original em `site/assets/img/capas/<slug>.svg` (nunca desenhar personagens, logos ou marcas existentes). Vídeo: campo `video` `{youtube, titulo}` só com vídeo oficial confirmado.
4. Termine o artigo com uma linha "Fontes:" com links clicáveis.
5. Rode `python3 site/gerar.py` (gera a pasta `publico/`) e confira que não há erro.
6. **Não** coloque o artigo em `materias.json`. Salve o objeto do artigo como `rascunhos/<slug>.json` (o nome do arquivo é o slug, e o JSON é um único objeto com os mesmos campos). Rode `python3 site/gerar.py`, faça commit e envie direto para `main`. O rascunho aparece só na página protegida `alohanoticias.com/admin`, e não vai ao ar como matéria.
7. A pessoa abre o admin, lê a prévia e clica em Aprovar (ou Rejeitar). Isso abre um pedido (issue) no GitHub, e uma automação move o rascunho para `materias.json` e publica. Você nunca publica sozinho.

## Tom de escrita (não pode parecer feito por IA)
- Frases de tamanhos variados, voz direta, sem clichês ("em um mundo cada vez mais", "vale destacar", "no cenário atual").
- Sem listas de três itens em sequência por reflexo, sem conclusão moralista, sem repetir o título no primeiro parágrafo.
- Seja concreto: datas, números, nomes. Diga o que ainda não se sabe.
- Se uma informação vier de uma fonte só, deixe isso claro no texto.
- Não copie trechos das fontes; reescreva com suas palavras.

## Imagens e direitos
- Sem marca d'água. Sem fotos de pessoas públicas baixadas da web.
- Sempre crédito na legenda.
