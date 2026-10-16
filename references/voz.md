# Voz aprovada

`assets/voz-aprovada.wav` contém a voz feminina sintética escolhida para a S6Vid. Não é gravação pessoal nem clonagem da voz do usuário. A referência fixa e a transcrição em `assets/padrao.json` preservam a identidade melhor que redesenhar uma voz por descrição a cada vídeo.

Backend validado: [VoiceStudio](https://github.com/debpalash/VoiceStudio) 0.5.6, com `openbmb/VoxCPM2`. Consulte `/health`, `/openapi.json` e `/v1/audio/voices` no backend ativo; um catálogo não comprova que os pesos estejam instalados.

```sh
python scripts/voice.py doctor
python scripts/voice.py register --state caminho/do/projeto/work/voice-state.json
python scripts/voice.py generate caminho/do/projeto/projeto.json --out caminho/do/projeto/work/voz
```

O script registra a referência no backend local e grava o ID no projeto. Não publique estados locais nem copie um ID desta instalação para outra. Não acrescente instruções de estilo ao perfil sem necessidade: elas podem alterar o modo de geração. Uma semente não garante resultado idêntico entre versões ou equipamentos.

Gere frases naturais em grupos curtos, preferencialmente até cerca de 215 caracteres. Preserve tomadas completas e aproximadamente 0,26 s entre grupos. Acelere para 1,25× na montagem com preservação de tom, retimando legendas pelo mesmo fator. Aplique ganho 0,8 uma única vez.

Se houver corte, sotaque inadequado ou variação de timbre, confira a tomada específica e gere uma alternativa. A transcrição não prova que a pronúncia está perfeita. Não use a voz pessoal do usuário como fallback.

Modelo e licença declarada: [VoxCPM2, Apache-2.0](https://huggingface.co/openbmb/VoxCPM2). Os pesos não são incluídos. O script consulta `/models` e bloqueia a geração se os pesos não estiverem instalados e completos. Não baixe outro modelo nem use serviço externo sem escolha do usuário.
