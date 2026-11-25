import sys
import os
import io
from fastapi.testclient import TestClient
from services.web.main import app
from services.web.database import registrar_usuario, crear_sesion, init_db

init_db()
client = TestClient(app)

print("--- 1. Test Cuenta de Evaluacion Dylan (User 1) ---")
res_dylan = client.get("/api/analytics")
assert res_dylan.status_code == 200, f"Status {res_dylan.status_code}"
data_dylan = res_dylan.json()
print("Dylan tiene_datos:", data_dylan.get("tiene_datos"), "Total accesos:", data_dylan["kpis"]["total_accesos"])
assert data_dylan.get("tiene_datos") is True
assert data_dylan["kpis"]["total_accesos"] == 65050

import time
print("\n--- 2. Test Registro de Nuevo Usuario / Gimnasio ---")
email_test = f"gimnasio_nuevo_{int(time.time())}@gmail.com"
nuevo_gym = registrar_usuario(email_test, "password123", "Alejandro Fitness", "Club Olimpo", 1, "Pro")
token = crear_sesion(nuevo_gym["id"])
print(f"Nuevo usuario: {nuevo_gym['nombre_dueno']} ({nuevo_gym['nombre_gym']}) - ID: {nuevo_gym['id']}")

client_nuevo = TestClient(app, cookies={"fitpulse_session": token})

print("\n--- 3. Verificando API Analytics de Nuevo Usuario ---")
res_anal = client_nuevo.get("/api/analytics")
assert res_anal.status_code == 200
data_anal = res_anal.json()
print("Analytics tiene_datos:", data_anal.get("tiene_datos"), "Total accesos:", data_anal["kpis"]["total_accesos"])
assert data_anal.get("tiene_datos") is False
assert data_anal["kpis"]["total_accesos"] == 0
assert len(data_anal["graficas"]["tendencia"]["accesos"]) == 0

print("\n--- 4. Verificando API Churn Radar de Nuevo Usuario ---")
res_churn = client_nuevo.get("/api/churn-radar")
assert res_churn.status_code == 200
data_churn = res_churn.json()
print("Churn Radar tiene_datos:", data_churn.get("tiene_datos"), "Total socios:", data_churn["total"])
assert data_churn.get("tiene_datos") is False
assert data_churn["total"] == 0
assert len(data_churn["socios"]) == 0

print("\n--- 5. Verificando Pronostico SARIMA de Nuevo Usuario ---")
res_pron = client_nuevo.get("/pronostico")
assert res_pron.status_code == 200
data_pron = res_pron.json()
print("Pronostico tiene_datos:", data_pron.get("tiene_datos"), "Fechas:", len(data_pron["fechas"]))
assert data_pron.get("tiene_datos") is False
assert len(data_pron["fechas"]) == 0

print("\n--- 6. Verificando HTML de Dashboard para Nuevo Usuario ---")
res_dash = client_nuevo.get("/dashboard")
assert res_dash.status_code == 200
html = res_dash.text
assert "Aun no has agregado la base de datos de tu gimnasio" in html
assert "Radar de Desercion y Churn sin datos" in html
assert "Base de Datos: Vacia (0 registros)" in html
assert "contenedorGraficasAnalitica\" class=\"hidden" in html
assert "contenedorChurnContenido\" class=\"hidden" in html
print("HTML verificado con exito: Empty state presente y graficas ocultas.")

print("\n--- 7. Verificando Subida de CSV para Nuevo Usuario ---")
csv_content = """fecha,id_socio,sucursal,plan_membresia,monto_mensualidad,duracion_minutos,dias_sin_asistir
2026-11-20 08:30,SOC-9001,Sucursal Norte,VIP,1200.0,75,2
2026-11-21 09:15,SOC-9002,Sucursal Norte,General,700.0,55,9
2026-11-22 18:00,SOC-9003,Sucursal Norte,Estudiante,450.0,60,5
"""
files = {"file": ("mis_accesos.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
res_upload = client_nuevo.post("/api/upload-csv", files=files)
assert res_upload.status_code == 200, f"Upload status {res_upload.status_code}: {res_upload.text}"
upload_data = res_upload.json()
print("Upload status:", upload_data["status"], "Registros:", upload_data["registros"])
assert upload_data["status"] == "ok"
assert upload_data["registros"] == 3

# Verificar que tras la subida, las metricas y graficas se activan
res_anal_post = client_nuevo.get("/api/analytics")
data_anal_post = res_anal_post.json()
print("Post-upload analytics tiene_datos:", data_anal_post.get("tiene_datos"), "Total accesos:", data_anal_post["kpis"]["total_accesos"])
assert data_anal_post.get("tiene_datos") is True
assert data_anal_post["kpis"]["total_accesos"] == 3

res_churn_post = client_nuevo.get("/api/churn-radar")
data_churn_post = res_churn_post.json()
print("Post-upload churn tiene_datos:", data_churn_post.get("tiene_datos"), "Total socios:", data_churn_post["total"])
assert data_churn_post.get("tiene_datos") is True
assert data_churn_post["total"] == 3

# Limpiar archivo de prueba
user_csv = os.path.join(os.path.dirname(__file__), "..", "services", "web", "static", "uploads", f"custom_data_user_{nuevo_gym['id']}.csv")
if os.path.exists(user_csv):
    os.remove(user_csv)

print("\n--- TODAS LAS PRUEBAS PASARON EXITOSAMENTE AL 100% ---")
