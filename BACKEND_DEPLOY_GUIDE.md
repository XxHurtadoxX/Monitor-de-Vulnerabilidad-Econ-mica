# 🚀 Guía de Despliegue del Backend en Render

## Monitor de Vulnerabilidad Económica - Backend API

---

## 📋 Pre-requisitos

✅ Cuenta en GitHub (gratis)  
✅ Cuenta en Render (gratis) - [render.com](https://render.com)  
✅ Archivos listos:
- `render.yaml` ✓
- `requirements.txt` ✓
- `src/api/main.py` ✓
- Modelo: `models/final_optimized_xgboost.pkl` ✓
- Features: `data/processed/modeling/feature_names.txt` ✓
- Threshold: `models/threshold_optimization.json` ✓

---

## 🔧 PASO 1: Verificar Archivos Necesarios

Asegúrate de que estos archivos **EXISTEN** y **NO están en .gitignore**:

```bash
# Verifica que estos archivos existen:
ls models/final_optimized_xgboost.pkl
ls data/processed/modeling/feature_names.txt
ls models/threshold_optimization.json
ls src/pipeline/questionnaire_schema.json
```

Si alguno falta, el despliegue **FALLARÁ**.

---

## 📤 PASO 2: Subir el Código a GitHub

### Opción A: Primera vez (Nuevo Repositorio)

```bash
# 1. Vuelve a la raíz del proyecto
cd "E:\Daniel\Trabajos\2025\EA Tech Company\Proyectos\Monitor de Vulnerabilidad Economica"

# 2. Inicializa Git (si no lo has hecho)
git init

# 3. Agrega todos los archivos
git add .

# 4. Verifica qué se va a subir (IMPORTANTE)
git status

# 5. Haz el commit
git commit -m "Backend ready for Render deployment"

# 6. Crea el branch main
git branch -M main

# 7. Conecta con GitHub (primero crea el repo en github.com)
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git

# 8. Sube el código
git push -u origin main
```

### Opción B: Actualizar Repositorio Existente

```bash
git add .
git commit -m "Update: Backend ready for production"
git push
```

---

## 🌐 PASO 3: Desplegar en Render

### 3.1 Crear Web Service

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Click en **"New +"** (botón azul arriba a la derecha)
3. Selecciona **"Web Service"**

### 3.2 Conectar Repositorio

1. Si es tu primera vez:
   - Click en **"Connect account"** → GitHub
   - Autoriza Render en GitHub
2. Busca y selecciona tu repositorio
3. Click en **"Connect"**

### 3.3 Configurar el Servicio

**Configuración básica:**
- **Name**: `vulnerabilidad-api` (o el nombre que prefieras)
- **Region**: `Oregon (US West)` (más cercano, más rápido)
- **Branch**: `main`
- **Root Directory**: Dejar vacío (ya está en `render.yaml`)
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Selecciona **"Free"** (0 USD/mes)

### 3.4 Variables de Entorno (Opcional)

Si necesitas agregar variables:
- Click en **"Advanced"**
- **Environment Variables**:
  - `PYTHON_VERSION`: `3.11.0`

### 3.5 Deploy

1. Click en **"Create Web Service"**
2. Render comenzará el despliegue automáticamente
3. Espera 5-10 minutos (primera vez es más lento)

---

## ⏱️ PASO 4: Monitorear el Despliegue

### Logs en Tiempo Real

En Render verás:
```
==> Installing dependencies from requirements.txt
==> Building...
==> Starting server...
✓ Pipeline cargado exitosamente
INFO: Uvicorn running on http://0.0.0.0:10000
```

### Errores Comunes

**Error: "Module not found"**
- Verifica que `requirements.txt` tenga todas las dependencias

**Error: "File not found: models/final_optimized_xgboost.pkl"**
- Verifica `.gitignore` - asegúrate de NO ignorar el modelo
- Haz `git add -f models/final_optimized_xgboost.pkl`

**Error: "Port already in use"**
- Render maneja esto automáticamente, solo espera

---

## ✅ PASO 5: Verificar que Funciona

### 5.1 Obtener la URL

Render te dará una URL como:
```
https://vulnerabilidad-api.onrender.com
```

### 5.2 Probar los Endpoints

**Health Check:**
```bash
curl https://vulnerabilidad-api.onrender.com/health
```

Deberías ver:
```json
{"status": "ok"}
```

**Documentación Interactiva:**

Visita en tu navegador:
```
https://vulnerabilidad-api.onrender.com/docs
```

Verás la documentación automática de FastAPI con todos los endpoints.

---

## 🔗 PASO 6: Conectar con el Frontend (Netlify)

### 6.1 Actualizar CORS en el Backend

Una vez que tengas la URL de Netlify, actualiza `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://tu-sitio.netlify.app",  # ← Tu URL específica
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Luego:
```bash
git add src/api/main.py
git commit -m "Update CORS with Netlify URL"
git push
```

Render re-desplegará automáticamente.

### 6.2 Configurar Variable en Netlify

1. Ve a tu sitio en Netlify
2. **Site settings** → **Environment variables**
3. Agrega:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://vulnerabilidad-api.onrender.com`
4. **Deploys** → **Trigger deploy** → **Deploy site**

---

## 🎯 PASO 7: Prueba Final

1. Abre tu sitio de Netlify
2. Completa el formulario
3. Click en "Analizar"
4. ¡Deberías ver el resultado de la predicción! 🎉

---

## ⚠️ Limitaciones del Plan Gratuito de Render

- ✅ **750 horas/mes** (más que suficiente para un proyecto personal)
- ⚠️ **Se "duerme" después de 15 min sin actividad**
  - Primera petición después de "dormir" tarda ~30 segundos
  - Esto es normal y no es un error
- ✅ **HTTPS automático**
- ✅ **Re-deploy automático** en cada push a GitHub

---

## 💡 Alternativas Gratuitas

### Railway (Recomendado si Render es lento)

1. [railway.app](https://railway.app)
2. **"New Project"** → **"Deploy from GitHub"**
3. Selecciona tu repo
4. Railway detecta automáticamente Python y FastAPI
5. No necesitas configurar nada más ✨

**Ventajas:**
- No se duerme
- Más rápido
- $5 gratis/mes (suficiente)

### Fly.io

1. [fly.io](https://fly.io)
2. Requiere instalar Fly CLI
3. Más control pero más complejo

---

## 🐛 Solución de Problemas

### Build Falla

**Revisa logs en Render:**
```
Build failed - Check your requirements.txt
```

**Solución:**
- Verifica versiones en `requirements.txt`
- Prueba localmente: `pip install -r requirements.txt`

### Endpoint 500 Error

**Revisa logs en Render:**
```
ERROR: File not found
```

**Solución:**
- Verifica que el modelo existe en el repo
- Revisa `.gitignore`

### CORS Error en Frontend

**Error en consola:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solución:**
- Actualiza CORS en `src/api/main.py` con URL de Netlify
- Re-despliega

---

## 📞 Contacto

**Daniel Hurtado**  
Científico de Datos • Economista • Desarrollador Web  
EA Tech Company

---

## ✅ Checklist Final

- [ ] Código subido a GitHub
- [ ] Modelo incluido en el repositorio
- [ ] Servicio creado en Render
- [ ] Build exitoso
- [ ] Health check funciona
- [ ] CORS actualizado con URL de Netlify
- [ ] Variable `REACT_APP_API_URL` en Netlify
- [ ] Frontend se comunica con Backend
- [ ] Prueba completa exitosa

---

**¡Tu Backend está en producción!** 🚀

