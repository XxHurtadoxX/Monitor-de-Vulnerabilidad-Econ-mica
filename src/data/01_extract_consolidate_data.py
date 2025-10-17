#!/usr/bin/env python3
"""
Extracción y Consolidación de Datos GEIH 2024
Monitor de Vulnerabilidad Económica - Colombia

Este script extrae los datos de los 12 meses de 2024 de los archivos ZIP
y consolida todos los módulos en un único dataset.

Módulos GEIH:
1. Características generales, seguridad social en salud y educación
2. Datos del hogar y la vivienda
3. Fuerza de trabajo
4. Migración
5. No ocupados
6. Ocupados
7. Otras formas de trabajo
8. Otros ingresos e impuestos
"""

import pandas as pd
import zipfile
import os
from pathlib import Path
import json
from datetime import datetime

# Configuración
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(exist_ok=True)

# Mapeo de nombres de archivos ZIP a periodo
MONTH_MAPPING = {
    'Ene_2024.zip': 202401,
    'Febrero_2024.zip': 202402,
    'Marzo 2024.zip': 202403,
    'Abril 2024.zip': 202404,
    'Mayo_2024 1.zip': 202405,
    'Junio_2024.zip': 202406,
    'Julio_2024.zip': 202407,
    'Agosto_2024.zip': 202408,
    'Septiembre_2024.zip': 202409,
    'Octubre_2024.zip': 202410,
    'Noviembre_ 2024.zip': 202411,
    'Diciembre_2024.zip': 202412
}

# Nombres de módulos
MODULE_NAMES = {
    'Características generales, seguridad social en salud y educación.CSV': 'caracteristicas_generales',
    'Datos del hogar y la vivienda.CSV': 'datos_hogar',
    'Fuerza de trabajo.CSV': 'fuerza_trabajo',
    'Migración.CSV': 'migracion',
    'No ocupados.CSV': 'no_ocupados',
    'Ocupados.CSV': 'ocupados',
    'Otras formas de trabajo.CSV': 'otras_formas_trabajo',
    'Otros ingresos e impuestos.CSV': 'otros_ingresos'
}

# Identificadores según nivel de análisis
ID_COLUMNS = {
    'hogar': ['DIRECTORIO', 'SECUENCIA_P', 'HOGAR'],
    'persona': ['DIRECTORIO', 'SECUENCIA_P', 'ORDEN', 'HOGAR'],
    'mes': ['PERIODO']
}


def extract_module_from_zip(zip_path, module_name, periodo):
    """
    Extraer un módulo específico de un archivo ZIP
    
    Args:
        zip_path: Ruta al archivo ZIP
        module_name: Nombre del módulo CSV
        periodo: Periodo (YYYYMM)
        
    Returns:
        DataFrame con los datos del módulo
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Buscar el archivo CSV dentro del ZIP
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.CSV')]
            target_file = [f for f in csv_files if module_name in f]
            
            if not target_file:
                print(f"  ⚠ Módulo {module_name} no encontrado en {zip_path.name}")
                return None
            
            # Leer el CSV con codificación latin-1 y separador ;
            with zip_ref.open(target_file[0]) as file:
                df = pd.read_csv(file, encoding='latin-1', sep=';', low_memory=False)
                
                # Agregar columna PERIODO si no existe
                if 'PERIODO' not in df.columns:
                    df['PERIODO'] = periodo
                
                print(f"  ✓ {module_name}: {df.shape[0]:,} registros, {df.shape[1]} columnas")
                return df
                
    except Exception as e:
        print(f"  ✗ Error extrayendo {module_name}: {e}")
        return None


def consolidate_module_across_months(module_name, module_key):
    """
    Consolidar un módulo a través de los 12 meses
    
    Args:
        module_name: Nombre del archivo CSV del módulo
        module_key: Clave del módulo (caracteristicas_generales, etc.)
        
    Returns:
        DataFrame consolidado del módulo
    """
    print(f"\n{'='*60}")
    print(f"Consolidando módulo: {module_key}")
    print(f"{'='*60}")
    
    all_data = []
    
    for zip_file, periodo in MONTH_MAPPING.items():
        zip_path = RAW_DIR / zip_file
        
        if not zip_path.exists():
            print(f"⚠ Archivo no encontrado: {zip_file}")
            continue
        
        print(f"\nMes {periodo} ({zip_file}):")
        
        # Extraer módulo
        df = extract_module_from_zip(zip_path, module_name, periodo)
        
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        print(f"✗ No se encontraron datos para {module_key}")
        return None
    
    # Concatenar todos los meses
    consolidated_df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n{'─'*60}")
    print(f"TOTAL CONSOLIDADO: {consolidated_df.shape[0]:,} registros")
    print(f"Columnas: {consolidated_df.shape[1]}")
    print(f"Periodos: {sorted(consolidated_df['PERIODO'].unique())}")
    print(f"{'─'*60}")
    
    # No guardar módulos intermedios, solo retornar para el merge
    return consolidated_df


def identify_module_level(df, module_key):
    """
    Identificar si el módulo es a nivel hogar o persona
    
    Args:
        df: DataFrame del módulo
        module_key: Clave del módulo
        
    Returns:
        str: 'hogar' o 'persona'
    """
    # Módulos a nivel hogar (no tienen ORDEN)
    hogar_modules = ['datos_hogar']
    
    if module_key in hogar_modules or 'ORDEN' not in df.columns:
        return 'hogar'
    else:
        return 'persona'


def merge_all_modules(modules_data):
    """
    Hacer merge de todos los módulos consolidados
    
    Args:
        modules_data: Diccionario con los módulos consolidados
        
    Returns:
        DataFrame con todos los módulos unidos
    """
    print(f"\n{'='*60}")
    print(f"MERGE DE TODOS LOS MÓDULOS")
    print(f"{'='*60}")
    
    # Mostrar información de los módulos
    for module_key, module_info in modules_data.items():
        df = module_info['data']
        level = module_info['level']
        print(f"\n{module_key}:")
        print(f"  Nivel: {level}")
        print(f"  Shape: {df.shape}")
    
    # Empezar con el módulo de características generales (nivel persona)
    print(f"\n{'─'*60}")
    print("Iniciando merge desde características generales...")
    print(f"{'─'*60}")
    
    base_df = modules_data['caracteristicas_generales']['data'].copy()
    print(f"\nBase inicial: {base_df.shape}")
    
    # Merge con datos del hogar (nivel hogar)
    if 'datos_hogar' in modules_data:
        hogar_df = modules_data['datos_hogar']['data']
        
        # IDs para merge a nivel hogar
        merge_keys_hogar = ['DIRECTORIO', 'SECUENCIA_P', 'HOGAR', 'PERIODO']
        
        print(f"\nMerge con datos_hogar (nivel hogar)...")
        base_df = base_df.merge(
            hogar_df,
            on=merge_keys_hogar,
            how='left',
            suffixes=('', '_hogar')
        )
        print(f"Shape después del merge: {base_df.shape}")
    
    # Merge con módulos a nivel persona
    persona_modules = [k for k, v in modules_data.items() 
                      if k not in ['caracteristicas_generales', 'datos_hogar'] 
                      and v['level'] == 'persona']
    
    merge_keys_persona = ['DIRECTORIO', 'SECUENCIA_P', 'ORDEN', 'HOGAR', 'PERIODO']
    
    for module_key in persona_modules:
        print(f"\nMerge con {module_key} (nivel persona)...")
        module_df = modules_data[module_key]['data']
        
        base_df = base_df.merge(
            module_df,
            on=merge_keys_persona,
            how='left',
            suffixes=('', f'_{module_key}')
        )
        print(f"Shape después del merge: {base_df.shape}")
    
    print(f"\n{'─'*60}")
    print(f"MERGE FINAL COMPLETADO")
    print(f"Shape final: {base_df.shape}")
    print(f"Registros totales: {base_df.shape[0]:,}")
    print(f"Columnas totales: {base_df.shape[1]:,}")
    print(f"{'─'*60}")
    
    # Guardar dataset consolidado
    output_file = PROCESSED_DIR / "geih_2024_consolidated.csv"
    base_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Dataset consolidado guardado en: {output_file}")
    
    # Guardar resumen
    summary = {
        'fecha_consolidacion': datetime.now().isoformat(),
        'total_registros': int(base_df.shape[0]),
        'total_columnas': int(base_df.shape[1]),
        'periodos': sorted([int(p) for p in base_df['PERIODO'].unique()]),
        'modulos_incluidos': list(modules_data.keys()),
        'valores_nulos_por_columna': base_df.isnull().sum().to_dict(),
        'tipos_datos': base_df.dtypes.astype(str).to_dict()
    }
    
    with open(PROCESSED_DIR / 'consolidation_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Resumen guardado en: {PROCESSED_DIR / 'consolidation_summary.json'}")
    
    return base_df


def main():
    """
    Función principal
    """
    print("="*70)
    print("EXTRACCIÓN Y CONSOLIDACIÓN DE DATOS GEIH 2024")
    print("Monitor de Vulnerabilidad Económica - Colombia")
    print("="*70)
    
    # Paso 1: Consolidar cada módulo a través de los meses
    print("\n📊 PASO 1: Consolidando módulos individuales...")
    
    modules_data = {}
    for csv_name, module_key in MODULE_NAMES.items():
        df = consolidate_module_across_months(csv_name, module_key)
        if df is not None:
            level = identify_module_level(df, module_key)
            modules_data[module_key] = {
                'data': df,
                'level': level,
                'shape': df.shape
            }
    
    # Paso 2: Hacer merge de todos los módulos
    print("\n🔗 PASO 2: Uniendo todos los módulos...")
    
    final_df = merge_all_modules(modules_data)
    
    # Paso 3: Mostrar información sobre valores nulos
    print("\n📋 PASO 3: Análisis de valores nulos...")
    print(f"\n{'─'*60}")
    
    null_counts = final_df.isnull().sum()
    null_pct = (null_counts / len(final_df) * 100).round(2)
    
    # Mostrar columnas con más del 50% de nulos
    high_null_cols = null_pct[null_pct > 50].sort_values(ascending=False)
    
    if len(high_null_cols) > 0:
        print(f"\nColumnas con >50% valores nulos ({len(high_null_cols)} columnas):")
        print("(Pueden ser 'No Aplica' según el módulo)")
        for col, pct in high_null_cols.head(20).items():
            print(f"  {col}: {pct:.1f}%")
    
    print(f"\n{'='*70}")
    print("✅ CONSOLIDACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*70}")
    print(f"\nArchivo final: {PROCESSED_DIR / 'geih_2024_consolidated.csv'}")
    print(f"Registros: {final_df.shape[0]:,}")
    print(f"Columnas: {final_df.shape[1]:,}")


if __name__ == "__main__":
    main()
