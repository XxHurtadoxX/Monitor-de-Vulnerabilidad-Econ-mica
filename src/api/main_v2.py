"""
API REST - Monitor de Vulnerabilidad Económica (VERSIÓN 2)
FastAPI para predicción de vulnerabilidad con nuevo target

NUEVO TARGET: Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)

Endpoints:
- POST /predict: Predicción de vulnerabilidad
- GET /questionnaire: Esquema del cuestionario
- GET /health: Health check
- GET /: Documentación básica

Autor: Data Science Team
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
from pathlib import Path
import sys

# Agregar directorio raíz al path para importar pipeline
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.pipeline.production_pipeline_v2 import VulnerabilityPipelineV2

# ======================
# CONFIGURACIÓN DE FASTAPI
# ======================

app = FastAPI(
    title="API de Vulnerabilidad Económica V2",
    description="Predicción de vulnerabilidad económica (Vulnerable + Pobre) basada en características socioeconómicas",
    version="2.0.0"
)

# Configurar CORS para frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://moneave.netlify.app",  # Frontend en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# INICIALIZAR PIPELINE
# ======================

try:
    pipeline = VulnerabilityPipelineV2()
    print("[OK] Pipeline V2 inicializado correctamente")
except Exception as e:
    print(f"[ERROR] No se pudo inicializar el pipeline: {str(e)}")
    pipeline = None

# ======================
# MODELOS PYDANTIC
# ======================

class UserInput(BaseModel):
    """Modelo de entrada para datos del usuario."""
    
    # Características personales
    edad: Optional[int] = Field(30, ge=0, le=100, description="Edad de la persona")
    sexo: Optional[str] = Field("hombre", description="Sexo: hombre o mujer")
    departamento: Optional[int] = Field(11, description="Código del departamento")
    area: Optional[int] = Field(1, description="Área: 1=Cabecera, 2=Resto")
    
    # Educación
    nivel_educativo: Optional[str] = Field("secundaria", description="Nivel educativo más alto")
    años_educacion: Optional[int] = Field(11, ge=0, le=25, description="Años de educación")
    
    # Salud
    tiene_salud: Optional[bool] = Field(True, description="¿Tiene afiliación a salud?")
    tipo_salud: Optional[str] = Field("subsidiado", description="Tipo de afiliación a salud")
    tiene_hijos_menores: Optional[bool] = Field(False, description="¿Tiene hijos menores de 18 años?")
    requirio_atencion_medica: Optional[bool] = Field(False, description="¿Requirió atención médica en últimos 30 días?")
    gasto_salud_ultimos_30_dias: Optional[int] = Field(0, ge=0, description="Gasto en salud en últimos 30 días")
    
    # Trabajo
    ocupacion_codigo: Optional[int] = Field(1, ge=1, le=9, description="Código de ocupación")
    empleo_formal: Optional[bool] = Field(False, description="¿Tiene empleo formal?")
    posicion_ocupacional: Optional[int] = Field(1, ge=1, le=7, description="Posición ocupacional")
    ingreso_mensual: Optional[int] = Field(1000000, ge=0, description="Ingreso mensual en COP")
    
    # Vivienda
    tipo_vivienda: Optional[str] = Field("casa", description="Tipo de vivienda")
    tenencia_vivienda: Optional[str] = Field("arriendo", description="Tenencia de vivienda")
    num_cuartos: Optional[int] = Field(3, ge=1, le=20, description="Número de cuartos")
    num_personas_hogar: Optional[int] = Field(4, ge=1, le=20, description="Número de personas en el hogar")
    material_pisos: Optional[str] = Field("cemento", description="Material de los pisos")
    parentesco_jefe_hogar: Optional[int] = Field(1, ge=1, le=12, description="Parentesco con jefe de hogar")
    estado_civil: Optional[int] = Field(1, ge=1, le=6, description="Estado civil")
    
    # Servicios públicos
    tiene_acueducto: Optional[bool] = Field(True, description="¿Tiene acueducto?")
    tiene_alcantarillado: Optional[bool] = Field(True, description="¿Tiene alcantarillado?")
    tiene_gas: Optional[bool] = Field(False, description="¿Tiene gas natural?")
    tiene_recoleccion_basuras: Optional[bool] = Field(True, description="¿Tiene recolección de basuras?")
    
    # Gastos
    gasto_alimentos: Optional[int] = Field(200000, ge=0, description="Gasto mensual en alimentos")
    gasto_transporte: Optional[int] = Field(100000, ge=0, description="Gasto mensual en transporte")
    gasto_otros: Optional[int] = Field(150000, ge=0, description="Otros gastos mensuales")
    gasto_energia: Optional[int] = Field(50000, ge=0, description="Gasto mensual en energía eléctrica")

class PredictionResponse(BaseModel):
    """Modelo de respuesta para predicción."""
    prediccion: int = Field(..., description="Predicción: 0=No vulnerable, 1=Vulnerable")
    es_vulnerable: bool = Field(..., description="¿Es vulnerable económicamente?")
    probabilidad_vulnerable: float = Field(..., description="Probabilidad de ser vulnerable (0-1)")
    probabilidad_no_vulnerable: float = Field(..., description="Probabilidad de no ser vulnerable (0-1)")
    umbral_usado: float = Field(..., description="Umbral usado para la clasificación")
    nivel_riesgo: str = Field(..., description="Nivel de riesgo: bajo, medio, alto")
    mensaje: str = Field(..., description="Mensaje interpretativo")
    modelo_version: str = Field(..., description="Versión del modelo")
    target_definition: str = Field(..., description="Definición del target")

# ======================
# ENDPOINTS
# ======================

@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API."""
    return {
        "message": "API de Vulnerabilidad Económica V2",
        "version": "2.0.0",
        "target": "Vulnerable + Pobre (ingreso <= 1.5x línea de pobreza)",
        "description": "Predicción de vulnerabilidad económica basada en características socioeconómicas",
        "endpoints": {
            "predict": "POST /predict - Realizar predicción",
            "questionnaire": "GET /questionnaire - Esquema del cuestionario",
            "health": "GET /health - Estado de la API",
            "model_info": "GET /model-info - Información del modelo"
        }
    }

@app.get("/health")
async def health_check():
    """Health check para verificar el estado de la API."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline no inicializado")
    
    return {
        "status": "ok",
        "model_version": "v2",
        "target": "Vulnerable + Pobre",
        "pipeline_status": "activo"
    }

@app.get("/questionnaire")
async def get_questionnaire():
    """Obtener el esquema del cuestionario."""
    try:
        # Cargar esquema del cuestionario
        schema_path = Path("src/pipeline/questionnaire_schema.json")
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        else:
            # Esquema por defecto si no existe el archivo
            schema = {
                "title": "Cuestionario de Vulnerabilidad Económica V2",
                "description": "Formulario para evaluar vulnerabilidad económica",
                "sections": [
                    {
                        "id": "personal",
                        "title": "Información Personal",
                        "questions": [
                            {"id": "edad", "type": "number", "label": "Edad", "required": True},
                            {"id": "sexo", "type": "select", "label": "Sexo", "options": ["hombre", "mujer"]},
                            {"id": "departamento", "type": "number", "label": "Departamento", "required": True}
                        ]
                    }
                ]
            }
        
        return schema
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando cuestionario: {str(e)}")

@app.get("/model-info")
async def get_model_info():
    """Obtener información del modelo."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline no inicializado")
    
    try:
        model_info = pipeline.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información del modelo: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_vulnerability(user_input: UserInput):
    """
    Realizar predicción de vulnerabilidad económica.
    
    Args:
        user_input: Datos del usuario para la predicción
        
    Returns:
        Predicción de vulnerabilidad con métricas y mensaje interpretativo
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline no inicializado")
    
    try:
        # Convertir input a diccionario
        user_data = user_input.dict()
        
        # Realizar predicción
        result = pipeline.predict(user_data)
        
        # Verificar si hubo error
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return PredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

# ======================
# MANEJO DE ERRORES
# ======================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint no encontrado", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Error interno del servidor", "detail": str(exc)}

# ======================
# INICIALIZACIÓN
# ======================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
