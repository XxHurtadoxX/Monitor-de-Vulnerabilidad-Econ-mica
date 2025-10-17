#!/usr/bin/env python3
"""
Notebook 3: EDA y Feature Engineering (VERSIÓN 2 - NUEVO TARGET)
Monitor de Vulnerabilidad Económica - Colombia

NUEVO TARGET: Vulnerable + Pobre
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
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Configuración
pd.set_option('display.max_columns', None)
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 6)

print("="*80)
print("NOTEBOOK 3: EDA Y FEATURE ENGINEERING (VERSIÓN 2 - NUEVO TARGET)")
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
# 2. DEFINIR NUEVO TARGET
# ===========================
print("\n" + "="*80)
print("2. DEFINICIÓN DEL NUEVO TARGET")
print("="*80)

LINEA_POBREZA_2024 = 515000
FACTOR_VULNERABILIDAD = 1.5

df['ingreso_persona'] = df['INGLABO']
df_valid = df[df['ingreso_persona'] > 0].copy()

print(f"\n[OK] Registros con ingreso válido: {len(df_valid):,} ({len(df_valid)/len(df)*100:.1f}%)")

# NUEVO TARGET: Vulnerable + Pobre
limite_vulnerabilidad = LINEA_POBREZA_2024 * FACTOR_VULNERABILIDAD

# Target actual (solo vulnerable) para comparación
df_valid['IS_VULNERABLE_ACTUAL'] = (
    (df_valid['ingreso_persona'] >= LINEA_POBREZA_2024) & 
    (df_valid['ingreso_persona'] <= limite_vulnerabilidad)
).astype(int)

# Target nuevo (vulnerable + pobre)
df_valid['IS_VULNERABLE'] = (
    df_valid['ingreso_persona'] <= limite_vulnerabilidad
).astype(int)

print(f"\nLímites:")
print(f"  Línea Pobreza:        ${LINEA_POBREZA_2024:>12,}")
print(f"  Límite Vulnerabilidad: ${limite_vulnerabilidad:>12,}")

# Comparación de targets
actual_counts = df_valid['IS_VULNERABLE_ACTUAL'].value_counts().sort_index()
actual_pcts = df_valid['IS_VULNERABLE_ACTUAL'].value_counts(normalize=True).sort_index() * 100

nuevo_counts = df_valid['IS_VULNERABLE'].value_counts().sort_index()
nuevo_pcts = df_valid['IS_VULNERABLE'].value_counts(normalize=True).sort_index() * 100

print(f"\nTARGET ACTUAL (Solo Vulnerable):")
print(f"  Clase 0 (No Vulnerable): {actual_counts[0]:>8,} ({actual_pcts[0]:>5.2f}%)")
print(f"  Clase 1 (Vulnerable):    {actual_counts[1]:>8,} ({actual_pcts[1]:>5.2f}%)")

print(f"\nTARGET NUEVO (Vulnerable + Pobre):")
print(f"  Clase 0 (No Vulnerable): {nuevo_counts[0]:>8,} ({nuevo_pcts[0]:>5.2f}%)")
print(f"  Clase 1 (Vulnerable+Pobre): {nuevo_counts[1]:>8,} ({nuevo_pcts[1]:>5.2f}%)")

print(f"\nCOMPARACIÓN:")
print(f"  Cambio en Clase 1: +{nuevo_counts[1] - actual_counts[1]:>8,} registros")
print(f"  Cambio en %:      +{nuevo_pcts[1] - actual_pcts[1]:>8.2f} puntos porcentuales")

# Ratio de desbalanceo
actual_ratio = actual_counts[0] / actual_counts[1]
nuevo_ratio = nuevo_counts[0] / nuevo_counts[1]

print(f"\nRatio de desbalanceo:")
print(f"  Target Actual:  {actual_ratio:.2f}:1")
print(f"  Target Nuevo:   {nuevo_ratio:.2f}:1")
print(f"  Mejora:         {actual_ratio/nuevo_ratio:.2f}x menos desbalanceado")

# ===========================
# 3. EDA - ANALIZAR VARIABLES
# ===========================
print("\n" + "="*80)
print("3. ANÁLISIS DE VARIABLES")
print("="*80)

exclude_cols = ['PERIODO', 'DIRECTORIO', 'SECUENCIA_P', 'ORDEN', 'HOGAR', 'ingreso_persona', 'INGLABO', 'IS_VULNERABLE', 'IS_VULNERABLE_ACTUAL']
feature_cols = [col for col in df_valid.columns if col not in exclude_cols]

print(f"\nFeatures candidatos: {len(feature_cols)}")

# Analizar cardinalidad
cardinalidad_info = {}
vars_constantes = []

print(f"\n{'Variable':<15} {'Únicos':<10} {'Tipo'}")
print("-" * 50)

for col in sorted(feature_cols):
    n_unique = df_valid[col].nunique()
    
    if n_unique == 1:
        tipo = "Constante"
        vars_constantes.append(col)
    elif n_unique == 2:
        tipo = "Binaria"
    elif n_unique <= 10:
        tipo = "Cat Baja"
    elif n_unique <= 30:
        tipo = "Cat Media"
    elif n_unique <= 100:
        tipo = "Cat Alta"
    else:
        tipo = "Muy Alta"
    
    cardinalidad_info[col] = {'n_unique': n_unique, 'tipo': tipo}
    print(f"{col:<15} {n_unique:<10} {tipo}")

# Solo eliminar constantes
vars_eliminar = vars_constantes

print(f"\n[WARN] Variables constantes (sin varianza) - ELIMINAR:")
for var in vars_eliminar:
    print(f"  - {var}")

features_base = [col for col in feature_cols if col not in vars_eliminar]
print(f"\n[OK] Features base: {len(features_base)}")

# ===========================
# 4. FEATURE ENGINEERING
# ===========================
print("\n" + "="*80)
print("4. FEATURE ENGINEERING")
print("="*80)

df_fe = df_valid.copy()
nuevas_features = []

# 1. Grupos de Edad
if 'P6040' in df_fe.columns:
    df_fe['edad_grupo'] = pd.cut(df_fe['P6040'], 
                                bins=[0, 18, 30, 45, 60, 100], 
                                labels=[1, 2, 3, 4, 5])
    df_fe['edad_grupo'] = df_fe['edad_grupo'].cat.add_categories([0]).fillna(0).astype(int)
    nuevas_features.append('edad_grupo')
    print("[OK] Feature edad_grupo creado")

# 2. Hacinamiento
if 'P5000' in df_fe.columns and 'P5010' in df_fe.columns:
    # Evitar división por cero
    df_fe['hacinamiento'] = np.where(
        df_fe['P5010'] > 0,
        df_fe['P5000'] / df_fe['P5010'],
        0
    )
    
    # Categorizar hacinamiento
    df_fe['hacinamiento_cat'] = pd.cut(df_fe['hacinamiento'], 
                                      bins=[0, 1, 2, 3, float('inf')], 
                                      labels=[1, 2, 3, 4])
    df_fe['hacinamiento_cat'] = df_fe['hacinamiento_cat'].cat.add_categories([0]).fillna(0).astype(int)
    nuevas_features.append('hacinamiento_cat')
    print("[OK] Feature hacinamiento_cat creado")

# 3. Score de Servicios Públicos
servicios_vars = ['P5080', 'P5090', 'P5100', 'P5110']
servicios_disponibles = [var for var in servicios_vars if var in df_fe.columns]

if servicios_disponibles:
    df_fe['servicios_score'] = 0
    for var in servicios_disponibles:
        # Asumir que valores > 0 indican acceso al servicio
        df_fe['servicios_score'] += (df_fe[var] > 0).astype(int)
    
    nuevas_features.append('servicios_score')
    print(f"[OK] Feature servicios_score creado ({len(servicios_disponibles)} servicios)")

# 4. Formalidad Laboral
if 'P6250' in df_fe.columns:
    df_fe['es_formal'] = (df_fe['P6250'] == 1).astype(int)
    nuevas_features.append('es_formal')
    print("[OK] Feature es_formal creado")

# 5. P5100 - Energía Eléctrica (HÍBRIDA)
if 'P5100' in df_fe.columns:
    # Binaria: Tiene energía eléctrica
    df_fe['tiene_energia'] = (df_fe['P5100'] > 0).astype(int)
    
    # Categórica de nivel de gasto en energía
    df_fe['nivel_gasto_energia'] = 0  # No aplica
    df_fe.loc[df_fe['P5100'] == -1, 'nivel_gasto_energia'] = 0  # No aplica
    df_fe.loc[(df_fe['P5100'] > 0) & (df_fe['P5100'] <= 50000), 'nivel_gasto_energia'] = 1  # Bajo
    df_fe.loc[(df_fe['P5100'] > 50000) & (df_fe['P5100'] <= 150000), 'nivel_gasto_energia'] = 2  # Medio
    df_fe.loc[df_fe['P5100'] > 150000, 'nivel_gasto_energia'] = 3  # Alto
    
    nuevas_features.extend(['tiene_energia', 'nivel_gasto_energia'])
    print("[OK] Features de P5100 (energía eléctrica) creados: tiene_energia, nivel_gasto_energia")

# 6. P5110 - Recolección Basuras (HÍBRIDA)
if 'P5110' in df_fe.columns:
    # Binaria: Tiene recolección de basuras
    df_fe['tiene_recoleccion'] = (df_fe['P5110'] > 0).astype(int)
    
    # Categórica de estado de recolección
    df_fe['estado_recoleccion'] = 0  # No aplica
    df_fe.loc[df_fe['P5110'] == -1, 'estado_recoleccion'] = 0  # No aplica
    df_fe.loc[df_fe['P5110'] == 1, 'estado_recoleccion'] = 1  # Regular
    df_fe.loc[df_fe['P5110'] == 2, 'estado_recoleccion'] = 2  # Irregular
    df_fe.loc[df_fe['P5110'] == 3, 'estado_recoleccion'] = 3  # No hay
    
    nuevas_features.extend(['tiene_recoleccion', 'estado_recoleccion'])
    print("[OK] Features de P5110 (recolección basuras) creados: tiene_recoleccion, estado_recoleccion")

# 7. P6120 - Atención Médica (HÍBRIDA)
if 'P6120' in df_fe.columns:
    # Binaria: Requirió atención médica
    df_fe['requirio_atencion_medica'] = (df_fe['P6120'] > 0).astype(int)
    
    # Categórica de nivel de gasto en salud
    df_fe['nivel_gasto_salud'] = 0  # No aplica
    df_fe.loc[df_fe['P6120'] == -1, 'nivel_gasto_salud'] = 0  # No requirió
    df_fe.loc[(df_fe['P6120'] > 0) & (df_fe['P6120'] <= 60000), 'nivel_gasto_salud'] = 1  # Bajo
    df_fe.loc[(df_fe['P6120'] > 60000) & (df_fe['P6120'] <= 150000), 'nivel_gasto_salud'] = 2  # Medio
    df_fe.loc[df_fe['P6120'] > 150000, 'nivel_gasto_salud'] = 3  # Alto
    
    # Variable continua normalizada (log del gasto, para los que tienen)
    df_fe['log_gasto_salud'] = 0.0
    mask_gasto = (df_fe['P6120'] > 0) & (df_fe['P6120'] < 98)
    df_fe.loc[mask_gasto, 'log_gasto_salud'] = np.log1p(df_fe.loc[mask_gasto, 'P6120'])
    
    nuevas_features.extend(['requirio_atencion_medica', 'nivel_gasto_salud', 'log_gasto_salud'])
    print("[OK] Features de P6120 (atención médica) creados: requirio_atencion_medica, nivel_gasto_salud, log_gasto_salud")

print(f"\n[OK] {len(nuevas_features)} nuevas features creadas")

# Ahora ELIMINAR las variables originales híbridas (ya extraímos la info)
vars_hibridas_originales = ['P5100', 'P5110', 'P6120']
features_finales = [f for f in features_base if f not in vars_hibridas_originales]

print(f"\n[OK] Variables originales híbridas reemplazadas por features engineered:")
for var in vars_hibridas_originales:
    print(f"  - {var} (reemplazada)")

# ===========================
# 5. PREPARAR DATASET FINAL
# ===========================
print("\n" + "="*80)
print("5. PREPARACIÓN DE DATASET FINAL")
print("="*80)

all_features = features_finales + [f for f in nuevas_features if f != 'hacinamiento']

X = df_fe[all_features].copy()
y = df_fe['IS_VULNERABLE'].copy()

print(f"\nDataset final:")
print(f"  Features: {X.shape[1]}")
print(f"  Muestras: {X.shape[0]:,}")
print(f"  Target distribución:")
print(f"    Clase 0: {sum(y == 0):>8,} ({sum(y == 0)/len(y)*100:.2f}%)")
print(f"    Clase 1: {sum(y == 1):>8,} ({sum(y == 1)/len(y)*100:.2f}%)")

# ===========================
# 6. DIVISIÓN TRAIN/TEST
# ===========================
print("\n" + "="*80)
print("6. DIVISIÓN TRAIN/TEST")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y
)

print(f"\nDivisión de datos:")
print(f"  Train: {X_train.shape[0]:,} muestras")
print(f"  Test:  {X_test.shape[0]:,} muestras")

print(f"\nDistribución del target en train:")
train_counts = y_train.value_counts().sort_index()
train_pcts = y_train.value_counts(normalize=True).sort_index() * 100
print(f"  Clase 0: {train_counts[0]:>8,} ({train_pcts[0]:>5.2f}%)")
print(f"  Clase 1: {train_counts[1]:>8,} ({train_pcts[1]:>5.2f}%)")

# ===========================
# 7. GUARDAR DATASET
# ===========================
print("\n" + "="*80)
print("7. GUARDAR DATASET")
print("="*80)

# Crear directorio de modeling
modeling_dir = Path('data/processed/modeling_v2')
modeling_dir.mkdir(exist_ok=True)

# Guardar datasets
X_train.to_csv(modeling_dir / 'X_train.csv', index=False)
X_test.to_csv(modeling_dir / 'X_test.csv', index=False)
y_train.to_csv(modeling_dir / 'y_train.csv', index=False, header=['IS_VULNERABLE'])
y_test.to_csv(modeling_dir / 'y_test.csv', index=False, header=['IS_VULNERABLE'])

# Guardar nombres de features
with open(modeling_dir / 'feature_names.txt', 'w') as f:
    for feature in all_features:
        f.write(f"{feature}\n")

# Guardar metadata
metadata = {
    'dataset_info': {
        'n_samples_total': len(df_valid),
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test),
        'n_features': len(all_features),
        'test_size': 0.2,
        'random_state': 42
    },
    'target_info': {
        'name': 'IS_VULNERABLE',
        'definition': 'Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)',
        'linea_pobreza': LINEA_POBREZA_2024,
        'factor_vulnerabilidad': FACTOR_VULNERABILIDAD,
        'limite_vulnerabilidad': limite_vulnerabilidad,
        'class_balance_train': {
            '0_no_vulnerable': int(train_counts[0]),
            '1_vulnerable_pobre': int(train_counts[1])
        },
        'imbalance_ratio': float(train_counts[0] / train_counts[1])
    },
    'features': {
        'all_features': all_features,
        'n_originales': len(features_finales),
        'n_engineered': len(nuevas_features),
        'features_originales_mantenidas': features_finales,
        'features_engineered': nuevas_features,
        'features_eliminadas_constantes': vars_eliminar,
        'features_transformadas_hibridas': vars_hibridas_originales
    },
    'transformaciones_especiales': {
        'P5100_energia': 'Transformada a: tiene_energia, nivel_gasto_energia',
        'P5110_recoleccion': 'Transformada a: tiene_recoleccion, estado_recoleccion',
        'P6120_salud': 'Transformada a: requirio_atencion_medica, nivel_gasto_salud, log_gasto_salud'
    },
    'comparacion_targets': {
        'target_actual_ratio': float(actual_ratio),
        'target_nuevo_ratio': float(nuevo_ratio),
        'mejora_balanceo': float(actual_ratio/nuevo_ratio),
        'registros_adicionales_clase_1': int(nuevo_counts[1] - actual_counts[1])
    }
}

with open(modeling_dir / 'metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Datasets guardados en: {modeling_dir}")
print(f"  - X_train.csv: Features de entrenamiento")
print(f"  - X_test.csv: Features de prueba")
print(f"  - y_train.csv: Target de entrenamiento")
print(f"  - y_test.csv: Target de prueba")
print(f"  - feature_names.txt: Lista de features")
print(f"  - metadata.json: Metadatos del dataset")

print(f"\n" + "="*80)
print("FEATURE ENGINEERING COMPLETADO - VERSIÓN 2")
print("="*80)
