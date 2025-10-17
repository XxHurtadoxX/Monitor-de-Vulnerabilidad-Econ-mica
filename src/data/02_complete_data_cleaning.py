#!/usr/bin/env python3
"""
Script de tratamiento adicional de nulos
Complemento al Notebook 2
"""

import pandas as pd
import numpy as np

# Cargar dataset
print("Cargando dataset...")
df = pd.read_csv('data/processed/geih_2024_ipm_variables.csv')
print(f"Dataset cargado: {df.shape}")

# Aplicar limpieza ya hecha
print("\nAplicando limpieza básica...")
df_clean = df[df['AREA'].notnull()].copy()

# Imputaciones "NO APLICA"
df_clean.loc[df_clean['P6040'] < 10, 'FT'] = df_clean.loc[df_clean['P6040'] < 10, 'FT'].fillna(-1)
mask_no_ocupado = (df_clean['FT'] != 1) | (df_clean['FT'].isnull())
vars_ocupados = ['INGLABO', 'P6250', 'P6430', 'P6920']
for var in vars_ocupados:
    if var in df_clean.columns:
        df_clean.loc[mask_no_ocupado, var] = df_clean.loc[mask_no_ocupado, var].fillna(-1)

df_clean.loc[df_clean['P6040'] >= 18, 'P6585S1'] = df_clean.loc[df_clean['P6040'] >= 18, 'P6585S1'].fillna(-1)
df_clean.loc[df_clean['P6040'] >= 18, 'P6585S2'] = df_clean.loc[df_clean['P6040'] >= 18, 'P6585S2'].fillna(-1)
df_clean.loc[df_clean['P6040'] >= 18, 'P6585S3'] = df_clean.loc[df_clean['P6040'] >= 18, 'P6585S3'].fillna(-1)
df_clean['P6120'] = df_clean['P6120'].fillna(-1)

# Imputar servicios
vars_servicios = ['P5070', 'P5080', 'P5090', 'P5100', 'P5110']
for var in vars_servicios:
    if var in df_clean.columns:
        if df_clean[var].isnull().sum() > 0:
            moda = df_clean[var].mode()[0] if len(df_clean[var].mode()) > 0 else 2
            df_clean[var] = df_clean[var].fillna(moda)

print(f"Dataset después de limpieza básica: {df_clean.shape}")

# TRATAMIENTO ADICIONAL DE NULOS RESTANTES
print("\n" + "="*60)
print("TRATAMIENTO ADICIONAL DE NULOS")
print("="*60)

# 1. P6110 (Mortalidad) - Solo mujeres en edad fértil
if 'P6110' in df_clean.columns and 'P6016' in df_clean.columns:
    es_mujer_fertil = (df_clean['P6016'] == 2) & (df_clean['P6040'] >= 15) & (df_clean['P6040'] <= 49)
    antes = df_clean['P6110'].isnull().sum()
    df_clean.loc[~es_mujer_fertil, 'P6110'] = df_clean.loc[~es_mujer_fertil, 'P6110'].fillna(-1)
    df_clean['P6110'] = df_clean['P6110'].fillna(2)  # Asumir "No" para restantes
    print(f"P6110: {antes:,} → 0 nulos")

# 2. P6250 (Tipo empleo) - Para ocupados sin dato, asumir informal (2)
if 'P6250' in df_clean.columns:
    antes = df_clean['P6250'].isnull().sum()
    # Solo para ocupados (FT == 1) sin dato
    mask_ocupado_sin_dato = (df_clean['FT'] == 1) & (df_clean['P6250'].isnull())
    df_clean.loc[mask_ocupado_sin_dato, 'P6250'] = 2  # Asumir informal
    print(f"P6250: {antes:,} → {df_clean['P6250'].isnull().sum():,} nulos")

# 3. FT - Para >= 10 años sin dato, asumir inactivo (0)
if 'FT' in df_clean.columns:
    antes = df_clean['FT'].isnull().sum()
    mask_sin_ft = (df_clean['P6040'] >= 10) & (df_clean['FT'].isnull())
    df_clean.loc[mask_sin_ft, 'FT'] = 0  # Inactivo
    print(f"FT: {antes:,} → {df_clean['FT'].isnull().sum():,} nulos")

# 4. P6585 (Niñez) - Para < 18 sin dato, eliminar estas variables (no son críticas)
vars_ninez = ['P6585S1', 'P6585S2', 'P6585S3']
for var in vars_ninez:
    if var in df_clean.columns:
        # Impuar con -2 para menores sin dato (diferente de -1 que es NO APLICA)
        mask_menor_sin_dato = (df_clean['P6040'] < 18) & (df_clean[var].isnull())
        df_clean.loc[mask_menor_sin_dato, var] = -2
        print(f"{var}: Imputados con -2 (sin dato)")

# 5. P6240 (Tiempo buscando trabajo) - Solo aplica a desocupados
# FT: 2=Desocupados
if 'P6240' in df_clean.columns:
    antes = df_clean['P6240'].isnull().sum()
    # Imputar -1 para no desocupados
    mask_no_desocupado = (df_clean['FT'] != 2) | (df_clean['FT'].isnull())
    df_clean.loc[mask_no_desocupado, 'P6240'] = df_clean.loc[mask_no_desocupado, 'P6240'].fillna(-1)
    # Para desocupados sin dato, imputar con moda o -2
    df_clean['P6240'] = df_clean['P6240'].fillna(-2)
    print(f"P6240: {antes:,} → 0 nulos")

# 6. INGLABO - Para ocupados sin ingreso, imputar con 0
if 'INGLABO' in df_clean.columns:
    antes = df_clean['INGLABO'].isnull().sum()
    df_clean['INGLABO'] = df_clean['INGLABO'].fillna(0)
    print(f"INGLABO: {antes:,} → 0 nulos")

# 7. P6430, P6920 - Variables ocupados, imputar con -2
for var in ['P6430', 'P6920']:
    if var in df_clean.columns:
        antes = df_clean[var].isnull().sum()
        df_clean[var] = df_clean[var].fillna(-2)
        print(f"{var}: {antes:,} → 0 nulos")

# 8. P6100 (Acceso salud) - Imputar con moda (2 = No)
if 'P6100' in df_clean.columns:
    antes = df_clean['P6100'].isnull().sum()
    moda = df_clean['P6100'].mode()[0] if len(df_clean['P6100'].mode()) > 0 else 2
    df_clean['P6100'] = df_clean['P6100'].fillna(moda)
    print(f"P6100: {antes:,} → 0 nulos (moda={moda})")

# 9. P6160, P6170 (Educación) - Imputar con valores típicos
if 'P6160' in df_clean.columns:
    antes = df_clean['P6160'].isnull().sum()
    df_clean['P6160'] = df_clean['P6160'].fillna(1)  # Sí sabe leer
    print(f"P6160: {antes:,} → 0 nulos")

if 'P6170' in df_clean.columns:
    antes = df_clean['P6170'].isnull().sum()
    # Imputar con mediana de edad
    mediana = df_clean['P6170'].median()
    df_clean['P6170'] = df_clean['P6170'].fillna(mediana)
    print(f"P6170: {antes:,} → 0 nulos (mediana={mediana})")

# 10. P5030 (Material techos) - Imputar con moda
if 'P5030' in df_clean.columns:
    antes = df_clean['P5030'].isnull().sum()
    moda = df_clean['P5030'].mode()[0] if len(df_clean['P5030'].mode()) > 0 else 1
    df_clean['P5030'] = df_clean['P5030'].fillna(moda)
    print(f"P5030: {antes:,} → 0 nulos (moda={moda})")

# Verificación final
print("\n" + "="*60)
print("VERIFICACIÓN FINAL")
print("="*60)

nulos_finales = df_clean.isnull().sum()
nulos_restantes = nulos_finales[nulos_finales > 0]

print(f"\nVariables con nulos restantes: {len(nulos_restantes)}")
if len(nulos_restantes) > 0:
    for var, count in nulos_restantes.items():
        print(f"  {var}: {count:,} ({count/len(df_clean)*100:.2f}%)")
else:
    print("✓ NO HAY NULOS RESTANTES")

# Guardar dataset completamente limpio
output_file = 'data/processed/geih_2024_ipm_clean.csv'
df_clean.to_csv(output_file, index=False)

print(f"\n{'='*60}")
print("DATASET LIMPIO GUARDADO")
print(f"{'='*60}")
print(f"Archivo: {output_file}")
print(f"Registros: {df_clean.shape[0]:,}")
print(f"Columnas: {df_clean.shape[1]}")
print(f"\n✓ Dataset listo para Feature Engineering y Modelado")

