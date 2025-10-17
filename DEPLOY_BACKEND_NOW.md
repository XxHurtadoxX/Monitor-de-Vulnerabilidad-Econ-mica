# 🚀 DESPLIEGUE DEL BACKEND - COMANDOS RÁPIDOS

## ⚡ Sigue estos pasos en orden:

---

## 📤 PASO 1: Subir a GitHub

```bash
# Asegúrate de estar en la raíz del proyecto
cd "E:\Daniel\Trabajos\2025\EA Tech Company\Proyectos\Monitor de Vulnerabilidad Economica"

# Inicializa git (si no lo has hecho)
git init

# Agrega todos los archivos
git add .

# Commit
git commit -m "Backend ready: Monitor Vulnerabilidad Economica"

# Branch main
git branch -M main

# Conecta con GitHub (primero crea el repo en github.com)
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git

# Push
git push -u origin main
```

---

## 🌐 PASO 2: Desplegar en Render

1. **Ir a:** [dashboard.render.com](https://dashboard.render.com)
2. **Click en:** `New +` → `Web Service`
3. **Conectar** tu repositorio de GitHub
4. **Configurar:**
   - **Name:** `vulnerabilidad-api`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
5. **Click:** `Create Web Service`
6. **Esperar** 5-10 minutos

---

## 📋 PASO 3: Obtener URL

Render te dará una URL como:
```
https://vulnerabilidad-api.onrender.com
```

**Cópiala!** La necesitarás para el siguiente paso.

---

## 🔗 PASO 4: Conectar con Netlify

1. Ve a tu sitio en **Netlify**
2. **Site settings** → **Environment variables**
3. **Add a variable:**
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `https://vulnerabilidad-api.onrender.com`
4. **Deploys** → **Trigger deploy** → **Deploy site**

---

## ✅ PASO 5: Actualizar CORS (Después de tener URL de Netlify)

Una vez que tengas tu URL de Netlify (ej: `https://tu-sitio.netlify.app`):

1. Edita `src/api/main.py`
2. Actualiza el CORS:
```python
allow_origins=[
    "http://localhost:3000",
    "https://tu-sitio.netlify.app",  # ← TU URL AQUÍ
],
```
3. Haz push:
```bash
git add src/api/main.py
git commit -m "Update CORS with Netlify URL"
git push
```

Render re-desplegará automáticamente.

---

## 🎯 VERIFICAR QUE FUNCIONA

**Probar Health Check:**

Abre en tu navegador:
```
https://vulnerabilidad-api.onrender.com/health
```

Deberías ver:
```json
{"status": "ok"}
```

**Probar Documentación:**
```
https://vulnerabilidad-api.onrender.com/docs
```

---

## ⚠️ IMPORTANTE: Primera Carga

La primera vez que visites la API después de que "se duerma" (15 min sin uso), tardará ~30 segundos en responder. **Esto es NORMAL** en el plan gratuito.

---

## 📁 Archivos Creados

- ✅ `render.yaml` - Configuración automática de Render
- ✅ `BACKEND_DEPLOY_GUIDE.md` - Guía completa
- ✅ `.gitignore` - Actualizado para incluir modelos

---

## 🚨 SI ALGO FALLA

1. **Revisa los logs en Render** (pestaña "Logs")
2. **Verifica que estos archivos existen:**
   - `models/final_optimized_xgboost.pkl`
   - `data/processed/modeling/feature_names.txt`
   - `models/threshold_optimization.json`
3. **Lee:** `BACKEND_DEPLOY_GUIDE.md` para soluciones detalladas

---

## 💡 ALTERNATIVA: Railway (Más Rápido)

Si Render es muy lento:

1. Ve a [railway.app](https://railway.app)
2. `New Project` → `Deploy from GitHub`
3. Selecciona tu repositorio
4. ¡Listo! Railway detecta todo automáticamente

---

**¡Ahora tu backend estará en producción!** 🎉

