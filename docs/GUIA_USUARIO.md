# Guía de Usuario - FigmaToAngular

Esta guía te ayudará a utilizar FigmaToAngular para convertir tus diseños de Figma a código Angular de manera efectiva.

## Índice
1. [Primeros pasos](#primeros-pasos)
2. [Importación desde Figma](#importación-desde-figma)
3. [Importación de imágenes](#importación-de-imágenes)
4. [Configuración avanzada](#configuración-avanzada)
5. [Visualización y exportación](#visualización-y-exportación)
6. [Solución de problemas](#solución-de-problemas)
7. [Preguntas frecuentes](#preguntas-frecuentes)

## Primeros pasos

### Requisitos previos
- API key de OpenAI o Azure OpenAI
- Token de acceso personal de Figma (para la importación directa)
- Python 3.7+ instalado (para ejecución local)

### Instalación local
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/figma-to-angular.git
   cd figma-to-angular
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

### Interfaz principal
![Interfaz Principal](images/interfaz_principal.png)

La interfaz está dividida en dos paneles principales:
- **Panel izquierdo**: Opciones de entrada y configuración
- **Panel derecho**: Resultado y visualización de código generado

## Importación desde Figma

### Obtener un token de acceso personal de Figma
1. Inicia sesión en [Figma](https://www.figma.com/)
2. Ve a Ajustes (icono de engranaje) > Cuenta > Personal access tokens
3. Crea un nuevo token y cópialo (solo se muestra una vez)

### Obtener la clave del archivo Figma
1. Abre tu archivo de diseño en Figma
2. La clave del archivo se encuentra en la URL después de `/file/`
   ```
   https://www.figma.com/file/CLAVE_DEL_ARCHIVO/nombre-del-archivo
   ```

### Importar un diseño
1. Selecciona "Figma API" en la interfaz
2. Ingresa tu token de acceso personal en el panel lateral
3. Ingresa la clave del archivo Figma
4. (Opcional) Ingresa un ID de nodo específico si solo quieres convertir una parte del diseño
5. Haz clic en "Convertir a Angular"

### Opciones de importación
- **Generate Responsive Layout**: Genera código que se adapta a diferentes tamaños de pantalla
- **Use Angular Material Components**: Detecta y utiliza componentes de Angular Material
- **Additional Instructions**: Instrucciones adicionales para la generación de código

## Importación de imágenes

Si no tienes acceso directo a la API de Figma, puedes utilizar la opción de carga de imágenes:

1. Selecciona "Upload Image" en la interfaz
2. Haz clic en "Browse files" para seleccionar una imagen PNG o JPG de tu diseño
3. Configura las opciones adicionales según necesites
4. Haz clic en "Convert Image to Angular"

![Importación de imágenes](images/importacion_imagenes.png)

## Configuración avanzada

### Configuración de API
Puedes configurar la herramienta para usar OpenAI o Azure OpenAI:

- **OpenAI**: Ingresa tu API key en el campo correspondiente
- **Azure OpenAI**: Activa la opción "Use Azure OpenAI" e introduce tu endpoint, API key y nombre del modelo desplegado

### Configuración de nodos
El límite de nodos controla cuántos elementos de diseño procesará la herramienta:

- **Node Limit**: Valor recomendado entre 50-500. Valores más altos pueden generar código más completo pero consumir más recursos.

### Selección de modelo
Puedes elegir entre:

- **GPT-4o**: Mejor calidad, mayor costo
- **GPT-4o-mini**: Equilibrio entre calidad y costo

## Visualización y exportación

### Visualización del código
Una vez generado el código, se mostrará en el panel derecho con tres pestañas principales:

1. **Code**: Muestra el código generado (TypeScript, HTML, SCSS)
2. **Preview**: Visualización del componente generado
3. **History**: Historial de conversiones anteriores
4. **Debug**: Información de depuración (opcional)

### Opciones de exportación
- **Download Angular Components**: Descarga el código completo como archivo de texto
- **Download HTML Preview**: Descarga la vista previa HTML como archivo independiente
- **Download Preview Image**: Descarga la imagen de vista previa del diseño

## Solución de problemas

### Error "Out of Memory"
Si recibes un error de memoria:

1. Reduce el límite de nodos a un valor más bajo (50-100)
2. Intenta convertir una sección más pequeña del diseño (especifica un ID de nodo)
3. Utiliza la opción de carga de imágenes que suele ser menos intensiva en recursos

### Error en la API de Figma
Si no puedes obtener datos de la API de Figma:

1. Verifica que tu token de acceso personal sea correcto y esté vigente
2. Asegúrate de que la clave del archivo sea correcta
3. Comprueba que tengas permisos para acceder al archivo en Figma

### Problemas de calidad en la generación de código
Si el código generado no coincide con el diseño:

1. Intenta añadir instrucciones específicas en el campo "Additional Instructions"
2. Utiliza la opción "Use Angular Material Components" para diseños basados en Material Design
3. Prueba con diferentes modelos de IA

## Preguntas frecuentes

### ¿Puedo utilizar esta herramienta sin API key de OpenAI?
No, actualmente se requiere una API key de OpenAI o Azure OpenAI para la generación de código.

### ¿Qué formato tienen los archivos generados?
La herramienta genera tres archivos principales para cada componente Angular:
- `.component.ts` (TypeScript)
- `.component.html` (HTML)
- `.component.scss` (SCSS)

### ¿Funciona con cualquier diseño de Figma?
La herramienta funciona mejor con diseños que siguen prácticas estándar:
- Uso de Auto Layout
- Elementos agrupados lógicamente
- Componentes claramente nombrados

### ¿Los componentes generados son responsivos?
Sí, cuando se activa la opción "Generate Responsive Layout", el código generado incluirá:
- Media queries para diferentes tamaños de pantalla
- Unidades relativas (%, em, rem)
- Flexbox o CSS Grid según corresponda

### ¿Puedo personalizar los componentes generados?
Absolutamente. El código generado sigue las mejores prácticas de Angular y está estructurado para facilitar la personalización manual posterior.

### ¿Existe algún límite en el uso?
El límite principal está determinado por:
1. La API de Figma (para importación directa)
2. Tu plan de OpenAI (costos de API)
3. Recursos del sistema (memoria, CPU)

Para diseños muy grandes, considera convertir el diseño por secciones.

### ¿Puede generar código para proyectos empresariales?
Sí, la herramienta está diseñada para generar componentes de calidad profesional. Sin embargo, te recomendamos revisar y ajustar el código generado para cumplir con los estándares específicos de tu organización.