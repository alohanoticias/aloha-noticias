# Guia para publicar artigos no ALOHA NOTÍCIAS

Responda sempre em português do Brasil.

## Passo a passo
1. Pesquise na web (busca atual) um assunto em alta e **confirme fatos em pelo menos duas fontes**. Datas, preços e números só entram se aparecerem nas fontes.
2. Escolha a editoria (noticias, cinema, games, tecnologia, curiosidades, financas), alternando em relação aos últimos artigos de `site/conteudo/materias.json`.
3. Adicione um objeto ao `materias.json` com: `slug`, `editoria`, `titulo`, `linha_fina`, `autor` (use "Equipe Aloha"), `data` (formato `2026-11-04T08:00`, horário de Brasília), `tags`, `corpo` (lista de parágrafos).
   - Subtítulo: parágrafo começando com `## `.
   - Foto no meio do texto: `!img URL|texto alternativo|crédito`.
   - Link: `[texto](https://...)` dentro do parágrafo. Negrito: `**texto**` (use com moderação, só em termos-chave).
   - Capa: campo `imagem` `{url, alt, credito}`. Prefira foto gratuita do Unsplash (https://images.unsplash.com/..., licença gratuita, nunca Unsplash+) ou uma ilustração original em `site/assets/img/capas/<slug>.svg` (nunca desenhar personagens, logos ou marcas existentes). Vídeo: campo `video` `{youtube, titulo}` só com vídeo oficial confirmado.
4. Termine o artigo com uma linha "Fontes:" com links clicáveis.
5. Rode `python3 site/gerar.py` (gera a pasta `publico/`) e confira que não há erro.
6. **Não** coloque o artigo em `materias.json`. Salve o objeto do artigo como `rascunhos/<slug>.json` (o nome do arquivo é o slug, e o JSON é um único objeto com os mesmos campos). Rode `python3 site/gerar.py`, faça commit e envie direto para `main`. O rascunho aparece só na página protegida `alohanoticias.com/admin`, e não vai ao ar como matéria.
Crie **3 rascunhos por dia**, de editorias e assuntos diferentes, cada um em seu arquivo `rascunhos/<slug>.json`.
7. A pessoa abre o admin, lê a prévia e escolhe **Publicar agora**, **Agendar** (data e hora de saída) ou **Rejeitar**. Os agendados ficam em `agendados/` e uma automação publica na hora marcada. A pessoa abre o admin, lê a prévia e clica em Aprovar (ou Rejeitar). Isso abre um pedido (issue) no GitHub, e uma automação move o rascunho para `materias.json` e publica. Você nunca publica sozinho.

## Tom de escrita (não pode parecer feito por IA)
- Frases de tamanhos variados, voz direta, sem clichês ("em um mundo cada vez mais", "vale destacar", "no cenário atual").
- Sem listas de três itens em sequência por reflexo, sem conclusão moralista, sem repetir o título no primeiro parágrafo.
- Seja concreto: datas, números, nomes. Diga o que ainda não se sabe.
- Se uma informação vier de uma fonte só, deixe isso claro no texto.
- Não copie trechos das fontes; reescreva com suas palavras.

## Imagens e direitos
- Sem marca d'água. Sem fotos de pessoas públicas baixadas da web.
- Sempre crédito na legenda.

## Foco editorial (prioridade atual)
- **Games e Cinema são o foco**: dos 3 rascunhos diários, pelo menos 2 devem ser de Games ou Cinema (lançamentos, estreias, trailers, bilheteria, anúncios oficiais, premiações). O terceiro alterna entre Tecnologia, Notícias, Curiosidades e Finanças.
- **Finanças** só com fonte oficial ou jornalismo de peso (Banco Central, IBGE, Tesouro, CVM, Agência Brasil, grandes veículos), no máximo 1 ou 2 por semana. Nunca prometer ganhos nem recomendar investimento; incluir o aviso de que é conteúdo informativo.

## Regra de ouro: só informação verificada
- Nenhuma informação duvidosa. Nada de boatos, vazamentos não confirmados, "teria", "pode ter" como fato.
- Cada dado importante (data, preço, número, nome, citação) precisa aparecer em pelo menos duas fontes independentes, de preferência uma oficial (empresa, órgão público, comunicado). Abra e leia as páginas; não confie só no título dos resultados da busca.
- Confira o ano e a data de publicação de cada fonte: busca costuma trazer matéria velha com título parecido.
- Se as fontes divergem, diga no texto que divergem (e quais). Se não dá para confirmar, deixe de fora ou não faça o artigo.
- Cálculos próprios devem ser conferidos e descritos como "conta simples" ou "estimativa".
- Se o assunto depende de um evento que acontece nas próximas horas (decisão, resultado, estreia), escreva de modo que o texto continue correto depois, ou avise no PR/mensagem que precisa de atualização.

## Liberação automática após revisão final
Rascunho que ninguém aprovou nem rejeitou em /admin até a manhã seguinte à criação (a data do rascunho é anterior a hoje) é liberado automaticamente pela tarefa diária, **mas só depois desta revisão completa**. Rascunhos já agendados pela pessoa (pasta agendados/) não entram: seguem o horário escolhido.

Para cada rascunho elegível, nesta ordem:
1. **Fatos de novo**: reabra as fontes, confira cada data, número, nome e citação, e veja se algo mudou desde a escrita (decisões, estreias, resultados). Se o assunto ficou desatualizado ou não dá para confirmar, atualize o texto; se não der para corrigir, mova o arquivo para fora (apague o rascunho) e avise na mensagem final.
2. **Humanização**: leia como um leitor. Corte frases de efeito vazias, abertura genérica ("No mundo dos games..."), fecho moralista, listas de três adjetivos, "vale ressaltar", "é importante destacar", "em um cenário", travessões em excesso, repetição de estrutura entre parágrafos e títulos em fórmula. Varie o ritmo, use voz direta e concreta, dados específicos, e uma observação própria do tema que não seja só repetição das fontes.
3. **Originalidade**: o texto precisa ser reescrito com palavras próprias, sem copiar trechos das fontes, e trazer algo a mais (contexto, comparação, explicação do que muda para o leitor).
4. **Risco de AdSense**: sem título sensacionalista ou clickbait, sem promessa de ganho, sem conteúdo médico/financeiro como recomendação, sem imagem de terceiros com direito autoral (use ilustração própria, foto com licença livre e crédito), links só para fontes confiáveis, aviso informativo em Finanças.
5. **Forma**: assinatura "Equipe Aloha", linha fina clara, tags coerentes, ortografia e pontuação revisadas, texto com pelo menos ~600 palavras quando o assunto permitir.
6. **Liberação**: com tudo certo, salve o texto revisado, mova para site/conteudo/materias.json com data = agora (BRT), apague o arquivo de rascunhos/, rode python3 site/gerar.py, commit e push. Anote na mensagem final o que foi alterado na revisão.

## Escolha dos assuntos
- Sempre assuntos do momento: o que está sendo comentado hoje, lançamentos e estreias da semana, anúncios oficiais, polêmicas já confirmadas. Confira nas buscas e nas páginas oficiais o que realmente está em alta antes de decidir.
- Pense no leitor: escolha o que é interessante e útil para o público brasileiro (o que muda para ele, o que vale assistir ou jogar, o que ele precisa saber), não o que só enche espaço.
- Escreva como uma pessoa escreveria para um amigo: voz natural, sem fórmula.

## Mínimo de um artigo publicado por dia
O site precisa ter pelo menos um artigo novo no ar todos os dias.
- Depois da liberação dos rascunhos antigos, confira se já existe artigo com a data de hoje em materias.json ou algum agendado para hoje em agendados/.
- Se não houver nenhum, escolha o melhor dos rascunhos novos, faça nele a revisão final completa (a mesma da seção acima) e publique-o hoje mesmo, com data de agora. Os outros ficam em rascunhos/ para a pessoa aprovar ou para saírem na manhã seguinte.
- Se nenhum dos rascunhos passar na checagem de fatos, não publique algo duvidoso só para cumprir a meta: avise claramente na mensagem final que o dia ficou sem artigo e por quê.

## Capas e imagens (direitos autorais)
As capas devem parecer reais e chamativas, mas **nunca** podem usar material de terceiros com direito autoral: nada de quadros de trailer, capas de jogo, pôsteres, prints, logotipos, personagens ou marcas, nem editados ou recortados. Editar não torna a obra nossa e é risco de direitos autorais e de reprovação no AdSense.

**Capa em colagem de fotos livres (padrão).** Monte a capa com 2 ou 3 fotos reais de bancos com licença livre (Unsplash, Pexels, Wikimedia Commons), todas relacionadas ao tema do artigo (o lugar, o clima, o objeto, a situação), no formato de painéis inclinados com divisórias brancas, como a do GTA 6.
1. Ache as fotos. No Unsplash, abra a página da foto com WebFetch e peça o valor completo do og:image: o trecho `images.unsplash.com/photo-XXXX` é o endereço direto. Use sempre `https://images.unsplash.com/photo-XXXX?fm=jpg&q=80&w=1800&auto=format&fit=crop`. Anote o nome do fotógrafo. Não use a página unsplash.com/photos/... nem o endereço /download: exigem login.
2. Crie site/capas_fotos/<slug>.json, por exemplo: `{"layout": "tres", "fotos": [{"url": "...", "foco": [0.5, 0.5], "zoom": 1.0}, {...}, {...}]}`. Layouts: `tres` (3 fotos), `dois` (2 fotos), `um` (1 foto). `foco` escolhe a parte da foto que fica visível e `zoom` (1 ou mais) aproxima.
3. No JSON do artigo, use `"imagem": {"url": "assets/img/capas/<slug>.jpg", "alt": "descrição fiel do que as fotos mostram", "credito": "Fotos: Nome1, Nome2 e Nome3 / Unsplash"}`.
4. Faça commit e push. Uma automação do GitHub (capas.yml) baixa as fotos, monta site/assets/img/capas/<slug>.jpg (1200x675), regenera o site e faz commit em cerca de 2 minutos. Esta sessão não consegue baixar fotos; não tente montar a capa localmente. Se a capa ainda não existir, a prévia no admin mostra a imagem quebrada por alguns minutos, e isso é normal.
5. Confira depois (git pull) abrindo o .jpg gerado. Se o resultado estiver ruim (corte estranho, foto fora do tema), ajuste foco/zoom, apague o .jpg e envie de novo.
6. Escolha fotos bonitas, nítidas e coerentes entre si (cores que combinem). Nunca fotos com marcas visíveis em destaque, logotipos ou rostos reconhecíveis de pessoas famosas.

**Fallback.** Se não houver fotos livres boas para o tema, use uma ilustração original em SVG (e um PNG de mesmo nome, 1200x675, para o compartilhamento nas redes) no estilo limpo do site.

**Fotos dentro do texto**: só de bancos com licença livre, com crédito. **Vídeos**: apenas incorporação oficial do YouTube, nunca baixados.

## Todo artigo leva capa, fotos e vídeo (regra fixa)
Nenhum artigo vai para rascunhos/ ou materias.json sem:
- **Capa** em colagem de fotos livres, montada como descrito em "Capas e imagens".
- **Pelo menos 2 fotos dentro do texto** (linha `!img URL|descrição|crédito`), de bancos livres, relacionadas ao assunto, espalhadas entre os blocos (uma perto do começo, outra no meio ou no fim). Descrição fiel ao que a foto mostra; crédito com nome do fotógrafo e "/ Unsplash".
- **1 vídeo** no campo `"video": {"youtube": "ID", "titulo": "..."}`: trailer ou conteúdo oficial do assunto (canal da empresa, distribuidora, órgão público ou veículo reconhecido). Para Finanças, uma explicação de veículo de jornalismo ou órgão oficial, sem recomendação de investimento.
- **Como achar o ID do vídeo**: abra com WebFetch páginas de notícias confiáveis sobre o assunto e procure o iframe `youtube.com/embed/ID`; ou use WebSearch com allowed_domains youtube.com. Nunca invente um ID.
- **Conferir o vídeo**: rode o workflow "Checar vídeos do YouTube" (`gh api -X POST repos/alohanoticias/aloha-noticias/actions/workflows/videos.yml/dispatches -f ref=main -f 'inputs[ids]=ID1 ID2'`, espere ~40 s e leia o log do job com `gh api repos/alohanoticias/aloha-noticias/actions/jobs/<id>/logs`). Ele mostra canal e título de cada ID. Só use o vídeo se o canal e o título baterem com o assunto e a data. Sem vídeo confirmado, o rascunho não está pronto.
- **Fotos no texto**: o endereço direto vem do mesmo método das capas (og:image da página da foto no Unsplash). Use `https://images.unsplash.com/photo-XXXX?fm=jpg&q=70&w=1600&auto=format&fit=crop`.
