#!/usr/bin/env python3
"""
Optimización Bayesiana XGBoost (VERSIÓN 2 - NUEVO TARGET)
Monitor de Vulnerabilidad Económica - Colombia

NUEVO TARGET: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import optuna
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import xgboost as xgb
import pickle

print("="*80)
print("OPTIMIZACIÓN BAYESIANA XGBOOST - VERSIÓN 2")
print("="*80)

# ===========================
# 1. CARGAR DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGA DE DATOS")
print("="*80)

# Cargar datasets
modeling_dir = Path('data/processed/modeling_v2')

X_train = pd.read_csv(modeling_dir / 'X_train.csv')
X_test = pd.read_csv(modeling_dir / 'X_test.csv')
y_train = pd.read_csv(modeling_dir / 'y_train.csv').iloc[:, 0]
y_test = pd.read_csv(modeling_dir / 'y_test.csv').iloc[:, 0]

# Cargar metadata
with open(modeling_dir / 'metadata.json', 'r') as f:
    metadata = json.load(f)

print(f"\n[OK] Datasets cargados:")
print(f"  Train: {X_train.shape[0]:,} muestras, {X_train.shape[1]} features")
print(f"  Test:  {X_test.shape[0]:,} muestras, {X_test.shape[1]} features")

# Estadísticas del target
train_counts = y_train.value_counts().sort_index()
scale_pos_weight = train_counts[0] / train_counts[1]

print(f"\nTarget info:")
print(f"  Clase 0: {train_counts[0]:,} ({train_counts[0]/len(y_train)*100:.2f}%)")
print(f"  Clase 1: {train_counts[1]:,} ({train_counts[1]/len(y_train)*100:.2f}%)")
print(f"  Scale pos weight: {scale_pos_weight:.2f}")

# ===========================
# 2. DEFINIR FUNCIÓN OBJETIVO
# ===========================
print("\n" + "="*80)
print("2. CONFIGURACIÓN DE OPTIMIZACIÓN")
print("="*80)

def objective(trial):
    """Función objetivo para Optuna"""
    
    # Parámetros a optimizar
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'eval_metric': 'logloss'
    }
    
    # Crear modelo
    model = xgb.XGBClassifier(**params)
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc')
    
    return scores.mean()

# ===========================
# 3. EJECUTAR OPTIMIZACIÓN
# ===========================
print("\n" + "="*80)
print("3. EJECUTAR OPTIMIZACIÓN BAYESIANA")
print("="*80)

# Configurar estudio
study = optuna.create_study(
    direction='maximize',
    study_name='xgboost_optimization_v2',
    storage='sqlite:///optuna_study_v2.db'
)

print(f"\n[OK] Estudio de optimización creado")
print(f"  Objetivo: Maximizar ROC-AUC")
print(f"  Base de datos: optuna_study_v2.db")

# Ejecutar optimización
n_trials = 100
print(f"\n[INFO] Iniciando optimización con {n_trials} trials...")
print(f"[INFO] Esto puede tomar varios minutos...")

study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

print(f"\n[OK] Optimización completada!")
print(f"  Trials ejecutados: {len(study.trials)}")
print(f"  Mejor score: {study.best_value:.6f}")

# ===========================
# 4. ANÁLISIS DE RESULTADOS
# ===========================
print("\n" + "="*80)
print("4. ANÁLISIS DE RESULTADOS")
print("="*80)

# Mejores parámetros
best_params = study.best_params
print(f"\nMejores parámetros encontrados:")
for param, value in best_params.items():
    print(f"  {param}: {value}")

# ===========================
# 5. ENTRENAR MODELO FINAL
# ===========================
print("\n" + "="*80)
print("5. ENTRENAR MODELO FINAL OPTIMIZADO")
print("="*80)

# Crear modelo final con mejores parámetros
final_params = best_params.copy()
final_params['scale_pos_weight'] = scale_pos_weight
final_params['random_state'] = 42
final_params['eval_metric'] = 'logloss'

final_model = xgb.XGBClassifier(**final_params)

# Entrenar en todo el conjunto de entrenamiento
print(f"\n[INFO] Entrenando modelo final...")
final_model.fit(X_train, y_train)

# Evaluar en test
y_pred = final_model.predict(X_test)
y_pred_proba = final_model.predict_proba(X_test)[:, 1]

# Métricas
roc_auc = roc_auc_score(y_test, y_pred_proba)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\n[OK] Modelo final entrenado!")
print(f"  Test ROC-AUC: {roc_auc:.4f}")
print(f"  Test Precision: {precision:.4f}")
print(f"  Test Recall: {recall:.4f}")
print(f"  Test F1: {f1:.4f}")

# ===========================
# 6. ANÁLISIS DE IMPORTANCIA DE FEATURES
# ===========================
print("\n" + "="*80)
print("6. IMPORTANCIA DE FEATURES")
print("="*80)

feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'importance': final_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\nTop 15 Features más importantes:")
for i, (_, row) in enumerate(feature_importance.head(15).iterrows(), 1):
    print(f"  {i:2d}. {row['feature']:<30} {row['importance']:.4f}")

# ===========================
# 7. GUARDAR RESULTADOS
# ===========================
print("\n" + "="*80)
print("7. GUARDAR RESULTADOS")
print("="*80)

# Crear directorio de resultados
results_dir = Path('data/processed/modeling_v2/results')
results_dir.mkdir(exist_ok=True)

# Guardar modelo optimizado
with open(results_dir / 'final_optimized_xgboost_v2.pkl', 'wb') as f:
    pickle.dump(final_model, f)

# Guardar importancia de features
feature_importance.to_csv(
    results_dir / 'final_optimized_xgboost_v2_feature_importance.csv',
    index=False
)

# Guardar resultados de optimización
optimization_results = {
    'fecha_optimizacion': datetime.now().isoformat(),
    'target_info': metadata['target_info'],
    'dataset_info': metadata['dataset_info'],
    'optimizacion': {
        'n_trials': len(study.trials),
        'best_value': study.best_value,
        'best_params': best_params,
        'final_params': final_params
    },
    'metricas_finales': {
        'test_roc_auc': float(roc_auc),
        'test_precision': float(precision),
        'test_recall': float(recall),
        'test_f1': float(f1)
    },
    'top_features': feature_importance.head(20).to_dict('records')
}

with open(results_dir / 'optimization_results_v2.json', 'w') as f:
    json.dump(optimization_results, f, indent=2, ensure_ascii=False)

# Guardar estudio de Optuna
study_df = study.trials_dataframe()
study_df.to_csv(results_dir / 'optuna_study_results_v2.csv', index=False)

print(f"\n[OK] Resultados guardados en: {results_dir}")
print(f"  - final_optimized_xgboost_v2.pkl: Modelo optimizado")
print(f"  - final_optimized_xgboost_v2_feature_importance.csv: Importancia features")
print(f"  - optimization_results_v2.json: Resumen de optimización")
print(f"  - optuna_study_results_v2.csv: Resultados de todos los trials")

print(f"\n" + "="*80)
print("OPTIMIZACIÓN COMPLETADA - VERSIÓN 2")
print("="*80)
