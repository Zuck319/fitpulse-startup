# E2 · Cimientos en la Nube: Los Datos Viajan Solos
**Proyecto Integrador DATA STARTUP**  
*Computo en la Nube (IAD-2408) x Analitica de Datos (IAD-2403)*  
*Ingenieria en Inteligencia Artificial*  

---

## 1. Resumen de la Entrega E2

En E2 se construye la tuberia automatizada que lleva los datos desde la ingesta hasta el almacenamiento y el modelado analitico sin intervencion manual. Se implementa el microservicio de ingesta en FastAPI, la arquitectura desacoplada con cola y worker, y la deduccion e implementacion matematica de la **Regresion Lineal por Minimos Cuadrados (OLS)** a mano con NumPy.

---

## 2. Diagrama de Arquitectura del Sistema

```
[Negocio Cliente / Recepcion]
        |
        | POST /api/upload-csv o JSON /ventas
        v
+-------------------------------+
| Microservicio de Ingesta      |
| FastAPI en Contenedor Docker  |
+-------------------------------+
        |
        | Guarda archivo crudo sin procesar
        v
+-------------------------------+
| Data Lake: Zona raw/          |
| (Almacenamiento de Objetos)   |
+-------------------------------+
        |
        | Notifica nuevo archivo / Publica mensaje
        v
+-------------------------------+
| Middleware de Mensajes        |
| (Cola SQS / PubSub)           |
+-------------------------------+
        |
        | Desacoplamiento asincrono
        v
+-------------------------------+
| Worker de Limpieza            |
| (services/worker/limpieza.py) |
+-------------------------------+
        |
        | Depura 5 errores y escribe
        +-----------------------------------+
        |                                   |
        v                                   v
+-------------------------------+   +-------------------------------+
| Data Lake: Zona clean/        |   | Base de Datos Relacional      |
| CSV depurado para analitica   |   | PostgreSQL (Indices + UUID)   |
+-------------------------------+   +-------------------------------+
        |                                   |
        +-----------------+-----------------+
                          |
                          v
        +-----------------------------------+
        | Panel de Control (Dashboard Web)  |
        | Consume clean/ y muestra OLS +    |
        | 6 graficas de negocio             |
        +-----------------------------------+
```

---

## 3. Regresion Lineal por Minimos Cuadrados Ordinarios (OLS) a Mano

### Formulacion Matematica:
Dado el modelo matricial:
$$y = X\beta + \epsilon$$

Donde:
* $X \in \mathbb{R}^{N \times (p+1)}$ es la matriz de diseño que incluye la columna unitaria de intercepto.
* $y \in \mathbb{R}^N$ es el vector de asistencias diarias observadas.
* $\beta \in \mathbb{R}^{p+1}$ es el vector de coeficientes por estimar.

Minimizando la suma de residuos al cuadrado:
$$S(\beta) = (y - X\beta)^T (y - X\beta)$$
$$\frac{\partial S}{\partial \beta} = -2X^T y + 2X^T X \beta = 0$$

Se obtiene la **Ecuacion Normal**:
$$\beta = (X^T X)^{-1} X^T y$$

### Resultados de la Implementacion (`notebooks/regresion_minimos_cuadrados.py`):
Se analizaron 638 dias continuos con 3 variables predictoras: tendencia temporal ($t$), dia de la semana (0 a 6) y bandera de quincena ($1$ o $0$).

| Metrica / Coeficiente | NumPy a Mano | scikit-learn | Diferencia Absoluta |
| :--- | :--- | :--- | :--- |
| **Intercepto ($\beta_0$)** | 144.63109 | 144.63109 | $0.0 \times 10^0$ |
| **Tendencia temporal ($\beta_1$)** | 0.01938 | 0.01938 | $0.0 \times 10^0$ |
| **Dia de la semana ($\beta_2$)** | -17.26962 | -17.26962 | $0.0 \times 10^0$ |
| **Efecto quincena ($\beta_3$)** | 19.94230 | 19.94230 | $0.0 \times 10^0$ |
| **MSE (Error Cuadratico Medio)** | 414.7236 | 414.7236 | $0.0 \times 10^0$ |
| **RMSE (Raiz del MSE)** | 20.3648 | 20.3648 | $0.0 \times 10^0$ |
| **MAE (Error Absoluto Medio)** | 15.3720 | 15.3720 | $0.0 \times 10^0$ |
| **$R^2$ (Coeficiente Determinacion)** | 0.7510 | 0.7510 | $0.0 \times 10^0$ |

### Analisis de Residuos:
* La media de los residuos es $-0.000000$ (cumple el supuesto de insesgadez Gauss-Markov).
* La desviacion estandar es $20.36$ accesos diarios.
* El coeficiente de quincena $\beta_3 = +19.94$ demuestra con rigor estadistico que los dias de quincena aumentan en promedio 20 visitas sobre la media.

---

## 4. Esquema de Base de Datos (PostgreSQL)

```sql
CREATE TABLE IF NOT EXISTS sucursales (
    id_sucursal SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) DEFAULT 'Colima'
);

CREATE TABLE IF NOT EXISTS socios (
    id_socio VARCHAR(20) PRIMARY KEY,
    id_sucursal INT REFERENCES sucursales(id_sucursal),
    plan_membresia VARCHAR(30) NOT NULL,
    monto_mensualidad NUMERIC(10,2) NOT NULL,
    fecha_alta DATE NOT NULL,
    estado_socio VARCHAR(20) DEFAULT 'Activo'
);

CREATE TABLE IF NOT EXISTS registros_acceso (
    id_acceso BIGSERIAL PRIMARY KEY,
    id_socio VARCHAR(20) REFERENCES socios(id_socio),
    fecha_hora TIMESTAMP NOT NULL,
    duracion_minutos INT,
    dias_sin_asistir INT
);

CREATE INDEX idx_accesos_fecha ON registros_acceso(fecha_hora);
CREATE INDEX idx_accesos_socio ON registros_acceso(id_socio);
```

---

## 5. Control de Permisos y Politica de Minimo Privilegio (IAM)

* **Rol de Ingesta:** Unicamente permiso `s3:PutObject` sobre el prefijo `data/raw/*`.
* **Rol del Worker:** Permiso `s3:GetObject` en `data/raw/*`, `s3:PutObject` en `data/clean/*`, y lectura/escritura en la base de datos PostgreSQL. No posee permisos administrativos.
* **MFA (Autenticacion Multi-Factor):** Activo obligatoriamente en la cuenta raiz.
