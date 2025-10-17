# 🚀 Inicio Rápido - Sistema Completo

Monitor de Vulnerabilidad Económica - Sistema completo funcionando en 3 pasos.

## ⚡ Inicio en 3 Pasos

### Paso 1: Iniciar la API (Backend)

```bash
# Terminal 1 - Desde la raíz del proyecto
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

✅ La API debería estar corriendo en: http://localhost:8000  
✅ Documentación: http://localhost:8000/docs

### Paso 2: Iniciar el Frontend

```bash
# Terminal 2 - Desde la raíz del proyecto
cd frontend
npm install  # Solo la primera vez
npm start
```

✅ El frontend se abrirá automáticamente en: http://localhost:3000

### Paso 3: Probar el Sistema

1. Abre http://localhost:3000 en tu navegador
2. Completa el formulario paso a paso (7 pasos)
3. Haz clic en "Analizar"
4. ¡Observa los resultados!

---

## 📋 Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

- ✅ **Python 3.9+** con pip
- ✅ **Node.js 16+** con npm
- ✅ **Modelo entrenado**: `models/final_optimized_xgboost.pkl`

### Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

Las dependencias principales incluyen:
- fastapi, uvicorn (API)
- pandas, numpy, scikit-learn (Data Science)
- xgboost (Modelo)

### Verificar que el Modelo Existe

```bash
# Windows
dir models\final_optimized_xgboost.pkl

# Linux/Mac
ls -la models/final_optimized_xgboost.pkl
```

Si no existe, entrena el modelo primero:

```bash
python src/models/01_train_compare_models.py
python src/models/02_bayesian_optimization.py
```

---

## 🧪 Probar la API

### Opción 1: Navegador

Abre http://localhost:8000/health

Deberías ver:
```json
{
  "status": "ok",
  "message": "API funcionando correctamente",
  "pipeline_loaded": true
}
```

### Opción 2: Script de Pruebas

```bash
python test_api.py
```

Esto ejecuta 6 pruebas automáticas:
- ✅ Health check
- ✅ Obtener cuestionario
- ✅ Predicción caso vulnerable
- ✅ Predicción caso no vulnerable
- ✅ Predicción con datos mínimos

### Opción 3: curl

```bash
curl http://localhost:8000/health
```

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│                   USUARIO (Navegador)               │
│              http://localhost:3000                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ POST /predict (JSON)
                  │
┌─────────────────▼───────────────────────────────────┐
│            FRONTEND (React + TypeScript)            │
│  • Formulario de 7 pasos                           │
│  • Validaciones de inputs                          │
│  • Animaciones (Framer Motion)                     │
│  • Diseño fondo negro + contraste alto            │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP Request (axios)
                  │
┌─────────────────▼───────────────────────────────────┐
│              API REST (FastAPI)                     │
│         http://localhost:8000                       │
│  • CORS habilitado                                 │
│  • Validaciones Pydantic                           │
│  • Manejo de errores                               │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Llama a pipeline.predict()
                  │
┌─────────────────▼───────────────────────────────────┐
│       PIPELINE DE PRODUCCIÓN (Python)               │
│  • Mapeo de inputs a features GEIH                 │
│  • Feature engineering                             │
│  • Transformaciones (scaling, encoding)            │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Predicción
                  │
┌─────────────────▼───────────────────────────────────┐
│         MODELO ML (XGBoost Optimizado)              │
│  • ROC-AUC: 0.8119                                 │
│  • Recall: 92%                                     │
│  • Umbral optimizado: 0.5263                       │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ Resultado
                  │
┌─────────────────▼───────────────────────────────────┐
│            RESPUESTA AL USUARIO                     │
│  • Predicción: 0 o 1                               │
│  • Probabilidades                                  │
│  • Nivel de riesgo                                 │
│  • Mensaje interpretativo                          │
└─────────────────────────────────────────────────────┘
```

---

## 🗂️ Archivos Principales

### Backend (API)
```
src/api/main.py                          # ⭐ API FastAPI (150 líneas)
src/pipeline/production_pipeline.py      # Pipeline de transformación
src/pipeline/questionnaire_schema.json   # Esquema del cuestionario
test_api.py                              # Suite de pruebas
```

### Frontend
```
frontend/src/
├── components/
│   ├── VulnerabilityForm.tsx           # ⭐ Formulario principal
│   ├── FormSteps.tsx                   # ⭐ 7 pasos del formulario
│   ├── ResultDisplay.tsx               # Pantalla de resultados
│   ├── LoadingSpinner.tsx              # Spinner de carga
│   ├── Header.tsx                      # Header con logo
│   └── Footer.tsx                      # Footer
├── services/api.ts                      # Cliente HTTP (axios)
└── types/api.ts                         # Tipos TypeScript
```

### Modelos y Datos
```
models/
├── final_optimized_xgboost.pkl         # ⭐ Modelo entrenado
├── threshold_optimization.json          # Umbral óptimo
└── best_base_model_xgboost.pkl         # Modelo base

data/processed/modeling/
├── X_train.csv                          # Datos de entrenamiento
├── X_test.csv                           # Datos de prueba
├── y_train.csv                          # Labels entrenamiento
├── y_test.csv                           # Labels prueba
└── feature_names.txt                    # Nombres de features
```

---

## 🎯 Características del Sistema

### ✅ Backend (API)
- ✓ FastAPI con 4 endpoints
- ✓ CORS habilitado para React
- ✓ Validaciones con Pydantic
- ✓ Manejo de errores robusto
- ✓ Documentación automática (Swagger)
- ✓ Pipeline de producción integrado
- ✓ Tests automatizados (6 tests)

### ✅ Frontend
- ✓ Formulario de 7 pasos intuitivo
- ✓ Validaciones exhaustivas en cada paso
- ✓ Campos condicionales (aparecen según respuestas)
- ✓ Diseño fondo negro + contraste alto
- ✓ Animaciones suaves (Framer Motion)
- ✓ Barra de progreso visual
- ✓ Mensajes de error claros
- ✓ Visualización de resultados atractiva
- ✓ Responsive (móviles y tablets)

### ✅ Modelo ML
- ✓ XGBoost optimizado con Búsqueda Bayesiana
- ✓ ROC-AUC: 0.8119
- ✓ Recall: 92% (detecta 92% de vulnerables)
- ✓ Umbral optimizado: 0.5263
- ✓ Pipeline de transformación robusto
- ✓ Manejo de features calculadas

---

## 🐛 Troubleshooting

### Problema: API no inicia

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solución**:
```bash
pip install -r requirements.txt
```

---

### Problema: Modelo no encontrado

**Error**: `FileNotFoundError: models/final_optimized_xgboost.pkl`

**Solución**:
```bash
# Entrenar el modelo
python src/models/01_train_compare_models.py
python src/models/02_bayesian_optimization.py
```

---

### Problema: Frontend no conecta con API

**Error**: `Network Error` o `CORS Error`

**Solución**:
1. Verifica que la API esté corriendo en puerto 8000
2. Verifica que el frontend esté en puerto 3000
3. Revisa la consola de la API para ver si llegan requests

---

### Problema: Puerto ya en uso

**Error**: `Address already in use: 8000` o `Port 3000 is already in use`

**Solución Windows**:
```bash
# Encontrar proceso que usa el puerto
netstat -ano | findstr :8000
# Matar proceso
taskkill /PID <PID> /F
```

**Solución Linux/Mac**:
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9
```

---

### Problema: Frontend no compila

**Error**: `Cannot find module` o errores de TypeScript

**Solución**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📊 Validaciones del Formulario

El formulario previene inputs erróneos con estas validaciones:

| Campo | Validación |
|-------|-----------|
| **Edad** | 15-100 años (numérico) |
| **Sexo** | Hombre/Mujer (obligatorio) |
| **Departamento** | Lista de 22 departamentos |
| **Nivel educativo** | Lista predefinida |
| **Años educación** | 0-25 años |
| **Tiene salud** | Sí/No (obligatorio) |
| **Tipo salud** | Aparece solo si tiene salud |
| **Gasto salud** | Aparece solo si requirió atención, ≥0 |
| **Empleo formal** | Sí/No con descripción |
| **Num. cuartos** | Mínimo 1 |
| **Personas hogar** | Mínimo 1 |
| **Servicios** | Toggle Sí/No para cada uno |
| **Num. menores** | Aparece solo si tiene hijos, 0-10 |

---

## 📈 Métricas del Modelo

```
Modelo: XGBoost Optimizado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROC-AUC:      0.8119  ★★★★☆
Recall:       0.92    ★★★★★
Precision:    0.15    ★★☆☆☆
F1-Score:     0.26    ★★☆☆☆
Umbral:       0.5263
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Prioriza detectar vulnerables (Recall alto)
✓ Minimiza falsos negativos
✓ Optimizado para screening social
```

---

## 🎨 Diseño del Frontend

- **Paleta**: Fondo negro (#000) con texto blanco (#FFF)
- **Acentos**: Azul (#3B82F6) y Púrpura (#A855F7)
- **Animaciones**: Gradientes rotando, fade in/out
- **Fuente**: Inter (system font)
- **Contraste**: AAA (WCAG)

---

## 📞 Soporte

Si tienes problemas que no se resuelven con este documento:

1. ✅ Revisa que estén instaladas todas las dependencias
2. ✅ Verifica que el modelo esté entrenado
3. ✅ Confirma que ambos puertos (8000, 3000) estén libres
4. ✅ Revisa los logs de la API y la consola del navegador
5. ✅ Ejecuta `python test_api.py` para diagnóstico

---

## 🎉 ¡Listo!

Si todo funciona correctamente, deberías ver:

1. ✅ API corriendo en http://localhost:8000
2. ✅ Frontend corriendo en http://localhost:3000
3. ✅ Formulario de 7 pasos funcionando
4. ✅ Predicciones generándose correctamente
5. ✅ Resultados visualizándose bien

**¡Disfruta del sistema!** 🚀

---

**Versión**: 1.0.0  
**Fecha**: Octubre 2025  
**Empresa**: EA Tech Company

