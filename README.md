# bics-chatbot

Chatbot em Python para **apontar defeitos em trechos de código** e explicar problemas.
Hoje ele combina:

- checagem de sintaxe com `ast.parse` (erros como falta de `:`, parênteses, aspas);
- um **modelo leve de ML local** (TF‑IDF) treinado em um dataset de códigos Python para medir
  quão “natural” é o trecho analisado em relação ao corpus.

## ⚙️ Instalação (dev)

Crie um ambiente Python e instale as dependências do backend (o projeto está organizado como um monorepo em `apps/`):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r apps/codebug_bot/requirements.txt
```

## 🚀 Rodar API + Frontend (local)

1. Certifique-se de ter criado o ambiente Python e instalado as dependências conforme a seção anterior.

2. Iniciar a API (Flask):

```bash
python apps/api/server.py
# por padrão a API escuta na porta 6060
```

3. Iniciar o frontend (Vite/React):

```bash
cd apps/frontend
npm install
npm run dev
```

O dev server do Vite em `apps/frontend` está configurado para fazer proxy das requisições `'/api'` para `http://localhost:6060`. Se mudar a porta da API, atualize `apps/frontend/vite.config.js` ou ajuste a proxy.


## 🖥️ Utilizando o código

Opções principais:

- Usar a API + frontend (recomendado): abra o frontend em `http://localhost:5173` (Vite) após rodar ambos.
- Rodar a GUI localmente: se preferir a interface Tkinter, execute `python apps/codebug_bot/gui.py` (pode ser necessário executar a partir do diretório `apps/codebug_bot` ou ajustar `PYTHONPATH`).

Notas:
- A API recebe POST em `/api/analyze` com JSON `{ "code": "...", "apply_fix": false }` e retorna o resultado da análise.
- O frontend envia o texto bruto do código (a chave JSON é `code`) — mantenha esse formato se integrar outra interface.

## 🧰 Como funciona (resumo)

1. Tentamos fazer `ast.parse(code)`. Se houver `SyntaxError`, classificamos a falha em tipos comuns:
   - `missing_colon` (faltou `:` em `def`, `if`, etc.);
   - `missing_parenthesis` (parêntese/estrutura não fechada);
   - `missing_quotation` (string não fechada);
   - `syntax_error` genérico, quando a mensagem não se encaixa bem em nenhum caso acima.
2. Computamos um **score de similaridade** do trecho com um corpus grande de códigos Python válidos,
   usando um modelo TF‑IDF de n‑gramas de caracteres treinado localmente.
3. Retornamos:
   - `issues`: lista de problemas encontrados, com linha/coluna, mensagem e sugestão de correção;
   - `model_score`: quão parecido o código é com o dataset;
   - `similar_examples`: alguns trechos reais do dataset mais próximos do código analisado.

## 📦 Dataset (treinamento local)

O script `apps/codebug_bot/scripts/prepare_dataset.py` baixa e prepara o dataset
`iamtarun/python_code_instructions_18k_alpaca` para gerar um corpus local de trechos Python válidos.

Por padrão o modelo local (`apps/codebug_bot/local_model.py`) procurará o arquivo de corpus em:

```
apps/codebug_bot/corpus/python_outputs.txt
```

Se preferir gerar o corpus em outro local, exporte a variável de ambiente `BICS_CORPUS_PATH` apontando para o arquivo gerado.

Para gerar o corpus usando o script incluído (requer `datasets`):

```bash
cd apps/codebug_bot
python scripts/prepare_dataset.py
# o script por padrão escreve em `data/corpus/python_outputs.txt` dentro do diretório onde for executado;
# se quiser que o arquivo esteja no local que o modelo espera, mova/concatene o resultado para
# `apps/codebug_bot/corpus/python_outputs.txt` ou defina `BICS_CORPUS_PATH`.
```
