# DPM OCR — servidor independente

Este repositório executa somente OCR de imagens PNG. Não tem banco de dados e não armazena documentos de forma persistente. Arquivos temporários são removidos ao final de cada requisição.

## Implantação no Render

1. Crie um **novo repositório privado** no GitHub, por exemplo `dpm-ocr-servidor`, e envie os arquivos desta pasta para a raiz.
2. No Render, selecione **New > Web Service**, conecte o novo repositório e escolha **Docker** como runtime.
3. Escolha uma instância com **ao menos 2 GB de RAM para o teste inicial** (não use a mesma instância de 512 MB). Confirme o preço antes de criar.
4. Configure a variável de ambiente `DPM_OCR_REMOTE_TOKEN` com um segredo aleatório forte, de no mínimo 32 bytes, gerado por um gerenciador seguro. **Nunca coloque o token no GitHub.**
5. Aguarde o deploy. Abra `https://SEU-SERVICO.onrender.com/health`; a resposta esperada é `ok`.
6. No serviço Render do **DPM Inteligente principal** (versão 4.1), configure:
   - `DPM_OCR_MODE=remote`
   - `DPM_OCR_REMOTE_URL=https://SEU-SERVICO.onrender.com/ocr`
   - `DPM_OCR_REMOTE_TOKEN=O_MESMO_SEGREDO`
   - `DPM_OCR_TIMEOUT=180`
7. Reinicie o serviço principal e teste com PDF **fictício** contendo uma página digitalizada. Confira o texto reconhecido e os logs de ambos os serviços.

## Segurança e limites

- Endpoint `/ocr` exige token Bearer, HTTPS no Render e `image/png` com até 12 MB e 8 megapixels.
- `/health` é público e não expõe documentos.
- Um worker por vez limita concorrência; não é uma fila durável. Requisições podem falhar em reinicializações ou timeouts.
- O servidor usa OCR local via RapidOCR; não envia as imagens a terceiros por API. A hospedagem, contudo, processa os dados.
- **Não use documentos administrativos reais, dados médicos ou dados pessoais sensíveis** sem aprovação institucional, revisão de segurança/LGPD, política de retenção e contrato de hospedagem adequados.
- Não compartilhe tokens ou capturas de tela contendo segredos.

## Diagnóstico

- 401: token ausente ou diferente entre os serviços.
- 413: imagem excedeu 12 MB.
- 415: envio não foi PNG.
- 422: imagem inválida ou falha no motor OCR.
- 504: OCR ultrapassou 150 segundos.
- 502/instância reiniciada: confira memória e eventos do Render; talvez seja preciso aumentar RAM.
