import signal
import sys
import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

# Manejo de SIGTERM (graceful shutdown)
def handle_sigterm(*args):
    print("SIGTERM recibido, apagando servidor...")
    sys.exit(0

signal.signal(signal.SIGTERM, handle_sigterm)

# Conexión a PostgreSQL
def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "password")
    )

@app.route("/")
def index():
    return jsonify({"mensaje": "API funcionando", "status": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/usuarios")
def usuarios():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM usuarios;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"usuarios": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)