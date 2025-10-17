"""
Notebook 3: EDA y Feature Engineering (CORREGIDO)
Monitor de Vulnerabilidad Económica - Colombia

Corrección: NO eliminar P5100, P5110, P6120
Aplicar Feature Engineering inteligente a variables híbridas

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
print("NOTEBOOK 3: EDA Y FEATURE ENGINEERING (CORREGIDO)")
print("="*80)

# ===========================
# 1. CARGAR DATOS
# ===========================
print("\n" + "="*80)
print("1. CARGA DE DATOS")
print("="*80)

df = pd.read_csv('data/processed/geih_2024_ipm_clean.csv')

print(f"\n✓ Dataset cargado exitosamente")
print(f"  Registros: {df.shape[0]:,}")
print(f"  Columnas: {df.shape[1]}")

# ===========================
# 2. DEFINIR TARGET
# ===========================
print("\n" + "="*80)
print("2. DEFINICIÓN DEL TARGET")
print("="*80)

LINEA_POBREZA_2024 = 515000
FACTOR_VULNERABILIDAD = 1.5

df['ingreso_persona'] = df['INGLABO']
df_valid = df[df['ingreso_persona'] > 0].copy()

print(f"\n✓ Registros con ingreso válido: {len(df_valid):,} ({len(df_valid)/len(df)*100:.1f}%)")

# Definir target
limite_inferior = LINEA_POBREZA_2024
limite_superior = LINEA_POBREZA_2024 * FACTOR_VULNERABILIDAD

df_valid['IS_VULNERABLE'] = (
    (df_valid['ingreso_persona'] >= limite_inferior) & 
    (df_valid['ingreso_persona'] <= limite_superior)
).astype(int)

target_counts = df_valid['IS_VULNERABLE'].value_counts().sort_index()
target_pcts = df_valid['IS_VULNERABLE'].value_counts(normalize=True).sort_index() * 100

print(f"\nDistribución del target:")
print(f"  Clase 0 (No Vulnerable): {target_counts[0]:>8,} ({target_pcts[0]:>5.2f}%)")
print(f"  Clase 1 (Vulnerable):    {target_counts[1]:>8,} ({target_pcts[1]:>5.2f}%)")

imbalance_ratio = target_counts[0] / target_counts[1]
print(f"\n  Ratio de desbalanceo: {imbalance_ratio:.2f}:1")

# ===========================
# 3. EDA - ANALIZAR VARIABLES
# ===========================
print("\n" + "="*80)
print("3. ANÁLISIS DE VARIABLES")
print("="*80)

exclude_cols = ['PERIODO', 'DIRECTORIO', 'SECUENCIA_P', 'ORDEN', 'HOGAR', 'ingreso_persona', 'INGLABO', 'IS_VULNERABLE']
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

print(f"\n⚠️ Variables constantes (sin varianza) - ELIMINAR:")
for var in vars_eliminar:
    print(f"  ✗ {var}")

features_base = [col for col in feature_cols if col not in vars_eliminar]
print(f"\n✓ Features base: {len(features_base)}")

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
                                   bins=[0, 25, 40, 60, 200],
                                   labels=[1, 2, 3, 4]).astype(int)
    nuevas_features.append('edad_grupo')
    print("✓ Feature 'edad_grupo' creado")

# 2. Índice de Hacinamiento
if 'P5020' in df_fe.columns and 'P5030' in df_fe.columns:
    df_fe['hacinamiento'] = 0
    mask = df_fe['P5020'] > 0
    df_fe.loc[mask, 'hacinamiento'] = df_fe.loc[mask, 'P5030'] / df_fe.loc[mask, 'P5020']
    df_fe['hacinamiento_cat'] = pd.cut(df_fe['hacinamiento'], 
                                         bins=[0, 1.5, 3, 100],
                                         labels=[1, 2, 3]).astype(int)
    nuevas_features.append('hacinamiento_cat')
    print("✓ Feature 'hacinamiento_cat' creado")

# 3. Score de Servicios Públicos (sin incluir P5100, P5110 que tienen códigos especiales)
servicios_cols = ['P5070', 'P5080', 'P5090']
servicios_disponibles = [col for col in servicios_cols if col in df_fe.columns]
if len(servicios_disponibles) > 0:
    df_fe['servicios_score'] = 0
    for col in servicios_disponibles:
        df_fe['servicios_score'] += (df_fe[col] == 1).astype(int)
    nuevas_features.append('servicios_score')
    print(f"✓ Feature 'servicios_score' creado")

# 4. Indicador de Formalidad
if 'P6250' in df_fe.columns:
    df_fe['es_formal'] = (df_fe['P6250'] == 1).astype(int)
    nuevas_features.append('es_formal')
    print("✓ Feature 'es_formal' creado")

# 5. Tiene Empleo
if 'FT' in df_fe.columns:
    # FT es constante, ya fue eliminada
    pass

# ===========================
# 4B. FEATURE ENGINEERING PARA VARIABLES HÍBRIDAS
# ===========================
print("\n" + "="*80)
print("4B. TRANSFORMACIONES ESPECIALES PARA VARIABLES HÍBRIDAS")
print("="*80)

# P5100 - Energía Eléctrica
# 96% tiene valor 500,000 (código de "Sí tiene")
if 'P5100' in df_fe.columns:
    # Binaria: Tiene energía
    df_fe['tiene_energia'] = 1  # Todos tienen (96%+ tiene el mismo valor)
    
    # Categórica de nivel de gasto (solo para el 4% restante)
    df_fe['nivel_gasto_energia'] = 2  # Medio (por defecto)
    df_fe.loc[df_fe['P5100'] == 500000, 'nivel_gasto_energia'] = 2  # Valor estándar
    df_fe.loc[df_fe['P5100'] < 500000, 'nivel_gasto_energia'] = 1  # Bajo
    df_fe.loc[df_fe['P5100'] > 500000, 'nivel_gasto_energia'] = 3  # Alto
    
    nuevas_features.extend(['tiene_energia', 'nivel_gasto_energia'])
    print("✓ Features de P5100 (energía) creados: tiene_energia, nivel_gasto_energia")

# P5110 - Recolección de Basuras
# 71% código 98 (Sí tiene), 3% código 99 (No sabe), 26% valores altos (costos)
if 'P5110' in df_fe.columns:
    # Binaria: Tiene recolección
    df_fe['tiene_recoleccion'] = (df_fe['P5110'] == 98).astype(int)
    
    # Categórica simplificada
    df_fe['estado_recoleccion'] = 1  # Por defecto: Sí
    df_fe.loc[df_fe['P5110'] == 98, 'estado_recoleccion'] = 1  # Sí tiene
    df_fe.loc[df_fe['P5110'] == 99, 'estado_recoleccion'] = 2  # No sabe
    df_fe.loc[df_fe['P5110'] > 1000000, 'estado_recoleccion'] = 3  # Paga directamente
    
    nuevas_features.extend(['tiene_recoleccion', 'estado_recoleccion'])
    print("✓ Features de P5110 (recolección basuras) creados: tiene_recoleccion, estado_recoleccion")

# P6120 - Atención Médica (MUY IMPORTANTE)
# -1 = No requirió (71%), 98 = código especial (1%), otros = costos reales (28%)
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
    print("✓ Features de P6120 (atención médica) creados: requirio_atencion_medica, nivel_gasto_salud, log_gasto_salud")

print(f"\n✓ {len(nuevas_features)} nuevas features creadas")

# Ahora ELIMINAR las variables originales híbridas (ya extraímos la info)
vars_hibridas_originales = ['P5100', 'P5110', 'P6120']
features_finales = [f for f in features_base if f not in vars_hibridas_originales]

print(f"\n✓ Variables originales híbridas reemplazadas por features engineered:")
for var in vars_hibridas_originales:
    print(f"  ✗ {var} (reemplazada)")

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
print(f"  X shape: {X.shape}")
print(f"  y shape: {y.shape}")
print(f"  Features: {X.shape[1]}")

# ===========================
# 6. SPLIT ESTRATIFICADO
# ===========================
print("\n" + "="*80)
print("6. SPLIT TRAIN/TEST ESTRATIFICADO")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"\nTRAIN SET: {len(X_train):,} registros ({len(X_train)/len(X)*100:.1f}%)")
print(f"  No Vulnerable: {(y_train==0).sum():,} ({(y_train==0).sum()/len(y_train)*100:.2f}%)")
print(f"  Vulnerable:    {(y_train==1).sum():,} ({(y_train==1).sum()/len(y_train)*100:.2f}%)")

print(f"\nTEST SET: {len(X_test):,} registros ({len(X_test)/len(X)*100:.1f}%)")
print(f"  No Vulnerable: {(y_test==0).sum():,} ({(y_test==0).sum()/len(y_test)*100:.2f}%)")
print(f"  Vulnerable:    {(y_test==1).sum():,} ({(y_test==1).sum()/len(y_test)*100:.2f}%)")

# ===========================
# 7. EXPORTAR DATOS
# ===========================
print("\n" + "="*80)
print("7. EXPORTACIÓN DE DATOS PROCESADOS")
print("="*80)

output_dir = Path('data/processed/modeling')
output_dir.mkdir(exist_ok=True, parents=True)

# Guardar datasets
X_train.to_csv(output_dir / 'X_train.csv', index=False)
X_test.to_csv(output_dir / 'X_test.csv', index=False)
y_train.to_csv(output_dir / 'y_train.csv', index=False, header=['IS_VULNERABLE'])
y_test.to_csv(output_dir / 'y_test.csv', index=False, header=['IS_VULNERABLE'])

print(f"\n✓ Datasets guardados:")
print(f"  • X_train.csv ({X_train.shape})")
print(f"  • X_test.csv ({X_test.shape})")
print(f"  • y_train.csv ({y_train.shape})")
print(f"  • y_test.csv ({y_test.shape})")

# Guardar metadata
metadata = {
    'dataset_info': {
        'n_samples_total': len(X),
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test),
        'n_features': X.shape[1],
        'test_size': 0.2,
        'random_state': 42
    },
    'target_info': {
        'name': 'IS_VULNERABLE',
        'linea_pobreza': LINEA_POBREZA_2024,
        'factor_vulnerabilidad': FACTOR_VULNERABILIDAD,
        'class_balance_train': {
            '0_no_vulnerable': int((y_train==0).sum()),
            '1_vulnerable': int((y_train==1).sum())
        },
        'imbalance_ratio': float(imbalance_ratio)
    },
    'features': {
        'all_features': list(X.columns),
        'n_originales': len(features_finales),
        'n_engineered': len(nuevas_features),
        'features_originales_mantenidas': features_finales,
        'features_engineered': [f for f in nuevas_features if f != 'hacinamiento'],
        'features_eliminadas_constantes': vars_eliminar,
        'features_transformadas_hibridas': vars_hibridas_originales
    },
    'transformaciones_especiales': {
        'P5100_energia': 'Transformada a: tiene_energia, nivel_gasto_energia',
        'P5110_recoleccion': 'Transformada a: tiene_recoleccion, estado_recoleccion',
        'P6120_salud': 'Transformada a: requirio_atencion_medica, nivel_gasto_salud, log_gasto_salud'
    }
}

with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

with open(output_dir / 'feature_names.txt', 'w', encoding='utf-8') as f:
    for feat in X.columns:
        f.write(f"{feat}\n")

print(f"✓ Metadata guardada: metadata.json")
print(f"✓ Features guardadas: feature_names.txt")

# ===========================
# 8. RESUMEN FINAL
# ===========================
print("\n" + "="*80)
print("✅ RESUMEN FINAL - EDA Y FEATURE ENGINEERING COMPLETADO")
print("="*80)

print(f"\n📊 DATOS PROCESADOS:")
print(f"  Registros totales:        {len(X):>10,}")
print(f"  Features finales:         {X.shape[1]:>10}")
print(f"  Train set:                {len(X_train):>10,}")
print(f"  Test set:                 {len(X_test):>10,}")

print(f"\n🎯 TARGET:")
print(f"  Clase 0 (No Vulnerable):  {(y==0).sum():>10,} ({(y==0).sum()/len(y)*100:.2f}%)")
print(f"  Clase 1 (Vulnerable):     {(y==1).sum():>10,} ({(y==1).sum()/len(y)*100:.2f}%)")
print(f"  Ratio desbalanceo:        {imbalance_ratio:>10.2f}:1")

print(f"\n🔧 FEATURE ENGINEERING:")
print(f"  Features originales:      {len(features_finales):>10}")
print(f"  Features creadas:         {len(nuevas_features):>10}")
print(f"  Features eliminadas:      {len(vars_eliminar):>10}")
print(f"  Features transformadas:   {len(vars_hibridas_originales):>10}")

print(f"\n⚙️ TRANSFORMACIONES ESPECIALES:")
print(f"  P5100 → tiene_energia + nivel_gasto_energia")
print(f"  P5110 → tiene_recoleccion + estado_recoleccion")
print(f"  P6120 → requirio_atencion_medica + nivel_gasto_salud + log_gasto_salud")

print(f"\n💾 ARCHIVOS EXPORTADOS:")
print(f"  Directorio: data/processed/modeling/")
print(f"  • X_train.csv, X_test.csv")
print(f"  • y_train.csv, y_test.csv")
print(f"  • metadata.json")
print(f"  • feature_names.txt")

print(f"\n💡 RECOMENDACIONES PARA MODELADO:")
print(f"  1. Usar class_weight='balanced' o scale_pos_weight={imbalance_ratio:.1f}")
print(f"  2. Métrica principal: ROC-AUC")
print(f"  3. Evaluar: Recall, Precision, F1-Score")
print(f"  4. XGBoost funciona bien con categóricas")

print(f"\n{'='*80}")
print("✅ LISTO PARA NOTEBOOK 4 (MODELADO)")
print(f"{'='*80}")

