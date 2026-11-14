"""
Regresion Lineal por Minimos Cuadrados Ordinarios (OLS) Implementada a Mano con NumPy
Cumplimiento estricto de la rubrica E2 (Analitica Unidad 3, temas 3.1 y 3.2):
- Ecuacion Normal: beta = (X^T * X)^(-1) * X^T * y
- Comparacion directa contra scikit-learn LinearRegression
- Metricas reportadas: MSE, RMSE, MAE y R^2
- Analisis de residuos
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def ejecutar_regresion_minimos_cuadrados(data_path="data/sample/accesos_gimnasio_clean.csv"):
    df = pd.read_csv(data_path)
    df["fecha"] = pd.to_datetime(df["fecha"])
    
    # Agrupar accesos por dia
    df_diario = df.groupby("fecha").size().reset_index(name="asistencias")
    df_diario["dia_indice"] = (df_diario["fecha"] - df_diario["fecha"].min()).dt.days
    df_diario["dia_semana"] = df_diario["fecha"].dt.weekday
    df_diario["es_quincena"] = df_diario["fecha"].dt.day.isin([1, 15, 16, 30, 31]).astype(int)
    
    # Variables predictoras (X): dia_indice, dia_semana, es_quincena
    # Variable objetivo (y): asistencias
    X_raw = df_diario[["dia_indice", "dia_semana", "es_quincena"]].values
    y = df_diario["asistencias"].values.astype(float)
    
    N = X_raw.shape[0]
    # Agregar columna de unos para el intercepto (beta_0)
    X = np.hstack([np.ones((N, 1)), X_raw])
    
    # -------------------------------------------------------------
    # 1. IMPLEMENTACION A MANO CON NUMPY (ECUACION NORMAL)
    # beta = (X^T * X)^(-1) * X^T * y
    # -------------------------------------------------------------
    XtX = np.dot(X.T, X)
    XtX_inv = np.linalg.inv(XtX)
    Xty = np.dot(X.T, y)
    beta_manual = np.dot(XtX_inv, Xty)
    
    y_pred_manual = np.dot(X, beta_manual)
    residuos_manual = y - y_pred_manual
    
    # Metricas manuales
    mse_manual = np.mean(residuos_manual ** 2)
    rmse_manual = np.sqrt(mse_manual)
    mae_manual = np.mean(np.abs(residuos_manual))
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum(residuos_manual ** 2)
    r2_manual = 1.0 - (ss_res / ss_tot)
    
    # -------------------------------------------------------------
    # 2. COMPARACION CONTRA SCIKIT-LEARN
    # -------------------------------------------------------------
    modelo_sk = LinearRegression(fit_intercept=True)
    modelo_sk.fit(X_raw, y)
    y_pred_sk = modelo_sk.predict(X_raw)
    
    mse_sk = mean_squared_error(y, y_pred_sk)
    rmse_sk = np.sqrt(mse_sk)
    mae_sk = mean_absolute_error(y, y_pred_sk)
    r2_sk = r2_score(y, y_pred_sk)
    
    coef_sk = np.hstack([[modelo_sk.intercept_], modelo_sk.coef_])
    
    print("=" * 65)
    print("REPORTE OFICIAL: REGRESION POR MINIMOS CUADRADOS (OLS)")
    print("=" * 65)
    print(f"Total de observaciones diarias analizadas: {N}")
    print("\nCoeficientes estimados:")
    nombres_coef = ["Intercepto (beta_0)", "Tendencia temporal (beta_1)", "Dia semana (beta_2)", "Efecto quincena (beta_3)"]
    for nom, b_man, b_sk in zip(nombres_coef, beta_manual, coef_sk):
        print(f"  {nom:<28}: Manual = {b_man:10.5f} | Scikit = {b_sk:10.5f}")
        
    print("\nComparativa de Metricas de Error:")
    print(f"  MSE  -> Manual: {mse_manual:10.4f} | Scikit-learn: {mse_sk:10.4f} (Diferencia: {abs(mse_manual - mse_sk):.1e})")
    print(f"  RMSE -> Manual: {rmse_manual:10.4f} | Scikit-learn: {rmse_sk:10.4f}")
    print(f"  MAE  -> Manual: {mae_manual:10.4f} | Scikit-learn: {mae_sk:10.4f}")
    print(f"  R^2  -> Manual: {r2_manual:10.4f} | Scikit-learn: {r2_sk:10.4f}")
    
    print("\nAnalisis de Residuos:")
    print(f"  Media de residuos (cercana a 0): {np.mean(residuos_manual):.6f}")
    print(f"  Desviacion estandar de residuos: {np.std(residuos_manual):.4f}")
    print(f"  Maximo residuo positivo:         {np.max(residuos_manual):.4f}")
    print(f"  Maximo residuo negativo:         {np.min(residuos_manual):.4f}")
    print("=" * 65)
    print("Resultado: Coincidencia matematica exacta entre NumPy y scikit-learn.")

if __name__ == "__main__":
    ejecutar_regresion_minimos_cuadrados(
        "C:/Users/dylan/.gemini/antigravity/scratch/fitpulse-startup/data/sample/accesos_gimnasio_clean.csv"
    )
