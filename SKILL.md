---
name: s6vid
description: "Crie vídeos ilustrados e infográficos narrados da S6 Imóveis, especialmente Reels para Instagram, com identidade grafite e dourada, voz feminina aprovada, legendas sincronizadas e QR code. Use ao pedir S6Vid ou vídeos educativos nesse padrão; para tours com filmagem de um imóvel, use o fluxo próprio de edição imobiliária."
---

# S6Vid

Produza o vídeo e mostre o arquivo para revisão. Preserve o padrão aprovado, mudando conteúdo e ilustrações conforme o assunto. Instruções posteriores do usuário prevalecem sobre estes padrões.

## Confirmar destino antes de produzir

Sempre pergunte **qual será o formato e para qual rede social o vídeo será publicado**, antes de iniciar roteiro visual, locução ou renderização. Exemplo: “Em qual rede social você vai postar e em qual formato: Reels, Stories, feed ou outro?”. Se o pedido já informar ambos, confirme esses dados de forma breve e pergunte se são esses mesmos. Aguarde a resposta; não assuma Instagram/Reels por ser o vídeo anterior.

Após a confirmação, escolha proporção, resolução, área segura e enquadramento próprios do destino. O modelo incluído gera **Instagram Reels 9:16**; para outro destino, adapte o renderer e as legendas antes de gerar. Não estique, corte ou adicione barras automaticamente para forçar um formato. Confira o quadro inteiro e possíveis recortes na superfície de publicação escolhida, incluindo abertura e encerramento.

## Padrão aprovado

- Para Instagram Reels confirmado: vertical 9:16, 1080 × 1920, 24 fps, H.264/AAC, sem barras. Outros destinos exigem composição adaptada ao formato confirmado. Infográficos desenhados, linhas e animações suaves; exemplos visuais acompanhando o raciocínio da fala.
- Grafite `#111315`, painéis `#191C1F`, dourado `#C4A45C`, branco `#F7F5EF`, cinza `#A5A7A8`. Use o logo oficial em `assets/`, preservando proporções e transparência.
- Fonte **Instrument Sans**, regular e bold, incluída. Veja [identidade.md](references/identidade.md) para composição e referência visual.
- Para o modelo Reels, respeite a área segura em todas as cenas: em 1080 × 1920, mantenha logo, títulos, legendas, notas, site e QR dentro de **x=90–900 e y=300–1540**. Reserve o topo para foto/nome do perfil e as bordas direita e inferior para controles e descrição. Essas margens são o padrão conservador da S6Vid, não medidas garantidas da plataforma. Confira a prévia com sobreposições antes de entregar; use margens próprias para outros destinos.
- Voz feminina sintética **já aprovada**, preservada em `assets/voz-aprovada.wav`. Use a referência e sua transcrição; não redesenhe o timbre a cada vídeo, não use a voz pessoal do usuário nem uma voz de radialista. Veja [voz.md](references/voz.md).
- Gere fala em ritmo natural e aplique **1,25× na entrega**, preservando o tom e sincronizando cenas e legendas. Ganho linear **0,8 na voz**, uma única vez; não normalize depois.
- Trilha instrumental sem voz, aproximadamente **29 dB abaixo do RMS da fala ativa**, com fades suaves. O usuário rejeitou música mais alta. Ao revisar a trilha, preserve a narração. `scripts/music.py` mistura a composição original local incluída; outra faixa precisa de origem/licença adequadas.
- Legendas da narração **gravadas no vídeo**, também em SRT. Blocos curtos, até duas linhas, branco e destaque discreto em dourado. Não basta repetir os títulos dos gráficos. Confira acentos, finais e sincronismo após acelerar.
- Logo na abertura por **cerca de 3,5 s**, junto do gancho e com fala imediata. Não inserir vinheta silenciosa antes da mensagem. A primeira tela precisa de tempo para concluir a primeira ideia e ser lida.
- Site `s6imoveis.com.br` no rodapé. Encerramento com contato visual e QR para `https://s6imoveis.com.br/`, com cerca de **8 s** de leitura. Não acrescentar outra cartela de logo depois.
- Não narrar a marca nem o site no fechamento. Se a marca for solicitada em outro trecho, pronunciar **“Essi seis imóveis”**.

## Roteiro para Instagram

Aproveite o contexto e pergunte só pelo que realmente faltar. A identidade e a voz não precisam de nova aprovação em cada trabalho.

Comece com uma frase específica que desperte curiosidade e pertença ao assunto. Mostre cedo o exemplo que explica o gancho; desenvolva consequências e termine com uma conclusão útil. Quando pertinente, convide a enviar o vídeo a alguém que precise da informação. Não prometa alcance, viralização ou resultados.

Reescreva referências com estrutura e linguagem próprias, sem copiar frases, números ou exemplos automaticamente. Não invente dados de imóveis. Bairros, taxas e valores só entram quando necessários e confirmados. O vídeo aprovado é referência de forma, não um roteiro fixo a repetir.

Em conteúdo financeiro, diferencie despesas, poder de compra e custo de oportunidade; não some inflação e rendimento nominal como perdas independentes. CDB é exemplo condicional, sem promessa de rentabilidade. Considere aluguel e valorização quando relevantes à comparação.

## Execução e revisão

1. Estruture roteiro e cenas. Se o usuário pedir aprovação do texto antes, mostre-o e aguarde. Em revisões, altere o solicitado e suas dependências necessárias.
2. Use [producao.md](references/producao.md) para os scripts portáteis. `assets/projeto-exemplo.json` é um ponto de partida, não um limite criativo.
3. Gere tomadas curtas completas e preserve as que funcionaram. Refaça só falhas confirmadas. Nunca recorte sílabas para encaixar uma cena; prolongue a cena quando necessário.
4. Confira leitura em celular, movimento, controles do Instagram e correspondência entre fala e ilustração. Use a faixa livre entre título e gráfico para legendas. Revise abertura, cenas intermediárias e fechamento com as máscaras de interface geradas por `preview`; nenhum conteúdo essencial deve ficar sob o cabeçalho, botões ou descrição. Ajuste a composição por cena sem reduzir a fonte até prejudicar a leitura.
5. Confira decodificação integral, duração, dimensões, áudio sem saturação, leitura do QR **no MP4 exportado** e finais das palavras. Transcrição automática auxilia, mas não comprova ausência de sotaque ou corte fonético.
6. Entregue MP4 reproduzível, SRT e roteiro final. Preserve versões. Aprovar um vídeo não autoriza publicá-lo: confirme destino e ação quando houver pedido de publicação.

Na publicação de infográficos deste estilo, não ative automaticamente o rótulo manual de IA apenas por serem ilustrações narradas. Essa é a preferência do usuário. Se a plataforma exigir identificação para características específicas do conteúdo, explique a exigência antes de publicar; não presuma uma dispensa geral nem tente ocultar rótulos aplicados pela própria plataforma.

## Dependências e distribuição

Instalar esta skill não instala VoiceStudio nem pesos de voz/transcrição. Verifique o ambiente; não troque a voz ou contrate um serviço automaticamente se faltar uma dependência.

A distribuição pública contém só recursos de marca, voz sintética aprovada, código e referências permitidas. Não inclua gravações pessoais, credenciais, banco do VoiceStudio, perfis com caminhos locais ou arquivos de clientes. Veja [LICENSE](LICENSE) e [NOTICE.md](NOTICE.md).
