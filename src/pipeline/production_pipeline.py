"""
Pipeline de Producción - Monitor de Vulnerabilidad Económica
Transforma respuestas del usuario en features para el modelo

Features requeridas (37):
- 26 features originales de GEIH
- 11 features engineered

Autor: Data Science Team
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import joblib
from pathlib import Path
import json


class VulnerabilityPipeline:
    """
    Pipeline completo para predicción de vulnerabilidad económica
    
    Flujo:
    1. Recibe respuestas del usuario (dict)
    2. Valida y transforma a features GEIH
    3. Aplica Feature Engineering
    4. Hace predicción con umbral optimizado
    """
    
    def __init__(self, model_path: str = None, threshold: float = None):
        """
        Inicializar pipeline
        
        Args:
            model_path: Ruta al modelo .pkl
            threshold: Umbral de decisión personalizado
        """
        # Cargar modelo
        if model_path is None:
            model_path = 'models/final_optimized_xgboost.pkl'
        
        self.model = joblib.load(model_path)
        
        # Cargar umbral optimizado
        if threshold is None:
            threshold_file = Path('models/threshold_optimization.json')
            if threshold_file.exists():
                with open(threshold_file, 'r') as f:
                    threshold_data = json.load(f)
                    self.threshold = threshold_data['optimal_threshold']
            else:
                self.threshold = 0.5  # Default
        else:
            self.threshold = threshold
        
        # Orden de features requerido por el modelo
        self.feature_order = [
            'P6040', 'P6110', 'P5020', 'P6585S2', 'P6016', 'P6585S3', 'P6080', 
            'P6050', 'P6090', 'P6430', 'P6920', 'P5000', 'DPTO', 'P5080', 'P5040', 
            'AREA', 'P5090', 'P6250', 'P6240', 'P5030', 'P6585S1', 'P6160', 
            'P6100', 'P6170', 'P5070', 'P5010',
            'edad_grupo', 'hacinamiento_cat', 'servicios_score', 'es_formal',
            'tiene_energia', 'nivel_gasto_energia', 'tiene_recoleccion', 
            'estado_recoleccion', 'requirio_atencion_medica', 'nivel_gasto_salud', 
            'log_gasto_salud'
        ]
        
        print(f"✓ Pipeline inicializado")
        print(f"  Modelo: {model_path}")
        print(f"  Umbral: {self.threshold:.4f}")
        print(f"  Features requeridas: {len(self.feature_order)}")
    
    def transform_user_input(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma respuestas del usuario a features GEIH
        
        Args:
            user_data: Diccionario con respuestas del usuario
            
        Returns:
            features_dict: Diccionario con features para el modelo
        """
        features = {}
        
        # ======================
        # DEMOGRÁFICAS
        # ======================
        # P6040: Edad (continua)
        features['P6040'] = user_data.get('edad', 30)
        
        # P6016: Mes de nacimiento (1-12)
        features['P6016'] = user_data.get('mes_nacimiento', 6)
        
        # P6050: Sexo (1=Hombre, 2=Mujer)
        sexo_map = {'hombre': 1, 'mujer': 2, 'masculino': 1, 'femenino': 2}
        features['P6050'] = sexo_map.get(user_data.get('sexo', '').lower(), 1)
        
        # P6080: Parentesco con jefe de hogar (1-6)
        # 1=Jefe, 2=Cónyuge, 3=Hijo, 4=Nieto, 5=Otro pariente, 6=Otro no pariente
        parentesco_map = {
            'jefe': 1, 'conyuge': 2, 'esposo': 2, 'esposa': 2,
            'hijo': 3, 'hija': 3, 'nieto': 4, 'nieta': 4,
            'otro_pariente': 5, 'otro': 6
        }
        features['P6080'] = parentesco_map.get(user_data.get('parentesco', '').lower(), 1)
        
        # AREA: Área (1=Cabecera, 2=Rural) - pero codificado como departamento en dataset
        # Simplificamos: usamos código de ciudad principal
        features['AREA'] = user_data.get('area_codigo', 11)  # Default: Bogotá
        
        # DPTO: Departamento (código DANE)
        features['DPTO'] = user_data.get('departamento', 11)  # Default: Bogotá
        
        # ======================
        # EDUCACIÓN
        # ======================
        # P6160: Nivel educativo (1=Ninguno, 2=Preescolar, 3=Primaria, 4=Secundaria, 5=Media, 6=Superior)
        # Simplificado a binario en dataset: 1 o 2
        nivel_educativo = user_data.get('nivel_educativo', 'secundaria').lower()
        if nivel_educativo in ['ninguno', 'preescolar', 'primaria']:
            features['P6160'] = 1
        else:
            features['P6160'] = 2
        
        # P6170: Años de educación (0-20+)
        # Simplificado a binario en dataset
        años_edu = user_data.get('años_educacion', 11)
        features['P6170'] = 2 if años_edu >= 11 else 1
        
        # ======================
        # SALUD
        # ======================
        # P6090: Afiliación a salud (1=Sí, 2=No, 9=No sabe)
        tiene_salud = user_data.get('tiene_salud', True)
        features['P6090'] = 1 if tiene_salud else 2
        
        # P6100: Tipo de afiliación (1=Contributivo, 2=Subsidiado, 3=Especial, 4=No afiliado)
        tipo_salud_map = {'contributivo': 1, 'subsidiado': 2, 'especial': 3, 'ninguno': 4}
        features['P6100'] = tipo_salud_map.get(user_data.get('tipo_salud', '').lower(), 2)
        
        # P6110: Mortalidad infantil (-1=No aplica, 1=Sí, 2=No)
        # -1 para personas sin hijos menores
        tiene_hijos_menores = user_data.get('tiene_hijos_menores', False)
        if not tiene_hijos_menores:
            features['P6110'] = -1
        else:
            features['P6110'] = 2  # Asumimos no ha tenido fallecimientos
        
        # Variables de atención médica (original P6120, transformada)
        requirio_atencion = user_data.get('requirio_atencion_medica', False)
        gasto_salud = user_data.get('gasto_salud_ultimos_30_dias', 0)
        
        # ======================
        # TRABAJO
        # ======================
        # P6240: Ocupación principal (1-9 categorías)
        # Simplificamos a categorías principales
        features['P6240'] = user_data.get('ocupacion_codigo', 1)
        
        # P6250: Tipo de empleo (1=Formal, 2=Informal)
        es_formal = user_data.get('empleo_formal', False)
        features['P6250'] = 1 if es_formal else 2
        
        # P6430: Posición ocupacional (1-7)
        features['P6430'] = user_data.get('posicion_ocupacional', 1)
        
        # P6920: Rama de actividad (1-3)
        features['P6920'] = user_data.get('rama_actividad', 2)
        
        # ======================
        # VIVIENDA
        # ======================
        # P5000: Tipo de vivienda (1=Casa, 2=Apartamento, 3=Cuarto, etc.)
        tipo_vivienda_map = {
            'casa': 1, 'apartamento': 2, 'cuarto': 3, 
            'casa_lote': 4, 'otro': 5
        }
        features['P5000'] = tipo_vivienda_map.get(user_data.get('tipo_vivienda', '').lower(), 1)
        
        # P5010: Tenencia de vivienda (1=Propia, 2=Arriendo, 3=Usufructo, etc.)
        tenencia_map = {
            'propia': 1, 'arriendo': 2, 'arrendada': 2,
            'prestada': 3, 'usufructo': 3, 'otra': 4
        }
        features['P5010'] = tenencia_map.get(user_data.get('tenencia_vivienda', '').lower(), 2)
        
        # P5020: Número de cuartos (1-10+)
        features['P5020'] = user_data.get('num_cuartos', 3)
        
        # P5030: Número de personas en el hogar (1-20+)
        # Codificado como binario en dataset
        num_personas = user_data.get('num_personas_hogar', 4)
        features['P5030'] = 2 if num_personas >= 5 else 1
        
        # P5040: Material de pisos (1-6)
        material_map = {
            'cemento': 1, 'baldosa': 2, 'madera': 3,
            'tierra': 4, 'otro': 5
        }
        features['P5040'] = material_map.get(user_data.get('material_pisos', '').lower(), 2)
        
        # ======================
        # SERVICIOS PÚBLICOS
        # ======================
        # P5070: Acueducto (1=Sí, 2=No)
        features['P5070'] = 1 if user_data.get('tiene_acueducto', True) else 2
        
        # P5080: Alcantarillado (1=Sí, 2=No)
        features['P5080'] = 1 if user_data.get('tiene_alcantarillado', True) else 2
        
        # P5090: Gas (1=Sí, 2=No)
        features['P5090'] = 1 if user_data.get('tiene_gas', True) else 2
        
        # Variables de energía y recolección (originales transformadas)
        tiene_energia = user_data.get('tiene_energia', True)
        gasto_energia = user_data.get('gasto_energia_mensual', 500000)
        
        tiene_recoleccion = user_data.get('tiene_recoleccion_basuras', True)
        
        # ======================
        # NIÑEZ
        # ======================
        # P6585S1, S2, S3: Trabajo infantil (-1=No aplica, 1=Sí, 2=No)
        num_menores = user_data.get('num_menores_hogar', 0)
        if num_menores == 0:
            features['P6585S1'] = -1
            features['P6585S2'] = -1
            features['P6585S3'] = -1
        else:
            # Asumimos que no trabajan
            features['P6585S1'] = 2
            features['P6585S2'] = 2 if num_menores >= 2 else -1
            features['P6585S3'] = 2 if num_menores >= 3 else -1
        
        # ======================
        # FEATURE ENGINEERING
        # ======================
        # edad_grupo: Grupos de edad (1-4)
        edad = features['P6040']
        if edad <= 25:
            features['edad_grupo'] = 1
        elif edad <= 40:
            features['edad_grupo'] = 2
        elif edad <= 60:
            features['edad_grupo'] = 3
        else:
            features['edad_grupo'] = 4
        
        # hacinamiento_cat: Índice de hacinamiento (1-3)
        personas = num_personas
        cuartos = features['P5020']
        if cuartos > 0:
            hacinamiento = personas / cuartos
            if hacinamiento <= 1.5:
                features['hacinamiento_cat'] = 1
            elif hacinamiento <= 3:
                features['hacinamiento_cat'] = 2
            else:
                features['hacinamiento_cat'] = 3
        else:
            features['hacinamiento_cat'] = 3
        
        # servicios_score: Suma de servicios (0-3)
        features['servicios_score'] = sum([
            1 if features['P5070'] == 1 else 0,
            1 if features['P5080'] == 1 else 0,
            1 if features['P5090'] == 1 else 0
        ])
        
        # es_formal: Empleo formal (binario)
        features['es_formal'] = 1 if es_formal else 0
        
        # tiene_energia: Tiene energía (siempre 1 en práctica)
        features['tiene_energia'] = 1 if tiene_energia else 0
        
        # nivel_gasto_energia: Nivel de gasto en energía (1-3)
        if gasto_energia < 500000:
            features['nivel_gasto_energia'] = 1
        elif gasto_energia <= 500000:
            features['nivel_gasto_energia'] = 2
        else:
            features['nivel_gasto_energia'] = 3
        
        # tiene_recoleccion: Tiene recolección de basuras (binario)
        features['tiene_recoleccion'] = 1 if tiene_recoleccion else 0
        
        # estado_recoleccion: Estado de recolección (1-3)
        if tiene_recoleccion:
            features['estado_recoleccion'] = 1
        else:
            features['estado_recoleccion'] = 2
        
        # requirio_atencion_medica: Requirió atención médica (binario)
        features['requirio_atencion_medica'] = 1 if requirio_atencion else 0
        
        # nivel_gasto_salud: Nivel de gasto en salud (0-3)
        if not requirio_atencion or gasto_salud <= 0:
            features['nivel_gasto_salud'] = 0
        elif gasto_salud <= 60000:
            features['nivel_gasto_salud'] = 1
        elif gasto_salud <= 150000:
            features['nivel_gasto_salud'] = 2
        else:
            features['nivel_gasto_salud'] = 3
        
        # log_gasto_salud: Log del gasto en salud
        if requirio_atencion and gasto_salud > 0:
            features['log_gasto_salud'] = np.log1p(gasto_salud)
        else:
            features['log_gasto_salud'] = 0.0
        
        return features
    
    def predict(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice vulnerabilidad económica
        
        Args:
            user_data: Diccionario con respuestas del usuario
            
        Returns:
            result: Diccionario con predicción y detalles
        """
        # Transformar input del usuario a features
        features_dict = self.transform_user_input(user_data)
        
        # Crear DataFrame con features en el orden correcto
        features_df = pd.DataFrame([features_dict])[self.feature_order]
        
        # Obtener probabilidades
        proba = self.model.predict_proba(features_df)[0]
        proba_vulnerable = proba[1]
        
        # Aplicar umbral optimizado
        is_vulnerable = int(proba_vulnerable >= self.threshold)
        
        # Crear resultado
        result = {
            'prediccion': is_vulnerable,
            'es_vulnerable': bool(is_vulnerable),
            'probabilidad_vulnerable': float(proba_vulnerable),
            'probabilidad_no_vulnerable': float(proba[0]),
            'umbral_usado': float(self.threshold),
            'nivel_riesgo': self._get_risk_level(proba_vulnerable),
            'mensaje': self._get_message(is_vulnerable, proba_vulnerable),
            'features_usadas': features_dict
        }
        
        return result
    
    def _get_risk_level(self, proba: float) -> str:
        """Determina nivel de riesgo basado en probabilidad"""
        if proba < 0.3:
            return 'bajo'
        elif proba < 0.5:
            return 'medio'
        elif proba < 0.7:
            return 'alto'
        else:
            return 'muy_alto'
    
    def _get_message(self, is_vulnerable: int, proba: float) -> str:
        """Genera mensaje interpretable"""
        if is_vulnerable:
            if proba >= 0.7:
                return f"Alto riesgo de vulnerabilidad económica ({proba*100:.1f}% de probabilidad). Se recomienda evaluar programas de apoyo social."
            else:
                return f"Situación de vulnerabilidad económica detectada ({proba*100:.1f}% de probabilidad). Se sugiere evaluación detallada."
        else:
            if proba >= 0.4:
                return f"Situación económica estable pero con factores de riesgo ({proba*100:.1f}% de probabilidad). Monitoreo recomendado."
            else:
                return f"Situación económica estable ({proba*100:.1f}% de probabilidad de vulnerabilidad)."
    
    def batch_predict(self, users_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predice para múltiples usuarios
        
        Args:
            users_data: Lista de diccionarios con datos de usuarios
            
        Returns:
            results: Lista de resultados
        """
        return [self.predict(user_data) for user_data in users_data]


# ======================
# FUNCIONES DE UTILIDAD
# ======================

def get_questionnaire_schema() -> Dict[str, Any]:
    """
    Retorna el esquema del cuestionario para el frontend
    Define qué preguntas hacer y cómo mapearlas
    """
    return {
        'demograficas': {
            'edad': {'tipo': 'numero', 'min': 15, 'max': 100, 'requerido': True},
            'sexo': {'tipo': 'seleccion', 'opciones': ['Hombre', 'Mujer'], 'requerido': True},
            'departamento': {'tipo': 'seleccion', 'opciones': 'departamentos_colombia', 'requerido': True},
            'mes_nacimiento': {'tipo': 'numero', 'min': 1, 'max': 12, 'requerido': False},
            'parentesco': {'tipo': 'seleccion', 'opciones': ['Jefe', 'Cónyuge', 'Hijo', 'Nieto', 'Otro pariente', 'Otro'], 'requerido': False}
        },
        'educacion': {
            'nivel_educativo': {'tipo': 'seleccion', 'opciones': ['Ninguno', 'Primaria', 'Secundaria', 'Media', 'Superior'], 'requerido': True},
            'años_educacion': {'tipo': 'numero', 'min': 0, 'max': 25, 'requerido': True}
        },
        'salud': {
            'tiene_salud': {'tipo': 'booleano', 'requerido': True},
            'tipo_salud': {'tipo': 'seleccion', 'opciones': ['Contributivo', 'Subsidiado', 'Especial', 'Ninguno'], 'requerido': True},
            'requirio_atencion_medica': {'tipo': 'booleano', 'requerido': True},
            'gasto_salud_ultimos_30_dias': {'tipo': 'numero', 'min': 0, 'max': 10000000, 'requerido': False}
        },
        'trabajo': {
            'empleo_formal': {'tipo': 'booleano', 'requerido': True},
            'ocupacion_codigo': {'tipo': 'seleccion', 'opciones': 'ocupaciones', 'requerido': False}
        },
        'vivienda': {
            'tipo_vivienda': {'tipo': 'seleccion', 'opciones': ['Casa', 'Apartamento', 'Cuarto', 'Otro'], 'requerido': True},
            'tenencia_vivienda': {'tipo': 'seleccion', 'opciones': ['Propia', 'Arriendo', 'Prestada', 'Otra'], 'requerido': True},
            'num_cuartos': {'tipo': 'numero', 'min': 1, 'max': 20, 'requerido': True},
            'num_personas_hogar': {'tipo': 'numero', 'min': 1, 'max': 20, 'requerido': True},
            'material_pisos': {'tipo': 'seleccion', 'opciones': ['Cemento', 'Baldosa', 'Madera', 'Tierra', 'Otro'], 'requerido': True}
        },
        'servicios': {
            'tiene_acueducto': {'tipo': 'booleano', 'requerido': True},
            'tiene_alcantarillado': {'tipo': 'booleano', 'requerido': True},
            'tiene_gas': {'tipo': 'booleano', 'requerido': True},
            'tiene_energia': {'tipo': 'booleano', 'requerido': True},
            'gasto_energia_mensual': {'tipo': 'numero', 'min': 0, 'max': 2000000, 'requerido': False},
            'tiene_recoleccion_basuras': {'tipo': 'booleano', 'requerido': True}
        },
        'hogar': {
            'tiene_hijos_menores': {'tipo': 'booleano', 'requerido': True},
            'num_menores_hogar': {'tipo': 'numero', 'min': 0, 'max': 10, 'requerido': False}
        }
    }


# ======================
# TESTING
# ======================

if __name__ == '__main__':
    print("="*80)
    print("TESTING PIPELINE DE PRODUCCIÓN")
    print("="*80)
    
    # Inicializar pipeline
    pipeline = VulnerabilityPipeline()
    
    # Ejemplo de usuario
    ejemplo_usuario = {
        'edad': 35,
        'sexo': 'mujer',
        'departamento': 11,  # Bogotá
        'nivel_educativo': 'secundaria',
        'años_educacion': 11,
        'tiene_salud': True,
        'tipo_salud': 'subsidiado',
        'requirio_atencion_medica': True,
        'gasto_salud_ultimos_30_dias': 80000,
        'empleo_formal': False,
        'tipo_vivienda': 'casa',
        'tenencia_vivienda': 'arriendo',
        'num_cuartos': 3,
        'num_personas_hogar': 5,
        'material_pisos': 'cemento',
        'tiene_acueducto': True,
        'tiene_alcantarillado': True,
        'tiene_gas': False,
        'tiene_energia': True,
        'gasto_energia_mensual': 450000,
        'tiene_recoleccion_basuras': True,
        'tiene_hijos_menores': True,
        'num_menores_hogar': 2
    }
    
    # Hacer predicción
    print("\n" + "="*80)
    print("PREDICCIÓN DE EJEMPLO")
    print("="*80)
    
    resultado = pipeline.predict(ejemplo_usuario)
    
    print(f"\n✓ Predicción completada")
    print(f"\n📊 RESULTADO:")
    print(f"  Es vulnerable: {resultado['es_vulnerable']}")
    print(f"  Probabilidad vulnerable: {resultado['probabilidad_vulnerable']:.4f}")
    print(f"  Nivel de riesgo: {resultado['nivel_riesgo']}")
    print(f"  Umbral usado: {resultado['umbral_usado']:.4f}")
    print(f"\n💬 MENSAJE:")
    print(f"  {resultado['mensaje']}")
    
    print(f"\n{'='*80}")
    print("✅ PIPELINE FUNCIONANDO CORRECTAMENTE")
    print(f"{'='*80}")

