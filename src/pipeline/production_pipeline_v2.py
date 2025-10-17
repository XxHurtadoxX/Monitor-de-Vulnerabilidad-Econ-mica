#!/usr/bin/env python3
"""
Pipeline de Producción (VERSIÓN 2 - NUEVO TARGET)
Monitor de Vulnerabilidad Económica - Colombia

NUEVO TARGET: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)
- Clase 0: Ingreso > 1.5x línea de pobreza (> $772,500)
- Clase 1: Ingreso ≤ 1.5x línea de pobreza (≤ $772,500)

Autor: Data Science Team
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any, List
import json


class VulnerabilityPipelineV2:
    """
    Pipeline de producción para el modelo de vulnerabilidad económica v2.
    
    Nuevo target: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)
    """
    
    def __init__(self, model_dir: str = "data/processed/modeling_v2/results"):
        """
        Inicializar el pipeline con el modelo entrenado.
        
        Args:
            model_dir: Directorio donde están los archivos del modelo
        """
        self.model_dir = Path(model_dir)
        self.model = None
        self.feature_names = None
        self.threshold = None
        self.metadata = None
        
        self._load_model()
        self._load_metadata()
    
    def _load_model(self):
        """Cargar el modelo entrenado y sus componentes."""
        try:
            # Cargar modelo
            with open(self.model_dir / 'final_optimized_xgboost_v2.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            # Cargar nombres de features
            with open(self.model_dir.parent / 'feature_names.txt', 'r') as f:
                self.feature_names = [line.strip() for line in f.readlines()]
            
            # Cargar umbral optimizado
            with open(self.model_dir / 'threshold_optimization_v2.json', 'r') as f:
                threshold_data = json.load(f)
                self.threshold = threshold_data['umbral_optimo']
            
            print(f"[OK] Pipeline V2 inicializado:")
            print(f"  Modelo: XGBoost optimizado")
            print(f"  Features: {len(self.feature_names)}")
            print(f"  Umbral: {self.threshold:.4f}")
            
        except Exception as e:
            raise RuntimeError(f"Error cargando modelo: {str(e)}")
    
    def _load_metadata(self):
        """Cargar metadatos del modelo."""
        try:
            with open(self.model_dir.parent / 'metadata.json', 'r') as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"[WARN] No se pudieron cargar metadatos: {str(e)}")
            self.metadata = {}
    
    def transform_user_input(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transformar datos del usuario al formato esperado por el modelo.
        
        Args:
            user_data: Diccionario con los datos del usuario
            
        Returns:
            Diccionario con las features transformadas
        """
        features = {}
        
        # ======================
        # CARACTERÍSTICAS PERSONALES
        # ======================
        # P6040: Edad
        features['P6040'] = user_data.get('edad', 30)
        
        # P5020: Sexo (1=Hombre, 2=Mujer)
        sexo = user_data.get('sexo', 'hombre').lower()
        features['P5020'] = 1 if sexo == 'hombre' else 2
        
        # DPTO: Departamento (código numérico)
        features['DPTO'] = user_data.get('departamento', 11)  # Bogotá por defecto
        
        # AREA: Área (1=Cabecera, 2=Resto)
        features['AREA'] = user_data.get('area', 1)  # Cabecera por defecto
        
        # ======================
        # EDUCACIÓN
        # ======================
        # P6160: Nivel educativo más alto alcanzado (1 o 2)
        nivel_educativo = user_data.get('nivel_educativo', 'secundaria').lower()
        if nivel_educativo in ['ninguno', 'preescolar', 'primaria']:
            features['P6160'] = 1
        else:
            features['P6160'] = 2
        
        # P6170: Años de educación (1 o 2)
        años_edu = user_data.get('años_educacion', 11)
        features['P6170'] = 2 if años_edu >= 11 else 1
        
        # ======================
        # SALUD
        # ======================
        # P6090: Afiliación a salud (1=Sí, 2=No)
        tiene_salud = user_data.get('tiene_salud', True)
        features['P6090'] = 1 if tiene_salud else 2
        
        # P6100: Tipo de afiliación (1=Contributivo, 2=Subsidiado, 3=Especial, 4=No afiliado)
        tipo_salud_map = {'contributivo': 1, 'subsidiado': 2, 'especial': 3, 'ninguno': 4}
        features['P6100'] = tipo_salud_map.get(user_data.get('tipo_salud', '').lower(), 2)
        
        # P6110: Mortalidad infantil (-1=No aplica, 1=Sí, 2=No)
        tiene_hijos_menores = user_data.get('tiene_hijos_menores', False)
        if not tiene_hijos_menores:
            features['P6110'] = -1
        else:
            features['P6110'] = 2  # Asumimos no ha tenido fallecimientos
        
        # ======================
        # TRABAJO
        # ======================
        # P6240: Ocupación principal (1-9 categorías)
        features['P6240'] = user_data.get('ocupacion_codigo', 1)
        
        # P6250: Tipo de empleo (1=Formal, 2=Informal)
        es_formal = user_data.get('empleo_formal', False)
        features['P6250'] = 1 if es_formal else 2
        
        # P6430: Posición ocupacional (1-7)
        features['P6430'] = user_data.get('posicion_ocupacional', 1)
        
        # ======================
        # VIVIENDA
        # ======================
        # P5000: Número de cuartos
        features['P5000'] = user_data.get('num_cuartos', 3)
        
        # P5010: Número de personas en el hogar
        features['P5010'] = user_data.get('num_personas_hogar', 4)
        
        # P5030: Material de pisos (1=Otro, 2=Baldosa, 3=Madera, 4=Otro)
        material_pisos = user_data.get('material_pisos', 'cemento').lower()
        material_map = {'cemento': 1, 'baldosa': 2, 'madera': 3, 'tierra': 1}
        features['P5030'] = material_map.get(material_pisos, 1)
        
        # P5040: Tipo de vivienda (1=Casa, 2=Apartamento, 3=Otro)
        tipo_vivienda = user_data.get('tipo_vivienda', 'casa').lower()
        tipo_map = {'casa': 1, 'apartamento': 2, 'cuarto': 3}
        features['P5040'] = tipo_map.get(tipo_vivienda, 1)
        
        # P5070: Tenencia de vivienda (1=Propia, 2=Arriendo, 3=Otro)
        tenencia_vivienda = user_data.get('tenencia_vivienda', 'arriendo').lower()
        tenencia_map = {'propia': 1, 'arriendo': 2, 'usufructo': 3}
        features['P5070'] = tenencia_map.get(tenencia_vivienda, 2)
        
        # ======================
        # SERVICIOS PÚBLICOS
        # ======================
        # P5080: Acueducto (1=Sí, 2=No)
        features['P5080'] = 1 if user_data.get('tiene_acueducto', True) else 2
        
        # P5090: Alcantarillado (1=Sí, 2=No)
        features['P5090'] = 1 if user_data.get('tiene_alcantarillado', True) else 2
        
        # P6016: Gas natural (1=Sí, 2=No)
        features['P6016'] = 1 if user_data.get('tiene_gas', False) else 2
        
        # ======================
        # VARIABLES ADICIONALES
        # ======================
        # P6050: Parentesco con jefe de hogar (1-12)
        features['P6050'] = user_data.get('parentesco_jefe_hogar', 1)
        
        # P6080: Estado civil (1-6)
        features['P6080'] = user_data.get('estado_civil', 1)
        
        # P6920: Ingreso laboral (variable clave)
        # Esta es la variable más importante según el modelo
        ingreso = user_data.get('ingreso_mensual', 1000000)
        features['P6920'] = ingreso
        
        # Variables de gastos (P6585S1, P6585S2, P6585S3)
        features['P6585S1'] = user_data.get('gasto_alimentos', 200000)
        features['P6585S2'] = user_data.get('gasto_transporte', 100000)
        features['P6585S3'] = user_data.get('gasto_otros', 150000)
        
        # ======================
        # FEATURES ENGINEERED
        # ======================
        # edad_grupo: Grupos de edad
        edad = features['P6040']
        if edad < 18:
            features['edad_grupo'] = 1
        elif edad < 30:
            features['edad_grupo'] = 2
        elif edad < 45:
            features['edad_grupo'] = 3
        elif edad < 60:
            features['edad_grupo'] = 4
        else:
            features['edad_grupo'] = 5
        
        # hacinamiento_cat: Categoría de hacinamiento
        num_personas = features['P5010']
        num_cuartos = features['P5000']
        if num_cuartos > 0:
            hacinamiento = num_personas / num_cuartos
        else:
            hacinamiento = 0
        
        if hacinamiento <= 1:
            features['hacinamiento_cat'] = 1
        elif hacinamiento <= 2:
            features['hacinamiento_cat'] = 2
        elif hacinamiento <= 3:
            features['hacinamiento_cat'] = 3
        else:
            features['hacinamiento_cat'] = 4
        
        # servicios_score: Score de servicios públicos
        servicios = 0
        servicios += 1 if features['P5080'] == 1 else 0
        servicios += 1 if features['P5090'] == 1 else 0
        servicios += 1 if features['P6016'] == 1 else 0
        features['servicios_score'] = servicios
        
        # es_formal: Formalidad laboral
        features['es_formal'] = 1 if features['P6250'] == 1 else 0
        
        # Variables de energía eléctrica (P5100 transformada)
        gasto_energia = user_data.get('gasto_energia', 0)
        features['tiene_energia'] = 1 if gasto_energia > 0 else 0
        
        if gasto_energia <= 50000:
            features['nivel_gasto_energia'] = 1
        elif gasto_energia <= 150000:
            features['nivel_gasto_energia'] = 2
        else:
            features['nivel_gasto_energia'] = 3
        
        # Variables de recolección basuras (P5110 transformada)
        tiene_recoleccion = user_data.get('tiene_recoleccion_basuras', True)
        features['tiene_recoleccion'] = 1 if tiene_recoleccion else 0
        
        if tiene_recoleccion:
            features['estado_recoleccion'] = 1  # Regular
        else:
            features['estado_recoleccion'] = 3  # No hay
        
        # Variables de atención médica (P6120 transformada)
        requirio_atencion = user_data.get('requirio_atencion_medica', False)
        gasto_salud = user_data.get('gasto_salud_ultimos_30_dias', 0)
        
        features['requirio_atencion_medica'] = 1 if requirio_atencion else 0
        
        if gasto_salud <= 60000:
            features['nivel_gasto_salud'] = 1
        elif gasto_salud <= 150000:
            features['nivel_gasto_salud'] = 2
        else:
            features['nivel_gasto_salud'] = 3
        
        # log_gasto_salud: Log del gasto en salud
        if gasto_salud > 0:
            features['log_gasto_salud'] = np.log1p(gasto_salud)
        else:
            features['log_gasto_salud'] = 0.0
        
        return features
    
    def predict(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realizar predicción de vulnerabilidad económica.
        
        Args:
            user_data: Datos del usuario
            
        Returns:
            Diccionario con la predicción y métricas
        """
        try:
            # Transformar datos del usuario
            features = self.transform_user_input(user_data)
            
            # Crear DataFrame con las features en el orden correcto
            feature_df = pd.DataFrame([features])[self.feature_names]
            
            # Realizar predicción
            probability = self.model.predict_proba(feature_df)[0, 1]
            
            # Aplicar umbral optimizado
            prediction = 1 if probability >= self.threshold else 0
            
            # Determinar nivel de riesgo
            if probability < 0.3:
                risk_level = "bajo"
            elif probability < 0.6:
                risk_level = "medio"
            else:
                risk_level = "alto"
            
            # Generar mensaje interpretativo
            if prediction == 1:
                if risk_level == "alto":
                    message = f"Situación económica crítica ({probability*100:.1f}% de probabilidad de vulnerabilidad). Se recomienda atención prioritaria."
                elif risk_level == "medio":
                    message = f"Situación económica en riesgo ({probability*100:.1f}% de probabilidad de vulnerabilidad). Monitoreo recomendado."
                else:
                    message = f"Situación económica vulnerable ({probability*100:.1f}% de probabilidad de vulnerabilidad). Prevención recomendada."
            else:
                if risk_level == "bajo":
                    message = f"Situación económica estable ({probability*100:.1f}% de probabilidad de vulnerabilidad)."
                else:
                    message = f"Situación económica relativamente estable ({probability*100:.1f}% de probabilidad de vulnerabilidad)."
            
            return {
                "prediccion": prediction,
                "es_vulnerable": prediction == 1,
                "probabilidad_vulnerable": float(probability),
                "probabilidad_no_vulnerable": float(1 - probability),
                "umbral_usado": float(self.threshold),
                "nivel_riesgo": risk_level,
                "mensaje": message,
                "modelo_version": "v2",
                "target_definition": "Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)"
            }
            
        except Exception as e:
            return {
                "error": f"Error en la predicción: {str(e)}",
                "prediccion": 0,
                "es_vulnerable": False,
                "probabilidad_vulnerable": 0.0,
                "probabilidad_no_vulnerable": 1.0,
                "umbral_usado": float(self.threshold),
                "nivel_riesgo": "indeterminado",
                "mensaje": "No se pudo realizar la predicción debido a un error técnico."
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo."""
        return {
            "version": "v2",
            "target_definition": "Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)",
            "model_type": "XGBoost Optimizado",
            "n_features": len(self.feature_names),
            "threshold": float(self.threshold),
            "metadata": self.metadata
        }
