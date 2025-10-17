#!/usr/bin/env python3
"""
Análisis del Nuevo Target: Vulnerable + Pobre
Monitor de Vulnerabilidad Económica - Colombia

Objetivo: Analizar el impacto de cambiar el target para incluir
tanto población vulnerable como pobre.

Nuevo Target:
- Clase 0: Ingreso > 1.5x línea de pobreza (> $772,500)
- Clase 1: Ingreso ≤ 1.5x línea de pobreza (≤ $772,500)

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Configuración
pd.set_option('display.max_columns', None)
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 6)

print("="*80)
print("ANÁLISIS DEL NUEVO TARGET: VULNERABLE + POBRE")
print("="*80)

# ===========================
# 1. CARGAR DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGA DE DATOS")
print("="*80)

df = pd.read_csv('data/processed/geih_2024_ipm_clean.csv')

print(f"\n[OK] Dataset cargado exitosamente")
print(f"  Registros: {df.shape[0]:,}")
print(f"  Columnas: {df.shape[1]}")

# ===========================
# 2. ANÁLISIS DE INGRESOS
# ===========================
print("\n" + "="*80)
print("2. ANÁLISIS DE INGRESOS")
print("="*80)

LINEA_POBREZA_2024 = 515000
FACTOR_VULNERABILIDAD = 1.5

df['ingreso_persona'] = df['INGLABO']
df_valid = df[df['ingreso_persona'] > 0].copy()

print(f"\n[OK] Registros con ingreso válido: {len(df_valid):,} ({len(df_valid)/len(df)*100:.1f}%)")

# Estadísticas de ingreso
print(f"\nEstadísticas de ingreso:")
print(f"  Media:    ${df_valid['ingreso_persona'].mean():>15,.0f}")
print(f"  Mediana:  ${df_valid['ingreso_persona'].median():>15,.0f}")
print(f"  Mínimo:   ${df_valid['ingreso_persona'].min():>15,.0f}")
print(f"  Máximo:   ${df_valid['ingreso_persona'].max():>15,.0f}")

# Límites
limite_vulnerabilidad = LINEA_POBREZA_2024 * FACTOR_VULNERABILIDAD

print(f"\nLímites:")
print(f"  Línea Pobreza:        ${LINEA_POBREZA_2024:>12,}")
print(f"  Límite Vulnerabilidad: ${limite_vulnerabilidad:>12,}")

# ===========================
# 3. COMPARAR TARGETS
# ===========================
print("\n" + "="*80)
print("3. COMPARACIÓN DE TARGETS")
print("="*80)

# Target actual (solo vulnerable)
df_valid['IS_VULNERABLE_ACTUAL'] = (
    (df_valid['ingreso_persona'] >= LINEA_POBREZA_2024) & 
    (df_valid['ingreso_persona'] <= limite_vulnerabilidad)
).astype(int)

# Target nuevo (vulnerable + pobre)
df_valid['IS_VULNERABLE_NUEVO'] = (
    df_valid['ingreso_persona'] <= limite_vulnerabilidad
).astype(int)

# Análisis de distribución
print(f"\nTARGET ACTUAL (Solo Vulnerable):")
actual_counts = df_valid['IS_VULNERABLE_ACTUAL'].value_counts().sort_index()
actual_pcts = df_valid['IS_VULNERABLE_ACTUAL'].value_counts(normalize=True).sort_index() * 100

print(f"  Clase 0 (No Vulnerable): {actual_counts[0]:>8,} ({actual_pcts[0]:>5.2f}%)")
print(f"  Clase 1 (Vulnerable):    {actual_counts[1]:>8,} ({actual_pcts[1]:>5.2f}%)")

print(f"\nTARGET NUEVO (Vulnerable + Pobre):")
nuevo_counts = df_valid['IS_VULNERABLE_NUEVO'].value_counts().sort_index()
nuevo_pcts = df_valid['IS_VULNERABLE_NUEVO'].value_counts(normalize=True).sort_index() * 100

print(f"  Clase 0 (No Vulnerable): {nuevo_counts[0]:>8,} ({nuevo_pcts[0]:>5.2f}%)")
print(f"  Clase 1 (Vulnerable+Pobre): {nuevo_counts[1]:>8,} ({nuevo_pcts[1]:>5.2f}%)")

# Comparación
print(f"\nCOMPARACIÓN:")
print(f"  Cambio en Clase 1: +{nuevo_counts[1] - actual_counts[1]:>8,} registros")
print(f"  Cambio en %:      +{nuevo_pcts[1] - actual_pcts[1]:>8.2f} puntos porcentuales")

# ===========================
# 4. ANÁLISIS DETALLADO POR RANGOS
# ===========================
print("\n" + "="*80)
print("4. ANÁLISIS POR RANGOS DE INGRESO")
print("="*80)

# Definir rangos
rangos = [
    (0, LINEA_POBREZA_2024, "Pobreza Extrema"),
    (LINEA_POBREZA_2024, limite_vulnerabilidad, "Vulnerable"),
    (limite_vulnerabilidad, limite_vulnerabilidad * 2, "Clase Media Baja"),
    (limite_vulnerabilidad * 2, limite_vulnerabilidad * 4, "Clase Media"),
    (limite_vulnerabilidad * 4, float('inf'), "Clase Alta")
]

print(f"\n{'Rango':<20} {'Registros':<10} {'%':<8} {'Acumulado %':<12}")
print("-" * 55)

acumulado = 0
for i, (min_ing, max_ing, nombre) in enumerate(rangos):
    if max_ing == float('inf'):
        mask = df_valid['ingreso_persona'] >= min_ing
    else:
        mask = (df_valid['ingreso_persona'] >= min_ing) & (df_valid['ingreso_persona'] < max_ing)
    
    count = mask.sum()
    pct = count / len(df_valid) * 100
    acumulado += pct
    
    print(f"{nombre:<20} {count:>8,} {pct:>6.2f}% {acumulado:>10.2f}%")

# ===========================
# 5. IMPACTO EN BALANCEO
# ===========================
print("\n" + "="*80)
print("5. IMPACTO EN BALANCEO DE CLASES")
print("="*80)

# Ratio de desbalanceo
actual_ratio = actual_counts[0] / actual_counts[1]
nuevo_ratio = nuevo_counts[0] / nuevo_counts[1]

print(f"\nRatio de desbalanceo:")
print(f"  Target Actual:  {actual_ratio:.2f}:1")
print(f"  Target Nuevo:   {nuevo_ratio:.2f}:1")
print(f"  Mejora:         {actual_ratio/nuevo_ratio:.2f}x menos desbalanceado")

# ===========================
# 6. ANÁLISIS GEOGRÁFICO
# ===========================
print("\n" + "="*80)
print("6. ANÁLISIS GEOGRÁFICO")
print("="*80)

# Top departamentos por vulnerabilidad
departamentos = df_valid.groupby('DPTO').agg({
    'IS_VULNERABLE_ACTUAL': ['count', 'sum'],
    'IS_VULNERABLE_NUEVO': 'sum'
}).round(2)

departamentos.columns = ['Total', 'Vulnerable_Actual', 'Vulnerable_Nuevo']
departamentos['Pct_Actual'] = (departamentos['Vulnerable_Actual'] / departamentos['Total'] * 100).round(2)
departamentos['Pct_Nuevo'] = (departamentos['Vulnerable_Nuevo'] / departamentos['Total'] * 100).round(2)

# Top 10 departamentos con mayor cambio
departamentos['Cambio_Pct'] = departamentos['Pct_Nuevo'] - departamentos['Pct_Actual']
top_departamentos = departamentos.nlargest(10, 'Cambio_Pct')

print(f"\nTop 10 departamentos con mayor cambio en % de vulnerabilidad:")
print(f"{'DPTO':<6} {'Total':<8} {'Actual %':<10} {'Nuevo %':<10} {'Cambio %':<10}")
print("-" * 50)

for dpto, row in top_departamentos.iterrows():
    print(f"{dpto:<6} {row['Total']:>7,} {row['Pct_Actual']:>8.2f}% {row['Pct_Nuevo']:>8.2f}% {row['Cambio_Pct']:>+8.2f}%")

# ===========================
# 7. GUARDAR ANÁLISIS
# ===========================
print("\n" + "="*80)
print("7. GUARDAR ANÁLISIS")
print("="*80)

# Crear directorio de resultados
results_dir = Path('data/processed/target_analysis')
results_dir.mkdir(exist_ok=True)

# Guardar dataset con ambos targets para comparación
df_valid[['ingreso_persona', 'IS_VULNERABLE_ACTUAL', 'IS_VULNERABLE_NUEVO', 'DPTO']].to_csv(
    results_dir / 'target_comparison.csv', index=False
)

# Guardar resumen del análisis
analysis_summary = {
    'fecha_analisis': pd.Timestamp.now().isoformat(),
    'linea_pobreza_2024': LINEA_POBREZA_2024,
    'factor_vulnerabilidad': FACTOR_VULNERABILIDAD,
    'limite_vulnerabilidad': limite_vulnerabilidad,
    'total_registros_validos': len(df_valid),
    'target_actual': {
        'clase_0_count': int(actual_counts[0]),
        'clase_1_count': int(actual_counts[1]),
        'clase_0_pct': float(actual_pcts[0]),
        'clase_1_pct': float(actual_pcts[1]),
        'imbalance_ratio': float(actual_ratio)
    },
    'target_nuevo': {
        'clase_0_count': int(nuevo_counts[0]),
        'clase_1_count': int(nuevo_counts[1]),
        'clase_0_pct': float(nuevo_pcts[0]),
        'clase_1_pct': float(nuevo_pcts[1]),
        'imbalance_ratio': float(nuevo_ratio)
    },
    'cambio': {
        'registros_clase_1_adicionales': int(nuevo_counts[1] - actual_counts[1]),
        'puntos_porcentuales_adicionales': float(nuevo_pcts[1] - actual_pcts[1]),
        'mejora_balanceo': float(actual_ratio/nuevo_ratio)
    }
}

with open(results_dir / 'target_analysis_summary.json', 'w') as f:
    json.dump(analysis_summary, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Análisis guardado en: {results_dir}")
print(f"  - target_comparison.csv: Dataset con ambos targets")
print(f"  - target_analysis_summary.json: Resumen del análisis")

print(f"\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)
