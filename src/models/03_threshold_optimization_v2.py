#!/usr/bin/env python3
"""
Optimización de Umbral (VERSIÓN 2 - NUEVO TARGET)
Monitor de Vulnerabilidad Económica - Colombia

NUEVO TARGET: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    precision_recall_curve, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("OPTIMIZACIÓN DE UMBRAL - VERSIÓN 2")
print("="*80)

# ===========================
# 1. CARGAR MODELO Y DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGA DE MODELO Y DATOS")
print("="*80)

# Cargar modelo optimizado
modeling_dir = Path('data/processed/modeling_v2')
results_dir = modeling_dir / 'results'

with open(results_dir / 'final_optimized_xgboost_v2.pkl', 'rb') as f:
    model = pickle.load(f)

# Cargar datos de test
X_test = pd.read_csv(modeling_dir / 'X_test.csv')
y_test = pd.read_csv(modeling_dir / 'y_test.csv').iloc[:, 0]

# Cargar metadata
with open(modeling_dir / 'metadata.json', 'r') as f:
    metadata = json.load(f)

print(f"\n[OK] Modelo y datos cargados:")
print(f"  Modelo: XGBoost optimizado")
print(f"  Test samples: {len(X_test):,}")
print(f"  Features: {X_test.shape[1]}")

# Distribución del target en test
test_counts = y_test.value_counts().sort_index()
test_pcts = y_test.value_counts(normalize=True).sort_index() * 100
print(f"\nDistribución del target en test:")
print(f"  Clase 0: {test_counts[0]:>8,} ({test_pcts[0]:>5.2f}%)")
print(f"  Clase 1: {test_counts[1]:>8,} ({test_pcts[1]:>5.2f}%)")

# ===========================
# 2. OBTENER PREDICCIONES
# ===========================
print("\n" + "="*80)
print("2. OBTENER PREDICCIONES")
print("="*80)

# Predicciones de probabilidad
y_pred_proba = model.predict_proba(X_test)[:, 1]

print(f"\n[OK] Predicciones obtenidas:")
print(f"  Probabilidades min: {y_pred_proba.min():.4f}")
print(f"  Probabilidades max: {y_pred_proba.max():.4f}")
print(f"  Probabilidades mean: {y_pred_proba.mean():.4f}")

# ===========================
# 3. ANÁLISIS DE CURVAS ROC Y PRECISION-RECALL
# ===========================
print("\n" + "="*80)
print("3. ANÁLISIS DE CURVAS ROC Y PRECISION-RECALL")
print("="*80)

# Curva ROC
fpr, tpr, roc_thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = np.trapz(tpr, fpr)

# Curva Precision-Recall
precision, recall, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)

print(f"\n[OK] Curvas calculadas:")
print(f"  ROC-AUC: {roc_auc:.4f}")
print(f"  Precision-Recall AUC: {np.trapz(precision, recall):.4f}")

# ===========================
# 4. OPTIMIZACIÓN DE UMBRAL
# ===========================
print("\n" + "="*80)
print("4. OPTIMIZACIÓN DE UMBRAL")
print("="*80)

# Umbrales a evaluar
thresholds = np.arange(0.1, 0.9, 0.01)

results = []
for threshold in thresholds:
    y_pred_thresh = (y_pred_proba >= threshold).astype(int)
    
    precision = precision_score(y_test, y_pred_thresh)
    recall = recall_score(y_test, y_pred_thresh)
    f1 = f1_score(y_test, y_pred_thresh)
    
    # Calcular número de predicciones positivas
    n_positive = y_pred_thresh.sum()
    
    results.append({
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'n_positive': n_positive
    })

# Convertir a DataFrame
results_df = pd.DataFrame(results)

print(f"\n[OK] Evaluación completada para {len(thresholds)} umbrales")

# ===========================
# 5. ENCONTRAR UMBRAL ÓPTIMO
# ===========================
print("\n" + "="*80)
print("5. ENCONTRAR UMBRAL ÓPTIMO")
print("="*80)

# Estrategia 1: Máximo F1-Score
best_f1_idx = results_df['f1'].idxmax()
best_f1_threshold = results_df.loc[best_f1_idx, 'threshold']
best_f1_metrics = results_df.loc[best_f1_idx]

print(f"\nEstrategia 1 - Máximo F1-Score:")
print(f"  Umbral: {best_f1_threshold:.4f}")
print(f"  Precision: {best_f1_metrics['precision']:.4f}")
print(f"  Recall: {best_f1_metrics['recall']:.4f}")
print(f"  F1-Score: {best_f1_metrics['f1']:.4f}")

# Estrategia 2: Recall mínimo del 90%
min_recall = 0.90
candidates = results_df[results_df['recall'] >= min_recall]

if len(candidates) > 0:
    # Entre los candidatos, elegir el de mayor precision
    best_precision_idx = candidates['precision'].idxmax()
    best_precision_threshold = candidates.loc[best_precision_idx, 'threshold']
    best_precision_metrics = candidates.loc[best_precision_idx]
    
    print(f"\nEstrategia 2 - Recall >= 90% y máxima Precision:")
    print(f"  Umbral: {best_precision_threshold:.4f}")
    print(f"  Precision: {best_precision_metrics['precision']:.4f}")
    print(f"  Recall: {best_precision_metrics['recall']:.4f}")
    print(f"  F1-Score: {best_precision_metrics['f1']:.4f}")
    
    optimal_threshold = best_precision_threshold
    optimal_metrics = best_precision_metrics
    strategy = "Recall >= 90% + Max Precision"
else:
    print(f"\n[WARN] No se encontró umbral con recall >= 90%")
    print(f"  Usando estrategia de máximo F1-Score")
    
    optimal_threshold = best_f1_threshold
    optimal_metrics = best_f1_metrics
    strategy = "Máximo F1-Score"

# ===========================
# 6. EVALUAR UMBRAL ÓPTIMO
# ===========================
print("\n" + "="*80)
print("6. EVALUACIÓN DEL UMBRAL ÓPTIMO")
print("="*80)

# Predicciones con umbral óptimo
y_pred_optimal = (y_pred_proba >= optimal_threshold).astype(int)

# Métricas finales
final_precision = precision_score(y_test, y_pred_optimal)
final_recall = recall_score(y_test, y_pred_optimal)
final_f1 = f1_score(y_test, y_pred_optimal)

# Matriz de confusión
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred_optimal)

print(f"\nUmbral óptimo seleccionado:")
print(f"  Estrategia: {strategy}")
print(f"  Umbral: {optimal_threshold:.4f}")

print(f"\nMétricas finales:")
print(f"  Precision: {final_precision:.4f}")
print(f"  Recall: {final_recall:.4f}")
print(f"  F1-Score: {final_f1:.4f}")

print(f"\nMatriz de Confusión:")
print(f"                Predicción")
print(f"Real      No Vulnerable  Vulnerable")
print(f"No Vulnerable    {cm[0,0]:>8}    {cm[0,1]:>8}")
print(f"Vulnerable       {cm[1,0]:>8}    {cm[1,1]:>8}")

# ===========================
# 7. ANÁLISIS DE SENSIBILIDAD
# ===========================
print("\n" + "="*80)
print("7. ANÁLISIS DE SENSIBILIDAD")
print("="*80)

# Análisis de umbrales cercanos
threshold_range = np.arange(
    max(0.1, optimal_threshold - 0.05), 
    min(0.9, optimal_threshold + 0.05), 
    0.01
)

sensitivity_analysis = []
for threshold in threshold_range:
    y_pred_temp = (y_pred_proba >= threshold).astype(int)
    
    precision = precision_score(y_test, y_pred_temp)
    recall = recall_score(y_test, y_pred_temp)
    f1 = f1_score(y_test, y_pred_temp)
    
    sensitivity_analysis.append({
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

sensitivity_df = pd.DataFrame(sensitivity_analysis)

print(f"\nAnálisis de sensibilidad (umbrales cercanos):")
print(f"{'Umbral':<8} {'Precision':<10} {'Recall':<8} {'F1':<8}")
print("-" * 40)

for _, row in sensitivity_df.iterrows():
    marker = " <--" if abs(row['threshold'] - optimal_threshold) < 0.001 else ""
    print(f"{row['threshold']:<8.3f} {row['precision']:<10.4f} {row['recall']:<8.4f} {row['f1']:<8.4f}{marker}")

# ===========================
# 8. GUARDAR RESULTADOS
# ===========================
print("\n" + "="*80)
print("8. GUARDAR RESULTADOS")
print("="*80)

# Guardar resultados de optimización de umbral
threshold_results = {
    'fecha_optimizacion': datetime.now().isoformat(),
    'target_info': metadata['target_info'],
    'estrategia_seleccionada': strategy,
    'umbral_optimo': float(optimal_threshold),
    'metricas_finales': {
        'precision': float(final_precision),
        'recall': float(final_recall),
        'f1_score': float(final_f1)
    },
    'matriz_confusion': cm.tolist(),
    'analisis_completo': results_df.to_dict('records'),
    'analisis_sensibilidad': sensitivity_df.to_dict('records')
}

with open(results_dir / 'threshold_optimization_v2.json', 'w') as f:
    json.dump(threshold_results, f, indent=2, ensure_ascii=False)

# Guardar DataFrame de resultados
results_df.to_csv(results_dir / 'threshold_analysis_v2.csv', index=False)

print(f"\n[OK] Resultados guardados en: {results_dir}")
print(f"  - threshold_optimization_v2.json: Resumen de optimización")
print(f"  - threshold_analysis_v2.csv: Análisis completo de umbrales")

print(f"\n" + "="*80)
print("OPTIMIZACIÓN DE UMBRAL COMPLETADA - VERSIÓN 2")
print("="*80)
