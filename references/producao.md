# Produção portátil

Use Python 3.10+ e ambiente isolado para `requirements.txt`. VoiceStudio e os pesos VoxCPM2/Whisper são dependências separadas. O FFmpeg precisa de libx264, AAC e libass.

Copie `assets/projeto-exemplo.json` para o novo projeto e substitua roteiro, títulos e elementos visuais. O renderer é um ponto de partida adaptável, não um limite criativo. O campo opcional `closing`, com `title` e `cta`, personaliza o fechamento para o assunto. A prévia inclui `preview-first-body.png`, mostrando a primeira cena após a abertura; as legendas devem ser revisadas no MP4 final.

```sh
python scripts/voice.py doctor
python scripts/voice.py generate projeto.json --out work/voz
python scripts/video.py prepare projeto.json --ledger work/voz/ledger.json --work work/montagem
python scripts/video.py preview projeto.json --work work/montagem
python scripts/captions.py --work work/montagem --model-path caminho/do/modelo-whisper-local
python scripts/video.py render projeto.json --work work/montagem --output outputs/video-s6vid.mp4
python scripts/video.py verify outputs/video-s6vid.mp4 --qr-url https://s6imoveis.com.br/
```

`voice.py` reaproveita tomadas cujo texto e referência continuam iguais. O estado fica na pasta do projeto. A geração é bloqueada quando `/models` não confirma os pesos VoxCPM2 instalados e completos. O script não instala programas nem inicia esse download.

`prepare` conserva os WAVs completos, aplica ritmo de entrega e ganho da voz, gera a trilha original discreta e registra a origem temporal para as legendas. Acrescenta o encerramento de 8 s.

`captions.py` usa apenas o modelo local informado, sem download automático. Alinha o roteiro aos tempos reconhecidos para corrigir transcrição, não erros audíveis da voz. Revise as divergências do relatório. Produz SRT e ASS sem sobreposição de eventos.

`render` exige legendas e as grava no vídeo. Caminhos de arquivos no projeto são relativos ao JSON do projeto. Scripts e recursos não dependem das pastas do criador da skill.

`preview` também gera `storyboard-interface.jpg` e `preview-interface-*.png`, com máscaras ilustrativas do cabeçalho, controles laterais e descrição do Instagram. Inclui a primeira cena de conteúdo após a abertura. Revise todos esses quadros; logo, chamada, título, notas, site e QR devem ficar dentro da área segura definida em `assets/padrao.json`. As legendas reais devem ser conferidas no MP4 com a mesma área reservada. Máscaras são uma simulação conservadora, não uma cópia exata da interface atual.

Verifique o MP4 inteiro, início das cenas em movimento, leitura em celular, sobreposição de texto, finais de palavras e QR decodificado de um quadro do arquivo final. Compare a música com a fala. Preserve versões anteriores e não publique automaticamente após a aprovação da edição.
