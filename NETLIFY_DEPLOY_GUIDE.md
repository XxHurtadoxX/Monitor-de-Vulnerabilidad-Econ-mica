# 🚀 Guía Completa: Despliegue en Netlify

## Monitor de Vulnerabilidad Económica - Frontend

---

## 📋 OPCIÓN 1: Desplegar desde GitHub (Recomendado)

Esta es la forma **MÁS FÁCIL** y automatiza todo.

---

### ✅ PASO 1: Asegurar que el Frontend esté en GitHub

Ya lo hicimos, pero verifica:

```bash
cd frontend
git status
```

Si hay cambios sin commit:

```bash
git add .
git commit -m "Frontend ready for Netlify"
git push origin main
```

---

### 🌐 PASO 2: Crear Cuenta en Netlify

1. Ve a [netlify.com](https://www.netlify.com)
2. Click en **"Sign up"**
3. Selecciona **"Sign up with GitHub"** (más fácil)
4. Autoriza Netlify en GitHub

---

### 🔗 PASO 3: Conectar Repositorio

1. En el dashboard de Netlify, click en **"Add new site"**
2. Selecciona **"Import an existing project"**
3. Click en **"Deploy with GitHub"**
4. Busca y selecciona tu repositorio:
   ```
   Monitor-de-Vulnerabilidad-Econ-mica
   ```
5. Click en **"Select"**

---

### ⚙️ PASO 4: Configurar el Build

Netlify detectará automáticamente la configuración, pero verifica:

**Site settings:**
- **Branch to deploy:** `main`
- **Base directory:** `frontend`
- **Build command:** `npm run build`
- **Publish directory:** `frontend/build`

**IMPORTANTE:** Si no detecta automáticamente, copia exactamente:
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `frontend/build`

---

### 🚀 PASO 5: Deploy!

1. Click en **"Deploy site"**
2. Espera 2-5 minutos
3. Netlify te dará una URL temporal como:
   ```
   https://silly-name-123456.netlify.app
   ```

---

### 🔧 PASO 6: Configurar Variables de Entorno

**MUY IMPORTANTE:** El frontend necesita saber dónde está el backend.

1. En Netlify, ve a tu sitio
2. **Site settings** → **Environment variables**
3. Click en **"Add a variable"**
4. Configura:
   - **Key:** `REACT_APP_API_URL`
   - **Value:** Por ahora: `http://localhost:8000` (lo cambiaremos cuando despliegues el backend)
5. Click en **"Create variable"**

---

### 🔄 PASO 7: Re-deploy con Variables

1. Ve a **Deploys**
2. Click en **"Trigger deploy"** → **"Deploy site"**
3. Espera 1-2 minutos

---

### ✅ PASO 8: Verificar que Funciona

1. Abre tu URL de Netlify
2. Deberías ver el formulario funcionando
3. **NOTA:** Las predicciones NO funcionarán hasta que despliegues el backend

---

## 📋 OPCIÓN 2: Desplegar desde Build Local (Manual)

Si prefieres subir el build directamente:

---

### 🔨 PASO 1: Construir el Proyecto

```bash
cd frontend
npm run build
```

Esto crea la carpeta `build/` con los archivos estáticos.

---

### 📤 PASO 2: Subir a Netlify

**Opción A: Arrastrar y Soltar**

1. Ve a [app.netlify.com/drop](https://app.netlify.com/drop)
2. Arrastra la carpeta `build/` completa
3. ¡Listo!

**Opción B: CLI de Netlify**

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd build
netlify deploy --prod
```

---

## 🎨 PASO 9: Personalizar Dominio (Opcional)

### Cambiar el Nombre del Sitio

1. En Netlify: **Site settings** → **General** → **Site details**
2. Click en **"Change site name"**
3. Escribe un nombre único:
   ```
   vulnerabilidad-economica
   ```
4. Tu URL será:
   ```
   https://vulnerabilidad-economica.netlify.app
   ```

### Usar Dominio Personalizado (Si tienes uno)

1. **Site settings** → **Domain management**
2. **Add custom domain**
3. Sigue las instrucciones de Netlify

---

## 🔗 PASO 10: Conectar con Backend (Render)

Una vez que despliegues el backend en Render:

### A. Actualizar Variable en Netlify

1. **Site settings** → **Environment variables**
2. Edita `REACT_APP_API_URL`
3. Cambia a tu URL de Render:
   ```
   https://vulnerabilidad-api.onrender.com
   ```
4. **Trigger deploy** para aplicar cambios

### B. Actualizar CORS en Backend

1. Edita `src/api/main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://vulnerabilidad-economica.netlify.app",  # ← Tu URL
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Haz commit y push:
   ```bash
   git add src/api/main.py
   git commit -m "Update CORS with Netlify URL"
   git push
   ```

Render re-desplegará automáticamente.

---

## 🎯 PASO 11: Prueba Final

1. Abre tu sitio en Netlify
2. Completa el formulario
3. Click en **"Analizar"**
4. ¡Deberías ver el resultado! 🎉

---

## 🔥 Ventajas de Netlify

✅ **HTTPS automático** (certificado SSL gratis)  
✅ **CDN global** (sitio rápido en todo el mundo)  
✅ **Deploy automático** en cada push a GitHub  
✅ **Preview deploys** para pull requests  
✅ **Rollback** a versiones anteriores  
✅ **100% GRATIS** para proyectos personales

---

## 🐛 Solución de Problemas

### Build Falla

**Error:** `npm ERR! Failed at the build script`

**Solución:**
1. Verifica que el build funciona localmente:
   ```bash
   cd frontend
   npm run build
   ```
2. Si falla, revisa los errores de TypeScript/ESLint
3. Corrige y haz push

---

### Página en Blanco

**Causa:** Rutas mal configuradas

**Solución:**
- Verifica que `netlify.toml` esté en `frontend/`
- Revisa la redirección `/*` → `/index.html`

---

### API No Responde

**Error en consola:** `Failed to fetch` o `CORS error`

**Solución:**
1. Verifica que `REACT_APP_API_URL` esté configurada
2. Verifica que el backend tenga CORS configurado correctamente
3. Prueba la API directamente: `https://tu-api.onrender.com/health`

---

### Build Tarda Mucho

**Causa:** Instalando dependencias en cada build

**Solución:** Netlify cachea automáticamente `node_modules`, pero si quieres optimizar:
1. **Site settings** → **Build & deploy** → **Build settings**
2. Verifica que **"Dependency caching"** esté activado

---

## 📊 Monitoreo

### Ver Logs de Build

1. **Deploys** → Click en el deploy más reciente
2. Verás logs detallados del build
3. Busca errores en rojo

### Analytics (Gratis)

1. **Analytics** → Verás visitas, páginas más vistas, etc.

---

## 🚀 Deploy Automático

Una vez configurado, cada vez que hagas:

```bash
git push origin main
```

Netlify:
1. Detecta el cambio
2. Clona el repo
3. Ejecuta `npm run build`
4. Publica automáticamente
5. Te notifica por email

**Todo en 2-3 minutos** ⚡

---

## ✅ Checklist Final

- [ ] Repositorio subido a GitHub
- [ ] Cuenta en Netlify creada
- [ ] Sitio conectado a GitHub
- [ ] Build exitoso
- [ ] Variable `REACT_APP_API_URL` configurada
- [ ] Sitio accesible públicamente
- [ ] Nombre personalizado (opcional)
- [ ] Backend desplegado en Render
- [ ] CORS actualizado en backend
- [ ] Prueba completa exitosa

---

## 🎉 ¡Listo!

Tu frontend está en producción con:
- ✅ HTTPS
- ✅ CDN Global
- ✅ Deploy automático
- ✅ 100% Gratis

---

## 📞 Recursos

- **Documentación Netlify:** [docs.netlify.com](https://docs.netlify.com)
- **Status de Netlify:** [netlifystatus.com](https://www.netlifystatus.com)
- **Comunidad:** [community.netlify.com](https://community.netlify.com)

---

**Daniel Hurtado**  
Científico de Datos • Economista • Desarrollador Web  
EA Tech Company

---

**Próximo paso:** Despliega el backend en Render siguiendo `render.yaml`

