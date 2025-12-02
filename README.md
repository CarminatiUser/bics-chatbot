# bics-chatbot

Chatbot em Python para **apontar defeitos em trechos de código** e explicar problemas.
Hoje ele combina:

- checagem de sintaxe com `ast.parse` (erros como falta de `:`, parênteses, aspas);
- um **modelo leve de ML local** (TF‑IDF) treinado em um dataset de códigos Python para medir
  quão “natural” é o trecho analisado em relação ao corpus.

## ⚙️ Instalação (dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Rodar API + Frontend (local)

1. Criar e ativar ambiente virtual e instalar dependências do Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Iniciar API:

```bash
python src/server.py
```

1. Iniciar Frontend:

```bash
cd frontend
npm install
npm run dev
```

O servidor de desenvolvimento do React faz proxy das requisições para /api/analyze para o servidor Flask quando ambos estão rodando na mesma máquina. Se você executar o servidor Flask em uma porta personalizada, altere a URL do fetch em frontend/src/App.jsx de acordo.


## 🖥️ Utilizando o código

```bash
python -m codebug_bot.gui
```

- Campo de texto para colar/escrever código.
- Botão “Analisar código” roda a análise completa (sintaxe + similaridade com dataset).
- Mostra problemas detectados, nível de confiança e exemplos semelhantes vindos do dataset.

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

O script `scripts/prepare_dataset.py` explica como baixar e limpar o dataset
[`iamtarun/python_code_instructions_18k_alpaca`](https://huggingface.co/datasets/iamtarun/python_code_instructions_18k_alpaca)
para gerar um **corpus** local de trechos Python válidos (coluna `output`).
Esse corpus é salvo em `data/corpus/python_outputs.txt` e é usado para:

- treinar o modelo TF‑IDF local na primeira execução;
- calcular o score de similaridade e trazer exemplos parecidos na interface.
