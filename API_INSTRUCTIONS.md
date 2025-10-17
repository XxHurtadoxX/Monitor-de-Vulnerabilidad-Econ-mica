# 🚀 API de Vulnerabilidad Económica

API REST simple con FastAPI para predicción de vulnerabilidad económica.

## 📋 Prerequisitos

```bash
# Instalar dependencias (si no están instaladas)
pip install fastapi uvicorn pydantic requests
```

## ▶️ Iniciar la API

### Opción 1: Desde la raíz del proyecto (recomendado)

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Desde el archivo directamente

```bash
cd src/api
python main.py
```

### Opciones adicionales

```bash
# Sin auto-reload (para producción)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# En otro puerto
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8080

# Solo localhost (más seguro para desarrollo)
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

## 📡 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información general de la API |
| GET | `/health` | Health check - Verifica que la API esté corriendo |
| GET | `/questionnaire` | Obtiene el esquema del cuestionario (JSON) |
| POST | `/predict` | Realiza predicción de vulnerabilidad |
| GET | `/docs` | Documentación interactiva (Swagger UI) |
| GET | `/redoc` | Documentación alternativa (ReDoc) |

## 🧪 Probar la API

### 1. Verificar que está corriendo

```bash
# Desde el navegador
http://localhost:8000

# Desde curl
curl http://localhost:8000/health
```

### 2. Ejecutar suite de pruebas completa

```bash
python test_api.py
```

Este script prueba:
- ✅ Endpoint raíz
- ✅ Health check
- ✅ Obtener cuestionario
- ✅ Predicción caso vulnerable
- ✅ Predicción caso no vulnerable
- ✅ Predicción con datos mínimos

### 3. Pruebas manuales con curl

```bash
# Health check
curl http://localhost:8000/health

# Obtener cuestionario
curl http://localhost:8000/questionnaire

# Predicción (ejemplo completo)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "edad": 35,
    "sexo": "mujer",
    "nivel_educativo": "secundaria",
    "años_educacion": 11,
    "empleo_formal": false,
    "num_personas_hogar": 5
  }'
```

### 4. Pruebas con Python requests

```python
import requests

# Predicción
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "edad": 30,
        "sexo": "hombre",
        "empleo_formal": False
    }
)

resultado = response.json()
print(f"Es vulnerable: {resultado['es_vulnerable']}")
print(f"Probabilidad: {resultado['probabilidad_vulnerable']:.2%}")
```

## 📊 Ejemplo de Respuesta

```json
{
  "prediccion": 0,
  "es_vulnerable": false,
  "probabilidad_vulnerable": 0.4452,
  "probabilidad_no_vulnerable": 0.5548,
  "umbral_usado": 0.5263,
  "nivel_riesgo": "medio",
  "mensaje": "Situación económica estable pero con factores de riesgo (44.5% de probabilidad). Monitoreo recomendado."
}
```

## 🌐 Documentación Interactiva

Una vez que la API esté corriendo, visita:

- **Swagger UI**: http://localhost:8000/docs
  - Interfaz interactiva para probar endpoints
  - Documentación automática generada
  - Permite enviar requests directamente

- **ReDoc**: http://localhost:8000/redoc
  - Documentación alternativa más limpia
  - Mejor para lectura

## 🔧 Configuración CORS

La API está configurada para aceptar requests desde:
- `http://localhost:3000` (frontend React default)
- `http://localhost:3001`
- `http://127.0.0.1:3000`

Para agregar otros orígenes, edita `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://tu-dominio.com",  # Agregar aquí
    ],
    ...
)
```

## 🐛 Troubleshooting

### Error: "Pipeline no inicializado"

**Causa**: El modelo no se encuentra en `models/final_optimized_xgboost.pkl`

**Solución**: Ejecuta primero los scripts de entrenamiento:
```bash
python src/models/01_train_compare_models.py
python src/models/02_bayesian_optimization.py
```

### Error: "Module not found"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"

**Causa**: El puerto 8000 ya está siendo usado

**Solución**: 
```bash
# Usar otro puerto
uvicorn src.api.main:app --reload --port 8001

# O matar el proceso que usa el puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

## 📁 Estructura de Archivos

```
.
├── src/
│   ├── api/
│   │   └── main.py                      # ⭐ API principal (este archivo)
│   ├── pipeline/
│   │   ├── production_pipeline.py       # Pipeline de transformación
│   │   └── questionnaire_schema.json    # Esquema del cuestionario
│   └── models/
│       ├── 01_train_compare_models.py
│       └── 02_bayesian_optimization.py
├── models/
│   ├── final_optimized_xgboost.pkl     # Modelo entrenado
│   └── threshold_optimization.json      # Umbral óptimo
├── test_api.py                          # ⭐ Suite de pruebas
└── requirements.txt
```

## 🚀 Próximos Pasos

1. ✅ **API funcionando**: Ya está lista
2. ⏭️ **Conectar con frontend**: Usa los endpoints desde React
3. 🎨 **Ajustar estilos**: Personalizar interfaz
4. 🔍 **Verificar lógica**: Validar flujo de preguntas

## 📞 Soporte

Si tienes problemas:
1. Verifica que el modelo esté entrenado
2. Confirma que todas las dependencias estén instaladas
3. Revisa los logs de la API
4. Ejecuta `test_api.py` para diagnóstico

---

**Modelo**: XGBoost Optimizado | **ROC-AUC**: 0.8119 | **Recall**: 92%

