# FitPulse Analytics

> Plataforma SaaS B2B de inteligencia analitica, prediccion de afluencia y retencion de socios para centros fitness y gimnasios independientes.

Desarrollada para el **Proyecto Integrador DATA STARTUP**  
*Computo en la Nube (IAD-2408) x Analitica de Datos (IAD-2403)*  
*Ingenieria en Inteligencia Artificial*

---

## Mision del Negocio
FitPulse resuelve el mayor problema financiero de los gimnasios: el **50-60% de desercion en los primeros 90 dias**.  
Mediante la ingesta de registros de acceso de torniquetes y cobros, FitPulse calcula la probabilidad de abandono (*Anti-Churn*), proyecta la afluencia de personas a 7-14 dias para optimizar turnos de entrenadores y detecta ciclos de ingresos mediante analisis espectral de Fourier.

---

## Estructura del Repositorio

```text
fitpulse-startup/
├── README.md                # Presentacion general y manual de arranque
├── docs/
│   └── E0-propuesta.md      # Lean Canvas, entrevista de validacion, costos e inventario
├── data/
│   └── sample/              # Datasets raw y clean con mas de 65,000 registros
├── notebooks/
│   └── generar_datos_gimnasio.py # Generador sintetico con estacionalidad y errores
├── services/
│   ├── web/                 # Aplicacion Web (FastAPI + Landing + Dashboard nativo)
│   ├── worker/              # Modulo de limpieza y calidad de datos (5 errores)
│   ├── ingesta/             # Microservicio de ingesta FastAPI
│   └── modelos/             # API de modelos predictivos
├── tests/
│   └── test_limpieza.py     # Pruebas unitarias automatizadas del worker
├── infra/terraform/         # Infraestructura como codigo
├── k8s/                     # Manifiestos de Kubernetes
└── docker-compose.yml       # Orquestacion de servicios en local
```

---

## Como Iniciar la Aplicacion Web en Local

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar el Servidor Web (FastAPI + Uvicorn):**
   ```bash
   python -m uvicorn services.web.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Abre tu navegador en `http://localhost:8000`.

3. **Ejecutar pruebas unitarias de limpieza:**
   ```bash
   python tests/test_limpieza.py
   ```

---

## Planes Comerciales (SaaS)
* **Basico ($499 MXN/mes):** Multi-sucursal (hasta 2 sedes), monitoreo diario, 6 visualizaciones clave y carga de CSV.
* **Pro ($899 MXN/mes):** Multi-sucursal (hasta 5 sedes), alertas tempranas Anti-Churn, socios en riesgo y FFT de quincenas.
* **Premium ($1,499 MXN/mes):** Multi-sucursal ilimitada, conexion API a torniquete, soporte multi-sucursal y pronostico a 30 dias.
