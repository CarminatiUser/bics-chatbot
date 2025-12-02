from __future__ import annotations

from typing import Any

from .analyzer import analyze_code


def chat_process(user_code: str, apply_fix: bool = True) -> dict[str, Any]:
    """
    Pipeline principal de análise usando SOMENTE o modelo local treinado no dataset.

    - `analyzer.analyze_code` usa o modelo TF‑IDF treinado no corpus
      para avaliar a naturalidade do código e trazer exemplos parecidos.
    - Não há mais heurísticas manuais nem LLM externo neste pipeline.
    """

    analysis = analyze_code(user_code)
    # Mantemos a chave para compatibilidade com a GUI/CLI, mas agora
    # não geramos código corrigido automaticamente — apenas análise baseada no dataset.
    return {"analysis": analysis, "fixed_code": None}
