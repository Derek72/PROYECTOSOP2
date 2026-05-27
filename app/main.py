import signal
import sys
import os
import psycopg2
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

def handle_sigterm(*args):
    print("SIGTERM recibido, apagando servidor...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "postgres-service"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "password123")
    )

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            );
        """)
        cur.execute("SELECT COUNT(*) FROM tasks;")
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("""
                INSERT INTO tasks (description, completed) VALUES
                ('Configurar Docker con multi-stage build', TRUE),
                ('Desplegar cluster en GKE', TRUE),
                ('Configurar HPA y autoscaling', TRUE),
                ('Configurar IP estatica en GCP', TRUE),
                ('Implementar CI/CD con GitHub Actions', TRUE),
                ('Configurar Google Cloud Monitoring', TRUE);
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inicializando DB: {e}")

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
        .task-row { background: #0f172a; border-radius: 6px; padding: 12px; margin: 8px 0; display: flex; align-items: center; gap: 12px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #0f172a; padding: 10px; text-align: left; color: #3b82f6; }
        td { padding: 10px; border-bottom: 1px solid #334155; }
        .form-row { display: flex; gap: 10px; margin-bottom: 16px; }
        .form-row input { flex: 1; padding: 10px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #e2e8f0; font-size: 14px; }
        .btn { padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer; font-size: 14px; font-weight: bold; }
        .btn-add { background: #3b82f6; color: white; }
        .btn-done { background: #064e3b; color: #34d399; padding: 4px 10px; font-size: 12px; }
        .btn-delete { background: #7f1d1d; color: #fca5a5; padding: 4px 10px; font-size: 12px; }
        footer { text-align: center; padding: 20px; color: #475569; font-size: 12px; }
    </style>
</head>
<body>
    <header>
        <h1>🚀 Proyecto Final - Sistemas Operativos 2</h1>
        <p>Universidad Mariano Gálvez de Guatemala &nbsp;|&nbsp; Desplegado en Google Kubernetes Engine</p>
    </header>
    <div class="container">
        <div class="cards">
            <div class="card">
                <h3>Estado</h3>
                <p>✅ Online</p>
                <div class="sub">API + PostgreSQL activos</div>
            </div>
            <div class="card">
                <h3>Plataforma</h3>
                <p>GKE</p>
                <div class="sub">cluster-sop2 | us-central1</div>
            </div>
            <div class="card">
                <h3>Réplicas</h3>
                <p>2 Pods</p>
                <div class="sub">HPA habilitado</div>
            </div>
        </div>

        <div class="section">
            <h2>📋 Gestión de Tareas (PostgreSQL)</h2>
            <div class="form-row">
                <input type="text" id="newTask" placeholder="Escribe una nueva tarea..." />
                <button class="btn btn-add" onclick="addTask()">+ Agregar</button>
            </div>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
                <tbody id="taskList"></tbody>
            </table>
        </div>

        <div class="section">
            <h2>📦 Infraestructura GCP</h2>
            <div class="task-row">
                <span>🔵</span><span>Clúster GKE: <strong>cluster-sop2</strong></span>
                <span class="badge green" style="margin-left:auto">Running</span>
            </div>
            <div class="task-row">
                <span>🔵</span><span>IP Estática: <strong>136.111.214.27</strong></span>
                <span class="badge green" style="margin-left:auto">Asignada</span>
            </div>
            <div class="task-row">
                <span>🔵</span><span>Artifact Registry: <strong>proyecto-repo</strong></span>
                <span class="badge green" style="margin-left:auto">Activo</span>
            </div>
            <div class="task-row">
                <span>🔵</span><span>CI/CD: <strong>GitHub Actions</strong></span>
                <span class="badge green" style="margin-left:auto">Configurado</span>
            </div>
        </div>
    </div>
    <footer>Proyecto Final SOP2 &nbsp;|&nbsp; Universidad Mariano Gálvez 2026</footer>

    <script>
        async function loadTasks() {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            const tbody = document.getElementById('taskList');
            tbody.innerHTML = '';
            tasks.forEach(t => {
                tbody.innerHTML += `
                    <tr>
                        <td>${t.id}</td>
                        <td>${t.description}</td>
                        <td>${t.completed ? '<span class="badge green">✅ Completado</span>' : '<span class="badge" style="background:#7c2d12;color:#fb923c">⏳ Pendiente</span>'}</td>
                        <td>
                            ${!t.completed ? `<button class="btn btn-done" onclick="completeTask(${t.id})">✔ Completar</button>` : ''}
                            <button class="btn btn-delete" onclick="deleteTask(${t.id})">🗑 Eliminar</button>
                        </td>
                    </tr>`;
            });
        }

        async function addTask() {
            const input = document.getElementById('newTask');
            if (!input.value.trim()) return;
            await fetch('/api/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({description: input.value})
            });
            input.value = '';
            loadTasks();
        }

        async function completeTask(id) {
            await fetch('/api/tasks/' + id, {method: 'PUT'});
            loadTasks();
        }

        async function deleteTask(id) {
            await fetch('/api/tasks/' + id, {method: 'DELETE'});
            loadTasks();
        }

        loadTasks();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, description, completed FROM tasks ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{"id": r[0], "description": r[1], "completed": r[2]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (description) VALUES (%s) RETURNING id;", (data["description"],))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id, "description": data["description"], "completed": False}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def complete_task(task_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = TRUE WHERE id = %s;", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)