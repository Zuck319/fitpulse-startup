"""
Módulo de limpieza y validación de datos para FitPulse Analytics.
Diseñado para la Unidad 1/2 de Analítica y el Worker de E2/E3.
Detecta y corrige los 5 tipos de fallas:
1. Duplicados
2. Valores faltantes
3. Errores de formato (tipos y strings)
4. Errores lógicos (valores negativos)
5. Valores atípicos (outliers)
"""

import pandas as pd
import numpy as np

def limpiar_datos_accesos(df_raw: pd.DataFrame):
    """
    Recibe un DataFrame crudo y devuelve:
    (df_clean, reporte_metricas)
    """
    reporte = {
        "inicial": len(df_raw),
        "duplicados_eliminados": 0,
        "faltantes_corregidos": 0,
        "errores_logicos_corregidos": 0,
        "atipicos_corregidos": 0,
        "formatos_normalizados": 0,
        "final": 0
    }
    
    df = df_raw.copy()
    
    # 1. Duplicados
    duplicados_antes = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    reporte["duplicados_eliminados"] = int(duplicados_antes)
    
    # 2. Formato en cadenas (plan_membresia a Capitalize)
    if "plan_membresia" in df.columns:
        inconsistencias = (~df["plan_membresia"].isin(["Estudiante", "General", "VIP_Anual"])).sum()
        df["plan_membresia"] = df["plan_membresia"].astype(str).str.strip()
        # Mapeo normalizado
        mapeo = {
            "estudiante": "Estudiante",
            "general": "General",
            "vip_anual": "VIP_Anual",
            "vip": "VIP_Anual"
        }
        df["plan_membresia"] = df["plan_membresia"].apply(lambda x: mapeo.get(x.lower(), x.title()))
        reporte["formatos_normalizados"] = int(inconsistencias)
        
    # 3. Errores lógicos (duracion_minutos negativos)
    if "duracion_minutos" in df.columns:
        # Mediana considerando únicamente valores válidos y realistas (entre 10 y 240 minutos)
        filtro_validos = (df["duracion_minutos"] > 10) & (df["duracion_minutos"] <= 240)
        mediana_duracion = df.loc[filtro_validos, "duracion_minutos"].median()
        if pd.isna(mediana_duracion):
            mediana_duracion = 60.0
            
        negativos = (df["duracion_minutos"] < 0).sum()
        df.loc[df["duracion_minutos"] < 0, "duracion_minutos"] = mediana_duracion
        reporte["errores_logicos_corregidos"] = int(negativos)
        
        # 4. Valores atípicos (duración > 240 minutos)
        atipicos = (df["duracion_minutos"] > 240).sum()
        df.loc[df["duracion_minutos"] > 240, "duracion_minutos"] = mediana_duracion
        reporte["atipicos_corregidos"] = int(atipicos)
        
        # Faltantes en duracion
        faltantes_dur = df["duracion_minutos"].isna().sum()
        df["duracion_minutos"] = df["duracion_minutos"].fillna(mediana_duracion)
        reporte["faltantes_corregidos"] += int(faltantes_dur)
        
    # Faltantes en dias_sin_asistir
    if "dias_sin_asistir" in df.columns:
        faltantes_dias = df["dias_sin_asistir"].isna().sum()
        mediana_dias = df["dias_sin_asistir"].dropna().median()
        if pd.isna(mediana_dias):
            mediana_dias = 2
        df["dias_sin_asistir"] = df["dias_sin_asistir"].fillna(mediana_dias)
        reporte["faltantes_corregidos"] += int(faltantes_dias)
        
        # Negativos en días sin asistir
        neg_dias = (df["dias_sin_asistir"] < 0).sum()
        df.loc[df["dias_sin_asistir"] < 0, "dias_sin_asistir"] = mediana_dias
        reporte["errores_logicos_corregidos"] += int(neg_dias)

    # Conversión estricta de tipos de fecha
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
        
    reporte["final"] = len(df)
    return df, reporte

if __name__ == "__main__":
    test_df = pd.DataFrame({
        "id_socio": ["S1", "S1", "S2", "S3"],
        "plan_membresia": ["general", "general", "ESTUDIANTE", "vip_anual"],
        "duracion_minutos": [60, 60, -45, 999],
        "dias_sin_asistir": [1, 1, np.nan, 5]
    })
    clean, rep = limpiar_datos_accesos(test_df)
    print("Reporte de limpieza de prueba:", rep)
