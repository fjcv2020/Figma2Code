# Referencia de Módulos - FigmaToAngular

Esta documentación proporciona detalles técnicos sobre cada módulo del sistema FigmaToAngular.

## Índice
1. [app.py - Interfaz Principal](#apppy---interfaz-principal)
2. [figma_api.py - Cliente de API Figma](#figma_apipy---cliente-de-api-figma)
3. [alt_nodes.py - Sistema de Nodos Intermedios](#alt_nodespy---sistema-de-nodos-intermedios)
4. [angular_generator.py - Generador de Código Angular](#angular_generatorpy---generador-de-código-angular)
5. [enhanced_generator.py - Integrador de Generación](#enhanced_generatorpy---integrador-de-generación)
6. [code_generator.py - Generador basado en IA](#code_generatorpy---generador-basado-en-ia)
7. [image_to_code.py - Conversión de Imágenes](#image_to_codepy---conversión-de-imágenes)
8. [utils.py - Utilidades Generales](#utilspy---utilidades-generales)
9. [cost_estimator.py - Estimador de Costos](#cost_estimatorpy---estimador-de-costos)
10. [api_tools.py - Herramientas de API](#api_toolspy---herramientas-de-api)

---

## app.py - Interfaz Principal

El módulo principal que configura la interfaz de usuario de Streamlit y coordina las interacciones entre los distintos componentes.

### Componentes principales:
- Configuración de la interfaz de Streamlit
- Manejo de sesiones y estados
- Instanciación de módulos de procesamiento
- Coordinación del flujo de trabajo

### Funciones clave:
- `main()`: Punto de entrada de la aplicación
- Configuración de las secciones de la UI
- Lógica de manejo de métodos de entrada (Figma API / imagen)
- Procesamiento de resultados y visualización

### Ejemplo de uso:
```bash
streamlit run app.py
```

---

## figma_api.py - Cliente de API Figma

Cliente para interactuar con la API oficial de Figma.

### Funcionalidades:
- Autenticación con la API de Figma
- Recuperación de datos de archivos y nodos
- Obtención de imágenes de vista previa
- Procesamiento y limpieza de datos

### Clase principal:
#### `FigmaAPI`
- **Métodos**:
  - `get_file(file_key, node_id=None)`: Obtiene datos de un archivo Figma
  - `get_image_urls(file_key, ids, scale=1)`: Obtiene URLs de imágenes
  - `get_style_metadata(file_key)`: Obtiene metadatos de estilos
  - `extract_colors(document)`: Extrae estilos de color

### Ejemplo de uso:
```python
figma_api = FigmaAPI(access_token)
file_data = figma_api.get_file(file_key, node_id)
image_urls = figma_api.get_image_urls(file_key, [node_id])
```

---

## alt_nodes.py - Sistema de Nodos Intermedios

Implementa el sistema de representación intermedia para el análisis de diseño.

### Componentes principales:

#### Clase `AngularNode`
Representa un nodo de diseño en formato optimizado para generación de código Angular.

- **Propiedades**:
  - `id`: Identificador único del nodo
  - `name`: Nombre descriptivo (limpiado para uso en código)
  - `type`: Tipo de nodo (FRAME, TEXT, VECTOR, etc.)
  - `parent`: Referencia al nodo padre
  - `children`: Lista de nodos hijos
  - `position`: Datos de posición (x, y, position)
  - `size`: Datos de tamaño (width, height, tipos)
  - `style`: Propiedades visuales (fills, strokes, etc.)
  - `layout`: Información de layout (tipo, dirección, espaciado)
  - `content`: Contenido específico del nodo
  - `component_type`: Tipo de componente Angular/Material
  - `flex_props`: Propiedades CSS Flexbox
  - `grid_props`: Propiedades CSS Grid

- **Métodos**:
  - `_clean_name(name)`: Limpia un nombre para uso como identificador
  - `_extract_position(node)`: Extrae datos de posición
  - `_extract_size(node)`: Extrae datos de tamaño
  - `_extract_style(node)`: Extrae propiedades visuales
  - `_extract_radius(node)`: Extrae border-radius
  - `_extract_layout(node)`: Extrae configuración de layout
  - `_extract_content(node)`: Extrae contenido específico
  - `_detect_component_type(node)`: Detecta tipo de componente Angular
  - `add_child(child)`: Añade un nodo hijo
  - `to_dict()`: Serializa a diccionario para depuración

#### Funciones de conversión
- `convert_to_angular_nodes(figma_nodes)`: Convierte nodos Figma a AngularNodes

#### Funciones de análisis de layout
- `analyze_layout(nodes)`: Analiza layout de nodos raíz
- `_analyze_node_layout(node)`: Analiza layout de un nodo individual
- `_children_aligned_horizontally(children)`: Detecta alineación horizontal
- `_children_aligned_vertically(children)`: Detecta alineación vertical
- `_calculate_horizontal_spacing(children)`: Calcula espaciado horizontal
- `_calculate_vertical_spacing(children)`: Calcula espaciado vertical
- `_detect_vertical_alignment(children)`: Detecta tipo de alineación vertical
- `_detect_horizontal_alignment(children)`: Detecta tipo de alineación horizontal
- `_appears_to_be_grid(children)`: Detecta estructura de cuadrícula
- `_detect_grid_dimensions(children)`: Detecta columnas y filas
- `_calculate_grid_gaps(children, cols, rows)`: Calcula espaciado en grid

### Ejemplo de uso:
```python
# Convertir nodos Figma a representación intermedia
angular_nodes = convert_to_angular_nodes(flattened_nodes)

# Analizar layout 
analyze_layout(angular_nodes)
```

---

## angular_generator.py - Generador de Código Angular

Genera código Angular basado en los nodos intermedios analizados.

### Clase principal:
#### `AngularGenerator`
Genera código TypeScript, HTML y SCSS optimizado para Angular.

- **Propiedades**:
  - `use_material`: Si detectar/generar componentes Angular Material
  - `responsive`: Si generar layouts responsivos
  - `component_name`: Nombre del componente a generar
  - `component_selector`: Selector CSS del componente
  - `imports`: Conjunto de importaciones Angular Material
  - `colors`: Diccionario de colores extraídos
  - `text_styles`: Diccionario de estilos de texto

- **Métodos principales**:
  - `generate(nodes, options)`: Genera todo el código del componente
  - `_generate_html(nodes)`: Genera código HTML
  - `_generate_scss(nodes)`: Genera estilos SCSS
  - `_generate_typescript(nodes)`: Genera código TypeScript
  - `_generate_node_html(node, indent_level)`: Genera HTML para un nodo individual
  - `_generate_node_scss(node)`: Genera SCSS para un nodo individual
  - `_get_element_tag(node)`: Determina la etiqueta HTML para un nodo
  - `_get_class_name(node)`: Genera nombre de clase CSS
  - `_add_material_import(component_type)`: Añade importación de Angular Material
  - `_extract_design_tokens(nodes)`: Extrae tokens de diseño (colores, tipografía)
  - `_extract_colors(node)`: Extrae colores de un nodo
  - `_to_class_name(kebab_name)`: Convierte nombres kebab-case a PascalCase

### Ejemplo de uso:
```python
generator = AngularGenerator(use_material=True, responsive=True)
code_files = generator.generate(angular_nodes, {"component_name": "my-component"})

html_code = code_files["html"]
scss_code = code_files["scss"]
ts_code = code_files["ts"]
```

---

## enhanced_generator.py - Integrador de Generación

Módulo que integra los diferentes enfoques de generación y determina cuál utilizar.

### Funciones principales:
- `generate_enhanced_angular_code(figma_data, responsive, use_material, additional_instructions, node_limit)`: Genera código Angular usando el enfoque estructural
- `process_figma_with_mixed_approach(figma_data, openai_api_key, ...)`: Determina qué enfoque de generación usar

### Lógica de selección:
El sistema selecciona automáticamente el mejor enfoque basándose en factores como:
- Presencia de Auto Layout
- Uso de restricciones (constraints)
- Complejidad del diseño
- Preferencias del usuario (uso de Material UI)

### Optimizaciones implementadas:
- Límites de seguridad para nodos
- Manejo robusto de errores
- Logging detallado
- Protección contra problemas de memoria

### Ejemplo de uso:
```python
code = process_figma_with_mixed_approach(
    file_data,
    openai_api_key=api_key,
    responsive=True,
    use_material=True,
    node_limit=300
)
```

---

## code_generator.py - Generador basado en IA

Módulo para generar código utilizando modelos de IA (OpenAI o Azure).

### Función principal:
- `generate_angular_code(figma_data, responsive, additional_instructions, use_azure, azure_endpoint, azure_model, node_limit, openai_model)`: Genera código Angular usando OpenAI/Azure

### Funcionalidades:
- Construcción automática de prompts óptimos
- Manejo de tokens y límites de tamaño
- Soporte para OpenAI y Azure OpenAI
- Integración de instrucciones personalizadas

### Ejemplo de uso:
```python
code = generate_angular_code(
    figma_data,
    responsive=True,
    additional_instructions="Use Material Design principles",
    openai_model="gpt-4o"
)
```

---

## image_to_code.py - Conversión de Imágenes

Módulo para procesar imágenes y convertirlas a código Angular.

### Funciones principales:
- `encode_image_to_base64(image_file)`: Codifica imagen para envío a API
- `resize_image_if_needed(image_file, max_size)`: Redimensiona imágenes grandes
- `generate_angular_from_image(image_file, responsive, additional_instructions, ...)`: Genera código a partir de una imagen

### Proceso:
1. Carga y preprocesamiento de imagen
2. Codificación para API Vision
3. Construcción de prompt especializado
4. Generación de código con OpenAI/Azure
5. Post-procesamiento de resultados

### Ejemplo de uso:
```python
code = generate_angular_from_image(
    uploaded_file,
    responsive=True,
    additional_instructions="Create a responsive grid layout",
    openai_model="gpt-4o"
)
```

---

## utils.py - Utilidades Generales

Funciones de utilidad general para el proyecto.

### Funciones principales:
- `save_file(file_path, content)`: Guarda contenido en un archivo
- `read_file(file_path)`: Lee contenido de un archivo
- `validate_inputs(file_key, access_token, openai_api_key)`: Valida entradas de usuario
- `extract_nodes(document)`: Extrae nodos de un documento Figma
- `flatten_figma_tree(nodes)`: Aplana la estructura jerárquica de nodos
- `rgb_to_hex(r, g, b)`: Convierte colores RGB a hexadecimal
- `extract_text_styles(nodes)`: Extrae estilos de texto de nodos

### Ejemplo de uso:
```python
# Validar entradas
valid, error_message = validate_inputs(file_key, access_token, openai_api_key)

# Extraer y aplanar nodos
figma_nodes = extract_nodes(document)
flattened_nodes = flatten_figma_tree(figma_nodes)

# Guardar resultados
save_file("output.txt", generated_code)
```

---

## cost_estimator.py - Estimador de Costos

Módulo para estimar costos de API según el uso.

### Funciones principales:
- `estimate_cost_per_thousand_tokens(model)`: Devuelve costo por 1000 tokens
- `estimate_tokens_from_nodes(node_count, avg_complexity)`: Estima tokens según nodos
- `estimate_cost(node_count, model, avg_complexity)`: Estima costo total

### Ejemplo de uso:
```python
cost_estimate = estimate_cost(350, "gpt-4o", avg_complexity=1.2)
print(f"Costo estimado: ${cost_estimate['total_cost']:.4f}")
```

---

## api_tools.py - Herramientas de API

Funciones auxiliares para trabajo con APIs.

### Funciones principales:
- `export_to_json(figma_data, output_path)`: Exporta datos de Figma a JSON
- `extract_specific_nodes(figma_data, node_types, max_depth)`: Extrae nodos específicos
- `get_figma_node_structure(figma_api, file_key, node_id)`: Obtiene estructura similar a v0/Lovable

### Ejemplo de uso:
```python
# Extraer solo nodos FRAME y TEXT
frames_and_texts = extract_specific_nodes(figma_data, ["FRAME", "TEXT"])

# Exportar a formato compatible con .jam
export_to_json(figma_data, "exported_design.json")
```