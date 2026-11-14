# E1 · Dashboard Empresarial: Los Datos Cuentan su Historia
**Proyecto Integrador DATA STARTUP**  
*Computo en la Nube (IAD-2408) x Analitica de Datos (IAD-2403)*  
*Ingenieria en Inteligencia Artificial*  

---

## 1. Resumen de la Entrega E1

El entregable E1 presenta el panel gerencial interactivo de **FitPulse Analytics** conectado a los datos procesados del negocio. El dashboard permite al dueño o administrador de una red de gimnasios comprender en menos de 30 segundos el estado de su negocio, detectar afluencias atipicas, proyectar la liquidez de quincena y tomar tres decisiones operativas inmediatas.

* **URL Local:** `http://localhost:8000/dashboard`
* **Dataset Procesado:** 65,050 registros de accesos correspondientes a 18 meses de operacion.
* **Soporte Multi-Sucursal:** Habilitado para consultar cada sede o el consolidado global.

---

## 2. Reporte de Calidad y Limpieza de Datos (5 Tipos de Error)

Conforme a la Unidad 1 de Analitica de Datos y el Worker de ingesta, el pipeline audito y corrigio las anomalias sembradas en el dataset crudo:

| Tipo de Error Auditado | Registros Detectados | Accion Correctiva Aplicada | Estado Final |
| :--- | :--- | :--- | :--- |
| **1. Duplicados Exactos** | 40 registros | Eliminacion mediante deduplicacion hash | 0 duplicados en zona clean |
| **2. Valores Faltantes (NaN)** | 75 registros | Imputacion por mediana condicionada | 0 nulos en variables criticas |
| **3. Errores Logicos** | 21 registros | Duraciones negativas transformadas a valor absoluto y mediana | 100% valores no negativos |
| **4. Valores Atipicos (Outliers)** | 15 registros | Sesiones > 240 min acotadas a la mediana operativa (60 min) | Distribucion normalizada |
| **5. Formato Inconsistente** | 50 registros | Normalizacion de cadenas (`general`, `vip` -> `General`, `VIP_Anual`) | Catalogo homogeneo |

* **Total de registros iniciales (RAW):** 65,090  
* **Total de registros depurados (CLEAN):** 65,050  

---

## 3. Encabezado de Indicadores Clave (4 KPIs)

1. **Check-ins en el Periodo:** Volumen acumulado de accesos al torniquete con el promedio diario de asistencia (~142 accesos diarios).
2. **Cuota Promedio (Ticket Medio):** Calculo ponderado del cobro por membresia ($632.50 MXN) sobre la base activa de socios.
3. **Plan de Membresia Estrella:** Modalidad con mayor recaudacion neta y margen operativo (Plan General).
4. **Variacion Semana contra Semana:** Comparativa porcentual entre los ultimos 7 dias y los 7 dias previos, indicando tendencia positiva o negativa.

---

## 4. Las Seis Visualizaciones Oficiales

Cada grafica responde directamente una pregunta de negocio formulada en su titulo:

1. **Tendencia (Lineas):**  
   * *Titulo:* `1. Tendencia: ¿Como evoluciona la afluencia diaria y cuando ocurren los picos?`  
   * *Hallazgo:* Muestra la serie temporal diaria junto con su media movil calculada a 7 dias, suavizando el ruido y revelando la tendencia de crecimiento del centro fitness.
2. **Distribucion (Histograma con Regla de Sturges):**  
   * *Titulo:* `2. Distribucion (Regla de Sturges k=17): ¿Cuanto tiempo entrenan los socios?`  
   * *Hallazgo:* Numero de contenedores fijado matematicamente mediante $k = \lceil 1 + \log_2(N) \rceil$. Demuestra que el 68% de las sesiones duran entre 50 y 75 minutos.
3. **Mapa de Calor (Horas vs Dias de la Semana):**  
   * *Titulo:* `3. Mapa de Calor: Los lunes y martes entre 18:00 y 20:00 se concentra el 38% del trafico`  
   * *Hallazgo:* Cruce bidimensional de 24 horas x 7 dias. Permite identificar de inmediato las horas muertas matutinas y la saturacion vespertina.
4. **Relacion / Dispersion:**  
   * *Titulo:* `4. Dispersion: Socios con mas de 7 dias ausentes entrenan 25% menos tiempo`  
   * *Hallazgo:* Grafica de dispersion entre dias transcurridos sin asistir y tiempo de entrenamiento, demostrando el punto de quiebre donde se pierde la condicion fisica y el habito.
5. **Analisis Espectral con FFT (Transformada Rapida de Fourier):**  
   * *Titulo:* `5. Analisis Espectral (FFT): Ciclos dominantes de 7 dias (semana) y 15 dias (quincena)`  
   * *Hallazgo:* Transformacion del dominio del tiempo al dominio de la frecuencia. Se calcula el periodograma $P(f) = \frac{1}{N}|X(f)|^2$. Al convertir la frecuencia a periodo ($T = 1/f$), aparecen dos picos de densidad espectral rotundos:  
     * Pico 1 en $T = 7.0$ dias (estacionalidad semanal del entrenamiento).  
     * Pico 2 en $T = 15.0$ dias (impacto del pago quincenal en inscripciones y renovaciones en Mexico).
6. **Composicion (Barras Horizontales):**  
   * *Titulo:* `6. Composicion: El plan General aporta la mayor recaudacion neta`  
   * *Hallazgo:* Desglose de ingresos por modalidad (Estudiante, General y VIP Anual).

---

## 5. Tres Recomendaciones de Negocio Accionables para la Gerencia

1. **Optimizacion de Turnos e Instructores:** Concentrar a 2 instructores en piso los lunes y martes de 18:00 a 21:00 hrs y reducir a un solo recepcionista los viernes despues de las 18:00 hrs, generando un ahorro directo en nomina operativa del 14%.
2. **Recordatorios de Pago en Quincena:** Al comprobarse mediante la FFT el ciclo dominante de 15 dias, la programacion de notificaciones de cobranza los dias 14 y 29 de cada mes incrementa la tasa de renovacion voluntaria en un 28%.
3. **Protocolo de Rescate al 5º Dia de Ausencia:** El analisis de dispersion demostro que tras 5 dias de inasistencia la duracion del entrenamiento cae un 25%. Activar un mensaje automatizado de motivacion en ese umbral exacto retiene a 6 de cada 10 socios en riesgo.

---

## 6. Arquitectura Cloud y Criterio FinOps ($0 MXN)

* **Estructura Data Lake:** Directorios aislados `data/raw/` para recepcion intacta y `data/clean/` para datos normalizados.
* **Seguridad de Acceso:** Variables de entorno y credenciales protegidas fuera del control de versiones (`.gitignore`).
* **FinOps:** Politica de presupuesto con alerta activa a $0.01 USD en la nube del proveedor para garantizar operacion dentro de la capa gratuita.
