# Documentación Técnica de FigmaToAngular

Este documento proporciona una visión técnica detallada del sistema FigmaToAngular, explicando la arquitectura, los principales algoritmos y las decisiones de diseño.

## Índice
1. [Arquitectura General](#arquitectura-general)
2. [Sistema de Nodos Intermedios](#sistema-de-nodos-intermedios)
3. [Algoritmos de Análisis de Layout](#algoritmos-de-análisis-de-layout)
4. [Generador de Código Angular](#generador-de-código-angular)
5. [Integración con APIs de IA](#integración-con-apis-de-ia)
6. [Manejo de Memoria y Rendimiento](#manejo-de-memoria-y-rendimiento)
7. [Extensibilidad](#extensibilidad)

## Arquitectura General

FigmaToAngular sigue una arquitectura modular con componentes claramente definidos que procesan los datos en una canalización secuencial:

1. **Adquisición de Datos**: 
   - Mediante la API oficial de Figma (`figma_api.py`)
   - A través de cargas de imágenes directas (`image_to_code.py`)

2. **Procesamiento de Diseño**:
   - Transformación a nodos intermedios (`alt_nodes.py`)
   - Análisis estructural para detectar layouts y relaciones espaciales

3. **Generación de Código**:
   - Generador estructural basado en los nodos analizados (`angular_generator.py`)
   - Generador asistido por IA para casos complejos (`code_generator.py`)

4. **Presentación y Exportación**:
   - Vista previa HTML/CSS renderizada
   - Exportación de archivos de componentes Angular

La aplicación emplea un patrón de estrategia que selecciona dinámicamente entre dos enfoques de generación basándose en la complejidad del diseño:

```python
# Selección de estrategia (simplificado)
if design_complexity_requires_enhanced_approach():
    return generate_with_structural_approach()
else:
    return generate_with_ai_approach()
```

## Sistema de Nodos Intermedios

Uno de los aspectos más críticos de la arquitectura es el sistema de nodos intermedios (inspirado en AltNodes de FigmaToCode), que transforma los datos de Figma en una estructura optimizada para el análisis.

### Clase AngularNode

La clase `AngularNode` almacena toda la información necesaria en un formato optimizado:

```python
class AngularNode:
    def __init__(self, figma_node, parent=None):
        self.id = figma_node.get("id", "")
        self.name = self._clean_name(figma_node.get("name", ""))
        self.type = figma_node.get("type", "")
        self.parent = parent
        self.children = []
        
        # Propiedades específicas extraídas del nodo Figma
        self.position = self._extract_position(figma_node)
        self.size = self._extract_size(figma_node)
        self.style = self._extract_style(figma_node) 
        self.layout = self._extract_layout(figma_node)
        self.content = self._extract_content(figma_node)
        
        # Propiedades para la generación de Angular
        self.component_type = self._detect_component_type(figma_node)
        self.is_container = self._determine_if_container(figma_node)
        self.flex_props = {}  # Propiedades Flexbox
        self.grid_props = {}  # Propiedades Grid
```

### Proceso de Conversión

El proceso de conversión a nodos intermedios ocurre en dos fases:

1. **Creación de Nodos**: Cada nodo de Figma se convierte en un `AngularNode`.
2. **Establecimiento de Relaciones**: Se crean las relaciones padre-hijo basadas en los IDs.

```python
# Conversión de nodos simplificada
def convert_to_angular_nodes(figma_nodes):
    node_map = {}  # Mapeo de ID a nodo
    root_nodes = []
    
    # Primera pasada: Crear los nodos
    for node in figma_nodes:
        angular_node = AngularNode(node)
        node_map[angular_node.id] = angular_node
        if "parent_id" not in node:
            root_nodes.append(angular_node)
    
    # Segunda pasada: Establecer relaciones padre-hijo
    for node in figma_nodes:
        if "parent_id" in node and node["parent_id"] in node_map:
            parent = node_map[node["parent_id"]]
            child = node_map[node["id"]]
            parent.add_child(child)
    
    return root_nodes
```

## Algoritmos de Análisis de Layout

El sistema incluye algoritmos sofisticados para detectar automáticamente layouts:

### Detección de Flexbox

Para detectar si un conjunto de nodos hijos debe representarse como un layout Flexbox (horizontal o vertical):

```python
def _children_aligned_horizontally(children):
    # Verificar si los elementos están a la misma altura (Y)
    y_positions = [c.position["y"] for c in children]
    y_avg = sum(y_positions) / len(y_positions)
    aligned = all(abs(y - y_avg) <= MAX_DEVIATION for y in y_positions)
    
    # Verificar distribución horizontal
    if aligned:
        x_positions = [c.position["x"] for c in children]
        return max(x_positions) - min(x_positions) > MIN_DISTRIBUTION
    return False
```

### Detección de Grid

Para estructuras más complejas, se implementa la detección de cuadrículas:

```python
def _appears_to_be_grid(children):
    # Detectar posibles columnas y filas
    x_positions = set(round(c.position["x"] / 10) * 10 for c in children)
    y_positions = set(round(c.position["y"] / 10) * 10 for c in children)
    
    # Verificar si hay múltiples columnas y filas
    return len(x_positions) > 1 and len(y_positions) > 1
```

### Análisis de Espaciado

El análisis también incluye la detección de espaciado consistente entre elementos:

```python
def _calculate_horizontal_spacing(children):
    # Ordenar por posición X
    sorted_children = sorted(children, key=lambda c: c.position["x"])
    
    # Calcular espacios entre elementos adyacentes
    spacings = []
    for i in range(len(sorted_children) - 1):
        curr_right = sorted_children[i].position["x"] + sorted_children[i].size["width"]
        next_left = sorted_children[i+1].position["x"]
        spacings.append(next_left - curr_right)
    
    # Calcular promedio de espacios positivos
    positive_spacings = [s for s in spacings if s > 0]
    return sum(positive_spacings) / len(positive_spacings) if positive_spacings else 0
```

## Generador de Código Angular

El generador de código Angular (`angular_generator.py`) convierte los nodos procesados en código Angular completo:

### Generación de HTML

```python
def _generate_html(self, nodes):
    html_parts = []
    
    # Si hay múltiples nodos raíz, envolverlos en un contenedor
    if len(nodes) > 1:
        html_parts.append('<div class="figma-component-container">')
        for node in nodes:
            html_parts.append(self._generate_node_html(node, 1))
        html_parts.append('</div>')
    elif len(nodes) == 1:
        html_parts.append(self._generate_node_html(nodes[0], 0))
    
    return "\n".join(html_parts)
```

### Generación de SCSS

```python
def _generate_scss(self, nodes):
    scss_parts = []
    
    # Generar variables para tokens de diseño
    if self.colors:
        scss_parts.append("// Design tokens")
        scss_parts.append("// Colors")
        for name, color in self.colors.items():
            variable_name = name.replace(" ", "-").lower()
            scss_parts.append(f"$color-{variable_name}: {color['hex']};")
    
    # Generar estilos para el contenedor principal
    scss_parts.append(".figma-component-container {")
    scss_parts.append("  position: relative;")
    if self.responsive:
        scss_parts.append("  width: 100%;")
        scss_parts.append("  max-width: 1200px;")
        scss_parts.append("  margin: 0 auto;")
    scss_parts.append("}")
    
    # Generar estilos para cada nodo
    for node in nodes:
        scss_parts.append(self._generate_node_scss(node))
    
    return "\n".join(scss_parts)
```

### Detección de Componentes Angular Material

El sistema incluye lógica para convertir elementos de Figma en componentes de Angular Material:

```python
def _detect_component_type(self, node):
    name = node.get("name", "").lower()
    
    # Detección basada en nombres
    if "button" in name or name.endswith("btn"):
        return "mat-button"
    elif "card" in name:
        return "mat-card"
    elif "input" in name or "textfield" in name:
        return "mat-form-field"
    # ... más detecciones
    
    # Detección basada en apariencia
    if node.get("type") == "TEXT" and "style" in node:
        if node["style"].get("fontSize", 0) > 24:
            return "h1"
        # ... más reglas
    
    # Por defecto
    return node.get("type", "div").lower()
```

## Integración con APIs de IA

El proyecto integra con OpenAI y Azure OpenAI para casos donde la generación estructural no es suficiente:

```python
def generate_angular_code_with_ai(figma_data, api_key, model="gpt-4o"):
    # Preparar contexto con información de diseño
    prompt = construct_prompt_from_figma_data(figma_data)
    
    # Llamar a la API
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ANGULAR_GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.2
    )
    
    return response.choices[0].message.content
```

## Manejo de Memoria y Rendimiento

Para garantizar que la aplicación funcione con diseños grandes sin agotar la memoria:

### Límites de Nodos

```python
# Limitar número de nodos para prevenir problemas de memoria
max_safe_nodes = min(node_limit, 500)  # Limitar a un máximo seguro
if len(flattened_nodes) > max_safe_nodes:
    st.warning(f"Diseño contiene {len(flattened_nodes)} nodos. Procesando solo los primeros {max_safe_nodes}...")
    flattened_nodes = flattened_nodes[:max_safe_nodes]
```

### Muestreo para Análisis

```python
# Calcular complejidad con muestreo
complexity_factors = {
    "has_auto_layout": any("layoutMode" in node for node in flattened_nodes[:100]),
    "has_constraints": any("constraints" in node for node in flattened_nodes[:100]),
    # ...
}
```

### Manejo de Errores Robusto

```python
try:
    # Procesamiento de nodos
    # ...
except MemoryError:
    st.error("Error de memoria: El procesamiento requiere demasiados recursos")
    return "// Error: Se produjo un error de memoria. Intente reducir el límite de nodos."
except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    st.error(f"Error en la generación de código: {str(e)}")
    return f"// Error: {str(e)}"
```

## Extensibilidad

El sistema está diseñado para ser extensible en múltiples dimensiones:

### Nuevos Componentes Angular Material

Se pueden añadir fácilmente nuevos componentes de Angular Material:

```python
# En angular_generator.py
def _add_material_import(self, component_type):
    if component_type == "mat-button":
        self.imports.add("MatButtonModule")
    elif component_type == "mat-card":
        self.imports.add("MatCardModule")
    # ... añadir más módulos según sea necesario
```

### Soporte para Otros Frameworks

La arquitectura permite extender el sistema para generar código para otros frameworks:

```python
# Ejemplo conceptual de cómo añadir soporte para React
class ReactGenerator(BaseGenerator):
    def generate(self, nodes, options={}):
        # Implementación específica para React
        # ...
```

### Extensión para Efectos Visuales

```python
# Ejemplo de cómo añadir soporte para efectos visuales adicionales
def _extract_advanced_effects(self, node):
    effects = []
    
    # Detectar efectos de desenfoque
    if "effects" in node and any(e.get("type") == "BLUR" for e in node["effects"]):
        # Procesar efectos de desenfoque
        # ...
    
    # Detectar efectos de superposición
    # ...
    
    return effects
```