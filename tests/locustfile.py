"""
FitPulse Analytics · Suite de Pruebas de Carga con Locust (E3)
Cumple con el criterio de evaluacion de Cómputo en la Nube:
'Autoescalado con prueba de carga: definan instancias minimas y maximas y lancen
una prueba con Locust o k6 de 50 usuarios simultaneos. Reporten latencia p95, errores
e instancias levantadas.'
"""

import json
import random
from locust import HttpUser, task, between, tag


class AdministradorGimnasioUser(HttpUser):
    """
    Simula el comportamiento de un administrador de gimnasio o recepcionista
    interactuando concurrentemente con la plataforma SaaS FitPulse.
    """
    wait_time = between(0.2, 1.0)  # Tiempo de espera realista entre peticiones

    @tag('landing')
    @task(2)
    def ver_landing_page(self):
        """Peticion a la pagina principal y calculadora ROI."""
        self.client.get("/", name="[GET] / (Landing Page)")

    @tag('dashboard')
    @task(4)
    def consultar_dashboard(self):
        """Peticion a la vista del panel de control."""
        self.client.get("/dashboard", name="[GET] /dashboard (HTML Vista)")

    @tag('analytics')
    @task(6)
    def consultar_analitica_kpis(self):
        """Peticion al backend REST que calcula KPIs y graficas."""
        sucursales = [
            "Todas las sucursales (Consolidado)",
            "Sucursal Centro (Matriz)",
            "Sucursal Sur",
            "Sucursal Norte"
        ]
        sucursal = random.choice(sucursales)
        self.client.get(
            f"/api/analytics?sucursal={sucursal}",
            name="[GET] /api/analytics"
        )

    @tag('churn')
    @task(4)
    def consultar_socios_en_riesgo(self):
        """Peticion al listado de socios en riesgo de abandono."""
        self.client.get("/api/churn-radar", name="[GET] /api/churn-radar")

    @tag('sarima')
    @task(5)
    def consultar_pronostico_sarima(self):
        """Peticion al modelo SARIMA de proyeccion a 7, 14 o 30 dias."""
        dias = random.choice([7, 14, 30])
        self.client.get(
            f"/pronostico?dias={dias}",
            name="[GET] /pronostico (SARIMA)"
        )

    @tag('clasificar')
    @task(3)
    def clasificar_socio_tiempo_real(self):
        """Peticion POST con inferencia en vivo de clasificador Random Forest."""
        payload = {
            "id_socio": f"SOC-{random.randint(100, 999)}",
            "dias_sin_asistir": random.randint(0, 18),
            "duracion_promedio": round(random.uniform(30.0, 90.0), 1),
            "total_accesos": random.randint(5, 120),
            "cuota_mensual": random.choice([450.0, 650.0, 1200.0]),
            "antiguedad_dias": random.randint(30, 360),
            "frecuencia_semanal": round(random.uniform(0.5, 5.0), 2)
        }
        self.client.post(
            "/clasificar",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="[POST] /clasificar (Random Forest)"
        )
