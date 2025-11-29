# VT BacBo Analyzer

Aplicativo desktop para analisar resultados de BacBo (OCR via prints), gerar estatísticas e enviar alertas para Telegram.

## Como usar (resumo)
1. Baixe/clone este repositório.
2. Copie `config.ini.template` para `config.ini` e preencha seu `token` e `chat_id` localmente.
3. Instale Tesseract OCR (https://github.com/tesseract-ocr/tesseract).
4. Local: `python -m pip install -r requirements.txt`
5. Local: `python bacbo_gui.py`

## Gerar EXE (recomendado)
- Use o workflow do GitHub Actions — basta commitar para `main` e rodar o workflow.
- Ou localmente:
