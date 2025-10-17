# 🎨 Frontend - Monitor de Vulnerabilidad Económica

Frontend en React + TypeScript con formulario paso a paso amigable para el usuario.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `frontend/`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

### 3. Iniciar el servidor de desarrollo

```bash
npm start
```

El frontend se abrirá automáticamente en `http://localhost:3000`

## 📋 Prerequisitos

- ✅ **Node.js** (v16 o superior)
- ✅ **npm** (v8 o superior)
- ✅ **API corriendo** en http://localhost:8000

## 🎯 Características del Formulario

### Validaciones Implementadas

El formulario incluye validaciones exhaustivas para prevenir inputs erróneos:

#### 1. Demográficas (Paso 1)
- ✓ Edad: 15-100 años (numérico)
- ✓ Sexo: Hombre/Mujer (obligatorio)
- ✓ Departamento: Lista predefinida de 22 departamentos (obligatorio)

#### 2. Educación (Paso 2)
- ✓ Nivel educativo: Lista predefinida (ninguno, primaria, secundaria, media, superior)
- ✓ Años de educación: 0-25 años (numérico)

#### 3. Salud (Paso 3)
- ✓ Afiliación a salud: Sí/No (obligatorio)
- ✓ Tipo de afiliación: Condicional si tiene salud
- ✓ Atención médica reciente: Sí/No
- ✓ Gasto en salud: Condicional si requirió atención, debe ser ≥ 0

#### 4. Trabajo (Paso 4)
- ✓ Empleo formal: Sí/No con descripción clara

#### 5. Vivienda (Paso 5)
- ✓ Tipo de vivienda: Casa/Apartamento/Cuarto/Otro
- ✓ Tenencia: Propia/Arriendo/Prestada/Otra
- ✓ Número de cuartos: Mínimo 1
- ✓ Personas en el hogar: Mínimo 1
- ✓ Material de pisos: Lista predefinida

#### 6. Servicios Públicos (Paso 6)
- ✓ 5 servicios con toggle Sí/No (Acueducto, Alcantarillado, Gas, Energía, Basuras)
- ✓ Gasto en energía: Condicional si tiene energía

#### 7. Hogar (Paso 7)
- ✓ Tiene hijos menores: Sí/No
- ✓ Número de menores: Condicional si tiene hijos, 0-10

### Características de UX

#### 🎨 Diseño
- **Fondo negro** con gradientes animados (azul/púrpura)
- **Texto blanco** con máximo contraste
- **Animaciones suaves** con Framer Motion
- **Efectos de iluminación** en cards y bordes
- **Responsive** para móviles y tablets

#### 🔄 Navegación
- Barra de progreso visual
- Botones Anterior/Siguiente
- Validación en cada paso antes de avanzar
- Mensajes de error claros y contextuales
- Scroll automático al cambiar de paso

#### ⚡ Interactividad
- Botones tipo toggle para Sí/No
- Campos condicionales que aparecen según respuestas previas
- Inputs numéricos con límites (min/max)
- Selectores con opciones predefinidas
- Loading spinner durante el análisis

#### 📊 Resultados
- Visualización clara del nivel de riesgo
- Código de colores intuitivo:
  - 🟢 Verde: Riesgo Bajo
  - 🟡 Amarillo: Riesgo Medio
  - 🟠 Naranja: Riesgo Alto
  - 🔴 Rojo: Riesgo Muy Alto
- Gráfico de probabilidades
- Mensaje interpretativo
- Detalles técnicos plegables
- Recomendaciones si es vulnerable
- Botón para nuevo análisis

## 📁 Estructura de Componentes

```
frontend/src/
├── components/
│   ├── VulnerabilityForm.tsx      # Componente principal del formulario
│   ├── FormSteps.tsx               # Pasos individuales del formulario
│   ├── ResultDisplay.tsx           # Pantalla de resultados
│   ├── LoadingSpinner.tsx          # Indicador de carga
│   ├── Header.tsx                  # Encabezado con logo
│   └── Footer.tsx                  # Pie de página
├── services/
│   └── api.ts                      # Cliente API (axios)
├── types/
│   └── api.ts                      # Tipos TypeScript
├── config/
│   └── app.ts                      # Configuración
├── App.tsx                         # Componente raíz
└── index.css                       # Estilos globales (Tailwind)
```

## 🔧 Scripts Disponibles

```bash
# Desarrollo
npm start           # Inicia servidor de desarrollo (puerto 3000)

# Build
npm run build       # Genera build optimizado para producción

# Tests
npm test            # Ejecuta tests

# Linting
npm run lint        # Verifica errores de código
```

## 🌐 Endpoints de la API Consumidos

| Endpoint | Método | Uso |
|----------|--------|-----|
| `/predict` | POST | Envía datos del formulario y recibe predicción |
| `/questionnaire` | GET | (Opcional) Obtiene esquema dinámico del cuestionario |
| `/health` | GET | Verifica que la API esté disponible |

## 🎯 Flujo de Usuario

1. **Landing** → Usuario ve header con logo y descripción
2. **Paso 1-7** → Completa formulario paso a paso con validaciones
3. **Envío** → Click en "Analizar" envía datos a `/predict`
4. **Loading** → Spinner animado mientras procesa
5. **Resultados** → Visualización del nivel de vulnerabilidad
6. **Reinicio** → Puede hacer nuevo análisis

## 🛠️ Troubleshooting

### Error: "Cannot find module"

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: "API not available"

Verifica que la API esté corriendo:
```bash
# En otra terminal
uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Error de CORS

La API ya está configurada para aceptar requests de `localhost:3000`. Si cambias el puerto del frontend, actualiza `src/api/main.py`:

```python
allow_origins=[
    "http://localhost:3000",  # Puerto default
    "http://localhost:3001",  # Agrega más puertos si necesario
]
```

### Build falla

Revisa errores de TypeScript:
```bash
npm run lint
```

## 📊 Dependencias Principales

```json
{
  "react": "^18.x",
  "react-dom": "^18.x",
  "typescript": "^5.x",
  "framer-motion": "^10.x",  // Animaciones
  "axios": "^1.x",            // HTTP client
  "tailwindcss": "^3.x"       // CSS utility-first
}
```

## 🎨 Paleta de Colores

- **Fondo**: Negro (#000000)
- **Texto principal**: Blanco (#FFFFFF)
- **Acentos primarios**: Azul (#3B82F6) y Púrpura (#A855F7)
- **Éxito**: Verde (#10B981)
- **Advertencia**: Amarillo (#FBBF24)
- **Peligro**: Rojo (#EF4444)
- **Bordes**: Gris (#374151)

## 🚀 Despliegue a Producción

### Build optimizado

```bash
npm run build
```

Esto genera una carpeta `build/` con archivos estáticos optimizados.

### Servir con servidor web

```bash
# Con serve
npm install -g serve
serve -s build -p 3000

# Con nginx (ejemplo de configuración)
# Copia los archivos de build/ a /var/www/html
# Configura reverse proxy a la API
```

### Variables de entorno para producción

Actualiza `.env` o configura en tu servidor:

```bash
REACT_APP_API_URL=https://tu-api.com
```

## ✅ Checklist de Testing

Antes de desplegar, verifica:

- [ ] Todos los 7 pasos del formulario funcionan
- [ ] Validaciones previenen inputs erróneos
- [ ] Campos condicionales aparecen/desaparecen correctamente
- [ ] Botones Anterior/Siguiente funcionan
- [ ] Barra de progreso se actualiza
- [ ] Loading spinner aparece durante predicción
- [ ] Resultados se muestran correctamente
- [ ] Botón "Nuevo Análisis" reinicia el formulario
- [ ] Diseño responsive en móvil
- [ ] No hay errores en consola
- [ ] API responde correctamente

## 📞 Soporte

Si tienes problemas:
1. Verifica que la API esté corriendo y respondiendo
2. Revisa la consola del navegador para errores
3. Confirma que las variables de entorno estén configuradas
4. Revisa que todas las dependencias estén instaladas

---

**🎨 Diseño**: Fondo negro con máximo contraste  
**✨ Animaciones**: Framer Motion  
**🔒 Validaciones**: En cada paso  
**📱 Responsive**: Mobile-first

