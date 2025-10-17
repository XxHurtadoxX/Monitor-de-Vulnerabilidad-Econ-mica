"""
Script 1: Entrenamiento y Comparación de Modelos
Monitor de Vulnerabilidad Económica - Colombia

Objetivo: Encontrar el mejor modelo base usando validación cruzada
Modelos a probar: Logistic Regression, Random Forest, Gradient Boosting, XGBoost
Estrategia: class_weight/scale_pos_weight para manejar desbalanceo

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import time

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (roc_auc_score, f1_score, precision_score, 
                             recall_score, accuracy_score, classification_report)

import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("SCRIPT 1: ENTRENAMIENTO Y COMPARACIÓN DE MODELOS")
print("="*80)

# ===========================
# 1. CARGAR DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGA DE DATOS DE MODELADO")
print("="*80)

data_dir = Path('data/processed/modeling')

# Cargar datasets
X_train = pd.read_csv(data_dir / 'X_train.csv')
X_test = pd.read_csv(data_dir / 'X_test.csv')
y_train = pd.read_csv(data_dir / 'y_train.csv')['IS_VULNERABLE']
y_test = pd.read_csv(data_dir / 'y_test.csv')['IS_VULNERABLE']

# Cargar metadata
with open(data_dir / 'metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

print(f"\n✓ Datos cargados:")
print(f"  Train: {X_train.shape}")
print(f"  Test:  {X_test.shape}")
print(f"  Features: {X_train.shape[1]}")

print(f"\n✓ Balance del target (train):")
print(f"  No Vulnerable: {(y_train==0).sum():,} ({(y_train==0).sum()/len(y_train)*100:.2f}%)")
print(f"  Vulnerable:    {(y_train==1).sum():,} ({(y_train==1).sum()/len(y_train)*100:.2f}%)")

imbalance_ratio = metadata['target_info']['imbalance_ratio']
print(f"\n✓ Ratio de desbalanceo: {imbalance_ratio:.2f}:1")

# ===========================
# 2. CONFIGURAR MODELOS
# ===========================
print("\n" + "="*80)
print("2. CONFIGURACIÓN DE MODELOS")
print("="*80)

# Configuración de validación cruzada
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Modelos con manejo de desbalanceo
models = {
    'Logistic Regression': LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=42,
        solver='saga',
        n_jobs=-1
    ),
    
    'Random Forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=0
    ),
    
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=20,
        min_samples_leaf=10,
        subsample=0.8,
        random_state=42,
        verbose=0
    ),
    
    'XGBoost': XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=imbalance_ratio,  # Manejo de desbalanceo
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss',
        verbosity=0
    )
}

print(f"\n✓ Modelos configurados: {len(models)}")
for name in models.keys():
    print(f"  • {name}")

print(f"\n✓ Validación cruzada: {cv.n_splits}-fold estratificada")

# ===========================
# 3. ENTRENAR Y EVALUAR CON CV
# ===========================
print("\n" + "="*80)
print("3. ENTRENAMIENTO CON VALIDACIÓN CRUZADA")
print("="*80)

results_cv = {}
results_test = {}

for name, model in models.items():
    print(f"\n{'='*70}")
    print(f"🔄 Entrenando: {name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    # Validación cruzada en train
    print("  • Validación cruzada (ROC-AUC)...", end=" ")
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, 
                                scoring='roc_auc', n_jobs=-1)
    print(f"✓")
    
    # Entrenar en todo el train set
    print("  • Entrenando en train completo...", end=" ")
    model.fit(X_train, y_train)
    print(f"✓")
    
    # Predecir en test
    print("  • Prediciendo en test...", end=" ")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    print(f"✓")
    
    # Calcular métricas
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    
    training_time = time.time() - start_time
    
    # Guardar resultados
    results_cv[name] = {
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'cv_scores': cv_scores.tolist()
    }
    
    results_test[name] = {
        'roc_auc': roc_auc,
        'f1_score': f1,
        'precision': precision,
        'recall': recall,
        'accuracy': accuracy,
        'training_time': training_time
    }
    
    # Mostrar resultados
    print(f"\n  📊 Resultados:")
    print(f"     CV ROC-AUC:  {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    print(f"     Test ROC-AUC: {roc_auc:.4f}")
    print(f"     F1-Score:     {f1:.4f}")
    print(f"     Recall:       {recall:.4f}")
    print(f"     Precision:    {precision:.4f}")
    print(f"     Tiempo:       {training_time:.2f}s")

# ===========================
# 4. COMPARAR Y SELECCIONAR
# ===========================
print("\n" + "="*80)
print("4. COMPARACIÓN Y SELECCIÓN DEL MEJOR MODELO")
print("="*80)

# Crear tabla comparativa
comparison = pd.DataFrame(results_test).T
comparison['cv_roc_auc'] = [results_cv[m]['cv_mean'] for m in comparison.index]
comparison['cv_std'] = [results_cv[m]['cv_std'] for m in comparison.index]

# Reordenar columnas
comparison = comparison[['cv_roc_auc', 'cv_std', 'roc_auc', 'f1_score', 
                        'recall', 'precision', 'accuracy', 'training_time']]

# Ordenar por ROC-AUC test
comparison = comparison.sort_values('roc_auc', ascending=False)

print(f"\n📊 TABLA COMPARATIVA (ordenada por Test ROC-AUC):")
print(comparison.to_string())

# Identificar mejor modelo
best_model_name = comparison.index[0]
best_model = models[best_model_name]
best_metrics = results_test[best_model_name]

print(f"\n{'='*80}")
print(f"🏆 MEJOR MODELO: {best_model_name}")
print(f"{'='*80}")
print(f"  CV ROC-AUC:   {results_cv[best_model_name]['cv_mean']:.4f} (±{results_cv[best_model_name]['cv_std']:.4f})")
print(f"  Test ROC-AUC: {best_metrics['roc_auc']:.4f}")
print(f"  F1-Score:     {best_metrics['f1_score']:.4f}")
print(f"  Recall:       {best_metrics['recall']:.4f}")
print(f"  Precision:    {best_metrics['precision']:.4f}")
print(f"  Tiempo:       {best_metrics['training_time']:.2f}s")

# ===========================
# 5. GUARDAR RESULTADOS
# ===========================
print("\n" + "="*80)
print("5. GUARDAR RESULTADOS")
print("="*80)

models_dir = Path('models')
models_dir.mkdir(exist_ok=True)

# Guardar comparación
comparison.to_csv(models_dir / 'model_comparison.csv')
print(f"✓ Comparación guardada: models/model_comparison.csv")

# Guardar mejor modelo (entrenar de nuevo para guardar limpio)
print(f"✓ Entrenando mejor modelo para guardar...")
best_model.fit(X_train, y_train)

import joblib
model_filename = f'best_base_model_{best_model_name.lower().replace(" ", "_")}.pkl'
joblib.dump(best_model, models_dir / model_filename)
print(f"✓ Modelo guardado: models/{model_filename}")

# Guardar metadata de resultados
results_metadata = {
    'best_model': best_model_name,
    'best_model_file': model_filename,
    'cv_results': results_cv,
    'test_results': results_test,
    'comparison_table': comparison.to_dict(),
    'training_info': {
        'n_train': len(X_train),
        'n_test': len(X_test),
        'n_features': X_train.shape[1],
        'imbalance_ratio': imbalance_ratio
    }
}

with open(models_dir / 'training_results.json', 'w', encoding='utf-8') as f:
    json.dump(results_metadata, f, indent=2, ensure_ascii=False)
print(f"✓ Resultados guardados: models/training_results.json")

# ===========================
# 6. REPORTE DETALLADO DEL MEJOR MODELO
# ===========================
print("\n" + "="*80)
print("6. REPORTE DETALLADO DEL MEJOR MODELO")
print("="*80)

y_pred_best = best_model.predict(X_test)
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred_best, 
                          target_names=['No Vulnerable', 'Vulnerable'],
                          digits=4))

print(f"\n{'='*80}")
print("✅ SCRIPT 1 COMPLETADO")
print(f"{'='*80}")
print(f"\n🎯 PRÓXIMO PASO: Optimizar {best_model_name} con Búsqueda Bayesiana")
print(f"   Ejecutar: python src/models/02_bayesian_optimization.py")
print(f"{'='*80}")

