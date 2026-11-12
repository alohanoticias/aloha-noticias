# Vídeos curtos com o mascote

Um vídeo vertical (1080x1920, ~30 s) por matéria publicada no dia, com o tucano do Aloha
narrando no canto inferior esquerdo. Feito para Reels, TikTok, Shorts e Telegram.

- `GUIA-VIDEOS.md` — personalidade do apresentador e regras do roteiro (também é o pedido enviado à API).
- `roteiros/<slug>.json` — roteiro de cada matéria. Ideal: escrever junto com o rascunho do artigo.
- `mascote/` — artes de referência, `preparar_mascote.py` (gera o rig) e `boneco.py` (anima por deformação
  contínua: cabeça e braço dobram sem recorte; o bico é a peça do próprio desenho girando na dobradiça).
  Se a arte mudar: `python3 video/mascote/preparar_mascote.py nova-arte.png` (as coordenadas
  no topo do script são da arte de 1024x1536).
- `render.py` — fundo em tela cheia (fotos e vídeos), título no topo, legenda palavra a palavra, balão,
  selo, mascote que troca de lado, encerramento.
- `midia/` — fotos e vídeos guardados para os roteiros. A legenda usa `fontes/Gotham-Black.otf` se existir
  (precisa de licença); sem ela, usa a Inter Display Black.
- `fazer_videos.py` — junta tudo: matérias do dia → roteiro → voz (edge-tts) → vídeo em `video/saida/`.
- Workflow `.github/workflows/shorts.yml` — roda todo dia às 20h17 (Brasília) ou na mão
  (Actions → "Vídeos curtos do dia" → Run workflow). Os MP4 ficam nos artefatos da execução e,
  se existir o segredo `TELEGRAM_VIDEOS_CHAT_ID`, chegam num chat do Telegram para baixar no celular.

Segredos opcionais: `ANTHROPIC_API_KEY` (escreve o roteiro quando não houver arquivo em `roteiros/`)
e `TELEGRAM_VIDEOS_CHAT_ID` (use um chat separado do canal de rascunhos, que publica sozinho).

Teste local sem voz: `python3 video/fazer_videos.py --data 2026-11-11 --sem-voz`.
