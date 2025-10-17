# 📱 Guía Visual del Formulario

Descripción detallada de cada paso del formulario con ejemplos de usuario.

---

## 🎯 Paso 1: Información Demográfica

### Campos:
- **Edad**: Input numérico (15-100 años)
- **Sexo**: Botones tipo toggle (Hombre/Mujer)
- **Departamento**: Dropdown con 22 departamentos de Colombia

### Ejemplo de Usuario:
```
Edad: 35
Sexo: Mujer
Departamento: Bogotá D.C.
```

### Validaciones:
- ✓ Edad debe estar entre 15-100
- ✓ Sexo es obligatorio
- ✓ Departamento es obligatorio

---

## 🎓 Paso 2: Educación

### Campos:
- **Nivel Educativo**: Dropdown (Ninguno/Primaria/Secundaria/Media/Superior)
- **Años de Educación**: Input numérico (0-25)

### Ejemplo de Usuario:
```
Nivel Educativo: Secundaria
Años de Educación: 11
```

### Validaciones:
- ✓ Nivel educativo es obligatorio
- ✓ Años deben estar entre 0-25
- ✓ Coherencia sugerida pero no forzada (ej: secundaria ≈ 11 años)

---

## 🏥 Paso 3: Salud y Seguridad Social

### Campos:
- **¿Está afiliado a salud?**: Toggle Sí/No
- **Tipo de afiliación**: Dropdown (solo si respondió Sí)
  - Contributivo (EPS)
  - Subsidiado (SISBEN)
  - Especial
  - No afiliado
- **¿Requirió atención médica últimos 30 días?**: Toggle Sí/No
- **Gasto en salud**: Input numérico (solo si requirió atención)

### Ejemplo 1: Con atención médica
```
¿Afiliado a salud?: Sí
Tipo de afiliación: Subsidiado
¿Requirió atención médica?: Sí
Gasto en salud: $80,000 COP
```

### Ejemplo 2: Sin atención médica
```
¿Afiliado a salud?: Sí
Tipo de afiliación: Contributivo
¿Requirió atención médica?: No
```

### Validaciones:
- ✓ Afiliación a salud es obligatoria
- ✓ Tipo de afiliación aparece solo si tiene salud
- ✓ Gasto en salud aparece solo si requirió atención
- ✓ Gasto debe ser ≥ 0

---

## 💼 Paso 4: Situación Laboral

### Campos:
- **¿Tiene empleo formal?**: Toggle Sí/No
  - Empleo formal = contrato escrito + seguridad social + prestaciones

### Ejemplo 1: Formal
```
¿Empleo formal?: Sí
```

### Ejemplo 2: Informal
```
¿Empleo formal?: No
```

### Validaciones:
- ✓ Campo es obligatorio

---

## 🏠 Paso 5: Vivienda

### Campos:
- **Tipo de Vivienda**: Dropdown (Casa/Apartamento/Cuarto/Otro)
- **Tenencia**: Dropdown (Propia/Arriendo/Prestada/Otra)
- **Número de Cuartos**: Input numérico (1-20)
- **Personas en el Hogar**: Input numérico (1-20)
- **Material de Pisos**: Dropdown (Cemento/Baldosa/Madera/Tierra/Otro)

### Ejemplo de Usuario:
```
Tipo de Vivienda: Casa
Tenencia: Arriendo
Número de Cuartos: 3
Personas en el Hogar: 5
Material de Pisos: Cemento
```

### Validaciones:
- ✓ Todos los campos son obligatorios
- ✓ Cuartos mínimo 1
- ✓ Personas mínimo 1
- ⚠️ Hacinamiento detectado si: Personas/Cuartos > 3

---

## 🔌 Paso 6: Servicios Públicos

### Campos:
Cada servicio tiene un toggle Sí/No:
- 💧 **Acueducto**
- 🚰 **Alcantarillado**
- 🔥 **Gas Natural**
- 💡 **Energía Eléctrica**
- 🗑️ **Recolección de Basuras**
- **Gasto en Energía**: Input numérico (solo si tiene energía)

### Ejemplo 1: Urbano completo
```
Acueducto: ✓ Sí
Alcantarillado: ✓ Sí
Gas Natural: ✓ Sí
Energía Eléctrica: ✓ Sí
Gasto en Energía: $120,000 COP
Recolección de Basuras: ✓ Sí
```

### Ejemplo 2: Rural limitado
```
Acueducto: ✗ No
Alcantarillado: ✗ No
Gas Natural: ✗ No
Energía Eléctrica: ✓ Sí
Gasto en Energía: $50,000 COP
Recolección de Basuras: ✗ No
```

### Validaciones:
- ✓ Cada toggle puede ser Sí/No independientemente
- ✓ Gasto en energía aparece solo si tiene energía
- ✓ Gasto debe ser ≥ 0

---

## 👨‍👩‍👧‍👦 Paso 7: Composición del Hogar

### Campos:
- **¿Tiene hijos menores de 18 años?**: Toggle Sí/No
- **Número de menores en el hogar**: Input numérico (solo si tiene hijos)

### Ejemplo 1: Con menores
```
¿Tiene hijos menores?: Sí
Número de menores: 2
```

### Ejemplo 2: Sin menores
```
¿Tiene hijos menores?: No
```

### Validaciones:
- ✓ Campo es obligatorio
- ✓ Número de menores aparece solo si tiene hijos
- ✓ Debe ser entre 0-10

---

## 🎯 Pantalla Final: Análisis

Al hacer clic en **"Analizar"**, el sistema:

1. ✅ Valida todos los campos
2. 📤 Envía datos a la API
3. ⏳ Muestra spinner de carga
4. 📊 Recibe predicción
5. 🎨 Visualiza resultados

---

## 📊 Resultados: 4 Posibles Niveles

### 🟢 Riesgo Bajo (0-25% probabilidad)
```
Estado: ✅ No Vulnerable
Probabilidad: 18.5%
Nivel de Riesgo: BAJO
Mensaje: "Situación económica estable"

Colores: Verde brillante
```

### 🟡 Riesgo Medio (25-50% probabilidad)
```
Estado: ✅ No Vulnerable
Probabilidad: 42.3%
Nivel de Riesgo: MEDIO
Mensaje: "Situación estable pero con factores de riesgo. Monitoreo recomendado."

Colores: Amarillo
```

### 🟠 Riesgo Alto (50-75% probabilidad)
```
Estado: ⚠️ Vulnerable
Probabilidad: 65.8%
Nivel de Riesgo: ALTO
Mensaje: "Situación de vulnerabilidad detectada. Considere programas de apoyo."

Colores: Naranja
```

### 🔴 Riesgo Muy Alto (75-100% probabilidad)
```
Estado: 🚨 Vulnerable
Probabilidad: 89.2%
Nivel de Riesgo: MUY ALTO
Mensaje: "Alta vulnerabilidad económica. Urgente considerar programas sociales."

Colores: Rojo intenso
```

---

## 🎨 Elementos Visuales

### Barra de Progreso
- Se actualiza en cada paso
- Gradiente azul → púrpura
- Muestra "Paso X de 7" y porcentaje

### Animaciones
- ✨ Fade in al cambiar de paso
- 🌀 Gradientes rotando en fondo
- 💫 Hover effects en botones
- 🔄 Loading spinner durante predicción

### Mensajes de Error
- 🔴 Fondo rojo semi-transparente
- ⚠️ Icono de advertencia
- Texto claro y específico
- Aparece arriba del formulario

### Botones
- **Anterior**: Gris, habilitado desde paso 2
- **Siguiente**: Gradiente azul-púrpura
- **Analizar**: Gradiente verde-esmeralda (paso 7)
- **Nuevo Análisis**: Azul-púrpura (pantalla resultados)

---

## 📱 Responsive Design

### Desktop (>1024px)
- Formulario centrado, ancho máximo 4xl
- Dos columnas en algunos campos
- Header con logo + info del modelo

### Tablet (768-1024px)
- Formulario centrado, ancho máximo 3xl
- Una columna para todos los campos
- Header simplificado

### Mobile (<768px)
- Formulario full width con padding
- Botones apilados verticalmente
- Font sizes ajustados
- Touch-friendly (botones más grandes)

---

## ✅ Checklist de Testing

Prueba cada paso:

- [ ] **Paso 1**: Cambia edad, sexo y departamento
- [ ] **Paso 2**: Prueba diferentes niveles educativos
- [ ] **Paso 3**: Toggle salud Sí/No y verifica campos condicionales
- [ ] **Paso 4**: Toggle empleo formal
- [ ] **Paso 5**: Ingresa diferentes números de cuartos/personas
- [ ] **Paso 6**: Activa/desactiva servicios
- [ ] **Paso 7**: Toggle hijos menores y verifica campo condicional
- [ ] **Validaciones**: Intenta valores inválidos (negativos, fuera de rango)
- [ ] **Navegación**: Usa botones Anterior/Siguiente
- [ ] **Submit**: Click en Analizar y verifica resultados
- [ ] **Reset**: Click en Nuevo Análisis y verifica que se reinicie

---

## 🎯 Casos de Uso Ejemplo

### Caso 1: Persona Vulnerable
```
📋 Demográficas:
  Edad: 28
  Sexo: Mujer
  Departamento: Bolívar

🎓 Educación:
  Nivel: Primaria
  Años: 5

🏥 Salud:
  Afiliado: Sí
  Tipo: Subsidiado
  Atención médica: Sí
  Gasto: $120,000

💼 Trabajo:
  Empleo formal: No

🏠 Vivienda:
  Tipo: Cuarto
  Tenencia: Arriendo
  Cuartos: 2
  Personas: 6
  Pisos: Tierra

🔌 Servicios:
  Acueducto: No
  Alcantarillado: No
  Gas: No
  Energía: Sí ($30,000)
  Basuras: No

👨‍👩‍👧‍👦 Hogar:
  Hijos menores: Sí
  Número: 3

RESULTADO ESPERADO: 🔴 Riesgo Alto/Muy Alto (>65%)
```

### Caso 2: Persona Estable
```
📋 Demográficas:
  Edad: 38
  Sexo: Hombre
  Departamento: Bogotá D.C.

🎓 Educación:
  Nivel: Superior
  Años: 16

🏥 Salud:
  Afiliado: Sí
  Tipo: Contributivo
  Atención médica: No

💼 Trabajo:
  Empleo formal: Sí

🏠 Vivienda:
  Tipo: Apartamento
  Tenencia: Propia
  Cuartos: 4
  Personas: 3
  Pisos: Baldosa

🔌 Servicios:
  Acueducto: Sí
  Alcantarillado: Sí
  Gas: Sí
  Energía: Sí ($150,000)
  Basuras: Sí

👨‍👩‍👧‍👦 Hogar:
  Hijos menores: Sí
  Número: 1

RESULTADO ESPERADO: 🟢 Riesgo Bajo (<25%)
```

---

## 📖 Glosario de Términos

- **Empleo Formal**: Contrato escrito + seguridad social + prestaciones
- **Hacinamiento**: Más de 3 personas por cuarto
- **Vulnerabilidad**: Situación de riesgo socioeconómico
- **IPM**: Índice de Pobreza Multidimensional
- **GEIH**: Gran Encuesta Integrada de Hogares (DANE)
- **Umbral**: Punto de corte para clasificación (0.5263)
- **Recall**: Porcentaje de vulnerables correctamente detectados (92%)

---

**🎨 Diseñado con**: React + TypeScript + Tailwind CSS + Framer Motion  
**🔒 Validaciones**: En cada campo y paso  
**📱 Responsive**: Desktop, Tablet, Mobile  
**♿ Accesibilidad**: Contraste AAA (WCAG)

