from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .chatbot import chat_process


class AnalyzerGUI:
    """Interface gráfica simples para inspecionar código com o BICS Chatbot."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("BICS Chatbot – Analisador de Código")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        # remove moldura padrão para podermos ter um header totalmente em dark mode
        self.root.overrideredirect(True)

        # Tema escuro básico
        self._apply_dark_theme()

        self.apply_fix_var = tk.BooleanVar(value=True)

        self._build_header_bar()
        self._build_layout()

    def _build_header_bar(self) -> None:
        """Barra de título customizada em dark mode, com botão de fechar."""
        header_bg = "#0b0b0b"
        header_fg = "#f5f5f5"

        self.header = tk.Frame(self.root, bg=header_bg, relief="flat", height=32)
        self.header.pack(fill=tk.X, side=tk.TOP)

        self.header_title = tk.Label(
            self.header,
            text="BICS Chatbot – Analisador de Código",
            bg=header_bg,
            fg=header_fg,
            padx=12,
        )
        self.header_title.pack(side=tk.LEFT, fill=tk.Y)

        close_btn = tk.Button(
            self.header,
            text="✕",
            bg=header_bg,
            fg=header_fg,
            activebackground="#c62828",
            activeforeground="#ffffff",
            borderwidth=0,
            padx=12,
            pady=4,
            command=self.root.destroy,
        )
        close_btn.pack(side=tk.RIGHT)

        # Permite arrastar a janela pela barra de título customizada
        self.header.bind("<ButtonPress-1>", self._start_move)
        self.header.bind("<B1-Motion>", self._do_move)
        self.header_title.bind("<ButtonPress-1>", self._start_move)
        self.header_title.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event: tk.Event) -> None:  # type: ignore[override]
        self._x_offset = event.x
        self._y_offset = event.y

    def _do_move(self, event: tk.Event) -> None:  # type: ignore[override]
        x = event.x_root - getattr(self, "_x_offset", 0)
        y = event.y_root - getattr(self, "_y_offset", 0)
        self.root.geometry(f"+{x}+{y}")

    def _apply_dark_theme(self) -> None:
        """Configura um tema escuro simples para a janela."""
        bg = "#121212"
        fg = "#f5f5f5"
        accent = "#1e88e5"
        accent_hover = "#42a5f5"
        secondary = "#1f1f1f"

        self.root.configure(bg=bg)
        style = ttk.Style(self.root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            # Fallback para o tema padrão se "clam" não estiver disponível
            pass

        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TCheckbutton", background=bg, foreground=fg)

        style.configure(
            "TButton",
            background=accent,
            foreground="#ffffff",
            borderwidth=0,
            padding=6,
        )
        style.map(
            "TButton",
            background=[("active", accent_hover)],
        )

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Código de entrada
        code_label = ttk.Label(main, text="Código para analisar")
        code_label.pack(anchor=tk.W)

        self.code_input = tk.Text(
            main,
            height=10,  # metade aproximadamente
            font=("Consolas", 11),
            undo=True,
            background="#0d1117",  # cor diferente do resultado
            foreground="#ffb74d",  # laranja suave para o código
            insertbackground="#f5f5f5",
        )
        self.code_input.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        # TAB visualmente e logicamente menor (recuo curto)
        self.code_input.configure(tabs=("0.8c",))
        self.code_input.bind("<Tab>", self._on_tab)

        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(0, 8))

        self.analyze_btn = ttk.Button(
            controls, text="Analisar código", command=self._on_analyze
        )
        self.analyze_btn.pack(side=tk.LEFT)

        clear_btn = ttk.Button(controls, text="Limpar", command=self._on_clear)
        clear_btn.pack(side=tk.LEFT, padx=(8, 0))

        apply_fix_cb = ttk.Checkbutton(
            controls,
            text="Aplicar correções automáticas",
            variable=self.apply_fix_var,
        )
        apply_fix_cb.pack(side=tk.LEFT, padx=(16, 0))

        # Resultado
        header_result = ttk.Frame(main)
        header_result.pack(fill=tk.X)

        result_label = ttk.Label(header_result, text="Resultado")
        result_label.pack(anchor=tk.W, side=tk.LEFT)

        # Indicador de loading em destaque
        self.loading_label = ttk.Label(
            header_result,
            text="",
            foreground="#ffb74d",
            font=("Segoe UI", 11, "bold"),
        )
        self.loading_label.pack(anchor=tk.E, side=tk.RIGHT, padx=(0, 8))

        self.result_output = tk.Text(
            main,
            height=16,
            font=("Consolas", 11),
            state=tk.DISABLED,
            background="#1e1e1e",
            foreground="#f5f5f5",
            insertbackground="#f5f5f5",
        )
        self.result_output.pack(fill=tk.BOTH, expand=True)

    def _on_clear(self) -> None:
        self.code_input.delete("1.0", tk.END)
        self._set_result("")

    def _on_analyze(self) -> None:
        code = self.code_input.get("1.0", tk.END).rstrip()
        if not code.strip():
            messagebox.showinfo(
                "BICS Chatbot", "Cole ou digite um código antes de analisar."
            )
            return

        # Mostra loading e desabilita botão enquanto analisa
        self.analyze_btn.config(state=tk.DISABLED)
        self.loading_label.config(text="ANALISANDO CÓDIGO...")
        self.root.update_idletasks()

        try:
            result = chat_process(code, apply_fix=self.apply_fix_var.get())
            rendered = self._render_result(result)
            self._set_result(rendered)
        except Exception as exc:  # pragma: no cover - salvaguarda da GUI
            messagebox.showerror("BICS Chatbot", f"Falha ao analisar código: {exc}")
        finally:
            self.loading_label.config(text="")
            self.analyze_btn.config(state=tk.NORMAL)

    def _set_result(self, text: str) -> None:
        self.result_output.configure(state=tk.NORMAL)
        self.result_output.delete("1.0", tk.END)
        self.result_output.insert(tk.END, text)
        self.result_output.configure(state=tk.DISABLED)

    @staticmethod
    def _on_tab(event: tk.Event) -> str:  # type: ignore[override]
        widget = event.widget
        if isinstance(widget, tk.Text):
            widget.insert(tk.INSERT, "  ")  # 2 espaços em vez de TAB longo
        return "break"

    def _render_result(self, result: dict[str, object]) -> str:
        analysis = result.get("analysis", {}) or {}
        issues = analysis.get("issues", []) or []
        ok = analysis.get("ok", False)
        model_score = analysis.get("model_score")
        similar_examples = analysis.get("similar_examples") or []

        lines: list[str] = []
        lines.append(
            "Status geral: OK" if ok else "Status geral: PROBLEMAS ENCONTRADOS"
        )

        if isinstance(model_score, (int, float)):
            lines.append(f"Score de similaridade com dataset: {model_score:.3f}")
        lines.append("")
        lines.append("Problemas encontrados:")
        if issues:
            for issue in issues:
                lines.append(f"- {self._format_issue(issue)}")
        else:
            lines.append("- Nenhum problema identificado.")

        if similar_examples:
            lines.append("")
            lines.append("Exemplos semelhantes do dataset:")
            for ex in similar_examples:
                code = ex.get("code", "")
                score = ex.get("score", 0.0)
                lines.append(f"- Score {float(score):.3f}")
                lines.append(code)
                lines.append("-" * 40)

        return "\n".join(lines)

    @staticmethod
    def _format_issue(issue: object) -> str:
        if not isinstance(issue, dict):
            return str(issue)
        issue_type = issue.get("issue_type", "desconhecido")
        line = issue.get("line")
        col = issue.get("col")
        message = issue.get("message", "")
        suggested_fix = issue.get("suggested_fix")
        location = "?"
        if line is not None:
            location = f"Linha {line}"
            if col is not None:
                location += f", Coluna {col}"
        confidence = issue.get("confidence")
        conf_txt = (
            f" (confiança {confidence:.2f})"
            if isinstance(confidence, (int, float))
            else ""
        )
        base = f"{location}: {issue_type}{conf_txt} — {message}"
        if suggested_fix:
            base += f" | Sugestão: {suggested_fix}"
        return base

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    AnalyzerGUI().run()


if __name__ == "__main__":
    main()
