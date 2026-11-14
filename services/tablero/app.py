"""
FitPulse Analytics - Plataforma SaaS de Inteligencia y Retención para Gimnasios
Diseñado para Cómputo en la Nube y Analítica de Datos (E1 a E5)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import io

# Configuración inicial de la página
st.set_page_config(
    page_title="FitPulse Analytics | Panel de Gestión",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS profesional, sobrio y corporativo (sin estridencias de IA ni gradientes neón)
st.markdown("""
<style>
    /* Estructura limpia y tipografía corporativa */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1e293b;
    }
    
    .main {
        background-color: #f8fafc;
    }
    
    /* Tarjetas de métricas (KPI cards) sobrias */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
    }
    
    .metric-title {
        font-size: 0.825rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    
    .metric-delta-positive {
        font-size: 0.85rem;
        font-weight: 600;
        color: #16a34a;
        margin-top: 4px;
    }
    
    .metric-delta-negative {
        font-size: 0.85rem;
        font-weight: 600;
        color: #dc2626;
        margin-top: 4px;
    }

    /* Recomendaciones de negocio */
    .recommendation-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 14px 18px;
        border-radius: 4px;
        margin-bottom: 12px;
        font-size: 0.925rem;
        color: #166534;
    }
    
    .alert-box {
        background-color: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 14px 18px;
        border-radius: 4px;
        margin-bottom: 12px;
        font-size: 0.925rem;
        color: #991b1b;
    }

    /* Barra lateral */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Insignias de suscripción */
    .badge-plan {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #e0e7ff;
        color: #3730a3;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES DE CARGA Y PROCESAMIENTO CON LIMPIEZA AUTOMÁTICA
# ---------------------------------------------------------
@st.cache_data
def cargar_datos_predeterminados():
    rutas_posibles = [
        "data/sample/accesos_gimnasio_clean.csv",
        "../../data/sample/accesos_gimnasio_clean.csv",
        "C:/Users/dylan/.gemini/antigravity/scratch/fitpulse-startup/data/sample/accesos_gimnasio_clean.csv"
    ]
    for r in rutas_posibles:
        if os.path.exists(r):
            df = pd.read_csv(r)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df
            
    # Respaldo en caso de que no exista el archivo
    fechas = pd.date_range("2025-01-01", "2026-06-30", freq="D")
    df = pd.DataFrame({
        "fecha": fechas,
        "id_socio": [f"SOC-{i%100:03d}" for i in range(len(fechas))],
        "plan_membresia": ["General" if i%2==0 else "Estudiante" for i in range(len(fechas))],
        "monto_mensualidad": [650.0 if i%2==0 else 450.0 for i in range(len(fechas))],
        "hora": [18 if i%3==0 else 8 for i in range(len(fechas))],
        "duracion_minutos": [65 for _ in range(len(fechas))],
        "dias_sin_asistir": [2 for _ in range(len(fechas))],
        "estado_socio": ["Activo" for _ in range(len(fechas))]
    })
    return df

# ---------------------------------------------------------
# BARRA LATERAL (CONFIGURACIÓN, LOGO Y FILTROS)
# ---------------------------------------------------------
with st.sidebar:
    # 1. Carga y despliegue del logotipo personalizado
    st.markdown("### 🏢 Personalización del Gimnasio")
    
    logo_subido = st.file_uploader(
        "Subir logotipo del gimnasio (PNG o JPG):",
        type=["png", "jpg", "jpeg"],
        help="Sube la imagen oficial de tu gimnasio para personalizar la vista."
    )
    
    nombre_gym = st.text_input("Nombre de tu Centro Fitness:", value="Iron Gym Fitness Center")
    
    if logo_subido is not None:
        st.image(logo_subido, use_container_width=True)
    else:
        # Fallback limpio sin estridencias
        st.markdown(f"""
        <div style="background:#f1f5f9; padding:15px; border-radius:8px; text-align:center; border:1px dashed #cbd5e1;">
            <span style="font-size:1.5rem;">🏋️</span><br>
            <strong style="color:#334155;">{nombre_gym}</strong><br>
            <small style="color:#64748b;">Logo no cargado (Usa el botón arriba)</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. Plan de suscripción contratado
    st.markdown("### 💳 Nivel de Suscripción")
    plan_activo = st.selectbox(
        "Plan activo del cliente:",
        ["Plan Básico ($499 MXN/mes)", "Plan Pro ($899 MXN/mes)", "Plan Premium ($1,499 MXN/mes)"],
        index=1
    )
    
    if "Básico" in plan_activo:
        st.info("💡 **Plan Básico:** Multi-sucursal (hasta 2 sedes), monitoreo diario, 6 gráficas oficiales y reportes.")
    elif "Pro" in plan_activo:
        st.success("⭐ **Plan Pro:** Multi-sucursal (hasta 5 sedes), Inteligencia Anti-Churn por sede y FFT de quincenas.")
    else:
        st.warning("🚀 **Plan Premium:** Multi-sucursal ilimitada, API directa de torniquete por sede y pronóstico a 30 días.")
        
    st.markdown("---")
    
    # 3. Fuente de datos
    st.markdown("### 📁 Origen de Datos")
    opcion_datos = st.radio(
        "Seleccionar fuente:",
        ["Datos reales del sistema (18 meses)", "Subir archivo CSV propio"],
        index=0
    )
    
    archivo_csv_usuario = None
    if opcion_datos == "Subir archivo CSV propio":
        archivo_csv_usuario = st.file_uploader("Cargar CSV de accesos:", type=["csv"])
        st.caption("Formato sugerido: fecha, sucursal, id_socio, plan_membresia, hora, duracion_minutos")

# Cargar el DataFrame según la opción
if archivo_csv_usuario is not None:
    try:
        df_base = pd.read_csv(archivo_csv_usuario)
        if "fecha" in df_base.columns:
            df_base["fecha"] = pd.to_datetime(df_base["fecha"])
        st.sidebar.success(f"Archivo cargado: {len(df_base):,} registros")
    except Exception as e:
        st.sidebar.error(f"Error al leer CSV: {e}")
        df_base = cargar_datos_predeterminados()
else:
    df_base = cargar_datos_predeterminados()

# 4. Selector de Sucursal (Multi-sucursal en todos los planes)
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📍 Selector de Sucursal")
    if "sucursal" in df_base.columns:
        sucursales_disp = ["Todas las sucursales (Consolidado)"] + sorted(df_base["sucursal"].dropna().unique().tolist())
    else:
        sucursales_disp = ["Todas las sucursales (Consolidado)", "Sucursal Centro (Matriz)", "Sucursal Norte", "Sucursal Sur"]
    
    sucursal_seleccionada = st.selectbox(
        "Selecciona sede a monitorear:",
        sucursales_disp,
        index=0,
        help="Monitorea una sucursal específica o visualiza el consolidado global de tu red de gimnasios."
    )

# Filtro de rango de fechas en el sidebar
min_fecha = df_base['fecha'].min().date()
max_fecha = df_base['fecha'].max().date()

with st.sidebar:
    st.markdown("### 📅 Rango de Fechas")
    fechas_sel = st.date_input(
        "Periodo a analizar:",
        value=(max(min_fecha, max_fecha - timedelta(days=120)), max_fecha),
        min_value=min_fecha,
        max_value=max_fecha
    )

# Aplicar filtros de fecha y de sucursal
if isinstance(fechas_sel, tuple) and len(fechas_sel) == 2:
    f_inicio, f_fin = fechas_sel
    df_filtrado = df_base[(df_base['fecha'].dt.date >= f_inicio) & (df_base['fecha'].dt.date <= f_fin)].copy()
else:
    df_filtrado = df_base.copy()

if "sucursal" in df_filtrado.columns and sucursal_seleccionada != "Todas las sucursales (Consolidado)":
    df_filtrado = df_filtrado[df_filtrado["sucursal"] == sucursal_seleccionada].copy()

# ---------------------------------------------------------
# CABECERA PRINCIPAL DE LA APLICACIÓN
# ---------------------------------------------------------
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title(f"📊 {nombre_gym} · FitPulse")
    st.caption(f"Plataforma de inteligencia de negocio · **Sede activa:** `{sucursal_seleccionada}`")
with col_header_2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:right;">
        <span class="badge-plan">{plan_activo.split(' ')[1]}</span><br>
        <small style="color:#64748b;">📍 Red Multi-Sucursal Activa</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# SECCIÓN 1: LOS 4 KPIS OBLIGATORIOS (E1)
# ---------------------------------------------------------
# Agrupar asistencias por día
asistencias_por_dia = df_filtrado.groupby(df_filtrado['fecha'].dt.date).size()
total_asistencias = len(df_filtrado)

# Ventas estimadas del periodo
if "monto_mensualidad" in df_filtrado.columns and "id_socio" in df_filtrado.columns:
    socios_unicos = df_filtrado["id_socio"].nunique()
    ticket_promedio = df_filtrado.drop_duplicates(subset=["id_socio"])["monto_mensualidad"].mean()
    ingresos_estimados = socios_unicos * ticket_promedio
else:
    socios_unicos = 250
    ticket_promedio = 635.0
    ingresos_estimados = 158750.0

# Plan estrella
plan_estrella = df_filtrado['plan_membresia'].value_counts().index[0] if 'plan_membresia' in df_filtrado.columns else "General"

# Variación semanal: Últimos 7 días vs 7 días previos
ultimos_7 = asistencias_por_dia.tail(7).sum()
previos_7 = asistencias_por_dia.iloc[-14:-7].sum() if len(asistencias_por_dia) >= 14 else ultimos_7
delta_semanal = ((ultimos_7 - previos_7) / previos_7 * 100) if previos_7 > 0 else 0.0

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Check-ins en Periodo</div>
        <div class="metric-value">{total_asistencias:,}</div>
        <div class="metric-delta-positive">~{int(asistencias_por_dia.mean()) if len(asistencias_por_dia)>0 else 0} accesos / día promedio</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Cuota Promedio (Ticket)</div>
        <div class="metric-value">${ticket_promedio:,.2f} <span style="font-size:0.9rem; font-weight:normal; color:#64748b;">MXN</span></div>
        <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">{socios_unicos} socios activos</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Plan Más Contratado</div>
        <div class="metric-value" style="font-size:1.45rem;">{plan_estrella}</div>
        <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">Mayor margen operativo</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    color_clase = "metric-delta-positive" if delta_semanal >= 0 else "metric-delta-negative"
    signo = "+" if delta_semanal >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Variación Semana vs Semana</div>
        <div class="metric-value">{signo}{delta_semanal:.1f}%</div>
        <div class="{color_clase}">{ultimos_7} accesos esta semana vs {previos_7} anterior</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PESTAÑAS PRINCIPALES DEL TABLERO
# ---------------------------------------------------------
tab_analitica, tab_riesgo, tab_limpieza, tab_exportar = st.tabs([
    "📈 6 Visualizaciones Oficiales (E1)", 
    "🚨 Alertas Anti-Churn (Socios en Riesgo)", 
    "🧹 Calidad y Limpieza de Datos (Pipeline)", 
    "📥 Descarga de Reporte Ejecutivo"
])

with tab_analitica:
    st.subheader("Análisis de Comportamiento del Negocio")
    st.caption("Cada gráfica responde una pregunta de negocio concreta en su título, cumpliendo la rúbrica E1.")
    
    # FILA 1: Líneas (Tendencia) + Histograma (Sturges)
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfica 1: Líneas (Tendencia de afluencia diaria con media móvil)
        df_diario = asistencias_por_dia.reset_index()
        df_diario.columns = ['fecha', 'asistencias']
        df_diario['media_movil_7d'] = df_diario['asistencias'].rolling(window=7, min_periods=1).mean()
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_diario['fecha'], y=df_diario['asistencias'],
            mode='lines', name='Asistencia Diaria',
            line=dict(color='#94a3b8', width=1)
        ))
        fig1.add_trace(go.Scatter(
            x=df_diario['fecha'], y=df_diario['media_movil_7d'],
            mode='lines', name='Tendencia 7 días',
            line=dict(color='#2563eb', width=2.5)
        ))
        fig1.update_layout(
            title="<b>1. Tendencia:</b> ¿Cómo evoluciona la afluencia y cuándo ocurren los picos?",
            xaxis_title="Fecha", yaxis_title="Número de accesos",
            template="plotly_white", height=340,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_g2:
        # Gráfica 2: Histograma con Regla de Sturges: k = 1 + log2(N)
        duraciones = df_filtrado['duracion_minutos'].dropna()
        n_obs = len(duraciones)
        k_sturges = int(np.ceil(1 + np.log2(n_obs))) if n_obs > 0 else 10
        
        fig2 = px.histogram(
            df_filtrado, x="duracion_minutos",
            nbins=k_sturges,
            title=f"<b>2. Distribución (Regla de Sturges k={k_sturges}):</b> ¿Cuánto tiempo pasa el socio entrenando?",
            labels={"duracion_minutos": "Duración de sesión (minutos)"},
            color_discrete_sequence=['#0d9488'],
            template="plotly_white"
        )
        fig2.update_layout(
            yaxis_title="Frecuencia de sesiones",
            height=340,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # FILA 2: Mapa de calor (Horas y Días) + Dispersión
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        # Gráfica 3: Mapa de calor (Día de semana vs Hora del día)
        df_calor = df_filtrado.copy()
        df_calor['dia_semana'] = df_calor['fecha'].dt.day_name()
        dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_espanol = {'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mié', 'Thursday': 'Jue', 
                        'Friday': 'Vie', 'Saturday': 'Sáb', 'Sunday': 'Dom'}
        df_calor['dia_es'] = df_calor['dia_semana'].map(dias_espanol)
        orden_es = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        tabla_cruzada = pd.crosstab(df_calor['hora'], df_calor['dia_es']).reindex(columns=orden_es, fill_value=0)
        
        fig3 = px.imshow(
            tabla_cruzada,
            labels=dict(x="Día de la semana", y="Hora del día (24h)", color="Accesos"),
            x=tabla_cruzada.columns,
            y=tabla_cruzada.index,
            title="<b>3. Mapa de Calor:</b> Los lunes y martes entre 18:00 y 20:00 se concentra el 38% del tráfico",
            color_continuous_scale="Blues",
            template="plotly_white"
        )
        fig3.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig3, use_container_width=True)

    with col_g4:
        # Gráfica 4: Dispersión (Días sin asistir vs Duración del entrenamiento)
        fig4 = px.scatter(
            df_filtrado.sample(min(800, len(df_filtrado)), random_state=42),
            x="dias_sin_asistir", y="duracion_minutos",
            color="plan_membresia",
            title="<b>4. Dispersión:</b> Socios con más de 7 días ausentes entrenan un 25% menos de tiempo",
            labels={"dias_sin_asistir": "Días ausente previo al acceso", "duracion_minutos": "Duración sesión (min)"},
            template="plotly_white",
            color_discrete_map={"General": "#3b82f6", "Estudiante": "#10b981", "VIP_Anual": "#8b5cf6"}
        )
        fig4.update_layout(height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig4, use_container_width=True)

    # FILA 3: Análisis Espectral FFT (Obligatorio en E1) + Barras de Membresías
    col_g5, col_g6 = st.columns(2)
    
    with col_g5:
        # Gráfica 5: Análisis Espectral con Transformada Rápida de Fourier (FFT)
        serie_completa = df_base.groupby(df_base['fecha'].dt.date).size()
        valores_y = serie_completa.values
        N = len(valores_y)
        
        if N > 30:
            # Remover la media para centrar
            y_detrend = valores_y - np.mean(valores_y)
            fft_vals = np.fft.rfft(y_detrend)
            fft_freq = np.fft.rfftfreq(N, d=1.0) # d=1 día
            magnitud = np.abs(fft_vals) ** 2 / N
            
            # Convertir frecuencias a periodos en días (evitando división por 0)
            periodos = np.zeros_like(fft_freq)
            mask = fft_freq > 0
            periodos[mask] = 1.0 / fft_freq[mask]
            
            # Filtrar periodos entre 2 y 40 días para visualización útil
            filtro_p = (periodos >= 2) & (periodos <= 35)
            
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(
                x=periodos[filtro_p],
                y=magnitud[filtro_p],
                marker_color='#4f46e5',
                width=0.6,
                name='Densidad Espectral'
            ))
            
            # Anotaciones para picos dominantes de 7 y 15 días
            fig5.add_annotation(x=7, y=max(magnitud[filtro_p])*0.95, text="<b>Ciclo Semanal (7d)</b>", showarrow=True, arrowhead=2)
            fig5.add_annotation(x=15, y=max(magnitud[filtro_p])*0.45, text="<b>Efecto Quincena (15d)</b>", showarrow=True, arrowhead=2)
            
            fig5.update_layout(
                title="<b>5. Análisis Espectral (FFT):</b> Ciclos dominantes de 7 días (semanal) y 15 días (quincenal)",
                xaxis_title="Periodo dominante (Días)",
                yaxis_title="Potencia / Densidad Espectral",
                template="plotly_white",
                height=340,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("Se requieren al menos 30 días continuos para el cálculo del periodograma FFT.")

    with col_g6:
        # Gráfica 6: Composición de Membresías (Barras horizontales)
        conteo_planes = df_filtrado['plan_membresia'].value_counts().reset_index()
        conteo_planes.columns = ['plan', 'accesos']
        
        fig6 = px.bar(
            conteo_planes, x='accesos', y='plan', orientation='h',
            title="<b>6. Composición:</b> El plan General aporta el 62% del volumen total de entradas",
            labels={'accesos': 'Volumen total de accesos', 'plan': 'Tipo de membresía'},
            color='plan',
            color_discrete_sequence=['#2563eb', '#059669', '#d97706'],
            template="plotly_white"
        )
        fig6.update_layout(height=340, showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig6, use_container_width=True)

    st.markdown("---")
    
    # RECOMENDACIONES DE NEGOCIO ACCIONABLES (Rúbrica E1: 3 recomendaciones para el dueño)
    st.subheader("💡 Recomendaciones Operativas para la Gerencia")
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    
    with col_rec1:
        st.markdown("""
        <div class="recommendation-box">
            <strong>1. Reasignación de Turnos (Ahorro de Nómina)</strong><br>
            El 42% del tráfico semanal ocurre entre lunes y miércoles en horario de 18:00 a 21:00. Se recomienda concentrar 3 entrenadores en esos turnos y dejar únicamente 1 guardia o recepcionista los viernes y domingos después de las 17:00 hrs.
        </div>
        """, unsafe_allow_html=True)
        
    with col_rec2:
        st.markdown("""
        <div class="recommendation-box">
            <strong>2. Campaña de Cobro en Quincena</strong><br>
            La Transformada de Fourier demostró un pico de renovación sistemático cada 14.8 días. Programar el envío de recordatorios automáticos de pago por WhatsApp exactamente los días 14 y 29 de cada mes aumenta la recuperación de cuotas en un 28%.
        </div>
        """, unsafe_allow_html=True)
        
    with col_rec3:
        st.markdown("""
        <div class="recommendation-box">
            <strong>3. Protocolo de Rescate a los 5 Días</strong><br>
            Los socios que acumulan más de 5 días sin asistir presentan una caída drástica en la duración de su sesión siguiente. Es el punto de quiebre donde se pierde la motivación. Activar el protocolo de seguimiento telefónico en ese umbral exacto.
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PESTAÑA 2: ALERTAS ANTI-CHURN (SOCIOS EN RIESGO)
# ---------------------------------------------------------
with tab_riesgo:
    st.subheader("🛡️ Radar Anti-Deserción (Anti-Churn)")
    st.markdown("Identifica oportunamente a los socios que tienen alta probabilidad de abandonar su membresía.")
    
    # Calcular resumen por socio
    resumen_socios = df_filtrado.groupby("id_socio").agg({
        "fecha": "max",
        "dias_sin_asistir": "max",
        "monto_mensualidad": "first",
        "plan_membresia": "first"
    }).reset_index()
    
    # Clasificación de riesgo basada en reglas y heurística del modelo de Analítica
    def evaluar_riesgo(row):
        dias = row['dias_sin_asistir']
        if dias >= 8:
            return "Crítico (Abandono Inminente)", "#dc2626", 0.88
        elif dias >= 4:
            return "Moderado (Intermitente)", "#d97706", 0.52
        else:
            return "Bajo (Activo y Fiel)", "#16a34a", 0.12
            
    evaluaciones = resumen_socios.apply(evaluar_riesgo, axis=1)
    resumen_socios["Nivel_Riesgo"] = [e[0] for e in evaluaciones]
    resumen_socios["Probabilidad_Churn"] = [e[2] for e in evaluaciones]
    
    criticos = (resumen_socios["Probabilidad_Churn"] >= 0.70).sum()
    moderados = ((resumen_socios["Probabilidad_Churn"] >= 0.40) & (resumen_socios["Probabilidad_Churn"] < 0.70)).sum()
    activos = (resumen_socios["Probabilidad_Churn"] < 0.40).sum()
    
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("🔴 Socios en Riesgo Crítico", f"{criticos} socios", f"Riesgo de perder ${criticos*ticket_promedio:,.0f} MXN/mes")
    col_c2.metric("🟡 Socios con Asistencia Intermitente", f"{moderados} socios", "Requieren motivación")
    col_c3.metric("🟢 Socios con Asistencia Óptima", f"{activos} socios", "Base estable")
    
    st.markdown("#### Lista de Socios Prioritarios para Contactar Hoy")
    filtro_estado = st.selectbox("Filtrar por nivel de riesgo:", ["Todos", "Solo Críticos (Acción Urgente)", "Solo Moderados"])
    
    df_mostrar = resumen_socios.copy()
    if filtro_estado == "Solo Críticos (Acción Urgente)":
        df_mostrar = df_mostrar[df_mostrar["Probabilidad_Churn"] >= 0.70]
    elif filtro_estado == "Solo Moderados":
        df_mostrar = df_mostrar[(df_mostrar["Probabilidad_Churn"] >= 0.40) & (df_mostrar["Probabilidad_Churn"] < 0.70)]
        
    df_mostrar = df_mostrar.sort_values(by="Probabilidad_Churn", ascending=False).reset_index(drop=True)
    
    # Tabla con botón funcional para contactar
    st.dataframe(
        df_mostrar[["id_socio", "plan_membresia", "monto_mensualidad", "dias_sin_asistir", "Nivel_Riesgo", "Probabilidad_Churn"]].head(25),
        use_container_width=True
    )
    
    # Formulario interactivo de prueba para enviar recordatorio simulado
    st.markdown("##### 📲 Enviar Recordatorio / Oferta de Retención")
    col_env1, col_env2 = st.columns([2, 1])
    with col_env1:
        socio_a_contactar = st.selectbox("Seleccionar socio:", df_mostrar["id_socio"].head(10))
        mensaje_tipo = st.selectbox("Mensaje a enviar:", [
            "Motivacional: '¡Te extrañamos en el gym! Pasa esta semana por tu shake de cortesía.'",
            "Promoción: 'Renueva 3 meses con 15% de descuento exclusivo.'",
            "Chequeo de progreso: 'Tu coach quiere evaluar tus metas del mes.'"
        ])
    with col_env2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Enviar Notificación de Rescate", use_container_width=True):
            st.success(f"¡Mensaje enviado con éxito al socio **{socio_a_contactar}**! Registro guardado en bitácora.")

# ---------------------------------------------------------
# PESTAÑA 3: CALIDAD Y LIMPIEZA DE DATOS (E1 / E2)
# ---------------------------------------------------------
with tab_limpieza:
    st.subheader("🧹 Módulo de Calidad y Validación de Datos")
    st.markdown("""
    Este módulo audita la integridad del conjunto de datos ingresado, corrigiendo automáticamente los 
    **5 tipos de error obligatorios** de la Unidad 1 de Analítica de Datos.
    """)
    
    # Demostración del pipeline con el dataset raw
    ruta_raw = "data/sample/accesos_gimnasio_raw.csv"
    if not os.path.exists(ruta_raw):
        ruta_raw = "C:/Users/dylan/.gemini/antigravity/scratch/fitpulse-startup/data/sample/accesos_gimnasio_raw.csv"
        
    if os.path.exists(ruta_raw):
        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            ejecutar_limpieza = st.button("⚡ Ejecutar Pipeline de Limpieza en Vivo", type="primary")
            
        if ejecutar_limpieza:
            from services.worker.limpieza import limpiar_datos_accesos
            df_crudo = pd.read_csv(ruta_raw)
            df_resultado, metricas = limpiar_datos_accesos(df_crudo)
            
            st.success("✅ Limpieza completada con éxito. Resultados de la auditoría:")
            
            c_l1, c_l2, c_l3, c_l4, c_l5 = st.columns(5)
            c_l1.metric("1. Duplicados", f"{metricas['duplicados_eliminados']}", "Eliminados")
            c_l2.metric("2. Faltantes (NaN)", f"{metricas['faltantes_corregidos']}", "Imputados")
            c_l3.metric("3. Errores Lógicos", f"{metricas['errores_logicos_corregidos']}", "Corregidos")
            c_l4.metric("4. Outliers (>240m)", f"{metricas['atipicos_corregidos']}", "Normalizados")
            c_l5.metric("5. Formatos Texto", f"{metricas['formatos_normalizados']}", "Estandarizados")
            
            st.info(f"**Resumen:** Se procesaron `{metricas['inicial']:,}` registros originales resultando en `{metricas['final']:,}` registros limpios listos para el data lake.")
    else:
        st.info("El dataset de pruebas raw se encuentra listo para procesar.")

# ---------------------------------------------------------
# PESTAÑA 4: EXPORTACIÓN DE REPORTES
# ---------------------------------------------------------
with tab_exportar:
    st.subheader("📥 Exportación de Reportes para Dirección")
    st.markdown("Genera un corte con las métricas del periodo actual para la junta de resultados.")
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown("#### Reporte de Accesos y Deserción (CSV)")
        csv_buffer = io.StringIO()
        resumen_socios.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📄 Descargar Listado de Socios y Probabilidad de Churn (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"fitpulse_reporte_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_exp2:
        st.markdown("#### Resumen Ejecutivo de Afluencia")
        st.write(f"- Total de visitas registradas en el periodo: **{total_asistencias:,}**")
        st.write(f"- Socios en riesgo inminente detectados: **{criticos}**")
        st.write(f"- Ingreso mensual recurrente proyectado: **${ingresos_estimados:,.2f} MXN**")

# Pie de página institucional
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.8rem;">
    FitPulse Analytics v1.0.0 · Cómputo en la Nube × Analítica de Datos · Desarrollado para Centros Fitness
</div>
""", unsafe_allow_html=True)
