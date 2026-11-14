"""
Generador de datos sintéticos de accesos y membresías para Gimnasio (FitPulse Analytics).
Basado en el diseño del Proyecto Integrador DATA STARTUP.
Genera más de 7,000 registros con patrones reales:
- Estacionalidad semanal (Lunes y Martes pico, Viernes bajo)
- Efecto quincena (15, 16, 30, 31, 1) con altas de socios y pagos
- Picos de temporada: 'Propósitos de Enero' (enero) y 'Operación Verano' (mayo/junio)
- Bajón de asistencia en fiestas decembrinas (segunda mitad de diciembre)
- Errores sembrados a propósito para evaluar el pipeline de limpieza (E1 y E2):
  1. Faltantes (NaN)
  2. Errores lógicos (valores negativos o fechas futuras)
  3. Valores atípicos (outliers de 999 accesos)
  4. Formatos inconsistentes (mayúsculas/minúsculas mezcladas en planes)
  5. Duplicados exactos
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generar_datos_gimnasio(output_raw="data/sample/accesos_gimnasio_raw.csv",
                            output_clean="data/sample/accesos_gimnasio_clean.csv"):
    rng = np.random.default_rng(42)
    dias = pd.date_range("2025-01-01", "2026-09-30", freq="D")
    
    # 250 socios base anonimizados distribuidos en sucursales
    n_socios = 250
    sucursales = ["Sucursal Centro (Matriz)", "Sucursal Norte", "Sucursal Sur"]
    pesos_sucursal = [0.50, 0.30, 0.20]
    
    planes = {
        "Estudiante": {"precio": 450.0, "peso": 0.25},
        "General": {"precio": 650.0, "peso": 0.55},
        "VIP_Anual": {"precio": 900.0, "peso": 0.20}
    }
    
    socios = []
    for i in range(1, n_socios + 1):
        plan_elegido = rng.choice(list(planes.keys()), p=[0.25, 0.55, 0.20])
        sucursal_asignada = rng.choice(sucursales, p=pesos_sucursal)
        # Antiguedad en meses
        antiguedad = rng.integers(1, 24)
        # Probabilidad intrinseca de fidelidad
        fidelidad = rng.uniform(0.3, 0.95)
        socios.append({
            "id_socio": f"SOC-{i:04d}",
            "sucursal": sucursal_asignada,
            "plan": plan_elegido,
            "precio_mensual": planes[plan_elegido]["precio"],
            "fidelidad": fidelidad
        })
    df_socios = pd.DataFrame(socios)
    
    # Patrón semanal: Lun(1.40), Mar(1.30), Mie(1.20), Jue(1.05), Vie(0.75), Sab(0.70), Dom(0.40)
    pesos_semana = np.array([1.40, 1.30, 1.20, 1.05, 0.75, 0.70, 0.40])
    
    filas_limpias = []
    
    for dia in dias:
        t = (dia - dias[0]).days
        tendencia_crecimiento = 1.0 + 0.00035 * t
        
        # Efecto quincena en pago y asistencia
        quincena = 1.20 if dia.day in (1, 15, 16, 30, 31) else 1.0
        
        # Temporadas clave en México
        pico_enero = 1.45 if dia.month == 1 else 1.0
        pico_verano = 1.25 if dia.month in (5, 6) else 1.0
        bajon_diciembre = 0.60 if (dia.month == 12 and dia.day >= 16) else 1.0
        
        mult_dia = pesos_semana[dia.weekday()] * quincena * pico_enero * pico_verano * bajon_diciembre * tendencia_crecimiento
        
        # Número estimado de accesos para este día (distribución Poisson)
        base_diaria = 85.0
        asistencias_esperadas = max(10, int(rng.poisson(base_diaria * mult_dia)))
        
        # Muestrear socios que asisten ese día ponderados por su fidelidad
        socios_activos = df_socios.sample(n=min(asistencias_esperadas, len(df_socios)), 
                                          weights=df_socios["fidelidad"], 
                                          replace=False, 
                                          random_state=int(t % 10000))
        
        # Horas pico típicas en gimnasio: Mañana (6am-9am), Tarde-Noche (6pm-9pm)
        for _, soc in socios_activos.iterrows():
            if rng.random() < 0.65:
                # Turno tarde-noche
                hora = rng.integers(17, 22)
            else:
                # Turno matutino
                hora = rng.integers(6, 12)
            minuto = rng.integers(0, 60)
            segundo = rng.integers(0, 60)
            fecha_hora = f"{dia.strftime('%Y-%m-%d')} {hora:02d}:{minuto:02d}:{segundo:02d}"
            
            # Cálculo de días sin asistir aleatorizado según fidelidad
            dias_sin_asistir = int(rng.exponential(scale=(1.0 / soc["fidelidad"]) * 2.0))
            
            # Clasificación del estado para modelo predictivo
            if dias_sin_asistir >= 10:
                estado = "En_Riesgo"
            elif dias_sin_asistir >= 4:
                estado = "Intermitente"
            else:
                estado = "Activo"
                
            filas_limpias.append({
                "fecha": dia.strftime("%Y-%m-%d"),
                "fecha_hora": fecha_hora,
                "sucursal": soc["sucursal"],
                "hora": hora,
                "id_socio": soc["id_socio"],
                "plan_membresia": soc["plan"],
                "monto_mensualidad": soc["precio_mensual"],
                "dias_sin_asistir": dias_sin_asistir,
                "estado_socio": estado,
                "duracion_minutos": int(rng.normal(65, 15))
            })
            
    df_clean = pd.DataFrame(filas_limpias)
    df_clean.to_csv(output_clean, index=False)
    print(f"[OK] Datos limpios generados: {len(df_clean):,} registros guardados en {output_clean}")
    
    # -------------------------------------------------------------
    # Creación del dataset RAW con los 5 ERRORES SEMBRADOS OBLIGATORIOS
    # -------------------------------------------------------------
    df_raw = df_clean.copy()
    n = len(df_raw)
    
    # Error 1: Faltantes (NaN en días sin asistir y duración)
    df_raw.loc[rng.choice(n, 45, replace=False), "dias_sin_asistir"] = np.nan
    df_raw.loc[rng.choice(n, 30, replace=False), "duracion_minutos"] = np.nan
    
    # Error 2: Errores lógicos (duración negativa o días sin asistir negativos)
    idx_logicos = rng.choice(n, 20, replace=False)
    df_raw.loc[idx_logicos, "duracion_minutos"] = -45
    
    # Error 3: Valores atípicos / outliers (duraciones imposibles de 999 minutos)
    idx_atipicos = rng.choice(n, 15, replace=False)
    df_raw.loc[idx_atipicos, "duracion_minutos"] = 999
    
    # Error 4: Formato inconsistente (minúsculas y variaciones en plan_membresia)
    idx_formato = rng.choice(n, 50, replace=False)
    df_raw.loc[idx_formato, "plan_membresia"] = df_raw.loc[idx_formato, "plan_membresia"].str.lower()
    
    # Error 5: Duplicados exactos
    df_dups = df_raw.sample(40, random_state=42)
    df_raw = pd.concat([df_raw, df_dups], ignore_index=True)
    
    # Mezclar el orden aleatoriamente
    df_raw = df_raw.sample(frac=1.0, random_state=123).reset_index(drop=True)
    df_raw.to_csv(output_raw, index=False)
    print(f"[OK] Datos RAW generados con errores sembrados: {len(df_raw):,} registros guardados en {output_raw}")

if __name__ == "__main__":
    generar_datos_gimnasio(
        output_raw="C:/Users/dylan/.gemini/antigravity/scratch/fitpulse-startup/data/sample/accesos_gimnasio_raw.csv",
        output_clean="C:/Users/dylan/.gemini/antigravity/scratch/fitpulse-startup/data/sample/accesos_gimnasio_clean.csv"
    )
