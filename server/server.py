from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/alerta", methods=["POST"])
def alerta():
    data = request.get_json(force=True, silent=True) or {}
    data["_received_at"] = datetime.utcnow().isoformat() + "Z"
    print(f"[ALERTA] {data}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Para testes locais
    app.run(host="0.0.0.0", port=5000)
