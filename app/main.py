import signal
import sys
import os
import psycopg2
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Manejo de SIGTERM (graceful shutdown)
def handle_sigterm(*args):
    print("SIGTERM recibido, apagando servidor...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

# Conexión a PostgreSQL
def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "password")
    )

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Proyecto SOP2 - UMG</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; }
        header { background: #1e293b; padding: 20px 40px; border-bottom: 2px solid #3b82f6; }
        header h1 { color: #3b82f6; font-size: 24px; }
        header p { color: #94a3b8; font-size: 14px; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
        .card { background: #1e293b; border-radius: 10px; padding: 24px; border: 1px solid #334155; }
        .card h3 { color: #3b82f6; margin-bottom: 8px; font-size: 14px; text-transform: uppercase; }
        .card p { font-size: 28px; font-weight: bold; }
        .card .sub { font-size: 12px; color: #64748b; margin-top: 4px; }
        .section { background: #1e293b; border-radius: 10px; padding: 24px; margin-bottom: 20px; border: 1px solid #334155; }
        .section h2 { color: #3b82f6; margin-bottom: 16px; }
        .badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 4px; }
        .green { background: #064e3b; color: #34d399; }
        .blue { background: #1e3a5f; color: #60a5fa; }
        .endpoint { background: #0f172a; border-radius: 6px; padding: 12px; margin: 8px 0; display: flex; align-items: center; gap: 12px; }
        .method { background: #1d4ed8; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        footer { text-align: center; padding: 20px; color: #475569; font-size: 12px; }
    </style>
</head>
<body>
    <header>
        <h1>🚀 Proyecto Final - Sistemas Operativos 2</h1>
        <p>Universidad Mariano Gálvez de Guatemala &nbsp;|&nbsp; Aplicación desplegada en Google Kubernetes Engine</p>
    </header>
    <div class="container">
        <div class="cards">
            <div class="card">
                <h3>Estado del Sistema</h3>
                <p>✅ Online</p>
                <div class="sub">API funcionando correctamente</div>
            </div>
            <div class="card">
                <h3>Plataforma</h3>
                <p>GKE</p>
                <div class="sub">Google Kubernetes Engine</div>
            </div>
            <div class="card">
                <h3>Réplicas</h3>
                <p>2 Pods</p>
                <div class="sub">Con HPA habilitado</div>
            </div>
        </div>

        <div class="section">
            <h2>🏗️ Stack Tecnológico</h2>
            <span class="badge green">Python Flask</span>
            <span class="badge green">PostgreSQL</span>
            <span class="badge blue">Docker</span>
            <span class="badge blue">Kubernetes</span>
            <span class="badge blue">Google Cloud</span>
            <span class="badge blue">GitHub Actions</span>
        </div>

        <div class="section">
            <h2>🔌 Endpoints Disponibles</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <span>/</span>
                <span style="color:#94a3b8; margin-left:auto">Página principal</span>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span>/health</span>
                <span style="color:#94a3b8; margin-left:auto">Health check del sistema</span>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span>/usuarios</span>
                <span style="color:#94a3b8; margin-left:auto">Lista de usuarios en PostgreSQL</span>
            </div>
        </div>

        <div class="section">
            <h2>📦 Infraestructura</h2>
            <div class="endpoint">
                <span>🔵</span>
                <span>Clúster GKE: <strong>cluster-sop2</strong></span>
                <span class="badge green" style="margin-left:auto">Running</span>
            </div>
            <div class="endpoint">
                <span>🔵</span>
                <span>IP Estática: <strong>136.111.214.27</strong></span>
                <span class="badge green" style="margin-left:auto">Asignada</span>
            </div>
            <div class="endpoint">
                <span>🔵</span>
                <span>Artifact Registry: <strong>proyecto-repo</strong></span>
                <span class="badge green" style="margin-left:auto">Activo</span>
            </div>
            <div class="endpoint">
                <span>🔵</span>
                <span>CI/CD: <strong>GitHub Actions</strong></span>
                <span class="badge green" style="margin-left:auto">Configurado</span>
            </div>
        </div>
    </div>
    <footer>Proyecto Final SOP2 &nbsp;|&nbsp; Derek Ruiz &nbsp;|&nbsp; Universidad Mariano Gálvez 2026</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

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