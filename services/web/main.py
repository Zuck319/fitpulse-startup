"""
FitPulse Analytics - Plataforma Web SaaS Integral
Backend FastAPI + Renderizado Jinja2 + REST API
Cumple con E0 a E5 del Proyecto Integrador DATA STARTUP.
"""

import os
import io
import shutil
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, Query, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import numpy as np

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "sample", "accesos_gimnasio_clean.csv")
RAW_DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "sample", "accesos_gimnasio_raw.csv")
UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="FitPulse Analytics Web App",
    description="SaaS de Inteligencia Predictiva y Retención para Centros Fitness",
    version="1.0.0"
)

# Montar archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Estado en memoria simple para la sesión de demostración
SESSION_STATE = {
    "usuario_autenticado": True,
    "nombre_usuario": "Dylan Espinosa",
    "nombre_gym": "Iron Gym Fitness Center",
    "plan_activo": "Pro",
    "email": "espinosadylan616@gmail.com",
    "logo_url": None, # URL relativa si se sube logo
    "sucursal_activa": "Todas las sucursales (Consolidado)"
}

# --------------------------------------------------------------------------
# CARGA Y CACHÉ DE DATOS
# --------------------------------------------------------------------------
def obtener_dataframe_limpio() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    else:
        # Respaldo si no existe el CSV
        dias = pd.date_range("2025-01-01", "2026-06-30", freq="D")
        return pd.DataFrame({
            "fecha": dias,
            "sucursal": "Sucursal Centro (Matriz)",
            "id_socio": [f"SOC-{i%100:03d}" for i in range(len(dias))],
            "plan_membresia": "General",
            "monto_mensualidad": 650.0,
            "hora": 18,
            "duracion_minutos": 60,
            "dias_sin_asistir": 3,
            "estado_socio": "Activo"
        })

# --------------------------------------------------------------------------
# RUTAS DE PÁGINAS WEB (HTML)
# --------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Página principal / Landing page de presentación del software."""
    contacto = {
        "telefono": "+52 312 190 0195",
        "telefono_link": "523121900195",
        "correo": "espinosadylan616@gmail.com",
        "fundador": "Dylan Espinosa",
        "ano": datetime.now().year
    }
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "contacto": contacto,
            "planes": [
                {
                    "id": "basico",
                    "nombre": "Plan Básico",
                    "precio": "499",
                    "sedes": "Hasta 2 sucursales",
                    "destacado": False,
                    "caracteristicas": [
                        "Soporte Multi-Sucursal (hasta 2 sedes)",
                        "Dashboard gerencial en tiempo real",
                        "Los 4 KPIs y 6 visualizaciones oficiales",
                        "Carga de datos por archivo CSV",
                        "Reportes ejecutivos exportables"
                    ]
                },
                {
                    "id": "pro",
                    "nombre": "Plan Pro",
                    "precio": "899",
                    "sedes": "Hasta 5 sucursales",
                    "destacado": True,
                    "caracteristicas": [
                        "Soporte Multi-Sucursal (hasta 5 sedes)",
                        "Radar Anti-Churn (Socios en riesgo de deserción)",
                        "Alertas predictivas por WhatsApp",
                        "Análisis espectral FFT de quincenas",
                        "Soporte prioritario y personalización con tu logo"
                    ]
                },
                {
                    "id": "premium",
                    "nombre": "Plan Premium",
                    "precio": "1,499",
                    "sedes": "Sedes ilimitadas",
                    "destacado": False,
                    "caracteristicas": [
                        "Multi-Sucursal Ilimitada (Cadenas y Franquicias)",
                        "API REST directa para torniquetes y lectores POS",
                        "Pronóstico de afluencia a 30 días",
                        "Consolidado corporativo y auditoría cloud",
                        "Gerente de cuenta dedicado"
                    ]
                }
            ]
        }
    )


@app.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request, plan: Optional[str] = "pro"):
    """Página de registro con selección de plan."""
    return templates.TemplateResponse(
        request=request,
        name="registro.html",
        context={
            "plan_seleccionado": plan.lower(),
            "contacto": {
                "telefono": "+52 312 190 0195",
                "correo": "espinosadylan616@gmail.com"
            }
        }
    )


@app.post("/registro")
async def procesar_registro(
    nombre_gym: str = Form(...),
    nombre_dueno: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    num_sucursales: int = Form(1),
    plan_elegido: str = Form("pro")
):
    """Procesa el registro del usuario y lo redirige al checkout o dashboard."""
    SESSION_STATE["nombre_gym"] = nombre_gym
    SESSION_STATE["nombre_usuario"] = nombre_dueno
    SESSION_STATE["email"] = email
    SESSION_STATE["plan_activo"] = plan_elegido.title()
    SESSION_STATE["usuario_autenticado"] = True
    
    # Redirigir directamente al panel de control activo
    return RedirectResponse(url="/dashboard?registro_exitoso=1", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de inicio de sesión."""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "contacto": {
                "telefono": "+52 312 190 0195",
                "correo": "espinosadylan616@gmail.com"
            }
        }
    )


@app.post("/login")
async def procesar_login(
    email: str = Form(...),
    password: str = Form(...)
):
    """Autentica al usuario."""
    SESSION_STATE["usuario_autenticado"] = True
    SESSION_STATE["email"] = email
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def logout():
    SESSION_STATE["usuario_autenticado"] = False
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Panel de control principal completo (No Streamlit, Web nativa)."""
    df = obtener_dataframe_limpio()
    
    sucursales = ["Todas las sucursales (Consolidado)"]
    if "sucursal" in df.columns:
        sucursales += sorted(df["sucursal"].dropna().unique().tolist())
        
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "session": SESSION_STATE,
            "sucursales": sucursales,
            "contacto": {
                "telefono": "+52 312 190 0195",
                "correo": "espinosadylan616@gmail.com"
            }
        }
    )

# --------------------------------------------------------------------------
# ENDPOINTS REST API (ALIMENTAN LOS DATOS Y GRÁFICAS DEL DASHBOARD)
# --------------------------------------------------------------------------

@app.get("/api/analytics")
async def api_analytics(sucursal: Optional[str] = "Todas las sucursales (Consolidado)"):
    """
    Calcula los 4 KPIs oficiales y prepara los datos para las 6 gráficas de E1.
    """
    df = obtener_dataframe_limpio()
    
    # Filtro por sucursal
    if sucursal and sucursal != "Todas las sucursales (Consolidado)" and "sucursal" in df.columns:
        df = df[df["sucursal"] == sucursal].copy()
        
    # 1. KPIs
    total_accesos = int(len(df))
    asistencias_diarias = df.groupby(df['fecha'].dt.date).size()
    promedio_diario = float(asistencias_diarias.mean()) if len(asistencias_diarias) > 0 else 0.0
    
    socios_unicos = int(df["id_socio"].nunique()) if "id_socio" in df.columns else 250
    df_socios = df.drop_duplicates(subset=["id_socio"]) if "id_socio" in df.columns else df
    ticket_promedio = float(df_socios["monto_mensualidad"].mean()) if "monto_mensualidad" in df_socios.columns else 650.0
    ingreso_mensual_estimado = float(socios_unicos * ticket_promedio)
    
    plan_estrella = str(df["plan_membresia"].value_counts().index[0]) if "plan_membresia" in df.columns and len(df)>0 else "General"
    
    # Variación semanal
    ultimos_7 = int(asistencias_diarias.tail(7).sum())
    previos_7 = int(asistencias_diarias.iloc[-14:-7].sum()) if len(asistencias_diarias) >= 14 else ultimos_7
    variacion_pct = float(((ultimos_7 - previos_7) / previos_7 * 100)) if previos_7 > 0 else 0.0
    
    # 2. GRÁFICA 1: Tendencia diaria con media móvil a 7 días (últimos 90 días para claridad)
    df_reciente = asistencias_diarias.tail(90).reset_index()
    df_reciente.columns = ["fecha", "accesos"]
    df_reciente["fecha_str"] = df_reciente["fecha"].astype(str)
    df_reciente["media_movil_7d"] = df_reciente["accesos"].rolling(window=7, min_periods=1).mean().round(1)
    
    grafica_tendencia = {
        "fechas": df_reciente["fecha_str"].tolist(),
        "accesos": df_reciente["accesos"].tolist(),
        "media_movil": df_reciente["media_movil_7d"].tolist()
    }
    
    # 3. GRÁFICA 2: Histograma con Regla de Sturges: k = ceil(1 + log2(N))
    duraciones = df["duracion_minutos"].dropna().tolist()
    n_dur = len(duraciones)
    k_sturges = int(np.ceil(1 + np.log2(n_dur))) if n_dur > 0 else 10
    
    counts, bin_edges = np.histogram(duraciones, bins=k_sturges)
    bin_labels = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}m" for i in range(len(counts))]
    grafica_histograma = {
        "labels": bin_labels,
        "valores": counts.tolist(),
        "k_sturges": k_sturges
    }
    
    # 4. GRÁFICA 3: Mapa de calor (Días vs Horas)
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_map = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    df_calor = df.copy()
    df_calor['dia_nombre'] = df_calor['fecha'].dt.weekday.map(dias_map)
    tabla_calor = pd.crosstab(df_calor['hora'], df_calor['dia_nombre']).reindex(columns=dias_orden, fill_value=0)
    
    grafica_calor = {
        "horas": [f"{h}:00" for h in tabla_calor.index.tolist()],
        "dias": dias_orden,
        "matriz": tabla_calor.values.tolist()
    }
    
    # 5. GRÁFICA 4: Dispersión (Días sin asistir vs Duración)
    muestra_disp = df.sample(min(300, len(df)), random_state=42)
    grafica_dispersion = [
        {
            "x": int(row["dias_sin_asistir"]),
            "y": int(row["duracion_minutos"]),
            "plan": str(row["plan_membresia"])
        }
        for _, row in muestra_disp.iterrows()
    ]
    
    # 6. GRÁFICA 5: Análisis Espectral FFT (Frecuencia a Periodos en Días)
    valores_serie = asistencias_diarias.values
    N = len(valores_serie)
    grafica_fft = {"periodos": [], "magnitud": [], "picos": []}
    
    if N > 30:
        y_centrada = valores_serie - np.mean(valores_serie)
        fft_v = np.fft.rfft(y_centrada)
        fft_f = np.fft.rfftfreq(N, d=1.0)
        magnitudes = (np.abs(fft_v) ** 2 / N).tolist()
        
        periodos = []
        for f in fft_f:
            periodos.append(float(round(1.0 / f, 1)) if f > 0 else 0.0)
            
        # Filtrar periodos representativos (entre 2 y 35 días)
        p_filtrados = []
        m_filtrados = []
        for p, m in zip(periodos, magnitudes):
            if 2.0 <= p <= 35.0:
                p_filtrados.append(p)
                m_filtrados.append(round(m, 1))
                
        grafica_fft = {
            "periodos": p_filtrados[:30],
            "magnitud": m_filtrados[:30]
        }
        
    # 7. GRÁFICA 6: Distribución de Planes (Composición)
    conteo_planes = df["plan_membresia"].value_counts()
    grafica_planes = {
        "labels": conteo_planes.index.tolist(),
        "valores": conteo_planes.values.tolist()
    }
    
    return {
        "kpis": {
            "total_accesos": total_accesos,
            "promedio_diario": round(promedio_diario, 1),
            "socios_unicos": socios_unicos,
            "ticket_promedio": round(ticket_promedio, 2),
            "ingreso_mensual_estimado": round(ingreso_mensual_estimado, 2),
            "plan_estrella": plan_estrella,
            "variacion_pct": round(variacion_pct, 1),
            "ultimos_7": ultimos_7,
            "previos_7": previos_7
        },
        "graficas": {
            "tendencia": grafica_tendencia,
            "histograma": grafica_histograma,
            "calor": grafica_calor,
            "dispersion": grafica_dispersion,
            "fft": grafica_fft,
            "planes": grafica_planes
        }
    }


@app.get("/api/churn-radar")
async def api_churn_radar(sucursal: Optional[str] = "Todas las sucursales (Consolidado)"):
    """Devuelve el listado de socios categorizados por riesgo de abandono."""
    df = obtener_dataframe_limpio()
    if sucursal and sucursal != "Todas las sucursales (Consolidado)" and "sucursal" in df.columns:
        df = df[df["sucursal"] == sucursal].copy()
        
    resumen = df.groupby("id_socio").agg({
        "sucursal": "first",
        "plan_membresia": "first",
        "monto_mensualidad": "first",
        "dias_sin_asistir": "max",
        "duracion_minutos": "mean"
    }).reset_index()
    
    socios = []
    for _, row in resumen.iterrows():
        dias = int(row["dias_sin_asistir"])
        if dias >= 8:
            nivel = "Crítico"
            prob = 0.88
            color = "red"
        elif dias >= 4:
            nivel = "Moderado"
            prob = 0.52
            color = "yellow"
        else:
            nivel = "Bajo"
            prob = 0.12
            color = "green"
            
        socios.append({
            "id_socio": row["id_socio"],
            "sucursal": str(row["sucursal"]),
            "plan": str(row["plan_membresia"]),
            "cuota": float(row["monto_mensualidad"]),
            "dias_sin_asistir": dias,
            "duracion_promedio": round(float(row["duracion_minutos"]), 1),
            "nivel": nivel,
            "probabilidad": prob,
            "color": color
        })
        
    socios.sort(key=lambda x: x["probabilidad"], reverse=True)
    return {
        "total": len(socios),
        "criticos": sum(1 for s in socios if s["nivel"] == "Crítico"),
        "moderados": sum(1 for s in socios if s["nivel"] == "Moderado"),
        "bajos": sum(1 for s in socios if s["nivel"] == "Bajo"),
        "socios": socios[:50] # Top 50 prioritarios
    }


@app.post("/api/upload-logo")
async def api_upload_logo(file: UploadFile = File(...)):
    """Permite al gimnasio subir su propio logotipo corporativo."""
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in [".png", ".jpg", ".jpeg", ".svg", ".webp"]:
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")
        
    nombre_archivo = f"gym_logo{extension}"
    ruta_guardado = os.path.join(UPLOADS_DIR, nombre_archivo)
    
    with open(ruta_guardado, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    SESSION_STATE["logo_url"] = f"/static/uploads/{nombre_archivo}?t={int(datetime.now().timestamp())}"
    return {"status": "ok", "logo_url": SESSION_STATE["logo_url"]}


@app.post("/api/limpieza")
async def api_ejecutar_limpieza():
    """Ejecuta en vivo el módulo de limpieza y auditoría sobre el dataset crudo."""
    from services.worker.limpieza import limpiar_datos_accesos
    if os.path.exists(RAW_DATA_PATH):
        df_crudo = pd.read_csv(RAW_DATA_PATH)
        df_limpio, reporte = limpiar_datos_accesos(df_crudo)
        return {"status": "ok", "reporte": reporte}
    else:
        return {"status": "error", "mensaje": "Dataset raw no encontrado"}


@app.get("/api/exportar-csv")
async def api_exportar_csv():
    """Descarga el reporte de socios y probabilidad de deserción en formato CSV."""
    df = obtener_dataframe_limpio()
    resumen = df.groupby("id_socio").agg({
        "sucursal": "first",
        "plan_membresia": "first",
        "monto_mensualidad": "first",
        "dias_sin_asistir": "max"
    }).reset_index()
    
    resumen["riesgo_desercion"] = resumen["dias_sin_asistir"].apply(
        lambda d: "Crítico (88%)" if d >= 8 else ("Moderado (52%)" if d >= 4 else "Bajo (12%)")
    )
    
    stream = io.StringIO()
    resumen.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=fitpulse_socios_{datetime.now().strftime('%Y%m%d')}.csv"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.web.main:app", host="0.0.0.0", port=8000, reload=True)
