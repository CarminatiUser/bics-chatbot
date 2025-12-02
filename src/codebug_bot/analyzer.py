from __future__ import annotations

import ast
from typing import Any

from .local_model import get_top_similar, score_code_naturalness


def analyze_code(code: str) -> dict[str, Any]:
    """
    Análise combinando:
    - modelo treinado no dataset (similaridade/naturalidade);
    - checagem de sintaxe via `ast.parse` para detectar erros como falta de ':'.
    """

    score = score_code_naturalness(code)
    similar_examples: list[dict[str, Any]] = get_top_similar(code, top_k=3)

    issues: list[dict[str, Any]] = []

    # Sinal 1: similaridade com o dataset
    if score < 0.3:
        issues.append(
            {
                "issue_type": "dataset_mismatch",
                "line": None,
                "col": None,
                "message": (
                    "O código parece pouco semelhante aos exemplos vistos no dataset "
                    "(baixa 'naturalidade' em relação ao corpus)."
                ),
                "confidence": float(1.0 - score),
            }
        )

    # Sinal 2: erro de sintaxe (por exemplo, falta de ':')
    try:
        ast.parse(code)
        has_syntax_error = False
    except SyntaxError as e:
        has_syntax_error = True
        msg = (e.msg or "").lower()
        issue_type = "syntax_error"
        message = f"Erro de sintaxe: {e.msg}"
        suggested_fix: str | None = None
        if "expected ':'" in msg:
            issue_type = "missing_colon"
            message = "Possível ':' ausente ao fim de um bloco (por exemplo em 'def' ou 'if')."
            suggested_fix = "Adicione ':' ao final da linha indicada."
        elif "was never closed" in msg or "unexpected eof while parsing" in msg:
            issue_type = "missing_parenthesis"
            message = "Parece faltar um parêntese ou fechamento de estrutura."
            suggested_fix = "Verifique os parênteses/colchetes/chaves e feche os que estiverem abertos."
        elif "string literal" in msg or "unterminated" in msg:
            issue_type = "missing_quotation"
            message = "Parece faltar o fechamento de uma string (aspas)."
            suggested_fix = "Feche as aspas da string na linha indicada."
        issues.append(
            {
                "issue_type": issue_type,
                "line": e.lineno,
                "col": e.offset,
                "message": message,
                "confidence": 0.95,
                "suggested_fix": suggested_fix,
            }
        )
    else:
        has_syntax_error = False

    analysis: dict[str, Any] = {
        "ok": (score >= 0.3) and not has_syntax_error,
        "issues": issues,
        "model_score": score,
        "similar_examples": similar_examples,
    }
    return analysis
