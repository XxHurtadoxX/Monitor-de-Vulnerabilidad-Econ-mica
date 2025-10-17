"""
Script 2: Optimización Bayesiana de Hiperparámetros con Optuna
Monitor de Vulnerabilidad Económica - Colombia

Objetivo: Optimizar XGBoost usando Bayesian Optimization (máximo 7 minutos)
Estrategia: Optuna con TPESampler y early stopping

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import time
import joblib

from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
import optuna
from optuna.samplers import TPESampler

import warnings
warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

print("="*80)
print("SCRIPT 2: OPTIMIZACIÓN BAYESIANA CON OPTUNA")
print("="*80)

# ===========================
# 1. CARGAR DATOS Y METADATA
# ===========================
print("\n" + "="*80)
print("1. CARGA DE DATOS")
print("="*80)

data_dir = Path('data/processed/modeling')
models_dir = Path('models')

# Cargar datos
X_train = pd.read_csv(data_dir / 'X_train.csv')
X_test = pd.read_csv(data_dir / 'X_test.csv')
y_train = pd.read_csv(data_dir / 'y_train.csv')['IS_VULNERABLE']
y_test = pd.read_csv(data_dir / 'y_test.csv')['IS_VULNERABLE']

# Cargar metadata
with open(data_dir / 'metadata.json', 'r') as f:
    metadata = json.load(f)

imbalance_ratio = metadata['target_info']['imbalance_ratio']

print(f"✓ Datos cargados: Train {X_train.shape}, Test {X_test.shape}")
print(f"✓ Desbalanceo: {imbalance_ratio:.2f}:1")

# ===========================
# 2. CONFIGURAR OPTUNA
# ===========================
print("\n" + "="*80)
print("2. CONFIGURACIÓN DE OPTIMIZACIÓN")
print("="*80)

# Configuración de CV
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)  # 3 folds para ser más rápido

# Límite de tiempo: 7 minutos = 420 segundos
MAX_TIME_SECONDS = 420
print(f"✓ Tiempo máximo: {MAX_TIME_SECONDS//60} minutos")
print(f"✓ Validación cruzada: {cv.n_splits}-fold estratificada")

# Función objetivo para Optuna
def objective(trial):
    """
    Función objetivo para Optuna
    Retorna: ROC-AUC promedio de validación cruzada
    """
    # Espacio de búsqueda de hiperparámetros
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 5),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 5),
        
        # Parámetros fijos
        'scale_pos_weight': imbalance_ratio,
        'random_state': 42,
        'n_jobs': -1,
        'eval_metric': 'logloss',
        'verbosity': 0
    }
    
    # Crear modelo
    model = XGBClassifier(**params)
    
    # Evaluación con CV
    scores = cross_val_score(model, X_train, y_train, cv=cv, 
                            scoring='roc_auc', n_jobs=-1)
    
    return scores.mean()

# ===========================
# 3. EJECUTAR OPTIMIZACIÓN
# ===========================
print("\n" + "="*80)
print("3. EJECUCIÓN DE BÚSQUEDA BAYESIANA")
print("="*80)

print(f"\n🔍 Iniciando optimización (máx {MAX_TIME_SECONDS//60} min)...")
print(f"   Cada trial toma ~10-20 segundos")
print(f"   Estimado: 20-40 trials en 7 minutos\n")

start_time = time.time()

# Crear estudio de Optuna
study = optuna.create_study(
    direction='maximize',
    sampler=TPESampler(seed=42)
)

# Optimizar con timeout
study.optimize(
    objective,
    n_trials=100,  # Máximo de trials (pero se detendrá por timeout)
    timeout=MAX_TIME_SECONDS,
    show_progress_bar=True
)

optimization_time = time.time() - start_time

print(f"\n✓ Optimización completada en {optimization_time:.2f}s ({optimization_time/60:.2f} min)")
print(f"✓ Trials ejecutados: {len(study.trials)}")

# ===========================
# 4. RESULTADOS DE OPTIMIZACIÓN
# ===========================
print("\n" + "="*80)
print("4. RESULTADOS DE OPTIMIZACIÓN")
print("="*80)

best_params = study.best_params
best_value = study.best_value

print(f"\n🏆 MEJORES HIPERPARÁMETROS:")
for param, value in best_params.items():
    print(f"  {param:<20}: {value}")

print(f"\n📊 MEJOR ROC-AUC (CV): {best_value:.4f}")

# Comparar con modelo base
with open(models_dir / 'training_results.json', 'r') as f:
    base_results = json.load(f)

base_cv_auc = base_results['cv_results']['XGBoost']['cv_mean']
improvement = (best_value - base_cv_auc) / base_cv_auc * 100

print(f"\n📈 MEJORA vs Modelo Base:")
print(f"  Base CV ROC-AUC:      {base_cv_auc:.4f}")
print(f"  Optimizado CV ROC-AUC: {best_value:.4f}")
print(f"  Mejora:               {improvement:+.2f}%")

# ===========================
# 5. ENTRENAR MODELO FINAL
# ===========================
print("\n" + "="*80)
print("5. ENTRENAR MODELO FINAL OPTIMIZADO")
print("="*80)

# Agregar parámetros fijos
final_params = best_params.copy()
final_params.update({
    'scale_pos_weight': imbalance_ratio,
    'random_state': 42,
    'n_jobs': -1,
    'eval_metric': 'logloss',
    'verbosity': 0
})

# Entrenar modelo final
print("  • Entrenando modelo optimizado...", end=" ")
final_model = XGBClassifier(**final_params)
final_model.fit(X_train, y_train)
print("✓")

# Evaluar en test
print("  • Evaluando en test set...", end=" ")
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, classification_report

y_pred = final_model.predict(X_test)
y_pred_proba = final_model.predict_proba(X_test)[:, 1]

test_roc_auc = roc_auc_score(y_test, y_pred_proba)
test_f1 = f1_score(y_test, y_pred)
test_recall = recall_score(y_test, y_pred)
test_precision = precision_score(y_test, y_pred, zero_division=0)
print("✓")

print(f"\n📊 MÉTRICAS EN TEST:")
print(f"  ROC-AUC:    {test_roc_auc:.4f}")
print(f"  F1-Score:   {test_f1:.4f}")
print(f"  Recall:     {test_recall:.4f}")
print(f"  Precision:  {test_precision:.4f}")

# Comparar test con base
base_test_auc = base_results['test_results']['XGBoost']['roc_auc']
test_improvement = (test_roc_auc - base_test_auc) / base_test_auc * 100

print(f"\n📈 MEJORA EN TEST vs Modelo Base:")
print(f"  Base Test ROC-AUC:      {base_test_auc:.4f}")
print(f"  Optimizado Test ROC-AUC: {test_roc_auc:.4f}")
print(f"  Mejora:                 {test_improvement:+.2f}%")

# ===========================
# 6. GUARDAR MODELO OPTIMIZADO
# ===========================
print("\n" + "="*80)
print("6. GUARDAR MODELO OPTIMIZADO")
print("="*80)

# Guardar modelo
model_filename = 'final_optimized_xgboost.pkl'
joblib.dump(final_model, models_dir / model_filename)
print(f"✓ Modelo guardado: models/{model_filename}")

# Guardar hiperparámetros y resultados
optimization_results = {
    'optimization_info': {
        'n_trials': len(study.trials),
        'optimization_time_seconds': optimization_time,
        'optimization_time_minutes': optimization_time / 60,
        'max_time_allowed': MAX_TIME_SECONDS
    },
    'best_hyperparameters': final_params,
    'cv_results': {
        'best_cv_roc_auc': best_value,
        'base_cv_roc_auc': base_cv_auc,
        'improvement_percent': improvement
    },
    'test_results': {
        'test_roc_auc': test_roc_auc,
        'test_f1_score': test_f1,
        'test_recall': test_recall,
        'test_precision': test_precision,
        'base_test_roc_auc': base_test_auc,
        'test_improvement_percent': test_improvement
    },
    'model_file': model_filename
}

with open(models_dir / 'optimization_results.json', 'w', encoding='utf-8') as f:
    json.dump(optimization_results, f, indent=2, ensure_ascii=False)
print(f"✓ Resultados guardados: models/optimization_results.json")

# Guardar historial de trials
trials_df = study.trials_dataframe()
trials_df.to_csv(models_dir / 'optuna_trials_history.csv', index=False)
print(f"✓ Historial de trials: models/optuna_trials_history.csv")

# ===========================
# 7. REPORTE FINAL
# ===========================
print("\n" + "="*80)
print("7. REPORTE FINAL")
print("="*80)

print(f"\nClassification Report (Test Set):")
print(classification_report(y_test, y_pred, 
                          target_names=['No Vulnerable', 'Vulnerable'],
                          digits=4))

print(f"\n{'='*80}")
print("✅ OPTIMIZACIÓN BAYESIANA COMPLETADA")
print(f"{'='*80}")
print(f"\n🎯 MODELO FINAL:")
print(f"   Archivo: models/{model_filename}")
print(f"   ROC-AUC: {test_roc_auc:.4f}")
print(f"   Recall:  {test_recall:.4f} (captura {test_recall*100:.1f}% de vulnerables)")
print(f"   F1:      {test_f1:.4f}")
print(f"\n💾 ARCHIVOS GENERADOS:")
print(f"   • models/{model_filename}")
print(f"   • models/optimization_results.json")
print(f"   • models/optuna_trials_history.csv")
print(f"\n🚀 LISTO PARA PRODUCCIÓN")
print(f"{'='*80}")

