# ⚡ NETLIFY - PASOS RÁPIDOS

## 5 minutos para desplegar tu frontend

---

## 🚀 MÉTODO 1: Desde GitHub (RECOMENDADO)

### ✅ Paso 1: Subir Frontend a GitHub

```bash
# Asegúrate de estar en la raíz del proyecto
cd "E:\Daniel\Trabajos\2025\EA Tech Company\Proyectos\Monitor de Vulnerabilidad Economica"

# Ver status
git status

# Si hay cambios, súbelos
git add frontend/
git commit -m "Frontend ready for Netlify deployment"
git push origin main
```

---

### 🌐 Paso 2: Netlify Dashboard

1. **Ir a:** [app.netlify.com](https://app.netlify.com)
2. **Sign up** con GitHub
3. **Add new site** → **Import an existing project**
4. **Deploy with GitHub**
5. Selecciona: `Monitor-de-Vulnerabilidad-Econ-mica`

---

### ⚙️ Paso 3: Configuración del Build

Copia exactamente:

```
Branch to deploy:    main
Base directory:      frontend
Build command:       npm run build
Publish directory:   frontend/build
```

Click en **"Deploy site"**

---

### 🔧 Paso 4: Variables de Entorno

**DESPUÉS del primer deploy:**

1. **Site settings** → **Environment variables**
2. **Add a variable:**
   - **Key:** `REACT_APP_API_URL`
   - **Value:** `http://localhost:8000` (temporal)
3. **Deploys** → **Trigger deploy**

**CUANDO TENGAS EL BACKEND EN RENDER:**
- Cambia el valor a: `https://tu-api.onrender.com`
- **Trigger deploy** de nuevo

---

## 🎯 MÉTODO 2: Deploy Manual (Rápido para Probar)

### Construir y Subir

```bash
# Construir
cd frontend
npm run build

# Ir a netlify.com/drop
# Arrastra la carpeta "build" completa
```

---

## 📋 Checklist Post-Deploy

- [ ] Sitio desplegado: `https://algo-random.netlify.app`
- [ ] Cambiar nombre del sitio (opcional):
  - **Site settings** → **Change site name**
  - Ejemplo: `vulnerabilidad-economica`
  - Nueva URL: `https://vulnerabilidad-economica.netlify.app`
- [ ] Variable `REACT_APP_API_URL` configurada
- [ ] Backend desplegado en Render
- [ ] CORS actualizado en backend con URL de Netlify

---

## 🔗 Conectar Frontend ↔ Backend

### En Netlify (Frontend):
```
REACT_APP_API_URL = https://vulnerabilidad-api.onrender.com
```

### En Backend (`src/api/main.py`):
```python
allow_origins=[
    "http://localhost:3000",
    "https://vulnerabilidad-economica.netlify.app",  # Tu URL
],
```

**Luego:**
```bash
git add src/api/main.py
git commit -m "Add Netlify URL to CORS"
git push
```

---

## ✅ Verificar

1. Abre tu URL de Netlify
2. El sitio debería cargar con el logo negro brillante ✨
3. Completa el formulario
4. Click en "Analizar"
5. ¡Funciona! 🎉

---

## 🐛 Si Algo Falla

**Build Error:**
- Lee los logs en Netlify
- Prueba `npm run build` localmente primero

**Página en Blanco:**
- Revisa que `netlify.toml` esté en `frontend/`
- Verifica la configuración de rutas

**API No Responde:**
- Verifica `REACT_APP_API_URL` en Netlify
- Prueba el backend: `https://tu-api.onrender.com/health`
- Revisa CORS en el backend

---

## 🎁 Bonus: Deploy Automático

Una vez configurado, **cada push a GitHub** despliega automáticamente:

```bash
# Haz cambios en el frontend
cd frontend/src
# ... editas algo ...

# Commit y push
git add .
git commit -m "Update: mejora UI"
git push

# ¡Netlify despliega automáticamente en 2-3 min! 🚀
```

---

## 📊 URLs Importantes

- **Dashboard:** https://app.netlify.com
- **Documentación:** https://docs.netlify.com
- **Drop (manual):** https://app.netlify.com/drop

---

**¡Listo para producción en 5 minutos!** ⚡

Archivo creado: `NETLIFY_DEPLOY_GUIDE.md` para guía completa.

