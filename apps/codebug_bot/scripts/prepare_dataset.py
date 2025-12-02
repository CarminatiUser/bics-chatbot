#!/usr/bin/env python3
"""
Baixa e prepara o dataset 'iamtarun/python_code_instructions_18k_alpaca' para formar um
corpus local de trechos Python válidos (coluna 'output').

Requer:
    pip install datasets tqdm
"""
import ast
import os

from datasets import load_dataset
from tqdm import tqdm

OUT_DIR = "data/corpus"
os.makedirs(OUT_DIR, exist_ok=True)


def is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def main():
    ds = load_dataset("iamtarun/python_code_instructions_18k_alpaca", split="train")
    kept = 0
    with open(os.path.join(OUT_DIR, "python_outputs.txt"), "w", encoding="utf-8") as f:
        for row in tqdm(ds, total=len(ds)):
            code = row.get("output") or ""
            if not code.strip():
                continue
            if is_valid_python(code):
                f.write(code.strip())
                f.write("\n\n# ---- SAMPLE SEP ----\n\n")
                kept += 1
    print(f"Trechos válidos: {kept}")


if __name__ == "__main__":
    main()
