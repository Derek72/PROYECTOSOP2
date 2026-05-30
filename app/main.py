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
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; color: #1a1a1a; }
        header { background: white; padding: 20px 40px; border-bottom: 1px solid #e0e0e0; }
        header h1 { font-size: 18px; font-weight: 600; color: #1a1a1a; }
        header p { color: #888; font-size: 13px; margin-top: 4px; }
        .container { max-width: 900px; margin: 32px auto; padding: 0 20px; }
        .cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
        .card { background: white; border-radius: 6px; padding: 20px; border: 1px solid #e0e0e0; }
        .card h3 { font-size: 11px; text-transform: uppercase; color: #888; margin-bottom: 8px; letter-spacing: 1px; }
        .card p { font-size: 22px; font-weight: 600; color: #1a1a1a; }
        .card .sub { font-size: 12px; color: #bbb; margin-top: 4px; }
        .section { background: white; border-radius: 6px; padding: 24px; margin-bottom: 16px; border: 1px solid #e0e0e0; }
        .section h2 { font-size: 14px; font-weight: 600; margin-bottom: 16px; color: #1a1a1a; text-transform: uppercase; letter-spacing: 1px; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-size: 12px; }
        .green { background: #e6f4ea; color: #2d6a4f; }
        .pending { background: #fff3e0; color: #b45309; }
        .task-row { background: #fafafa; border-radius: 4px; padding: 12px 16px; margin: 8px 0; display: flex; align-items: center; gap: 12px; border: 1px solid #e0e0e0; font-size: 14px; }
        table { width: 100%; border-collapse: collapse; }
        th { padding: 10px; text-align: left; color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #e0e0e0; font-weight: 500; }
        td { padding: 12px 10px; border-bottom: 1px solid #f0f0f0; font-size: 14px; color: #1a1a1a; }
        .form-row { display: flex; gap: 10px; margin-bottom: 16px; }
        .form-row input { flex: 1; padding: 10px 12px; background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px; color: #1a1a1a; font-size: 14px; outline: none; }
        .btn { padding: 10px 16px; border-radius: 4px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; }
        .btn-add { background: #1a1a1a; color: white; }
        .btn-done { background: #e6f4ea; color: #2d6a4f; padding: 5px 12px; font-size: 12px; }
        .btn-delete { background: #fdecea; color: #c0392b; padding: 5px 12px; font-size: 12px; }
        footer { text-align: center; padding: 24px; color: #bbb; font-size: 12px; }
    </style>
</head>
<body>
    <header>
        <h1>Proyecto Final — Sistemas Operativos II</h1>
        <p>Universidad Mariano Galvez de Guatemala &nbsp;|&nbsp; Google Kubernetes Engine</p>
    </header>
    <div class="container">
        <div class="cards">
            <div class="card">
                <h3>Estado</h3>
                <p>Online</p>
                <div class="sub">API + PostgreSQL activos</div>
            </div>
            <div class="card">
                <h3>Plataforma</h3>
                <p>GKE</p>
                <div class="sub">cluster-sop2 | us-central1</div>
            </div>
            <div class="card">
                <h3>Replicas</h3>
                <p>2 Pods</p>
                <div class="sub">HPA habilitado</div>
            </div>
        </div>

        <div class="section">
            <h2>Gestion de Tareas (PostgreSQL)</h2>
            <div class="form-row">
                <input type="text" id="newTask" placeholder="Nueva tarea..." />
                <button class="btn btn-add" onclick="addTask()">Agregar</button>
            </div>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Descripcion</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
                <tbody id="taskList"></tbody>
            </table>
        </div>

        <div class="section">
            <h2>Infraestructura GCP</h2>
            <div class="task-row">
                <span>Cluster GKE: <strong>cluster-sop2</strong></span>
                <span class="badge green" style="margin-left:auto">Running</span>
            </div>
            <div class="task-row">
                <span>IP Estatica: <strong>136.111.214.27</strong></span>
                <span class="badge green" style="margin-left:auto">Asignada</span>
            </div>
            <div class="task-row">
                <span>Artifact Registry: <strong>proyecto-repo</strong></span>
                <span class="badge green" style="margin-left:auto">Activo</span>
            </div>
            <div class="task-row">
                <span>CI/CD: <strong>GitHub Actions</strong></span>
                <span class="badge green" style="margin-left:auto">Configurado</span>
            </div>
        </div>
    </div>
    <footer>Proyecto Final SOP2 &nbsp;|&nbsp; Universidad Mariano Galvez 2026</footer>

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
                        <td>${t.completed ? '<span class="badge green">Completado</span>' : '<span class="badge pending">Pendiente</span>'}</td>
                        <td style="display:flex;gap:6px;padding-top:10px">
                            ${!t.completed ? `<button class="btn btn-done" onclick="completeTask(${t.id})">Completar</button>` : ''}
                            <button class="btn btn-delete" onclick="deleteTask(${t.id})">Eliminar</button>
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
