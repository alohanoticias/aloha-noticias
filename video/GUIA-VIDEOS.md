# Guia dos vídeos curtos do Aloha Notícias

Este guia vale para quem escreve o roteiro (a redação ou o Claude, pela API) de cada vídeo vertical
de ~30 segundos que sai a partir das matérias publicadas no dia.

## O apresentador

- É o tucano de terno preto e gravata vermelha do Aloha Notícias (folha de personagem em
  `video/mascote/referencias/`). Nome provisório: **Kekoa** (havaiano para "o corajoso"); dá para trocar.
- Personalidade: amigo gamer e cinéfilo que conta a novidade no grupo, não âncora de telejornal.
  Animado, curioso, um pouco debochado, nunca grosseiro. Ri das situações, não das pessoas.
- Fala como brasileiro fala: "galera", "pra", "tá", "olha só", "hein". Frases curtas.

## Regras do roteiro

1. **Duração**: entre 70 e 85 palavras no total (a voz faz ~30 s com o encerramento).
2. **Só fatos da matéria**: datas, preços e nomes têm de estar no texto do artigo. Nada inventado,
   nenhum boato tratado como confirmado. Se a matéria diz que algo não foi confirmado, o vídeo diz também.
3. **Começa pelo gancho**: a primeira frase já entrega a novidade mais chamativa (data, número, surpresa).
   Nada de "Olá, pessoal, hoje vamos falar sobre...".
4. **Dois comentários do apresentador** (tipo `comentario`), curtos (5 a 14 palavras), engraçados ou
   com opinião leve, no meio da notícia. Eles aparecem num balão saindo do bico, **sem emoji**.
5. **Fecha chamando para o site** de um jeito natural ("O passo a passo completo tá no Aloha Notícias!").
6. Números por extenso quando a voz possa ler errado ("nove e noventa e nove dólares"; "dezesseis horas").
   No campo `destaque` use a forma curta ("US$ 9,99", "16 HORAS ANTES").
7. Sem spoiler além do que a matéria já conta. Sem política, sem tragédia como piada.
8. Cada matéria do dia vira um vídeo; variar o formato das piadas entre um vídeo e outro.

## Formato (JSON)

```json
{
  "titulo_curto": "GTA 6: o truque da Nova Zelândia",
  "voz": {"nome": "pt-BR-AntonioNeural", "rate": "+10%", "pitch": "+5Hz"},
  "falas": [
    {"texto": "Atenção, galera: GTA 6 sai dia 19, mas a Nova Zelândia joga dezesseis horas antes da gente.",
     "tipo": "noticia", "destaque": "16 HORAS ANTES", "gesto": "aponta", "lado": "esq",
     "midia": [{"youtube": "VQRLujxTm3c", "inicio": 8, "dur": 4}, {"arquivo": "video/midia/gta-6/vice-city-noite.jpg"}]},
    {"texto": "Dezesseis horas! Dá pra zerar e ainda soltar spoiler no grupo da família.",
     "tipo": "comentario", "gesto": "risada", "lado": "esq",
     "midia": [{"arquivo": "video/midia/gta-6/jason-lucia-carro.jpg"}]}
  ]
}
```

- `titulo_curto`: até ~40 caracteres, fica fixo no topo. O trecho entre `*asteriscos*` sai em amarelo.
- `falas`: de 5 a 7. `tipo` é `noticia` (vira legenda grande, palavra a palavra) ou `comentario` (balão).
- `midia`: o que aparece no fundo (tela cheia) durante a fala, em ordem; o tempo da fala é dividido entre os itens.
  Use imagens e vídeos **do que está sendo falado**, de preferência diferentes dos que estão no artigo:
  `{"youtube": "<id>", "inicio": s, "dur": s}` (trecho de trailer oficial), `{"commons": "busca", "tipo": "video"|"imagem"}`
  (Wikimedia Commons), `{"url": "https://..."}`, `{"arquivo": "video/midia/..."}`. `"inteira": true` mostra a foto
  inteira sobre ela mesma desfocada (bom para foto de produto). O que não baixar é pulado.
- `lado`: `esq` ou `dir` — canto do mascote. Trocar de lado 1 ou 2 vezes por vídeo; nos comentários ele chega mais perto.
- `fundo_final`: mídia do cartão de encerramento.
- `destaque` (opcional, só em `noticia`): até ~18 caracteres, aparece num selo vermelho.
- `gesto` (opcional): `aponta` (levanta a mão), `risada` (fecha os olhos e balança), `pensativo`
  (inclina a cabeça, olhar meio fechado), `surpreso` (cabeça para trás), `tchau` (acena; use na última fala).
- `voz` (opcional): vozes do edge-tts. Padrão `pt-BR-AntonioNeural`, `+10%` de velocidade, `+5Hz` de tom.
