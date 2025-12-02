from __future__ import annotations

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

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
        except Exception as exc:  # keep simple error handling for now
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "6060"))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
