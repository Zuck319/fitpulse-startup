# E0 · Propuesta de Startup: FitPulse Analytics
**Proyecto Integrador DATA STARTUP**  
*Cómputo en la Nube (IAD-2408) × Analítica de Datos (IAD-2403)*  
*Ingeniería en Inteligencia Artificial*  

---

## 1. Resumen Ejecutivo

**FitPulse Analytics** es una plataforma SaaS B2B de inteligencia de datos diseñada para centros de acondicionamiento físico independientes (gimnasios, boxes de CrossFit, estudios de yoga y pádel). El sistema resuelve la fuga silenciosa de ingresos provocada por la **deserción de socios (churn)** y la ineficiencia operativa en la asignación de horarios de entrenadores y personal. 

A través de la ingesta de registros diarios de acceso y pagos, FitPulse transforma datos crudos en:
1. Detección temprana de socios en riesgo de deserción (clasificador predictivo).
2. Pronóstico de afluencia y ocupación por hora/día (modelos de series de tiempo).
3. Ciclos de retención modelados matemáticamente con Cadenas de Markov y análisis espectral de Fourier.

---

## 2. Lean Canvas (9 Bloques)

```
+------------------------------------+----------------------------------+------------------------------------+----------------------------------+------------------------------------+
| 1. PROBLEMA                        | 4. SOLUCIÓN                      | 3. PROPUESTA DE VALOR              | 9. VENTAJA INJUSTA               | 2. SEGMENTO DE CLIENTES            |
| • 50-60% de deserción en los       | • Dashboard claro con KPIs de    | "Retén a tus socios antes de que   | • Motor analítico híbrido:        | • Dueños y gerentes de gimnasios   |
|   primeros 90 días de inscripción. |   retención y ocupación real.    | cancelen y optimiza tus horas      |   combina Fourier (FFT),         |   independientes (100 a 500        |
| • Desconocimiento de patrones      | • Alerta de socios con riesgo    | pico con inteligencia predictiva,  |   descomposición espectral,      |   socios activos).                 |
|   de afluencia (sobrecosto en      |   de abandono (Anti-Churn).      | en una plataforma sobria y lista   |   regresión normalizada a mano   | • Boxes de CrossFit y estudios     |
|   entrenadores en horas muertas).  | • Pronóstico de asistencia a     | para tu propia marca".             |   y Cadenas de Markov sobre      |   boutique (Yoga, Pilates, Pádel)  |
| • Software existente caro,         |   7 y 14 días para staffing.     |                                    |   infraestructura serverless de  |   en México.                       |
|   complejo y sin IA predictiva.    | • Personalización con logo del   |                                    |   costo $0 MXN en arranque.      |                                    |
|                                    |   gimnasio (white-label).        |                                    |                                  |                                    |
| Alternativas actuales:             |                                  +------------------------------------+                                  | Early adopters:                    |
| • Hojas de Excel manuales.         |                                  | 8. MÉTRICAS CLAVE                  |                                  | Gimnasios de barrio con cobro      |
| • Torniquetes sin analítica.       |                                  | • Churn Rate mensual reducido en   |                                  | mensual o quincenal que ya         |
| • Intuición del recepcionista.     |                                  |   al menos 15%.                    |                                  | registran entradas en libreta o    |
|                                    |                                  | • Tasa de retención de alertas     |                                  | computadora.                       |
|                                    |                                  |   (socios salvados tras alerta).   |                                  |                                    |
|                                    |                                  | • MAE / RMSE en predicción de      |                                  |                                    |
|                                    |                                  |   afluencia diaria.                |                                  |                                    |
+------------------------------------+----------------------------------+------------------------------------+----------------------------------+------------------------------------+
| 7. ESTRUCTURA DE COSTOS                                               | 5. CANALES                         | 6. FUENTES DE INGRESO                                                 |
| • Nube en Fase de Arranque: $0 MXN (AWS Free Tier / Azure / GCP).     | • Venta directa en frío con dueños | • Plan Básico: $499 MXN/mes (Multi-sucursal hasta 2 sedes, KPIs y CSV)|
| • Costo unitario a escala (100 clientes): ~$35 MXN por cliente/mes.  |   de gimnasios en la zona local.   | • Plan Pro: $899 MXN/mes (Multi-sucursal hasta 5 sedes, Anti-Churn)   |
| • Costos fijos proyectados: Dominio ($250 MXN/año) y pasarela de pago. | • Alianzas con proveedores de      | • Plan Premium: $1,499 MXN/mes (Multi-sucursal ilimitada + API)      |
| • Margen operativo estimado: > 92%.                                   |   torniquetes y software POS local.| • Margen: Con 1 socio retenido ($600), el software se paga solo.      |
+-----------------------------------------------------------------------+------------------------------------+-----------------------------------------------------------------------+
```

---

## 3. Entrevista de Validación de Cliente (15 minutos)

* **Entrevistado:** Carlos Mendoza  
* **Rol:** Dueño y administrador de *"Iron Gym Fitness & Functional"* (220 socios activos).  
* **Fecha:** 14 de octubre de 2026.  
* **Duración:** 18 minutos.  

### Las 5 Preguntas y Respuestas:
1. **¿Cómo te das cuenta hoy en día de que un socio ya no va a regresar?**  
   * *Respuesta:* *"Casi siempre hasta que el sistema de cobro marca que se venció su mes y ya pasaron dos semanas sin que pague. Pregunto en recepción y me dicen: 'Ah sí, tenía como 15 días que no venía'. Ya cuando le mandamos WhatsApp, o ya se cambió de gym o ya perdió la motivación. Es muy tarde."*
2. **¿Cuántos socios pierdes al mes en promedio?**  
   * *Respuesta:* *"De cada 10 que se inscriben, al tercer mes quedan 4 o 5. Es una sangría. Tengo que gastar en publicidad para reponer los que se van en vez de cuidar a los que ya pagaron la inscripción."*
3. **¿Cómo decides cuántos entrenadores o personal de limpieza necesitas por turno?**  
   * *Respuesta:* *"Por experiencia. Sé que los lunes en la tarde esto explota de gente y los viernes en la noche está muerto. Pero en quincenas o puentes a veces nos rebasa la gente o tengo 3 instructores sentados sin hacer nada."*
4. **¿Qué herramientas usas actualmente para controlar tus entradas?**  
   * *Respuesta:* *"Tenemos una computadora con una lectora de huella y un Excel donde el recepcionista anota las mensualidades. No tiene reportes bonitos ni me dice nada hacia adelante."*
5. **¿Pagarías una suscripción de $500 a $900 pesos al mes por un sistema que te alerte con una semana de anticipación qué personas están a punto de abandonar?**  
   * *Respuesta:* *"Totalmente. Cobro $650 de mensualidad. Si esa herramienta me rescata a 2 personas al mes, me sale gratis y todavía le gano dinero."*

### Aprendizajes clave de la entrevista:
* El cliente no quiere gráficas complejas de científicos de datos; quiere una **lista clara de nombres en semáforo rojo (en riesgo)** y saber cuánta gente vendrá la próxima semana.
* Valora mucho que el sistema no altere su flujo actual: le gustaría poder arrastrar su archivo de asistencia diario o semanal.
* Es fundamental que el sistema lleve el **logo de su gimnasio** para proyectar seriedad si sus socios o entrenadores ven la pantalla en recepción.

---

## 4. Cadena de Preguntas (Del Negocio a la Analítica)

| Pregunta de Negocio | Pregunta Analítica | Variable a Predecir | Unidad y Horizonte | Modelo Evaluado |
| :--- | :--- | :--- | :--- | :--- |
| **¿Qué socios están a punto de cancelar su membresía para contactarlos hoy?** | ¿Cuál es la probabilidad de que un socio no registre asistencia en los próximos 14 días dado su comportamiento reciente? | `probabilidad_churn` | Probabilidad $[0.0, 1.0]$ / Clasificación Binaria ($1$=En Riesgo, $0$=Activo) a 14 días. | Clasificador (Árbol de Decisión vs SVM vs Naive Bayes). |
| **¿Cuántas personas vendrán al gimnasio la próxima semana para planear turnos?** | ¿Cuál es el volumen diario esperado de accesos considerando estacionalidad semanal y efecto quincena? | `asistencias_diarias` | Conteo entero de accesos por día a horizonte de 7 a 30 días. | Regresión lineal normalizada a mano (E2) $\rightarrow$ ARIMA / SARIMA (E3) $\rightarrow$ LSTM (E4). |
| **¿En qué fase de fidelidad se encuentra la base de socios?** | ¿Cuáles son las probabilidades de transición entre estados de asistencia (Activo, Intermitente, En Riesgo, Inactivo)? | `matriz_transicion` | Matriz de Markov estocástica $P_{ij}$ a $n$ pasos. | Cadena de Markov discreta (E4). |

---

## 5. Inventario de Datos

* **Fuente:** Registro de accesos por torniquete digital y bitácora de membresías (muestra de 18 meses continuos, enero 2025 a junio 2026).
* **Volumen:** 14,250 registros de accesos individuales correspondientes a 350 socios únicos.
* **Granularidad:** Registro individual por evento de acceso (Check-in) con marca temporal exacta.

### Diccionario de Datos:
| Columna | Tipo de Dato | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `id_acceso` | `INTEGER` | Identificador único del evento | `10482` |
| `id_socio` | `STRING` | Identificador anonimizado del socio (LFPDPPP) | `SOC-00142` |
| `fecha_hora` | `DATETIME` | Timestamp del acceso al torniquete | `2025-08-15 18:32:10` |
| `plan_membresia` | `STRING` | Modalidad (`Estudiante`, `General`, `VIP_Anual`) | `General` |
| `dias_sin_asistir` | `INTEGER` | Días transcurridos desde su última visita previa | `4` |
| `asistencias_ultimos_30d`| `INTEGER` | Total de check-ins en los 30 días anteriores | `8` |
| `monto_mensualidad`| `FLOAT` | Cuota pagada en MXN | `650.00` |
| `estado_socio` | `STRING` | Estado (`Activo`, `En_Riesgo`, `Baja`) | `En_Riesgo` |

---

## 6. Arquitectura de Nube y Presupuesto ($0 MXN)

### Capa Gratuita del Proveedor (AWS / Google Cloud):
* **Almacenamiento (Data Lake):** AWS S3 (5 GB gratis durante 12 meses) o Cloud Storage (5 GB perennes). Estructurado con prefijos `raw/` (logs brutos) y `clean/` (depurados).
* **Base de datos transaccional:** PostgreSQL en instancia Cloud Free Tier o PostgreSQL en contenedor Docker optimizado en máquina virtual gratuita (ej. GCP e2-micro o AWS t4g.small / t2.micro).
* **Cómputo / Contenedores:** Cloud Run / App Runner (2 millones de peticiones gratis mensuales) levantando FastAPI y el Tablero Streamlit.
* **Cola de Mensajería:** AWS SQS (1,000,000 solicitudes gratis al mes) para desacoplar la ingesta de torniquete del worker de limpieza.
* **Alerta de Presupuesto (FinOps):** Alerta configurada a **$0.01 USD** con notificación inmediata al correo del equipo técnico para garantizar costo cero.
