# ✅ CONFIGURACIÓN FINAL - Frontend ↔ Backend

## 🎯 URLs de tu Aplicación

- **Frontend (Netlify):** https://moneave.netlify.app
- **Backend (Render):** https://monitor-de-vulnerabilidad-econ-mica.onrender.com

---

## ✅ PASO 1: Backend LISTO ✓

Ya actualicé el CORS en el backend. Los cambios están en GitHub y Render se re-desplegará automáticamente en ~3-5 minutos.

**Archivo actualizado:** `src/api/main.py`
```python
allow_origins=[
    "http://localhost:3000",
    "https://moneave.netlify.app",  # ← Tu frontend
],
```

**Verificación:**
```bash
# Espera 3-5 minutos y verifica que Render termine el re-deploy
# Luego prueba:
curl https://monitor-de-vulnerabilidad-econ-mica.onrender.com/health
```

Deberías ver:
```json
{"status":"ok"}
```

---

## ⚙️ PASO 2: Configurar Variable en Netlify

Ahora necesitas decirle al frontend dónde está el backend:

### Opción A: Usando el Dashboard de Netlify (RECOMENDADO)

1. **Ve a:** [app.netlify.com](https://app.netlify.com)
2. **Selecciona tu sitio:** "moneave"
3. **Site settings** (menú lateral)
4. **Environment variables** (bajo "Build & deploy")
5. **Add a variable** (botón verde)
6. Configura:
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `https://monitor-de-vulnerabilidad-econ-mica.onrender.com`
   - **Scopes:** Marca todas (Production, Deploy previews, Branch deploys)
7. **Create variable**

### Opción B: Usando el archivo netlify.toml (YA HECHO)

Ya actualicé `frontend/netlify.toml` con:
```toml
[build.environment]
  REACT_APP_API_URL = "https://monitor-de-vulnerabilidad-econ-mica.onrender.com"
```

**PERO:** Necesitas hacer commit y push de este cambio.

---

## 🚀 PASO 3: Re-desplegar el Frontend

Después de configurar la variable de entorno:

### En Netlify Dashboard:

1. Ve a **Deploys**
2. Click en **Trigger deploy** (botón derecho)
3. Selecciona **Deploy site**
4. Espera 1-2 minutos

---

## 🧪 PASO 4: Verificar que TODO Funciona

### 4.1 Verificar Backend

Abre en tu navegador:
```
https://monitor-de-vulnerabilidad-econ-mica.onrender.com/docs
```

Deberías ver la documentación interactiva de FastAPI.

### 4.2 Verificar Frontend

1. Abre: https://moneave.netlify.app
2. Abre la **Consola del Navegador** (F12)
3. Busca errores en rojo

### 4.3 Prueba Completa

1. En https://moneave.netlify.app
2. Completa el formulario:
   - Género: Hombre
   - Edad: 35
   - Educación: Universitaria
   - Etc.
3. Click en **"Analizar"**
4. ¡Deberías ver el resultado de vulnerabilidad! 🎉

---

## 🐛 Si NO Funciona

### Error: "Network Error" o "Failed to fetch"

**Causa:** El frontend no puede conectar con el backend.

**Solución:**

1. **Verifica la variable de entorno en Netlify:**
   - Site settings → Environment variables
   - Debe ser: `REACT_APP_API_URL = https://monitor-de-vulnerabilidad-econ-mica.onrender.com`
   - SIN barra `/` al final

2. **Re-despliega el frontend:**
   - Deploys → Trigger deploy

3. **Espera que Render despierte:**
   - Si el backend estuvo inactivo >15 min, la primera petición tarda ~30 seg
   - Prueba primero: `https://monitor-de-vulnerabilidad-econ-mica.onrender.com/health`
   - Luego prueba el formulario

### Error: "CORS policy"

**Causa:** El backend no permite peticiones desde Netlify.

**Solución:**

1. **Verifica que Render haya re-desplegado:**
   - Ve a [dashboard.render.com](https://dashboard.render.com)
   - Selecciona tu servicio
   - Ve a "Logs"
   - Busca: "Deploy finished"

2. **Espera 3-5 minutos** después del push a GitHub

3. Si persiste, verifica manualmente `src/api/main.py` en GitHub:
   ```python
   allow_origins=[
       "https://moneave.netlify.app",  # Sin barra al final
   ]
   ```

### El sitio carga pero no hace nada

**Causa:** Variable de entorno mal configurada.

**Solución:**

1. Abre la consola del navegador (F12)
2. Ve a "Console"
3. Escribe: `console.log(process.env.REACT_APP_API_URL)`
4. Si dice `undefined`:
   - La variable NO está configurada
   - Configúrala en Netlify
   - Re-despliega

---

## 📊 Monitoreo

### Logs del Backend (Render)

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Selecciona tu servicio
3. Click en **"Logs"**
4. Verás peticiones en tiempo real:
   ```
   INFO: POST /predict - 200 OK
   ```

### Logs del Frontend (Netlify)

1. Ve a [app.netlify.com](https://app.netlify.com)
2. Selecciona tu sitio
3. **Deploys** → Click en el último deploy
4. Verás el log del build

---

## 🎯 Checklist Final

- [ ] Backend actualizado con CORS de Netlify
- [ ] Push a GitHub realizado
- [ ] Render re-desplegó (3-5 min)
- [ ] Variable `REACT_APP_API_URL` configurada en Netlify
- [ ] Frontend re-desplegado
- [ ] Backend `/health` responde OK
- [ ] Frontend carga correctamente
- [ ] Formulario funciona y devuelve predicción
- [ ] **¡TODO FUNCIONA!** 🎉

---

## 🚨 IMPORTANTE: Primera Petición

El plan gratuito de Render "duerme" el backend después de 15 minutos sin actividad.

**Síntoma:** Primera petición tarda ~30 segundos.

**Es NORMAL.** No es un error. Después de la primera petición, todo funciona rápido.

---

## 🎨 Próximos Pasos (Opcional)

### Personalizar Dominio de Netlify

Cambia de `moneave.netlify.app` a algo más descriptivo:

1. Site settings → General → Site details
2. **Change site name**
3. Ejemplo: `vulnerabilidad-economica`
4. Nueva URL: `https://vulnerabilidad-economica.netlify.app`

**RECUERDA:** Si cambias el nombre, actualiza el CORS en el backend.

---

## 📞 Verificación Rápida

Copia y pega en tu navegador:

**Backend Health Check:**
```
https://monitor-de-vulnerabilidad-econ-mica.onrender.com/health
```

**Backend Docs:**
```
https://monitor-de-vulnerabilidad-econ-mica.onrender.com/docs
```

**Frontend:**
```
https://moneave.netlify.app
```

---

**¡Tu aplicación está LISTA para producción!** 🚀

---

**Daniel Hurtado**  
Científico de Datos • Economista • Desarrollador Full Stack  
EA Tech Company

