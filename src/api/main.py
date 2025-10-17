"""
API REST - Monitor de Vulnerabilidad Económica
FastAPI simple y funcional para predicción de vulnerabilidad

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

from src.pipeline.production_pipeline import VulnerabilityPipeline

# ======================
# CONFIGURACIÓN DE FASTAPI
# ======================

app = FastAPI(
    title="API de Vulnerabilidad Económica",
    description="Predicción de vulnerabilidad económica basada en características socioeconómicas",
    version="1.0.0"
)

# Configurar CORS para frontend React
# URLs permitidas para acceder a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://moneave.netlify.app",  # Frontend en producción - SIN barra final
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar pipeline global
try:
    pipeline = VulnerabilityPipeline()
    print("[OK] Pipeline cargado exitosamente")
except Exception as e:
    print(f"[ERROR] Error cargando pipeline: {e}")
    pipeline = None

# ======================
# MODELOS PYDANTIC
# ======================

class UserInput(BaseModel):
    """Modelo de entrada del usuario con todos los campos opcionales"""
    
    # Demográficas
    edad: Optional[int] = Field(default=30, ge=15, le=100, description="Edad en años")
    sexo: Optional[str] = Field(default="hombre", description="Sexo: hombre o mujer")
    departamento: Optional[int] = Field(default=11, description="Código DANE del departamento")
    mes_nacimiento: Optional[int] = Field(default=6, ge=1, le=12, description="Mes de nacimiento")
    parentesco: Optional[str] = Field(default="jefe", description="Parentesco con jefe de hogar")
    
    # Educación
    nivel_educativo: Optional[str] = Field(default="secundaria", description="Nivel educativo alcanzado")
    años_educacion: Optional[int] = Field(default=11, ge=0, le=25, description="Años de educación formal")
    
    # Salud
    tiene_salud: Optional[bool] = Field(default=True, description="Tiene afiliación a salud")
    tipo_salud: Optional[str] = Field(default="subsidiado", description="Tipo de afiliación: contributivo, subsidiado, especial, ninguno")
    requirio_atencion_medica: Optional[bool] = Field(default=False, description="Requirió atención médica últimos 30 días")
    gasto_salud_ultimos_30_dias: Optional[int] = Field(default=0, ge=0, description="Gasto en salud últimos 30 días (COP)")
    tiene_hijos_menores: Optional[bool] = Field(default=False, description="Tiene hijos menores de 18 años")
    
    # Trabajo
    empleo_formal: Optional[bool] = Field(default=False, description="Tiene empleo formal con contrato")
    ocupacion_codigo: Optional[int] = Field(default=1, description="Código de ocupación")
    posicion_ocupacional: Optional[int] = Field(default=1, description="Posición ocupacional")
    rama_actividad: Optional[int] = Field(default=2, description="Rama de actividad económica")
    
    # Vivienda
    tipo_vivienda: Optional[str] = Field(default="casa", description="Tipo de vivienda: casa, apartamento, cuarto, otro")
    tenencia_vivienda: Optional[str] = Field(default="arriendo", description="Tenencia: propia, arriendo, prestada, otra")
    num_cuartos: Optional[int] = Field(default=3, ge=1, le=20, description="Número de cuartos")
    num_personas_hogar: Optional[int] = Field(default=4, ge=1, le=20, description="Número de personas en el hogar")
    material_pisos: Optional[str] = Field(default="cemento", description="Material predominante de pisos")
    
    # Servicios públicos
    tiene_acueducto: Optional[bool] = Field(default=True, description="Tiene servicio de acueducto")
    tiene_alcantarillado: Optional[bool] = Field(default=True, description="Tiene servicio de alcantarillado")
    tiene_gas: Optional[bool] = Field(default=False, description="Tiene servicio de gas")
    tiene_energia: Optional[bool] = Field(default=True, description="Tiene servicio de energía eléctrica")
    gasto_energia_mensual: Optional[int] = Field(default=500000, ge=0, description="Gasto mensual en energía (COP)")
    tiene_recoleccion_basuras: Optional[bool] = Field(default=True, description="Tiene servicio de recolección de basuras")
    
    # Hogar
    num_menores_hogar: Optional[int] = Field(default=0, ge=0, le=10, description="Número de menores de 18 años en el hogar")
    
    # Ubicación geográfica
    area_codigo: Optional[int] = Field(default=11, description="Código de área")

    class Config:
        schema_extra = {
            "example": {
                "edad": 35,
                "sexo": "mujer",
                "departamento": 11,
                "nivel_educativo": "secundaria",
                "años_educacion": 11,
                "tiene_salud": True,
                "tipo_salud": "subsidiado",
                "requirio_atencion_medica": True,
                "gasto_salud_ultimos_30_dias": 80000,
                "empleo_formal": False,
                "tipo_vivienda": "casa",
                "tenencia_vivienda": "arriendo",
                "num_cuartos": 3,
                "num_personas_hogar": 5,
                "material_pisos": "cemento",
                "tiene_acueducto": True,
                "tiene_alcantarillado": True,
                "tiene_gas": False,
                "tiene_energia": True,
                "gasto_energia_mensual": 450000,
                "tiene_recoleccion_basuras": True,
                "tiene_hijos_menores": True,
                "num_menores_hogar": 2
            }
        }


class PredictionResponse(BaseModel):
    """Modelo de respuesta de predicción"""
    prediccion: int = Field(description="0=No vulnerable, 1=Vulnerable")
    es_vulnerable: bool = Field(description="True si es vulnerable")
    probabilidad_vulnerable: float = Field(description="Probabilidad de ser vulnerable (0-1)")
    probabilidad_no_vulnerable: float = Field(description="Probabilidad de no ser vulnerable (0-1)")
    umbral_usado: float = Field(description="Umbral de decisión usado")
    nivel_riesgo: str = Field(description="Nivel de riesgo: bajo, medio, alto, muy_alto")
    mensaje: str = Field(description="Mensaje interpretativo para el usuario")


# ======================
# ENDPOINTS
# ======================

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "nombre": "API de Vulnerabilidad Económica",
        "version": "1.0.0",
        "descripcion": "Predicción de vulnerabilidad económica basada en características socioeconómicas",
        "endpoints": {
            "/health": "Health check",
            "/questionnaire": "Obtener esquema del cuestionario",
            "/predict": "Realizar predicción (POST)",
            "/docs": "Documentación interactiva Swagger",
            "/redoc": "Documentación ReDoc"
        },
        "modelo": {
            "tipo": "XGBoost Optimizado",
            "roc_auc": 0.8119,
            "recall": 0.92,
            "umbral": 0.5263
        }
    }


@app.get("/health")
async def health_check():
    """Health check - Verifica que la API esté funcionando"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline no inicializado")
    
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "pipeline_loaded": pipeline is not None
    }


@app.get("/questionnaire")
async def get_questionnaire():
    """Retorna el esquema del cuestionario para el frontend"""
    try:
        schema_path = Path(__file__).parent.parent / "pipeline" / "questionnaire_schema.json"
        
        if not schema_path.exists():
            raise HTTPException(status_code=404, detail="Esquema del cuestionario no encontrado")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        return schema
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando cuestionario: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict_vulnerability(user_input: UserInput):
    """
    Realiza predicción de vulnerabilidad económica
    
    Args:
        user_input: Datos del usuario (UserInput)
        
    Returns:
        PredictionResponse: Resultado de la predicción
    """
    # Verificar que el pipeline esté cargado
    if pipeline is None:
        raise HTTPException(
            status_code=503, 
            detail="Pipeline no disponible. Contacte al administrador."
        )
    
    try:
        # Convertir input Pydantic a diccionario
        user_data = user_input.dict()
        
        # Hacer predicción usando el pipeline
        resultado = pipeline.predict(user_data)
        
        # Retornar resultado (sin features_usadas para mantener respuesta limpia)
        return {
            "prediccion": resultado["prediccion"],
            "es_vulnerable": resultado["es_vulnerable"],
            "probabilidad_vulnerable": resultado["probabilidad_vulnerable"],
            "probabilidad_no_vulnerable": resultado["probabilidad_no_vulnerable"],
            "umbral_usado": resultado["umbral_usado"],
            "nivel_riesgo": resultado["nivel_riesgo"],
            "mensaje": resultado["mensaje"]
        }
    
    except Exception as e:
        # Manejo de errores
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Error al procesar predicción",
                "mensaje": str(e),
                "tipo": type(e).__name__
            }
        )


# ======================
# EVENTOS DE INICIO/CIERRE
# ======================

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la API"""
    print("\n" + "="*80)
    print("🚀 API DE VULNERABILIDAD ECONÓMICA INICIADA")
    print("="*80)
    print(f"✓ Pipeline cargado: {pipeline is not None}")
    print(f"✓ Endpoints disponibles:")
    print(f"   GET  /            - Información de la API")
    print(f"   GET  /health      - Health check")
    print(f"   GET  /questionnaire - Esquema del cuestionario")
    print(f"   POST /predict     - Predicción de vulnerabilidad")
    print(f"   GET  /docs        - Documentación Swagger")
    print(f"✓ CORS habilitado para localhost:3000")
    print("="*80 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al cerrar la API"""
    print("\n" + "="*80)
    print("🛑 API DETENIDA")
    print("="*80 + "\n")


# ======================
# EJECUCIÓN DIRECTA
# ======================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

