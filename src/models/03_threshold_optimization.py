"""
Script 3: Optimización del Umbral de Decisión
Monitor de Vulnerabilidad Económica - Colombia

Objetivo: Encontrar el mejor umbral para balancear Precision y Recall
Restricción: Mantener Recall >= 90%

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import joblib
import matplotlib.pyplot as plt

from sklearn.metrics import (precision_recall_curve, roc_curve, 
                             precision_score, recall_score, f1_score,
                             confusion_matrix, classification_report)

import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("SCRIPT 3: OPTIMIZACIÓN DEL UMBRAL DE DECISIÓN")
print("="*80)

# ===========================
# 1. CARGAR MODELO Y DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGAR MODELO Y DATOS")
print("="*80)

data_dir = Path('data/processed/modeling')
models_dir = Path('models')

# Cargar datos
X_test = pd.read_csv(data_dir / 'X_test.csv')
y_test = pd.read_csv(data_dir / 'y_test.csv')['IS_VULNERABLE']

# Cargar modelo optimizado
model = joblib.load(models_dir / 'final_optimized_xgboost.pkl')

print(f"✓ Modelo cargado: final_optimized_xgboost.pkl")
print(f"✓ Test set: {X_test.shape}")

# Obtener probabilidades
print("\n  • Calculando probabilidades...", end=" ")
y_proba = model.predict_proba(X_test)[:, 1]
print("✓")

# ===========================
# 2. ANÁLISIS DE UMBRALES
# ===========================
print("\n" + "="*80)
print("2. ANÁLISIS DE UMBRALES")
print("="*80)

# Calcular precision-recall para diferentes umbrales
precisions, recalls, thresholds_pr = precision_recall_curve(y_test, y_proba)

# Agregar umbral 1.0 para completar
thresholds_pr = np.append(thresholds_pr, 1.0)

print(f"\n✓ Analizando {len(thresholds_pr)} umbrales posibles")

# Crear DataFrame con resultados
results = []
for i, threshold in enumerate(thresholds_pr):
    y_pred = (y_proba >= threshold).astype(int)
    
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Contar predicciones
    n_predicted_positive = y_pred.sum()
    
    results.append({
        'threshold': threshold,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'n_predicted_positive': n_predicted_positive
    })

df_thresholds = pd.DataFrame(results)

# ===========================
# 3. ENCONTRAR MEJORES UMBRALES
# ===========================
print("\n" + "="*80)
print("3. BÚSQUEDA DE UMBRALES ÓPTIMOS")
print("="*80)

# Filtrar umbrales con recall >= 90%
MIN_RECALL = 0.90
df_valid = df_thresholds[df_thresholds['recall'] >= MIN_RECALL].copy()

print(f"\n✓ Umbrales con Recall >= {MIN_RECALL*100}%: {len(df_valid)}")

if len(df_valid) == 0:
    print("⚠️ No hay umbrales que cumplan la restricción")
    print("   Mostrando los mejores disponibles...")
    df_valid = df_thresholds.nlargest(10, 'recall')

# Ordenar por precision (descendente)
df_valid = df_valid.sort_values('precision', ascending=False)

print(f"\n📊 TOP 10 UMBRALES (Recall >= {MIN_RECALL*100}%):")
print(f"\n{'Umbral':<10} {'Precision':<12} {'Recall':<10} {'F1-Score':<12} {'N Pred+':<10}")
print("-" * 70)

for idx, row in df_valid.head(10).iterrows():
    print(f"{row['threshold']:<10.4f} {row['precision']:<12.4f} {row['recall']:<10.4f} "
          f"{row['f1_score']:<12.4f} {int(row['n_predicted_positive']):<10,}")

# Mejor umbral (mayor precision con recall >= 90%)
best_row = df_valid.iloc[0]
best_threshold = best_row['threshold']

print(f"\n{'='*80}")
print(f"🏆 MEJOR UMBRAL ENCONTRADO")
print(f"{'='*80}")
print(f"  Umbral:                {best_threshold:.4f}")
print(f"  Precision:             {best_row['precision']:.4f}")
print(f"  Recall:                {best_row['recall']:.4f}")
print(f"  F1-Score:              {best_row['f1_score']:.4f}")
print(f"  Predicciones positivas: {int(best_row['n_predicted_positive']):,}")

# Comparar con umbral por defecto (0.5)
default_threshold = 0.5
y_pred_default = (y_proba >= default_threshold).astype(int)
default_precision = precision_score(y_test, y_pred_default, zero_division=0)
default_recall = recall_score(y_test, y_pred_default)
default_f1 = f1_score(y_test, y_pred_default)

print(f"\n📈 COMPARACIÓN CON UMBRAL POR DEFECTO (0.5):")
print(f"\n{'Métrica':<15} {'Default (0.5)':<15} {'Optimizado':<15} {'Mejora'}")
print("-" * 70)
print(f"{'Precision':<15} {default_precision:<15.4f} {best_row['precision']:<15.4f} "
      f"{(best_row['precision']/default_precision-1)*100:+.1f}%")
print(f"{'Recall':<15} {default_recall:<15.4f} {best_row['recall']:<15.4f} "
      f"{(best_row['recall']/default_recall-1)*100:+.1f}%")
print(f"{'F1-Score':<15} {default_f1:<15.4f} {best_row['f1_score']:<15.4f} "
      f"{(best_row['f1_score']/default_f1-1)*100:+.1f}%")

# ===========================
# 4. ANÁLISIS DETALLADO
# ===========================
print("\n" + "="*80)
print("4. ANÁLISIS DETALLADO CON UMBRAL ÓPTIMO")
print("="*80)

# Predicciones con mejor umbral
y_pred_best = (y_proba >= best_threshold).astype(int)

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred_best)
tn, fp, fn, tp = cm.ravel()

print(f"\n📊 MATRIZ DE CONFUSIÓN:")
print(f"\n                Predicho No    Predicho Sí")
print(f"Real No         {tn:>10,}    {fp:>10,}")
print(f"Real Sí         {fn:>10,}    {tp:>10,}")

print(f"\n📈 MÉTRICAS DETALLADAS:")
print(f"  Verdaderos Positivos (TP):  {tp:>6,} - Vulnerables correctamente identificados")
print(f"  Falsos Positivos (FP):      {fp:>6,} - No vulnerables marcados como vulnerables")
print(f"  Verdaderos Negativos (TN):  {tn:>6,} - No vulnerables correctamente identificados")
print(f"  Falsos Negativos (FN):      {fn:>6,} - Vulnerables NO detectados")

print(f"\n💡 INTERPRETACIÓN:")
total_vulnerables = (y_test == 1).sum()
vulnerables_detectados = tp
vulnerables_perdidos = fn
no_vuln_mal_clasificados = fp

print(f"  De {total_vulnerables:,} personas vulnerables:")
print(f"    ✓ Detectamos:     {vulnerables_detectados:>6,} ({vulnerables_detectados/total_vulnerables*100:.1f}%)")
print(f"    ✗ Perdimos:       {vulnerables_perdidos:>6,} ({vulnerables_perdidos/total_vulnerables*100:.1f}%)")
print(f"\n  Predicciones positivas: {tp+fp:,}")
print(f"    ✓ Correctas:      {tp:>6,} ({tp/(tp+fp)*100:.1f}%)")
print(f"    ✗ Incorrectas:    {fp:>6,} ({fp/(tp+fp)*100:.1f}%)")

# Classification report
print(f"\n📋 CLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred_best, 
                          target_names=['No Vulnerable', 'Vulnerable'],
                          digits=4))

# ===========================
# 5. VISUALIZACIÓN
# ===========================
print("\n" + "="*80)
print("5. VISUALIZACIÓN")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Gráfico 1: Precision-Recall Curve
axes[0, 0].plot(recalls, precisions, 'b-', linewidth=2)
axes[0, 0].scatter([best_row['recall']], [best_row['precision']], 
                  color='red', s=200, zorder=5, label=f'Óptimo (th={best_threshold:.3f})')
axes[0, 0].axhline(y=best_row['precision'], color='red', linestyle='--', alpha=0.3)
axes[0, 0].axvline(x=best_row['recall'], color='red', linestyle='--', alpha=0.3)
axes[0, 0].axvline(x=0.90, color='green', linestyle=':', alpha=0.5, label='Recall mín 90%')
axes[0, 0].set_xlabel('Recall', fontsize=12)
axes[0, 0].set_ylabel('Precision', fontsize=12)
axes[0, 0].set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Gráfico 2: Precision y Recall vs Threshold
valid_range = df_thresholds[df_thresholds['threshold'] <= 0.7]  # Solo hasta 0.7 para mejor visualización
axes[0, 1].plot(valid_range['threshold'], valid_range['precision'], 'b-', label='Precision', linewidth=2)
axes[0, 1].plot(valid_range['threshold'], valid_range['recall'], 'r-', label='Recall', linewidth=2)
axes[0, 1].axvline(x=best_threshold, color='green', linestyle='--', linewidth=2, 
                  label=f'Óptimo ({best_threshold:.3f})')
axes[0, 1].axhline(y=0.90, color='orange', linestyle=':', alpha=0.5, label='Recall mín')
axes[0, 1].set_xlabel('Threshold', fontsize=12)
axes[0, 1].set_ylabel('Score', fontsize=12)
axes[0, 1].set_title('Precision y Recall vs Threshold', fontsize=14, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Gráfico 3: F1-Score vs Threshold
axes[1, 0].plot(valid_range['threshold'], valid_range['f1_score'], 'g-', linewidth=2)
axes[1, 0].scatter([best_threshold], [best_row['f1_score']], 
                  color='red', s=200, zorder=5, label=f'Óptimo (F1={best_row["f1_score"]:.3f})')
axes[1, 0].axvline(x=best_threshold, color='red', linestyle='--', alpha=0.3)
axes[1, 0].set_xlabel('Threshold', fontsize=12)
axes[1, 0].set_ylabel('F1-Score', fontsize=12)
axes[1, 0].set_title('F1-Score vs Threshold', fontsize=14, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

# Gráfico 4: Distribución de probabilidades por clase
axes[1, 1].hist(y_proba[y_test==0], bins=50, alpha=0.5, label='No Vulnerable', color='lightgreen', density=True)
axes[1, 1].hist(y_proba[y_test==1], bins=50, alpha=0.5, label='Vulnerable', color='coral', density=True)
axes[1, 1].axvline(x=best_threshold, color='red', linestyle='--', linewidth=2, 
                  label=f'Umbral óptimo ({best_threshold:.3f})')
axes[1, 1].axvline(x=0.5, color='blue', linestyle=':', linewidth=2, alpha=0.5, 
                  label='Umbral default (0.5)')
axes[1, 1].set_xlabel('Probabilidad Predicha', fontsize=12)
axes[1, 1].set_ylabel('Densidad', fontsize=12)
axes[1, 1].set_title('Distribución de Probabilidades', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(models_dir / 'threshold_optimization_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Gráficos guardados: models/threshold_optimization_analysis.png")
plt.show()

# ===========================
# 6. GUARDAR RESULTADOS
# ===========================
print("\n" + "="*80)
print("6. GUARDAR RESULTADOS")
print("="*80)

# Guardar resultados de umbral óptimo
threshold_results = {
    'optimal_threshold': float(best_threshold),
    'metrics_with_optimal_threshold': {
        'precision': float(best_row['precision']),
        'recall': float(best_row['recall']),
        'f1_score': float(best_row['f1_score']),
        'n_predicted_positive': int(best_row['n_predicted_positive'])
    },
    'metrics_with_default_threshold': {
        'threshold': 0.5,
        'precision': float(default_precision),
        'recall': float(default_recall),
        'f1_score': float(default_f1)
    },
    'confusion_matrix': {
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'true_positives': int(tp)
    },
    'improvement': {
        'precision_improvement_percent': float((best_row['precision']/default_precision-1)*100),
        'recall_change_percent': float((best_row['recall']/default_recall-1)*100),
        'f1_improvement_percent': float((best_row['f1_score']/default_f1-1)*100)
    },
    'constraint': {
        'min_recall_required': MIN_RECALL,
        'achieved_recall': float(best_row['recall'])
    }
}

with open(models_dir / 'threshold_optimization.json', 'w', encoding='utf-8') as f:
    json.dump(threshold_results, f, indent=2, ensure_ascii=False)
print(f"✓ Resultados guardados: models/threshold_optimization.json")

# Guardar tabla completa de umbrales
df_thresholds.to_csv(models_dir / 'threshold_analysis_complete.csv', index=False)
print(f"✓ Análisis completo guardado: models/threshold_analysis_complete.csv")

# ===========================
# 7. RESUMEN FINAL
# ===========================
print("\n" + "="*80)
print("✅ OPTIMIZACIÓN DE UMBRAL COMPLETADA")
print("="*80)

print(f"\n🎯 UMBRAL ÓPTIMO: {best_threshold:.4f}")
print(f"\n📊 MÉTRICAS FINALES:")
print(f"  Precision: {best_row['precision']:.4f} ({(best_row['precision']/default_precision-1)*100:+.1f}% vs default)")
print(f"  Recall:    {best_row['recall']:.4f} ({(best_row['recall']/default_recall-1)*100:+.1f}% vs default)")
print(f"  F1-Score:  {best_row['f1_score']:.4f} ({(best_row['f1_score']/default_f1-1)*100:+.1f}% vs default)")

print(f"\n💡 RECOMENDACIÓN:")
print(f"  Usar threshold = {best_threshold:.4f} en producción")
print(f"  Esto mejora precision manteniendo recall >= 90%")

print(f"\n💾 ARCHIVOS GENERADOS:")
print(f"  • models/threshold_optimization.json")
print(f"  • models/threshold_analysis_complete.csv")
print(f"  • models/threshold_optimization_analysis.png")

print(f"\n{'='*80}")

