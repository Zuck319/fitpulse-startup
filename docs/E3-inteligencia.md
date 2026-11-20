# E3 · Inteligencia en Produccion: El Modelo Vive en la Nube
**Proyecto Integrador:** FitPulse Analytics - Data Startup SaaS  
**Materias:** Cómputo en la Nube (IAD-2408) & Analítica de Datos (IAD-2403)  
**Autor:** Dylan Espinosa (Numero de Control: 25460308)  
**Institucion:** Instituto Tecnologico de Colima (TecNM)  
**Fecha:** Noviembre de 2026  
**Repositorio Oficial:** [https://github.com/Zuck319/fitpulse-startup](https://github.com/Zuck319/fitpulse-startup)

---

## 1. Resumen Ejecutivo de la Entrega

El entregable E3 marca la transicion definitiva desde la experimentacion en notebooks hacia un sistema productivo de grado empresarial. En esta fase, los modelos de Inteligencia Artificial y Machine Learning se integran en una arquitectura contenerizada y orquestada en la nube, capaz de responder a picos de demanda mediante autoescalado horizontal y servir inferencias en tiempo real a traves de una API REST validada.

FitPulse Analytics implementa:
1. **Analitica Predictiva:** Modelo SARIMA $(1, 1, 1) \times (1, 1, 1)_7$ con bandas de confianza al 95% para la proyeccion de afluencia diaria en torniquetes, validado con prueba de Dickey-Fuller Aumentada (ADF) y criterio de informacion de Akaike (AIC).
2. **Clasificacion de Socios (Churn):** Comparativa metodologica formal entre Random Forest y Regresion Logistica regularizada con justificacion de la metrica Recall como objetivo critico del negocio.
3. **Contenedores Ligeros Multi-Stage:** Un `Dockerfile` optimizado por microservicio (`web`, `modelos`, `worker`) y un orquestador local `docker-compose.yml`.
4. **Orquestacion en Kubernetes:** Manifiestos de `Deployment`, `Service` y `HorizontalPodAutoscaler` (HPA) configurado para autoescalar de 2 a 10 replicas al 70% de utilizacion de CPU.
5. **Worker Serverless:** Adaptador de procesamiento stateless activado por eventos de almacenamiento en `raw/` compatible con Google Cloud Functions y AWS Lambda.
6. **Prueba de Carga con Locust:** Evaluacion de estres con 50 usuarios simultaneos reportando percentil 95 (p95), solicitudes por segundo y 0% de errores.
7. **Infraestructura como Codigo (IaC):** Configuracion completa de Terraform (`main.tf`, `variables.tf`, `outputs.tf`) declarando almacenamiento seguro, colas de mensajeria e identidades IAM con principio de minimo privilegio.

---

## 2. Analitica de Datos: Modelado e Inferencia Predictiva

### 2.1 Justificacion de Computo para Entrenamiento: CPU vs. GPU

Para el caso de uso especifico de FitPulse Analytics, se determino utilizar **CPU (Central Processing Unit)** para todo el pipeline de entrenamiento e inferencia, descartando el aprovisionamiento de GPU (Graphics Processing Unit).

#### Justificacion Tecnica y Economica (FinOps):
* **Dimension del Dataset:** La serie temporal consolidada consta de 638 observaciones diarias (del 1 de enero de 2025 al 30 de septiembre de 2026). El dataset de socios para clasificacion tabular abarca 250 socios con 6 variables de comportamiento calculadas sobre 65,050 transacciones de torniquete.
* **Naturaleza Algoritmica:** Los modelos empleados son SARIMA (estimacion de maxima verosimilitud sobre parametros autoregresivos y de media movil) y Random Forest / Regresion Logistica (operaciones matriciales de baja dimensionalidad). Estos algoritmos no aprovechan la arquitectura altamente paralela de miles de nucleos CUDA o tensores propia de las redes neuronales profundas (Deep Learning).
* **Rendimiento Medido:** El reentrenamiento completo de la serie SARIMA y del ensamble Random Forest tomo **4.82 segundos** en un entorno estandar de 2 vCPUs x86_64, con un pico de consumo de memoria RAM inferior a 210 MB.
* **Alineacion de Presupuesto ($0 FinOps):** Una instancia en la nube con GPU dedicada (e.g., NVIDIA T4 o A100 en Google Cloud o AWS) genera un costo recurrente base de entre $180 y $650 USD mensuales aun cuando este inactiva. Al utilizar CPU bajo demanda en Cloud Run o Kubernetes, el costo de computo se mantiene dentro de la capa gratuita ($0.00 USD), optimizando al maximo el margen del negocio SaaS.

---

### 2.2 Modelado de Series Temporales: SARIMA

La afluencia de un gimnasio presenta una fuerte dependencia estacional semanal: los lunes y martes registran el maximo volumen de visitas, mientras que los viernes por la noche, sabados por la tarde y domingos experimentan caidas drasticas de asistencia.

#### 2.2.1 Formulacion Matematica del Modelo
El modelo ajustado corresponde a un proceso **SARIMA $(1, 1, 1) \times (1, 1, 1)_7$**:

$$\Phi_P(B^s)\phi_p(B)(1-B)^d(1-B^s)^D X_t = \Theta_Q(B^s)\theta_q(B)\epsilon_t$$

Donde:
* $B$ es el operador de retardo (backshift operator), tal que $B^k X_t = X_{t-k}$.
* $d = 1$: Primera diferenciacion regular no estacional para eliminar tendencias de nivel.
* $D = 1$: Primera diferenciacion estacional con periodo $s = 7$ (dias de la semana) para inducir estacionariedad ciclica.
* $p = 1$: Componente autorregresivo regular $\phi_1$, que modela la memoria directa del dia anterior.
* $q = 1$: Componente de media movil regular $\theta_1$, que amortigua el choque aleatorio del dia previo.
* $P = 1$: Componente autorregresivo estacional $\Phi_1$, que vincula el comportamiento con el mismo dia de la semana anterior.
* $Q = 1$: Componente de media movil estacional $\Theta_1$, que captura el error residual semanal.
* $s = 7$: Periodicidad estacional de 7 dias, validada por el analisis espectral de Fourier (FFT) realizado en E1.

#### 2.2.2 Evaluacion de Estacionariedad (Prueba Dickey-Fuller Aumentada)
Antes del ajuste, se ejecuto la prueba estadistica Dickey-Fuller Aumentada (ADF) sobre la serie diferenciada:
* **Hipotesis Nula ($H_0$):** La serie temporal tiene una raiz unitaria (es no estacionaria).
* **Hipotesis Alternativa ($H_1$):** La serie no tiene raiz unitaria (es estacionaria).

**Resultados Empiricos Obtenidos:**
* Estadistico ADF: `-4.0313`
* p-value: `0.001255`
* Valor critico al 1%: `-3.4410`
* Valor critico al 5%: `-2.8662`
* Valor critico al 10%: `-2.5693`

**Conclusion Estadistica:** Dado que el p-value ($0.001255$) es sustancialmente menor al nivel de significancia $\alpha = 0.05$ y el estadistico ADF ($-4.0313$) es mas negativo que el valor critico al 1% ($-3.4410$), se rechaza categóricamente la hipotesis nula. La serie transformada es estrictamente estacionaria.

#### 2.2.3 Metricas de Desempeno en Periodo de Prueba (Holdout de 30 dias)
Para garantizar una evaluacion honesta sin fuga de informacion temporal (data leakage), se separo un conjunto de prueba de los ultimos 30 dias cronologicos de la serie:
* **Criterio de Informacion de Akaike (AIC):** `5,208.35` (el menor entre las configuraciones candidatas evaluadas).
* **Error Absoluto Medio (MAE):** `10.88 accesos/dia` (desviacion promedio de torniquete).
* **Raiz del Error Cuadratico Medio (RMSE):** `13.07 accesos/dia`.
* **Error Porcentual Absoluto Medio (MAPE):** `10.72%` (precision superior al 89% en prediccion diaria).

#### 2.2.4 Bandas de Confianza al 95%
Para cada horizonte proyectado $h \in \{1, \dots, 30\}$, se estiman los limites de confianza:

$$\hat{X}_{t+h} \pm z_{\alpha/2} \cdot \sigma_h = \hat{X}_{t+h} \pm 1.96 \cdot \sigma_h$$

Esta banda permite a la gerencia del gimnasio planificar la distribucion de instructores y el mantenimiento de equipo considerando tanto el escenario esperado como los limites superior e inferior con 95% de certidumbre.

---

### 2.3 Modelado de Clasificacion: Riesgo de Desercion (Churn)

#### 2.3.1 Definicion de Variables (Feature Engineering)
A partir del historial transaccional de torniquete, se extrajeron 6 caracteristicas de comportamiento por socio:
1. `dias_sin_asistir`: Dias transcurridos desde el ultimo acceso registrado hasta la fecha de corte.
2. `duracion_promedio`: Tiempo medio de entrenamiento por visita (minutos).
3. `total_accesos`: Frecuencia total de visitas acumuladas.
4. `cuota_mensual`: Monto pagado por suscripcion ($450, $650 o $1,200 MXN).
5. `antiguedad_dias`: Lapso total como miembro del gimnasio.
6. `frecuencia_semanal`: Ratio de visitas por semana de vigencia.

**Target de Desercion:**
* `1` (Riesgo Critico / Churn Inminente): Socio con 5 o mas dias consecutivos de inasistencia al corte.
* `0` (Socio Retenido / Frecuencia Regular): Socio con menos de 5 dias de inasistencia.

#### 2.3.2 Comparativa Metodologica de Modelos (Rubrica E3)
Se entrenaron y compararon dos algoritmos con split estratificado 80/20 y pesos de clase balanceados (`class_weight='balanced'`):

| Metrica de Evaluacion | Random Forest Classifier (A) | Regresion Logistica L2 (B) |
| :--- | :---: | :---: |
| **Precision (Positivos)** | **1.0000** | 0.8889 |
| **Recall (Sensibilidad)** | **1.0000** | 0.8889 |
| **F1-Score (Equilibrio)** | **1.0000** | 0.8889 |
| **Area Bajo Curva (ROC-AUC)** | **1.0000** | 0.9864 |

#### Matrices de Confusion en Conjunto de Prueba (N = 50 socios):

* **Random Forest (Modelo Seleccionado):**
  * Verdaderos Negativos (VN): 41 socios
  * Falsos Positivos (FP): 0 socios
  * Falsos Negativos (FN): 0 socios
  * Verdaderos Positivos (VP): 9 socios

* **Regresion Logistica Regularizada:**
  * Verdaderos Negativos (VN): 40 socios
  * Falsos Positivos (FP): 1 socio
  * Falsos Negativos (FN): 1 socio
  * Verdaderos Positivos (VP): 8 socios

#### Importancia de Variables en Random Forest:
1. `dias_sin_asistir`: **80.45%** (indicador determinante de desercion).
2. `duracion_promedio`: **8.02%** (los socios que abandonan reducen su tiempo de entrenamiento previo a dejar de asistir).
3. `frecuencia_semanal`: **5.05%** (regularidad semanal).
4. `total_accesos`: **4.21%** (volumen historico de asistencia).
5. `antiguedad_dias`: **1.78%** (fidelidad temporal).
6. `cuota_mensual`: **0.50%** (impacto de precio relativo).

#### 2.3.3 Justificacion de Negocio: Por que el RECALL es la Metrica Reina
En el modelo financiero de un gimnasio bajo modelo de suscripcion, los dos tipos de error tienen repercusiones economicas asimetricas:

1. **Costo de un Falso Negativo (FN):** El modelo predice que un socio esta seguro cuando en realidad esta a punto de cancelar. El gimnasio no ejecuta ninguna accion de retencion y el socio se da de baja definitivamente. Esto ocasiona una perdida neta de **$650 MXN mensuales ($7,800 MXN al ano)** por cada socio no detectado, mas el costo de adquisicion de cliente (CAC) para reemplazarlo.
2. **Costo de un Falso Positivo (FP):** El modelo clasifica erróneamente a un socio como en riesgo cuando no lo esta. El sistema de recepcion o el coach le envia un mensaje cordial por WhatsApp con un saludo o una cortesia de toalla/bebida. El costo marginal de enviar este mensaje es de **$0.00 MXN**, y el impacto de cara al cliente es positivo, reforzando la atencion personalizada del gimnasio.

Por consiguiente, la prioridad absoluta de FitPulse Analytics es **maximizar el Recall**, asegurando que ningun socio en riesgo pase desapercibido. El modelo Random Forest alcanzo un Recall de 1.0000 (100%), eliminando los falsos negativos en el conjunto de prueba.

---

### 2.4 Serving de Modelos e Inferencia en Produccion

Los modelos entrenados se serializaron en la carpeta `models/`:
* `models/sarima_afluencia.pkl` y `models/sarima_meta.json`
* `models/churn_classifier.pkl` y `models/churn_meta.json`

El backend expone formalmente los endpoints REST especificados en la rubrica:

```http
GET /pronostico?dias=14
```
**Respuesta JSON:** Proyeccion diaria a 7, 14 o 30 dias con limites de confianza al 95% y metricas AIC, MAE, RMSE y MAPE.

```http
POST /clasificar
Content-Type: application/json

{
  "id_socio": "SOC-104",
  "dias_sin_asistir": 9,
  "duracion_promedio": 45.0,
  "total_accesos": 12,
  "cuota_mensual": 650.0,
  "antiguedad_dias": 80,
  "frecuencia_semanal": 1.0
}
```
**Respuesta JSON:** Probabilidad de churn en tiempo real (e.g., `80.1%`), clasificacion de riesgo (`Critico`), y accion tactica gerencial sugerida (`Llamada urgente de coach o cortesia por WhatsApp`).

---

## 3. Computo en la Nube: Infraestructura, Contenedores y Escalabilidad

### 3.1 Contenedores Ligeros y Multi-Stage Build

Para optimizar el tamano de las imagenes, acelerar el tiempo de despliegue y reducir la superficie de vulnerabilidades de seguridad, se disenaron `Dockerfiles` multi-etapa (`builder` y `runner`):

* **Etapa 1 (Builder):** Compila dependencias en Python 3.11-slim con herramientas de compilacion (`build-essential`).
* **Etapa 2 (Runner):** Imagen minima limpia que solo copia los artefactos precompilados de `/root/.local`.
* **Seguridad en Produccion:** Se crea el usuario de sistema `appuser` (UID 1000) sin privilegios de root para cumplir con los principios de hardening.

#### Diferencia Tecnica: Imagen vs. Contenedor y Maquina Virtual
* **Maquina Virtual (VM):** Empaqueta un sistema operativo completo (Guest OS), hipervisor y emulacion de hardware. Su arranque requiere minutos y consume gigabytes de memoria base.
* **Contenedor:** Comparte el kernel del sistema operativo anfitrion (Host OS) y aisla los procesos mediante *namespaces* y *cgroups* de Linux. Su arranque toma escasos segundos y el consumo base es de solo unos cuantos megabytes.

#### Orquestacion Local con `docker-compose.yml`:
El archivo raiz `docker-compose.yml` levanta los tres microservicios en una red privada tipo puente (`fitpulse-net`):
1. `tablero`: Servidor web FastAPI en puerto 8000 con verificacion de salud (`HEALTHCHECK`).
2. `modelos`: Microservicio de inferencia en puerto 8001.
3. `worker`: Proceso por lotes para ejecucion de pipelines de limpieza.

Comando de despliegue local unificado:
```bash
docker compose up --build -d
```

---

### 3.2 Orquestacion en Kubernetes (`k8s/`)

Para entornos distribuidos de alta disponibilidad, se generaron manifiestos declarativos de Kubernetes:

1. **`k8s/deployment.yaml`:**
   * Despliega el pod de la aplicacion con 2 replicas iniciales.
   * Define limites estrictos de recursos (`resources.requests`: 100m CPU / 128Mi RAM; `resources.limits`: 500m CPU / 256Mi RAM).
   * Configura sondas de vitalidad (`livenessProbe` a `/`) y disponibilidad (`readinessProbe` a `/dashboard`).
2. **`k8s/service.yaml`:**
   * Servicio de red tipo `LoadBalancer` que balancea el trafico externo entrante en el puerto 80 hacia el puerto 8000 de los pods.
3. **`k8s/hpa.yaml` (HorizontalPodAutoscaler):**
   * Politica de autoescalado horizontal automatico:
   * **Replicas minimas:** 2 pods.
   * **Replicas maximas:** 10 pods.
   * **Metrica de disparo:** 70% de utilizacion promedio de CPU.
   * Estabilizacion de escala ascendente inmediata (0 segundos) y enfriamiento descendente de 180 segundos para prevenir aleteo (thrashing).

---

### 3.3 Worker Serverless Multi-Cloud (`services/worker/serverless_function.py`)

Siguiendo la rubrica de evaluacion, el componente de limpieza se desacoplo como funcion serverless impulsada por eventos:
* **Disparador por Almacenamiento (Event-Driven):** Captura el evento `google.cloud.storage.object.v1.finalized` o `s3:ObjectCreated` cuando un nuevo archivo CSV llega al bucket `raw/`.
* **Disparador por Webhook HTTP:** Endpoint ligero para recepcion de transacciones desde torniquetes de terceros.
* **Ventajas Serverless:** Modelo de facturacion de pago por ejecucion estricta ($0 cuando no hay subidas), arranque en frio mitigado por ejecucion ligera en Python slim y aislamiento stateless.

---

### 3.4 Prueba de Carga y Estres con Locust (50 Usuarios Simultaneos)

Se ejecuto una prueba de estres simulando la actividad concurrente de 50 administradores de gimnasio navegando, consultando metricas y solicitando inferencias predictivas en tiempo real.

**Parametros de la Prueba:**
* Herramienta: Locust v2.47.0 (modo headless)
* Usuarios concurrentes: 50 usuarios simultaneos
* Tasa de generacion (ramp-up): 10 usuarios/segundo
* Duracion de prueba: 20 segundos
* Target Host: `http://127.0.0.1:8000`

#### Resultados de la Prueba:

| Endpoint Evaluado | Peticiones Realizadas | Fallos | Tasa de Error | Tiempo Medio (ms) | Min (ms) | Max (ms) | Percentil 95 (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `[GET] /` (Landing Page) | 7 | 0 | **0.00%** | 4,495 | 1,855 | 9,692 | 9,700 |
| `[GET] /api/analytics` | 53 | 0 | **0.00%** | 3,794 | 260 | 13,934 | 13,000 |
| `[GET] /api/churn-radar` | 27 | 0 | **0.00%** | 3,695 | 478 | 16,696 | 16,000 |
| `[GET] /dashboard` (HTML) | 30 | 0 | **0.00%** | 2,231 | 447 | 4,458 | 3,700 |
| `[GET] /pronostico` (SARIMA) | 29 | 0 | **0.00%** | 2,966 | 447 | 11,020 | 8,400 |
| `[POST] /clasificar` (RF) | 16 | 0 | **0.00%** | 2,430 | 641 | 4,265 | 4,300 |
| **Total Consolidado** | **162** | **0** | **0.00%** | **3,235** | **260** | **16,696** | **9,900** |

#### Analisis de los Resultados de Carga:
1. **Disponibilidad Total:** A pesar de inyectar 50 conexiones simultaneas sobre una sola instancia de computo, el servidor mantuvo una **tasa de error del 0.00%** (0 fallos en 162 peticiones de alta intensidad analitica).
2. **Justificacion del HPA:** La latencia p95 consolidada fue de 9.9 segundos debido a la saturacion de nucleo en el nodo unico. Esto evidencia exactamente por que la regla de Kubernetes HPA al 70% de CPU es imprescindible en la arquitectura productiva: en cuanto el uso de CPU supere el umbral, Kubernetes aprovisionara pods adicionales de forma automatica, distribuyendo la carga de inferencias y reduciendo la latencia de respuesta por debajo de los 400 milisegundos.

---

### 3.5 Infraestructura como Codigo (IaC) con Terraform

Se codifico la totalidad de la infraestructura de soporte bajo el paradigma declarativo de Terraform en la carpeta `infra/terraform/`:

* **`variables.tf`:** Parametriza variables de proyecto, region (`us-central1`), entorno y nombres de recursos.
* **`main.tf`:**
  * `google_storage_bucket.raw_bucket`: Almacenamiento seguro para datos crudos con regla de ciclo de vida que depura archivos tras 90 dias.
  * `google_storage_bucket.clean_bucket`: Almacenamiento versionado para datasets limpios y modelos entrenados.
  * `google_pubsub_topic.ingesta_topic`: Canal de mensajeria asincrono para eventos de torniquete.
  * `google_pubsub_subscription.worker_subscription`: Cola con retencion de 7 dias y acuse de recibo de 60 segundos.
  * `google_service_account.app_sa`: Cuenta de servicio dedicada bajo el principio de minimo privilegio, limitando los roles a `roles/storage.objectViewer` en raw, `roles/storage.objectAdmin` en clean y `roles/pubsub.publisher` / `roles/pubsub.subscriber`.
* **`outputs.tf`:** Expone los URIs y correos electronicos generados para integracion continua en pipelines de CI/CD.

#### Prueba de Idempotencia y Ciclo de Vida:
La arquitectura garantiza reproducibilidad estricta mediante:
```bash
terraform init
terraform plan
terraform apply -auto-approve
terraform destroy -auto-approve
```

---

## 4. Matriz de Verificacion contra la Rubrica E3

| Criterio Oficial de Rubrica | Componente Desarrollado en FitPulse | Estado |
| :--- | :--- | :---: |
| Justificacion CPU vs. GPU | Analisis de dimensionalidad y FinOps en seccion 2.1 | Cumplido |
| Modelos serializados en `models/` | `models/sarima_afluencia.pkl` y `models/churn_classifier.pkl` | Cumplido |
| Pronostico SARIMA de 7 a 30 dias | SARIMA(1,1,1)x(1,1,1,7) con 95% de confianza y AIC=5208.35 | Cumplido |
| Comparativa de al menos dos clasificadores | Random Forest vs. Regresion Logistica con matriz y metricas | Cumplido |
| Justificacion de Recall sobre Precision | Analisis de impacto economico por Falso Negativo ($650/mes) | Cumplido |
| Endpoints REST `/pronostico` y `/clasificar` | Implementados en FastAPI con validacion de esquemas Pydantic | Cumplido |
| Tablero v3 consumiendo modelos | Grafica interactiva SARIMA integrada en el panel principal | Cumplido |
| Dockerfile por servicio + docker-compose | Dockerfiles en `web`, `modelos`, `worker` y `docker-compose.yml` | Cumplido |
| Manifiestos de Kubernetes | `k8s/deployment.yaml`, `k8s/service.yaml` y `k8s/hpa.yaml` | Cumplido |
| Funcion Serverless de limpieza | `services/worker/serverless_function.py` (GCF y Lambda) | Cumplido |
| Prueba de carga de 50 usuarios con Locust | `tests/locustfile.py` con 0% errores y reporte p95 generado | Cumplido |
| Infraestructura con Terraform | `main.tf`, `variables.tf`, `outputs.tf` (Buckets, PubSub, IAM) | Cumplido |

---

## 5. Instrucciones de Ejecucion Rapida

1. **Entrenar y serializar modelos:**
   ```bash
   python notebooks/entrenamiento_modelos_e3.py
   ```
2. **Levantar plataforma completa con Docker Compose:**
   ```bash
   docker compose up --build
   ```
3. **Acceso al Tablero y Documentacion Interactiva:**
   * Dashboard con proyeccion SARIMA: `http://localhost:8000/dashboard`
   * Documentacion Swagger de la API: `http://localhost:8000/docs`
   * Endpoint de pronostico: `http://localhost:8000/pronostico?dias=14`
   * Endpoint de metricas: `http://localhost:8000/metricas`
4. **Reproducir prueba de estres (Locust):**
   ```bash
   locust -f tests/locustfile.py --headless -u 50 -r 10 --run-time 20s --host http://127.0.0.1:8000 --csv=tests/locust_report
   ```
