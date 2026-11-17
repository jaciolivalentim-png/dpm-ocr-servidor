# DPM OCR — Atualização de diagnóstico 4.1.1

## Motivo
O endpoint /ocr estava retornando HTTP 422 e o subprocesso encerrava com code=1. O código anterior descartava a saída de erro, impedindo identificar a causa.

## Alterações
- `app.py`: usa caminho absoluto para o worker e registra o final do stderr quando ele falha.
- `ocr_worker.py`: registra traceback de exceções Python em stderr.
- Nenhuma credencial é registrada deliberadamente. Mesmo assim, trate logs como internos e evite divulgar trechos sensíveis.

## Instalação
1. Faça backup do repositório do servidor OCR.
2. Atualize apenas `app.py` e `ocr_worker.py` no repositório dpm-ocr-servidor.
3. Aguarde o deploy no Render.
4. Faça teste com documento totalmente fictício e uma página escaneada.
5. Se aparecer 422, copie apenas o traceback dos logs, ocultando qualquer dado pessoal.

## Observação
Esta atualização melhora o diagnóstico; não garante que a dependência ou o ambiente do OCR esteja corrigido. O erro raiz será identificado pelo traceback após o teste. Não altere o DPM Inteligente principal.
