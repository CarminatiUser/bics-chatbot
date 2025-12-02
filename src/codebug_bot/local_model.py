from __future__ import annotations

"""
Modelo "local" treinado em cima do corpus de códigos válidos.

Aqui usamos um modelo bem leve de ML baseado em TF-IDF de n-gramas de caracteres
para funcionar como um "language model" simplificado:

- Treinamento: ajusta um TfidfVectorizer nos trechos válidos do corpus.
- Inferência: para um código de entrada, calcula quão parecido ele é com o corpus.

Isso nos dá uma pontuação de "naturalidade" do código Python em relação ao dataset.
"""

import os
from functools import lru_cache
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CORPUS_PATH = os.getenv(
    "BICS_CORPUS_PATH",
    os.path.join("data", "corpus", "python_outputs.txt"),
)


def _load_corpus(path: str = CORPUS_PATH) -> list[str]:
    if not os.path.exists(path):
        raise RuntimeError(
            f"Corpus não encontrado em '{path}'. "
            "Rode 'scripts/prepare_dataset.py' antes de usar o modelo local."
        )
    snippets: list[str] = []
    with open(path, encoding="utf-8") as f:
        buf: list[str] = []
        for line in f:
            if line.strip() == "# ---- SAMPLE SEP ----":
                code = "\n".join(buf).strip()
                if code:
                    snippets.append(code)
                buf = []
            else:
                buf.append(line.rstrip("\n"))
        # último trecho, se houver
        last = "\n".join(buf).strip()
        if last:
            snippets.append(last)
    if not snippets:
        raise RuntimeError(
            f"Nenhum trecho carregado do corpus em '{path}'. "
            "Verifique se o script de preparação rodou corretamente."
        )
    return snippets


@lru_cache(maxsize=1)
def _get_vectorizer_and_matrix() -> tuple[TfidfVectorizer, Any]:
    """
    Carrega o corpus e treina o modelo TF-IDF de forma preguiçosa (na primeira chamada).
    """
    snippets = _load_corpus()
    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=1,
    )
    matrix = vectorizer.fit_transform(snippets)
    return vectorizer, matrix


def score_code_naturalness(code: str, top_k: int = 5) -> float:
    """
    Retorna uma pontuação de "naturalidade" do código com base na similaridade
    com os exemplos do corpus (média das top_k similaridades de cosseno).
    """
    if not code.strip():
        return 0.0
    vectorizer, matrix = _get_vectorizer_and_matrix()
    vec = vectorizer.transform([code])
    sims = cosine_similarity(vec, matrix)[0]
    if sims.size == 0:
        return 0.0
    sims_sorted = sorted(sims, reverse=True)[: max(1, top_k)]
    return float(sum(sims_sorted) / len(sims_sorted))


def get_top_similar(code: str, top_k: int = 3) -> list[dict[str, Any]]:
    """
    Retorna os top_k trechos do corpus mais semelhantes ao código fornecido.
    Cada item contém: {"code": str, "score": float}.
    """
    if not code.strip():
        return []
    vectorizer, matrix = _get_vectorizer_and_matrix()
    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus_text = f.read()
    snippets = [
        s.strip() for s in corpus_text.split("# ---- SAMPLE SEP ----") if s.strip()
    ]
    vec = vectorizer.transform([code])
    sims = cosine_similarity(vec, matrix)[0]
    idx_scores = sorted(
        enumerate(sims),
        key=lambda x: x[1],
        reverse=True,
    )[: max(1, top_k)]
    results: list[dict[str, Any]] = []
    for idx, score in idx_scores:
        if 0 <= idx < len(snippets):
            results.append({"code": snippets[idx], "score": float(score)})
    return results
