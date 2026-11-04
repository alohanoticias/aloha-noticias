# Guia para publicar artigos no ALOHA NOTÍCIAS

Responda sempre em português do Brasil.

## Passo a passo
1. Pesquise na web (busca atual) um assunto em alta e **confirme fatos em pelo menos duas fontes**. Datas, preços e números só entram se aparecerem nas fontes.
2. Escolha a editoria (noticias, cinema, games, tecnologia, curiosidades, financas), alternando em relação aos últimos artigos de `site/conteudo/materias.json`.
3. Monte o objeto do artigo (ele será salvo como **rascunho**, veja o passo 6) com: `slug`, `editoria`, `titulo`, `linha_fina`, `autor` (use "Equipe Aloha"), `data` (formato `2026-11-04T08:00`, horário de Brasília), `tags`, `corpo` (lista de parágrafos).
   - Subtítulo: parágrafo começando com `## `.
   - Foto no meio do texto: `!img URL|texto alternativo|crédito`.
   - Link: `[texto](https://...)` dentro do parágrafo. Negrito: `**texto**` (use com moderação, só em termos-chave).
   - Capa: campo `imagem` `{url, alt, credito}`, feita como descrito em "Capas e imagens". Vídeo: campo `video` `{youtube, titulo}`, só com vídeo oficial confirmado (veja "Todo artigo leva capa, fotos e vídeo").
4. Termine o artigo com uma linha "Fontes:" com links clicáveis.
5. Rode `python3 site/gerar.py` (gera a pasta `publico/`) e confira que não há erro.
6. **Não** coloque o artigo em `materias.json`. Salve o objeto do artigo como `rascunhos/<slug>.json` (o nome do arquivo é o slug, e o JSON é um único objeto com os mesmos campos). Rode `python3 site/gerar.py`, faça commit e envie direto para `main`. O rascunho aparece só na página protegida `alohanoticias.com/admin`, e não vai ao ar como matéria.
Crie até **3 rascunhos por dia** (veja "Meta diária"), de editorias e assuntos diferentes, cada um em seu arquivo `rascunhos/<slug>.json`.
7. A pessoa abre o admin, lê a prévia e escolhe **Publicar agora**, **Agendar** (data e hora) ou **Rejeitar**. Os agendados ficam em `agendados/` e uma automação publica na hora marcada. **Você nunca publica sozinho.**

## Tom de escrita (não pode parecer feito por IA)
- Frases de tamanhos variados, voz direta, sem clichês ("em um mundo cada vez mais", "vale destacar", "no cenário atual").
- Sem listas de três itens em sequência por reflexo, sem conclusão moralista, sem repetir o título no primeiro parágrafo.
- Seja concreto: datas, números, nomes. Diga o que ainda não se sabe.
- Se uma informação vier de uma fonte só, deixe isso claro no texto.
- Não copie trechos das fontes; reescreva com suas palavras.

## Imagens e direitos
- Sem marca d'água de terceiros. Sem fotos de pessoas públicas (rostos reconhecíveis) baixadas da web.
- Sempre crédito na legenda.

## Foco editorial (prioridade atual)
O site é novo e vai pedir o AdSense, então o conteúdo precisa ter **tema claro e concentrado**, não virar um site genérico.
- **Games e Cinema são o foco principal**: dos 3 rascunhos diários, pelo menos 2 devem ser de Games ou Cinema (lançamentos, estreias, trailers, bilheteria, anúncios oficiais, premiações).
- O terceiro rascunho é de **Tecnologia**, de preferência ligada ao universo de games, cinema e streaming (consoles, hardware, plataformas). Notícias e Curiosidades só quando o assunto também for de entretenimento ou tecnologia.
- **Finanças está suspensa**: não escreva rascunhos de Finanças (nem de economia, juros, investimentos) até a pessoa dizer que voltou. Motivo: conteúdo financeiro é área sensível e dilui o foco do site no pedido de monetização.

## Regra de ouro: só informação verificada
- Nenhuma informação duvidosa. Nada de boatos, vazamentos não confirmados, "teria", "pode ter" como fato.
- Cada dado importante (data, preço, número, nome, citação) precisa aparecer em pelo menos duas fontes independentes, de preferência uma oficial (empresa, órgão público, comunicado). Abra e leia as páginas; não confie só no título dos resultados da busca.
- Confira o ano e a data de publicação de cada fonte: busca costuma trazer matéria velha com título parecido.
- Se as fontes divergem, diga no texto que divergem (e quais). Se não dá para confirmar, deixe de fora ou não faça o artigo.
- Cálculos próprios devem ser conferidos e descritos como "conta simples" ou "estimativa".
- Se o assunto depende de um evento que acontece nas próximas horas (decisão, resultado, estreia), escreva de modo que o texto continue correto depois, ou avise no PR/mensagem que precisa de atualização.

## Nada é publicado sem aprovação
**Nenhum artigo vai para o ar sem a aprovação da pessoa no /admin.** Rascunho não aprovado fica esperando, por mais tempo que leve. Não existe liberação automática, nem para cumprir meta diária. Só a automação do GitHub publica, e apenas o que a pessoa aprovou ou agendou. Nunca grave em `site/conteudo/materias.json` nem mova arquivo de `rascunhos/` para fora dela.

## Revisão final antes de entregar (vale para todo rascunho novo)
Antes de salvar um rascunho, passe por estes pontos, para a pessoa receber algo que já está pronto para aprovar:
1. **Fatos de novo**: reabra as fontes, confira cada data, número, nome e citação. Se não der para confirmar, tire a informação ou não faça o rascunho.
2. **Humanização**: leia como um leitor. Corte frases de efeito vazias, abertura genérica, fecho moralista, listas de três adjetivos, "vale ressaltar", "é importante destacar", "em um cenário", travessões em excesso. Varie o ritmo, use voz direta, dados específicos e uma observação própria do tema.
3. **Originalidade**: texto reescrito com palavras próprias, sem copiar trechos das fontes, trazendo algo a mais (contexto, comparação, o que muda para o leitor).
4. **Risco de AdSense**: sem título sensacionalista ou clickbait, sem promessa de ganho, sem conteúdo médico ou financeiro como recomendação, imagens de terceiros só com crédito e fonte na legenda (decisão da diretoria), links só para fontes confiáveis, aviso informativo em Finanças.
5. **Forma**: assinatura "Equipe Aloha", linha fina clara, tags coerentes, ortografia revisada, capa, fotos e vídeo conforme as regras abaixo.

## Manutenção dos rascunhos que estão esperando
Em cada execução, olhe os rascunhos pendentes em `rascunhos/`:
- Se algum fato mudou (decisão, estreia, preço, resultado, "nesta quinta" que já passou), atualize o texto e a data do rascunho, e conte isso na mensagem final.
- Se o assunto perdeu a relevância, **não apague**: diga na mensagem final qual é e por quê, para a pessoa decidir.
- Se já há 6 ou mais rascunhos pendentes, não escreva rascunhos novos nesse dia: avise que há fila e peça para a pessoa aprovar ou rejeitar alguns.

## Escolha dos assuntos
- Sempre assuntos do momento: o que está sendo comentado hoje, lançamentos e estreias da semana, anúncios oficiais, polêmicas já confirmadas. Confira nas buscas e nas páginas oficiais o que realmente está em alta antes de decidir.
- Pense no leitor: escolha o que é interessante e útil para o público brasileiro (o que muda para ele, o que vale assistir ou jogar, o que ele precisa saber), não o que só enche espaço.
- Escreva como uma pessoa escreveria para um amigo: voz natural, sem fórmula.

## Meta diária e horários
- Meta: 3 rascunhos por dia, quando a fila permitir (veja "Manutenção"). A publicação, no ritmo que a pessoa escolher: o recomendado é 2 a 3 artigos por dia, espaçados.
- **Horários padrão de saída** (horário de Brasília): **09:00, 13:00 e 19:00**. O admin tem atalhos para esses horários. Ao entregar os rascunhos, sugira na mensagem final qual rascunho ficaria bem em cada horário (ex.: o mais leve ao meio-dia, o mais denso à noite), sem agendar nada.

## Variação entre os posts (para não parecer produção em série)
Posts todos no mesmo molde denunciam automação. Em cada lote de rascunhos e entre dias, varie de propósito:
- **Tamanho (regra fixa): todo artigo deve ter de 3 a 4 minutos de leitura.** O site calcula os minutos como palavras ÷ 200 (arredondado), então o texto precisa ter entre **600 e 850 palavras** (nunca menos de 520 nem mais de 880, contando tudo que está em `corpo`). Não existe artigo curto nem longo: o que varia entre os posts é o formato, o número de subtítulos e o ritmo, não o tamanho. Confira a contagem antes de salvar (o `gerar.py` avisa os artigos fora da faixa) e não encha texto com enrolação: para chegar ao tamanho, traga contexto verificado, comparações e o que muda para o leitor, sempre com fonte. As 8 traduções acompanham o mesmo tamanho (mesmo número de parágrafos).
- **Formato**: alterne notícia direta (abertura com o fato, 0 a 2 subtítulos), explicativo com subtítulos em forma de pergunta, lista ou ranking com cada item desenvolvido, perguntas e respostas, linha do tempo, análise com contexto. Não repita o mesmo formato em dois artigos seguidos.
- **Estrutura**: varie o número de subtítulos (de 0 a 5), a posição das fotos (início, meio ou fim) e se há ou não lista. Alguns textos terminam em informação prática, outros em uma dúvida que ficou em aberto. Fecho resumindo "em resumo" é proibido.
- **Título e linha fina**: alterne estilos (pergunta, afirmação direta, número, contraste). Evite a fórmula "X: o que se sabe" mais de uma vez por semana. Confira os títulos dos últimos 10 artigos antes de escolher o seu. Linha fina com tamanhos diferentes.
- **Abertura**: alterne cena, dado, pergunta e fato direto. Nunca as mesmas primeiras palavras de outro artigo recente.

## Capas e imagens (direitos autorais)
**Decisão da diretoria (04/11/2026): podem ser usadas imagens e vídeos reais de qualquer fonte** (imagens oficiais de divulgação, quadros de trailer, pôsteres, capas de jogo, prints, fotos de sites e agências), em capas e dentro do texto, sempre com crédito e a fonte na legenda (ex.: "Imagem: Rockstar Games / divulgação"). Prefira, quando existir, material oficial de divulgação da própria empresa e o que está livre (Unsplash, Pexels, Wikimedia Commons). Os limites que continuam: sem marca d'água de terceiros, sem imagem de pessoas públicas (rostos reconhecíveis) baixada da web, e nada que a fonte proíba expressamente. Esta sessão do Claude não baixa imagens da web; quem baixa é a automação do GitHub (capas.yml) ou o endereço da imagem é usado direto no texto.

**Capa em colagem de fotos livres (padrão).** Monte a capa com 2 ou 3 fotos reais de bancos com licença livre (Unsplash, Pexels, Wikimedia Commons), todas relacionadas ao tema do artigo (o lugar, o clima, o objeto, a situação), em um formato de colagem **diferente do usado nos artigos anteriores** (veja os layouts abaixo): a home não pode ficar com todas as capas iguais.
1. Ache as fotos. No Unsplash, abra a página da foto com WebFetch e peça o valor completo do og:image: o trecho `images.unsplash.com/photo-XXXX` é o endereço direto. Use sempre `https://images.unsplash.com/photo-XXXX?fm=jpg&q=80&w=1800&auto=format&fit=crop`. Anote o nome do fotógrafo. Não use a página unsplash.com/photos/... nem o endereço /download: exigem login.
2. Crie site/capas_fotos/<slug>.json, por exemplo: `{"layout": "tres", "fotos": [{"url": "...", "foco": [0.5, 0.5], "zoom": 1.0}, {...}, {...}]}`. Layouts de 3 fotos: `tres` (painéis inclinados), `grade` (uma grande à esquerda e duas empilhadas), `grade_b` (o espelho da grade), `colunas` (três tiras verticais), `faixas` (três faixas horizontais, boas para paisagens), `destaque` (uma foto em tela cheia com duas molduras pequenas). Layouts de 2 fotos: `dois` (painéis inclinados), `moldura` (tela cheia com uma moldura sobreposta), `circulo` (tela cheia com um círculo). Layout de 1 foto: `um`. **Nenhuma foto pode se repetir no site**: antes de escolher, procure o ID (`photo-XXXX`) em todos os arquivos de site/capas_fotos/, em site/conteudo/materias.json e em rascunhos/ e só use fotos ainda não usadas, nem em capa nem no texto de outro artigo. Capas iguais ou parecidas entre artigos não são aceitas. **Antes de escolher, abra os 3 últimos arquivos de site/capas_fotos/ e use um layout diferente de todos eles**; alterne também entre foto principal em paisagem e em retrato quando der. A primeira foto da lista é sempre a principal (a maior). `foco` escolhe a parte da foto que fica visível e `zoom` (1 ou mais) aproxima.
3. No JSON do artigo, use `"imagem": {"url": "assets/img/capas/<slug>.jpg", "alt": "descrição fiel do que as fotos mostram", "credito": "Fotos: Nome1, Nome2 e Nome3 / Unsplash"}`.
4. Faça commit e push. Uma automação do GitHub (capas.yml) baixa as fotos, monta site/assets/img/capas/<slug>.jpg (1200x675), regenera o site e faz commit em cerca de 2 minutos. Esta sessão não consegue baixar fotos; não tente montar a capa localmente. Se a capa ainda não existir, a prévia no admin mostra a imagem quebrada por alguns minutos, e isso é normal.
5. Confira depois (git pull) abrindo o .jpg gerado. Se o resultado estiver ruim (corte estranho, foto fora do tema), ajuste foco/zoom, apague o .jpg e envie de novo.
6. Escolha fotos bonitas, nítidas e coerentes entre si (cores que combinem). Nunca fotos com marcas visíveis em destaque, logotipos ou rostos reconhecíveis de pessoas famosas.

**Fallback.** Se não houver fotos livres boas para o tema, use uma ilustração original em SVG (e um PNG de mesmo nome, 1200x675, para o compartilhamento nas redes) no estilo limpo do site.

**Fotos dentro do texto**: de qualquer fonte, com crédito e fonte na legenda; o endereço da imagem pode ser o do próprio site de origem (https). **Vídeos**: incorporação do YouTube (trailer, canal oficial ou veículo), nunca baixados.

## Formato das imagens (regra fixa)
**Toda imagem do site é horizontal, 16:9, em 1920x1080.** Nada de foto ou pôster em pé. Capas: o montar_capa.py já sai em 1920x1080. Fotos do Unsplash: use `https://images.unsplash.com/photo-XXXX?fm=jpg&q=80&w=1920&h=1080&auto=format&fit=crop`. Imagens de outras fontes: escolha versões horizontais (banners, quadros de trailer, arte de divulgação em paisagem); pôsteres verticais não entram, nem na capa nem no texto. O CSS recorta qualquer foto do texto em 16:9, mas a escolha já deve ser horizontal. **Capas só com imagens do próprio assunto** (arte oficial, prints, quadros de trailer, logotipos), nunca fotos genéricas de banco de imagens.

## Todo artigo leva capa, fotos e vídeo (regra fixa)
Nenhum rascunho é entregue sem:
- **Capa** em colagem de fotos livres, montada como descrito em "Capas e imagens".
- **Endereço da foto completo**: use sempre o código inteiro, com o sufixo, como `photo-1751823886813-0cfc86cb9478` (copie do og:image). Sem o sufixo a foto não carrega e o artigo fica com imagem quebrada. O `gerar.py` recusa endereço incompleto e o workflow "Checar fotos" abre cada foto no GitHub depois do push: se ele falhar, corrija na hora.
- **Pelo menos 2 fotos dentro do texto** (linha `!img URL|descrição|crédito`), de qualquer fonte (preferindo material oficial de divulgação), relacionadas ao assunto, espalhadas entre os blocos (uma perto do começo, outra no meio ou no fim). Descrição fiel ao que a foto mostra; crédito com nome do fotógrafo e "/ Unsplash".
- **1 vídeo** no campo `"video": {"youtube": "ID", "titulo": "..."}`: trailer ou conteúdo oficial do assunto (canal da empresa, distribuidora, órgão público ou veículo reconhecido). Para Finanças, uma explicação de veículo de jornalismo ou órgão oficial, sem recomendação de investimento.
- **Como achar o ID do vídeo**: abra com WebFetch páginas de notícias confiáveis sobre o assunto e procure o iframe `youtube.com/embed/ID`; ou use WebSearch com allowed_domains youtube.com. Nunca invente um ID.
- **Conferir o vídeo**: rode o workflow "Checar vídeos do YouTube" (`gh api -X POST repos/alohanoticias/aloha-noticias/actions/workflows/videos.yml/dispatches -f ref=main -f 'inputs[ids]=ID1 ID2'`, espere ~40 s e leia o log do job com `gh api repos/alohanoticias/aloha-noticias/actions/jobs/<id>/logs`). Ele mostra canal e título de cada ID. Só use o vídeo se o canal e o título baterem com o assunto e a data. Sem vídeo confirmado, o rascunho não está pronto.
- **Fotos no texto**: o endereço direto vem do mesmo método das capas (og:image da página da foto no Unsplash). Use `https://images.unsplash.com/photo-XXXX?fm=jpg&q=70&w=1600&auto=format&fit=crop`.

## Atualizações e correções em matérias publicadas
Quando uma matéria publicada tiver data, fato ou número que mudou, não basta trocar o texto: preencha em `site/conteudo/materias.json` os campos opcionais `"atualizado": "YYYY-MM-DDTHH:MM"` (aparece como "Atualizado em ..." ao lado da data e vai para o dateModified do Google) e, se foi correção ou novidade relevante, `"correcao": "texto curto"` (vira uma nota "Atualização:" no fim do artigo). Isso cumpre o que a política editorial promete. Essa edição em matéria já publicada só deve ser feita a pedido do usuário ou, na revisão de manutenção, apenas proposta a ele.

## Banco de pautas
Antes de escolher os assuntos do dia, leia `PAUTAS.md` (pautas por janela de publicação, com o que confirmar). Pode usar as de lá ou outras do momento; ao usar uma, marque com ★ e acrescente novas pautas no fim da tabela quando surgirem.

## Traduções: obrigatórias em todo rascunho (8 idiomas)
O site tem versões reais em /en/, /es/, /fr/, /de/, /it/, /ja/, /zh/ e /ar/. Cada rascunho novo sai com o campo `"traducoes"` no mesmo JSON, com as chaves `"en"`, `"es"`, `"fr"`, `"de"`, `"it"`, `"ja"`, `"zh"` e `"ar"`. Cada uma leva:
`titulo`, `linha_fina`, `corpo` (mesma estrutura do original, mesma quantidade e ordem de parágrafos: `## subtítulos`, `!img URL|alt|crédito`, links), `tags`, `alt` (descrição da capa), `credito` (crédito da capa), `video_titulo`, `slug`. Opcional: `correcao`.
`slug` é o endereço da matéria no idioma: minúsculas, só letras ASCII e hífens, até ~9 palavras. Em en/es/fr/de/it use as palavras do título traduzido; em ja/zh/ar use romanização (romaji, pinyin, transliteração) ou o título em inglês. Fica `/<idioma>/<prefixo>-<slug>.html`. Se faltar, o site usa o slug em português.
Regras:
- **Adaptar, não traduzir palavra por palavra.** Escreva como um redator nativo daquele idioma escreveria: expressões, ordem das ideias, formato de data, tom de notícia local. Para leitor de fora do Brasil, deixe claro quando algo é do Brasil (data de estreia, preço em R$, plataforma), e diga que datas em outros países podem ser diferentes.
- Mantenha os mesmos fatos, números, datas e fontes. Não acrescente informação nova (nem conversão de câmbio, nem gêneros, nem títulos oficiais locais) que a fonte não traz. Títulos de filmes e jogos: use o título internacional só quando ele é conhecido com certeza; do contrário, mantenha o título original/brasileiro (em ja/zh/ar, o nome em letras latinas). Nomes de personagens e atores que não tenham grafia local certa ficam em letras latinas.
- As fontes no fim vão com "(in Portuguese)" no idioma ("(en portugais)", "(auf Portugiesisch)", "(in portoghese)", "（ポルトガル語）", "（葡萄牙语）", "(بالبرتغالية)", "(en portugués)") quando o link é em português.
- Mantenha as URLs das imagens iguais; traduza apenas o texto alternativo e o crédito.
- Para ver como ficou, abra a prévia em /admin (link "Prévia das traduções" no rascunho). Aprovar o rascunho publica todas as versões juntas.
- Se um artigo for atualizado depois (campo `atualizado`/`correcao`), atualize também as traduções.
- Português continua sendo o idioma principal e o texto de referência; as outras páginas dizem isso ao leitor.
