#!/usr/bin/env python3
"""
Entrenamiento y Comparación de Modelos (VERSIÓN 2 - NUEVO TARGET)
Monitor de Vulnerabilidad Económica - Colombia

NUEVO TARGET: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)
- Clase 0: Ingreso > 1.5x línea de pobreza (> $772,500)
- Clase 1: Ingreso ≤ 1.5x línea de pobreza (≤ $772,500)

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Modelos
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    precision_score, recall_score, f1_score, roc_curve
)
import xgboost as xgb

print("="*80)
print("ENTRENAMIENTO Y COMPARACIÓN DE MODELOS - VERSIÓN 2")
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

print(f"\nDistribución del target:")
train_counts = y_train.value_counts().sort_index()
train_pcts = y_train.value_counts(normalize=True).sort_index() * 100
print(f"  Train - Clase 0: {train_counts[0]:>8,} ({train_pcts[0]:>5.2f}%)")
print(f"  Train - Clase 1: {train_counts[1]:>8,} ({train_pcts[1]:>5.2f}%)")

test_counts = y_test.value_counts().sort_index()
test_pcts = y_test.value_counts(normalize=True).sort_index() * 100
print(f"  Test  - Clase 0: {test_counts[0]:>8,} ({test_pcts[0]:>5.2f}%)")
print(f"  Test  - Clase 1: {test_counts[1]:>8,} ({test_pcts[1]:>5.2f}%)")

print(f"\nRatio de desbalanceo: {train_counts[0]/train_counts[1]:.2f}:1")

# ===========================
# 2. DEFINIR MODELOS
# ===========================
print("\n" + "="*80)
print("2. DEFINICIÓN DE MODELOS")
print("="*80)

# Configurar cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Modelos con configuraciones optimizadas para datos desbalanceados
models = {
    'Logistic_Regression': LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    ),
    
    'Random_Forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    ),
    
    'Gradient_Boosting': GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    ),
    
    'XGBoost': xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        scale_pos_weight=train_counts[0]/train_counts[1],  # Balancear clases
        eval_metric='logloss'
    )
}

print(f"\n[OK] {len(models)} modelos configurados:")
for name in models.keys():
    print(f"  - {name}")

# ===========================
# 3. ENTRENAMIENTO Y EVALUACIÓN
# ===========================
print("\n" + "="*80)
print("3. ENTRENAMIENTO Y EVALUACIÓN")
print("="*80)

results = {}
trained_models = {}

for name, model in models.items():
    print(f"\n--- Entrenando {name} ---")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc')
    
    # Entrenar en todo el conjunto de entrenamiento
    model.fit(X_train, y_train)
    
    # Predicciones
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Métricas
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Guardar resultados
    results[name] = {
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'test_roc_auc': roc_auc,
        'test_precision': precision,
        'test_recall': recall,
        'test_f1': f1,
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }
    
    trained_models[name] = model
    
    print(f"  CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    print(f"  Test ROC-AUC: {roc_auc:.4f}")
    print(f"  Test Precision: {precision:.4f}")
    print(f"  Test Recall: {recall:.4f}")
    print(f"  Test F1: {f1:.4f}")

# ===========================
# 4. COMPARACIÓN DE RESULTADOS
# ===========================
print("\n" + "="*80)
print("4. COMPARACIÓN DE RESULTADOS")
print("="*80)

# Crear DataFrame de resultados
results_df = pd.DataFrame({
    name: {
        'CV_ROC_AUC_Mean': results[name]['cv_mean'],
        'CV_ROC_AUC_Std': results[name]['cv_std'],
        'Test_ROC_AUC': results[name]['test_roc_auc'],
        'Test_Precision': results[name]['test_precision'],
        'Test_Recall': results[name]['test_recall'],
        'Test_F1': results[name]['test_f1']
    }
    for name in models.keys()
}).T

# Ordenar por ROC-AUC
results_df = results_df.sort_values('Test_ROC_AUC', ascending=False)

print(f"\nResultados ordenados por Test ROC-AUC:")
print(results_df.round(4))

# Mejor modelo
best_model_name = results_df.index[0]
best_model = trained_models[best_model_name]

print(f"\n[OK] Mejor modelo: {best_model_name}")
print(f"  Test ROC-AUC: {results_df.loc[best_model_name, 'Test_ROC_AUC']:.4f}")
print(f"  Test Precision: {results_df.loc[best_model_name, 'Test_Precision']:.4f}")
print(f"  Test Recall: {results_df.loc[best_model_name, 'Test_Recall']:.4f}")
print(f"  Test F1: {results_df.loc[best_model_name, 'Test_F1']:.4f}")

# ===========================
# 5. ANÁLISIS DETALLADO DEL MEJOR MODELO
# ===========================
print("\n" + "="*80)
print("5. ANÁLISIS DETALLADO DEL MEJOR MODELO")
print("="*80)

# Predicciones del mejor modelo
y_pred_best = best_model.predict(X_test)
y_pred_proba_best = best_model.predict_proba(X_test)[:, 1]

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred_best)
print(f"\nMatriz de Confusión ({best_model_name}):")
print(f"                Predicción")
print(f"Real      No Vulnerable  Vulnerable")
print(f"No Vulnerable    {cm[0,0]:>8}    {cm[0,1]:>8}")
print(f"Vulnerable       {cm[1,0]:>8}    {cm[1,1]:>8}")

# Reporte de clasificación
print(f"\nReporte de Clasificación ({best_model_name}):")
report = classification_report(y_test, y_pred_best)
print(report)

# ===========================
# 6. IMPORTANCIA DE FEATURES (si aplica)
# ===========================
print("\n" + "="*80)
print("6. IMPORTANCIA DE FEATURES")
print("="*80)

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 Features más importantes ({best_model_name}):")
    for i, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
        print(f"  {i:2d}. {row['feature']:<25} {row['importance']:.4f}")
    
    # Guardar importancia de features
    feature_importance.to_csv(
        modeling_dir / f'{best_model_name.lower().replace("_", "_")}_feature_importance.csv',
        index=False
    )

# ===========================
# 7. GUARDAR RESULTADOS
# ===========================
print("\n" + "="*80)
print("7. GUARDAR RESULTADOS")
print("="*80)

# Crear directorio de resultados
results_dir = Path('data/processed/modeling_v2/results')
results_dir.mkdir(exist_ok=True)

# Guardar modelo entrenado
import pickle
with open(results_dir / f'{best_model_name.lower().replace("_", "_")}_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

# Guardar resultados
results_summary = {
    'fecha_entrenamiento': datetime.now().isoformat(),
    'target_info': metadata['target_info'],
    'dataset_info': metadata['dataset_info'],
    'mejor_modelo': {
        'nombre': best_model_name,
        'metricas': results[best_model_name]
    },
    'todos_los_resultados': results,
    'comparacion_modelos': results_df.to_dict()
}

with open(results_dir / 'training_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2, ensure_ascii=False)

# Guardar DataFrame de resultados
results_df.to_csv(results_dir / 'model_comparison.csv')

print(f"\n[OK] Resultados guardados en: {results_dir}")
print(f"  - {best_model_name.lower().replace('_', '_')}_model.pkl: Modelo entrenado")
print(f"  - training_results.json: Resumen de resultados")
print(f"  - model_comparison.csv: Comparación de modelos")

if hasattr(best_model, 'feature_importances_'):
    print(f"  - {best_model_name.lower().replace('_', '_')}_feature_importance.csv: Importancia de features")

print(f"\n" + "="*80)
print("ENTRENAMIENTO COMPLETADO - VERSIÓN 2")
print("="*80)
