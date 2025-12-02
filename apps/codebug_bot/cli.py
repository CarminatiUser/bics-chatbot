from __future__ import annotations

import argparse
import json
import sys

from .chatbot import chat_process


def main():
    parser = argparse.ArgumentParser(
        description="Analisa trecho de código e sugere correção."
    )
    parser.add_argument("--file", type=str, help="Arquivo com o código a analisar")
    parser.add_argument(
        "--apply-fix", action="store_true", help="Aplicar correções automáticas simples"
    )
    args = parser.parse_args()

    if args.file:
        code = open(args.file, encoding="utf-8").read()
    else:
        code = sys.stdin.read()

    out = chat_process(code, apply_fix=args.apply_fix)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
