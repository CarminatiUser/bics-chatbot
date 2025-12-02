import sys
from pathlib import Path

# Garante que a pasta "src" esteja no sys.path quando rodar os testes localmente,
# sem precisar instalar o pacote ou configurar PYTHONPATH manualmente.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from codebug_bot.analyzer import analyze_code


def test_missing_colon():
    code = "def f(x)\n    return x"
    result = analyze_code(code)
    kinds = [i["issue_type"] for i in result["issues"]]
    assert "missing_colon" in kinds


def test_missing_parenthesis():
    code = "print((1+2)"
    result = analyze_code(code)
    kinds = [i["issue_type"] for i in result["issues"]]
    assert "missing_parenthesis" in kinds or "syntax_error" in kinds
