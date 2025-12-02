from __future__ import annotations

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Ensure the parent 'apps' folder is on sys.path so package imports like
# `from codebug_bot.chatbot import chat_process` work when running this file
# from the monorepo root or from `apps/api`.
import sys
ROOT_APPS = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_APPS not in sys.path:
    sys.path.insert(0, ROOT_APPS)

from codebug_bot.chatbot import chat_process


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/analyze")
    def analyze():
        data = request.get_json(silent=True) or {}
        code = data.get("code")
        apply_fix = data.get("apply_fix", True)
        if code is None:
            return jsonify({"error": "Missing 'code' in request body"}), 400
        try:
            out = chat_process(code, apply_fix=bool(apply_fix))
            return jsonify(out)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "6060"))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
