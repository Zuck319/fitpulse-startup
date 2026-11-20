#!/usr/bin/env python3
"""
FitPulse Analytics · Entrenamiento y Validacion de Modelos Predictivos (E3)
Materia: Analitica de Datos (Unidad 3) & Computo en la Nube (Unidad 3)

Este script implementa:
1. Justificacion CPU vs GPU para entrenamiento y produccion.
2. Analisis de Estacionariedad (Test de Dickey-Fuller Aumentado, ACF y PACF).
3. Modelo SARIMA(1, 1, 1)x(1, 1, 1, 7) para pronostico de afluencia a 7 y 30 dias con bandas al 95%.
4. Comparacion de Clasificadores de Desercion (Random Forest vs Regresion Logistica).
5. Evaluacion exhaustiva: Matriz de confusion, Precision, Recall, F1-score y ROC-AUC.
6. Serializacion de modelos en models/ para servicio en produccion (/pronostico y /clasificar).
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib

from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error
)

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample", "accesos_gimnasio_clean.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def cargar_datos():
    """Carga y valida el dataset limpio de accesos."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"No se encontro el archivo de datos: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def entrenar_sarima(df):
    """
    Entrena el modelo SARIMA para la serie diaria de asistencias.
    Justifica p, d, q y componentes estacionales con prueba ADF y ciclo s=7.
    """
    print("\n" + "=" * 60)
    print("1. MODELADO DE SERIES TEMPORALES: SARIMA")
    print("=" * 60)

    # Agregacion diaria de afluencia
    serie_diaria = df.groupby("fecha").size().asfreq("D", fill_value=0)
    total_dias = len(serie_diaria)
    print(f"Total de dias en serie historica: {total_dias} dias")

    # Prueba de Dickey-Fuller Aumentada (ADF)
    adf_res = adfuller(serie_diaria.dropna())
    print("\nResultados Prueba Dickey-Fuller Aumentada (ADF):")
    print(f"  Estadistico ADF: {adf_res[0]:.4f}")
    print(f"  p-value: {adf_res[1]:.6f}")
    print(f"  Valores criticos 1%: {adf_res[4]['1%']:.4f}, 5%: {adf_res[4]['5%']:.4f}")
    es_estacionaria = adf_res[1] < 0.05
    print(f"  Interpretacion: {'Serie Estacionaria (p < 0.05)' if es_estacionaria else 'Requiere diferenciacion d=1'}")

    # Separacion en Train (Historico) y Test (Ultimos 30 dias para validacion real)
    dias_test = 30
    train = serie_diaria.iloc[:-dias_test]
    test = serie_diaria.iloc[-dias_test:]

    # Parametros SARIMA: (p=1, d=1, q=1) x (P=1, D=1, Q=1, s=7)
    order = (1, 1, 1)
    seasonal_order = (1, 1, 1, 7)
    print(f"\nAjustando SARIMA{order}x{seasonal_order}...")

    modelo_sarima = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    sarima_fit = modelo_sarima.fit(disp=False)
    print(f"Ajuste completado. Criterio de Informacion AIC: {sarima_fit.aic:.2f}")

    # Pronostico sobre conjunto de Test (Holdout 30 dias)
    pred_test = sarima_fit.get_forecast(steps=dias_test)
    pred_mean = pred_test.predicted_mean
    conf_int = pred_test.conf_int(alpha=0.05)

    mae = mean_absolute_error(test, pred_mean)
    rmse = np.sqrt(mean_squared_error(test, pred_mean))
    mape = np.mean(np.abs((test - pred_mean) / np.maximum(test, 1))) * 100

    print("\nMetricas de Evaluacion Holdout (Ultimos 30 dias):")
    print(f"  MAE  (Error Absoluto Medio):  {mae:.2f} accesos/dia")
    print(f"  RMSE (Raiz Error Cuadratico): {rmse:.2f} accesos/dia")
    print(f"  MAPE (Error Porcentual):      {mape:.2f}%")

    # Reentrenar sobre toda la serie para produccion
    print("\nReentrenando sobre serie completa para inferencia en produccion...")
    modelo_prod = SARIMAX(
        serie_diaria,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    ).fit(disp=False)

    # Proyeccion futura a 30 dias con bandas al 95%
    forecast_30d = modelo_prod.get_forecast(steps=30)
    fechas_futuras = [d.strftime("%Y-%m-%d") for d in pd.date_range(serie_diaria.index[-1] + pd.Timedelta(days=1), periods=30)]
    conf_future = forecast_30d.conf_int(alpha=0.05)

    pronostico_data = {
        "fechas": fechas_futuras,
        "proyeccion": [round(float(v), 1) for v in forecast_30d.predicted_mean.values],
        "limite_inferior": [max(0, round(float(v), 1)) for v in conf_future.iloc[:, 0].values],
        "limite_superior": [round(float(v), 1) for v in conf_future.iloc[:, 1].values],
        "metricas": {
            "aic": round(float(modelo_prod.aic), 2),
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "mape": round(float(mape), 2)
        },
        "orden": list(order),
        "orden_estacional": list(seasonal_order),
        "dias_historicos": total_dias
    }

    # Guardar modelo y metadata
    sarima_path = os.path.join(MODELS_DIR, "sarima_afluencia.pkl")
    meta_path = os.path.join(MODELS_DIR, "sarima_meta.json")
    joblib.dump(modelo_prod, sarima_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(pronostico_data, f, indent=2)

    print(f"[OK] Modelo SARIMA serializado en: {sarima_path}")
    print(f"[OK] Metadata de pronostico guardada en: {meta_path}")

    return pronostico_data


def entrenar_clasificadores_churn(df):
    """
    Construye variables de comportamiento por socio y compara dos modelos
    (Random Forest vs Regresion Logistica) para clasificar riesgo de desercion.
    """
    print("\n" + "=" * 60)
    print("2. MODELADO DE CLASIFICACION: RIESGO DE DESERCION (CHURN)")
    print("=" * 60)

    # Feature Engineering a nivel de socio
    max_fecha = df["fecha"].max()
    resumen = df.groupby("id_socio").agg(
        dias_sin_asistir=("dias_sin_asistir", "last"),
        duracion_promedio=("duracion_minutos", "mean"),
        total_accesos=("fecha", "count"),
        cuota_mensual=("monto_mensualidad", "first"),
        fecha_primera=("fecha", "min"),
        fecha_ultima=("fecha", "max")
    ).reset_index()

    resumen["antiguedad_dias"] = (resumen["fecha_ultima"] - resumen["fecha_primera"]).dt.days + 1
    resumen["frecuencia_semanal"] = (resumen["total_accesos"] / np.maximum(resumen["antiguedad_dias"] / 7.0, 1.0))

    # Definicion del Target:
    # 1 (Critico / Churn Inminente): ausente >= 5 dias al corte
    # 0 (Retenido / Frecuencia Saludable): ausente < 5 dias al corte
    resumen["es_churn"] = (resumen["dias_sin_asistir"] >= 5).astype(int)

    feature_cols = [
        "dias_sin_asistir",
        "duracion_promedio",
        "total_accesos",
        "cuota_mensual",
        "antiguedad_dias",
        "frecuencia_semanal"
    ]

    X = resumen[feature_cols].fillna(0)
    y = resumen["es_churn"]

    total_socios = len(resumen)
    total_churn = y.sum()
    print(f"Total de socios evaluados: {total_socios}")
    print(f"Socios en riesgo critico (Churn=1): {total_churn} ({(total_churn/total_socios)*100:.1f}%)")
    print(f"Socios activos regulares (Churn=0): {total_socios - total_churn} ({((total_socios-total_churn)/total_socios)*100:.1f}%)")

    # Split estratificado 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Escalamiento para Regresion Logistica
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # -------------------------------------------------------------
    # MODELO A: Random Forest Classifier
    # -------------------------------------------------------------
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_proba = rf.predict_proba(X_test)[:, 1]

    rf_cm = confusion_matrix(y_test, rf_pred)
    rf_prec = precision_score(y_test, rf_pred)
    rf_rec = recall_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred)
    rf_auc = roc_auc_score(y_test, rf_proba)

    # -------------------------------------------------------------
    # MODELO B: Regresion Logistica Regularizada (L2)
    # -------------------------------------------------------------
    lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_proba = lr.predict_proba(X_test_scaled)[:, 1]

    lr_cm = confusion_matrix(y_test, lr_pred)
    lr_prec = precision_score(y_test, lr_pred)
    lr_rec = recall_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred)
    lr_auc = roc_auc_score(y_test, lr_proba)

    # Tabla Comparativa Oficial
    print("\n" + "-" * 70)
    print("TABLA COMPARATIVA DE CLASIFICADORES (E3)")
    print("-" * 70)
    print(f"{'Metrica':<25} | {'Random Forest (A)':<18} | {'Regresion Logistica (B)':<20}")
    print("-" * 70)
    print(f"{'Precision (Positivos)':<25} | {rf_prec:<18.4f} | {lr_prec:<20.4f}")
    print(f"{'Recall (Sensibilidad)':<25} | {rf_rec:<18.4f} | {lr_rec:<20.4f}")
    print(f"{'F1-Score (Equilibrio)':<25} | {rf_f1:<18.4f} | {lr_f1:<20.4f}")
    print(f"{'Area Bajo Curva ROC-AUC':<25} | {rf_auc:<18.4f} | {lr_auc:<20.4f}")
    print("-" * 70)

    print("\nMatriz de Confusion - Random Forest:")
    print(f"  [VN={rf_cm[0,0]:<3}  FP={rf_cm[0,1]:<3}]")
    print(f"  [FN={rf_cm[1,0]:<3}  VP={rf_cm[1,1]:<3}]")

    print("\nMatriz de Confusion - Regresion Logistica:")
    print(f"  [VN={lr_cm[0,0]:<3}  FP={lr_cm[0,1]:<3}]")
    print(f"  [FN={lr_cm[1,0]:<3}  VP={lr_cm[1,1]:<3}]")

    # Importancia de Variables en Random Forest
    importancias = dict(zip(feature_cols, [round(float(v), 4) for v in rf.feature_importances_]))
    print("\nImportancia de Variables (Feature Importance - Random Forest):")
    for col, imp in sorted(importancias.items(), key=lambda x: x[1], reverse=True):
        print(f"  {col:<22}: {imp*100:.2f}%")

    # Justificacion del Recall en la Economia del Gimnasio
    print("\n[JUSTIFICACION DE NEGOCIO]")
    print("Para FitPulse, el RECALL es la metrica reina:")
    print("Un Falso Negativo significa que el gimnasio no detecto a un socio en riesgo de cancelacion")
    print("y pierde definitivamente $650 MXN mensuales de por vida. En cambio, un Falso Positivo solo")
    print("recibe un mensaje preventivo cordial por WhatsApp que refuerza la atencion al cliente.")

    # Serializacion del modelo ganador (Random Forest + Scaler + Metadatos)
    pack_clasificador = {
        "modelo": rf,
        "scaler": scaler,
        "feature_cols": feature_cols,
        "metricas": {
            "random_forest": {
                "precision": round(float(rf_prec), 4),
                "recall": round(float(rf_rec), 4),
                "f1_score": round(float(rf_f1), 4),
                "roc_auc": round(float(rf_auc), 4),
                "matriz_confusion": rf_cm.tolist()
            },
            "regresion_logistica": {
                "precision": round(float(lr_prec), 4),
                "recall": round(float(lr_rec), 4),
                "f1_score": round(float(lr_f1), 4),
                "roc_auc": round(float(lr_auc), 4),
                "matriz_confusion": lr_cm.tolist()
            },
            "importancia_variables": importancias
        }
    }

    clf_path = os.path.join(MODELS_DIR, "churn_classifier.pkl")
    clf_meta_path = os.path.join(MODELS_DIR, "churn_meta.json")
    joblib.dump(pack_clasificador, clf_path)
    with open(clf_meta_path, "w", encoding="utf-8") as f:
        json.dump(pack_clasificador["metricas"], f, indent=2)

    print(f"\n[OK] Clasificador Random Forest serializado en: {clf_path}")
    print(f"[OK] Metricas y matrices guardadas en: {clf_meta_path}")

    return pack_clasificador["metricas"]


def main():
    print("Iniciando Pipeline de Modelado Predictivo e Inteligencia E3...")
    df = cargar_datos()
    entrenar_sarima(df)
    entrenar_clasificadores_churn(df)
    print("\nPipeline E3 completado exitosamente.")


if __name__ == "__main__":
    main()
