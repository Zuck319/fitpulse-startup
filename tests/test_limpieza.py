"""
Pruebas unitarias para el módulo de limpieza y calidad de datos (Worker E1/E2).
Verifica la corrección de los 5 tipos de error:
1. Duplicados
2. Faltantes (NaN)
3. Errores lógicos
4. Valores atípicos (outliers)
5. Inconsistencias de formato
"""

import sys
import os
import pandas as pd
import numpy as np

# Asegurar ruta del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.worker.limpieza import limpiar_datos_accesos

def test_limpieza_completa():
    # Dataset sucio sintético controlado
    df_sucio = pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "id_socio": ["SOC-001", "SOC-001", "SOC-002", "SOC-003", "SOC-004"],
        "plan_membresia": ["general", "general", "estudiante", "VIP_ANUAL", "otro"],
        "duracion_minutos": [60, 60, -45, 999, np.nan],
        "dias_sin_asistir": [2, 2, np.nan, -1, 5]
    })
    
    df_limpio, reporte = limpiar_datos_accesos(df_sucio)
    
    # 1. Verificar duplicados
    assert reporte["duplicados_eliminados"] == 1, f"Esperado 1 duplicado, obtenido {reporte['duplicados_eliminados']}"
    assert len(df_limpio) == 4, f"Esperado 4 registros, obtenido {len(df_limpio)}"
    
    # 2. Verificar que no haya duraciones negativas ni atípicas (999)
    assert (df_limpio["duracion_minutos"] < 0).sum() == 0, "Aún hay duraciones negativas"
    assert (df_limpio["duracion_minutos"] > 240).sum() == 0, "Aún hay duraciones atípicas mayores a 240"
    assert df_limpio["duracion_minutos"].isna().sum() == 0, "Aún hay duraciones NaN"
    
    # 3. Verificar que no haya días sin asistir negativos ni NaN
    assert (df_limpio["dias_sin_asistir"] < 0).sum() == 0, "Aún hay días sin asistir negativos"
    assert df_limpio["dias_sin_asistir"].isna().sum() == 0, "Aún hay días sin asistir NaN"
    
    # 4. Formatos estandarizados
    for plan in df_limpio["plan_membresia"]:
        assert plan[0].isupper(), f"Plan {plan} no inicia con mayúscula"
        
    print("[PASS] Todas las pruebas unitarias de limpieza pasaron exitosamente.")
    print("Reporte de limpieza:", reporte)

if __name__ == "__main__":
    test_limpieza_completa()
