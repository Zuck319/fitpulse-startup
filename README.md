# FitPulse Analytics 🏋️‍♂️

> Plataforma SaaS B2B de inteligencia analítica, predicción de afluencia y retención de socios para centros fitness y gimnasios independientes.

Desarrollada para el **Proyecto Integrador DATA STARTUP**  
*Cómputo en la Nube (IAD-2408) × Analítica de Datos (IAD-2403)*  
*Ingeniería en Inteligencia Artificial*

---

## 🚀 Misión del Negocio
FitPulse resuelve el mayor problema financiero de los gimnasios: el **50-60% de deserción en los primeros 90 días**.  
Mediante la ingesta de registros de acceso de torniquetes y cobros, FitPulse calcula la probabilidad de abandono (*Anti-Churn*), proyecta la afluencia de personas a 7-14 días para optimizar turnos de entrenadores y detecta ciclos de ingresos mediante análisis espectral de Fourier.

---

## 📦 Estructura del Repositorio

```text
fitpulse-startup/
├── README.md                # Presentación general y manual de arranque
├── docs/
│   └── E0-propuesta.md      # Lean Canvas, entrevista de validación, costos e inventario
├── data/
│   └── sample/              # Datasets raw y clean con más de 65,000 registros
├── notebooks/
│   └── generar_datos_gimnasio.py # Generador sintético con estacionalidad y errores
├── services/
│   ├── tablero/             # Dashboard interactivo con Streamlit y personalización de logo
│   ├── worker/              # Módulo de limpieza y calidad de datos (5 errores)
│   ├── ingesta/             # Microservicio de ingesta FastAPI
│   └── modelos/             # API de modelos predictivos
├── tests/
│   └── test_limpieza.py     # Pruebas unitarias automatizadas del worker
├── infra/terraform/         # Infraestructura como código
├── k8s/                     # Manifiestos de Kubernetes
└── docker-compose.yml       # Orquestación de servicios en local
```

---

## 🛠️ Cómo Iniciar el Dashboard en Local

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar el Tablero (Streamlit):**
   ```bash
   streamlit run services/tablero/app.py
   ```
   Abre tu navegador en `http://localhost:8501`.

3. **Ejecutar pruebas unitarias de limpieza:**
   ```bash
   python tests/test_limpieza.py
   ```

---

## 💳 Planes Comerciales (SaaS)
* **Básico ($499 MXN/mes):** Monitoreo diario, 6 visualizaciones clave y carga de CSV.
* **Pro ($899 MXN/mes):** Alertas tempranas Anti-Churn, socios en riesgo y FFT de quincenas.
* **Premium ($1,499 MXN/mes):** Conexión API a torniquete, soporte multi-sucursal y pronóstico a 30 días.
