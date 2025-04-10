"""
Generador de código Angular optimizado con soporte para Angular Material
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple
from alt_nodes import AngularNode


class AngularGenerator:
    """
    Generador de código optimizado para Angular basado en AltNodes
    """
    def __init__(self, use_material: bool = True, responsive: bool = True):
        self.use_material = use_material
        self.responsive = responsive
        self.component_name = "figma-component"
        self.component_selector = "app-figma-component"
        self.warnings = []
        self.imports = set()  # Conjunto para mantener los imports
        
        # Variables extraídas del diseño
        self.colors = {}
        self.text_styles = {}
        
    def generate(self, nodes: List[AngularNode], options: Dict = {}) -> Dict[str, str]:
        """
        Genera código Angular completo para los nodos proporcionados
        
        Args:
            nodes: Lista de nodos AngularNode raíz
            options: Opciones adicionales (nombre_componente, etc.)
            
        Returns:
            Dict con claves 'ts', 'html', 'scss' para los diferentes archivos
        """
        if options:
            if "component_name" in options:
                self.component_name = self._format_component_name(options["component_name"])
                self.component_selector = f"app-{self.component_name}"
        
        # Extraer colores y estilos
        self._extract_design_tokens(nodes)
        
        # Generar HTML, TS y SCSS
        html = self._generate_html(nodes)
        scss = self._generate_scss(nodes)
        ts = self._generate_typescript(nodes)
        
        return {
            "ts": ts,
            "html": html,
            "scss": scss
        }
    
    def _format_component_name(self, name: str) -> str:
        """Formatea un nombre de componente"""
        # Convertir a kebab-case para el selector
        kebab = re.sub(r'[^a-zA-Z0-9]', '-', name.lower())
        kebab = re.sub(r'-+', '-', kebab).strip('-')
        return kebab
    
    def _extract_design_tokens(self, nodes: List[AngularNode]):
        """Extrae tokens de diseño (colores, tipografía) de los nodos"""
        # Extraer colores
        for node in nodes:
            self._extract_colors(node)
            
            # Recursivamente procesar hijos
            for child in node.children:
                self._extract_design_tokens([child])
                
    def _extract_colors(self, node: AngularNode):
        """Extrae colores de un nodo"""
        # Extraer colores de fills
        for fill in node.style.get("fills", []):
            if fill.get("type") == "color" and "hex" in fill:
                color_hex = fill["hex"]
                # Generar un nombre para el color
                color_name = f"color-{len(self.colors) + 1}"
                if node.name:
                    color_name = f"{node.name}-color"
                
                # Añadir color si no existe ya
                if color_hex not in [c["hex"] for c in self.colors.values()]:
                    self.colors[color_name] = {
                        "hex": color_hex,
                        "rgba": fill.get("color", "")
                    }
        
        # Extraer colores de strokes
        for stroke in node.style.get("strokes", []):
            if "hex" in stroke:
                color_hex = stroke["hex"]
                # Generar un nombre para el color
                color_name = f"stroke-{len(self.colors) + 1}"
                if node.name:
                    color_name = f"{node.name}-stroke"
                
                # Añadir color si no existe ya
                if color_hex not in [c["hex"] for c in self.colors.values()]:
                    self.colors[color_name] = {
                        "hex": color_hex,
                        "rgba": stroke.get("color", "")
                    }
        
        # Extraer colores de texto
        if "text" in node.style and node.style.get("fills", []):
            text_fill = node.style["fills"][0]
            if "hex" in text_fill:
                color_hex = text_fill["hex"]
                color_name = f"text-{len(self.colors) + 1}"
                if node.name:
                    color_name = f"{node.name}-text"
                
                # Añadir color si no existe ya
                if color_hex not in [c["hex"] for c in self.colors.values()]:
                    self.colors[color_name] = {
                        "hex": color_hex,
                        "rgba": text_fill.get("color", "")
                    }
        
        # Extraer colores de efectos (sombras)
        for effect in node.style.get("effects", []):
            if effect.get("type") == "shadow" and "color" in effect:
                color_name = f"shadow-{len(self.colors) + 1}"
                rgba_color = effect["color"]
                
                # Extraer valores RGBA
                rgba_match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', rgba_color)
                if rgba_match:
                    r, g, b, a = rgba_match.groups()
                    hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                    
                    # Añadir color si no existe ya
                    if hex_color not in [c["hex"] for c in self.colors.values()]:
                        self.colors[color_name] = {
                            "hex": hex_color,
                            "rgba": rgba_color
                        }
    
    def _generate_html(self, nodes: List[AngularNode]) -> str:
        """
        Genera el HTML para los nodos proporcionados
        
        Args:
            nodes: Lista de nodos AngularNode
            
        Returns:
            String con el código HTML
        """
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
    
    def _generate_node_html(self, node: AngularNode, indent_level: int) -> str:
        """
        Genera el HTML para un nodo individual
        
        Args:
            node: Nodo a procesar
            indent_level: Nivel de indentación
            
        Returns:
            String con el HTML para este nodo
        """
        indent = "  " * indent_level
        class_name = self._get_class_name(node)
        element = self._get_element_tag(node)
        
        # Atributos base
        attributes = []
        
        # Para los componentes de Angular Material, aplicar las propiedades necesarias
        if node.component_type.startswith("mat-") and self.use_material:
            self._add_material_import(node.component_type)
            
            # Atributos específicos según el tipo de componente
            if node.component_type == "mat-button":
                attributes.append('mat-raised-button color="primary"')
                
                # Si es un botón, el contenido es el texto
                content = node.style.get("text", {}).get("content", "Button")
                html = f'{indent}<button {" ".join(attributes)} class="{class_name}">{content}</button>'
                return html
                
            elif node.component_type == "mat-card":
                attributes.append('class="mat-elevation-z2"')
                
                # Estructura de card
                html_parts = [f'{indent}<mat-card {" ".join(attributes)} class="{class_name}">']
                
                # Si tiene hijos, procesarlos
                if node.children:
                    # El primer hijo con texto podría ser el título de la tarjeta
                    title_node = next((c for c in node.children if c.type == "TEXT" and c.style.get("text", {})), None)
                    if title_node:
                        title_content = title_node.style.get("text", {}).get("content", "")
                        html_parts.append(f'{indent}  <mat-card-header>')
                        html_parts.append(f'{indent}    <mat-card-title>{title_content}</mat-card-title>')
                        html_parts.append(f'{indent}  </mat-card-header>')
                        
                        # Procesar los demás hijos como contenido
                        html_parts.append(f'{indent}  <mat-card-content>')
                        for child in node.children:
                            if child != title_node:  # Evitar duplicar el título
                                html_parts.append(self._generate_node_html(child, indent_level + 2))
                        html_parts.append(f'{indent}  </mat-card-content>')
                    else:
                        # Sin título específico, todos los hijos van al contenido
                        html_parts.append(f'{indent}  <mat-card-content>')
                        for child in node.children:
                            html_parts.append(self._generate_node_html(child, indent_level + 2))
                        html_parts.append(f'{indent}  </mat-card-content>')
                
                html_parts.append(f'{indent}</mat-card>')
                return "\n".join(html_parts)
                
            elif node.component_type == "mat-form-field":
                # Input field
                content = node.style.get("text", {}).get("content", "")
                placeholder = content if content else "Enter text"
                
                html_parts = [f'{indent}<mat-form-field class="{class_name}">']
                html_parts.append(f'{indent}  <mat-label>{placeholder}</mat-label>')
                html_parts.append(f'{indent}  <input matInput>')
                html_parts.append(f'{indent}</mat-form-field>')
                return "\n".join(html_parts)
                
            elif node.component_type == "mat-select":
                placeholder = node.style.get("text", {}).get("content", "Select")
                
                html_parts = [f'{indent}<mat-form-field class="{class_name}">']
                html_parts.append(f'{indent}  <mat-label>{placeholder}</mat-label>')
                html_parts.append(f'{indent}  <mat-select>')
                
                # Si tiene hijos, usarlos como opciones
                if node.children:
                    for i, child in enumerate(node.children):
                        content = child.style.get("text", {}).get("content", f"Option {i+1}")
                        html_parts.append(f'{indent}    <mat-option value="{i}">{content}</mat-option>')
                else:
                    # Opciones de ejemplo
                    html_parts.append(f'{indent}    <mat-option value="1">Option 1</mat-option>')
                    html_parts.append(f'{indent}    <mat-option value="2">Option 2</mat-option>')
                
                html_parts.append(f'{indent}  </mat-select>')
                html_parts.append(f'{indent}</mat-form-field>')
                return "\n".join(html_parts)
                
            elif node.component_type == "mat-tab-group":
                html_parts = [f'{indent}<mat-tab-group class="{class_name}">']
                
                # Cada hijo podría ser una tab
                if node.children:
                    for i, child in enumerate(node.children):
                        tab_label = child.name or f"Tab {i+1}"
                        html_parts.append(f'{indent}  <mat-tab label="{tab_label}">')
                        
                        # Si el hijo tiene contenido
                        if child.children:
                            html_parts.append(f'{indent}    <div class="tab-content">')
                            for grandchild in child.children:
                                html_parts.append(self._generate_node_html(grandchild, indent_level + 3))
                            html_parts.append(f'{indent}    </div>')
                        
                        html_parts.append(f'{indent}  </mat-tab>')
                else:
                    # Tabs de ejemplo
                    html_parts.append(f'{indent}  <mat-tab label="Tab 1">')
                    html_parts.append(f'{indent}    <div class="tab-content">Tab 1 Content</div>')
                    html_parts.append(f'{indent}  </mat-tab>')
                    html_parts.append(f'{indent}  <mat-tab label="Tab 2">')
                    html_parts.append(f'{indent}    <div class="tab-content">Tab 2 Content</div>')
                    html_parts.append(f'{indent}  </mat-tab>')
                
                html_parts.append(f'{indent}</mat-tab-group>')
                return "\n".join(html_parts)
        
        # Elementos estándar
        if element in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "strong", "em"]:
            content = node.style.get("text", {}).get("content", "")
            return f'{indent}<{element} class="{class_name}">{content}</{element}>'
            
        # Si es un div o elemento estándar
        html_parts = [f'{indent}<{element} class="{class_name}">']
        
        # Si tiene hijos, procesarlos
        if node.children:
            for child in node.children:
                html_parts.append(self._generate_node_html(child, indent_level + 1))
        # Si es texto, añadir el contenido
        elif node.type == "TEXT":
            content = node.style.get("text", {}).get("content", "")
            html_parts = [f'{indent}<{element} class="{class_name}">{content}']
        
        html_parts.append(f'{indent}</{element}>')
        return "\n".join(html_parts)
    
    def _get_element_tag(self, node: AngularNode) -> str:
        """Determina la etiqueta HTML apropiada para el nodo"""
        # Si es un componente de Material UI, usar el tag específico
        if node.component_type.startswith("mat-") and self.use_material:
            if node.component_type == "mat-button":
                return "button"
            elif node.component_type == "mat-card":
                return "mat-card"
            elif node.component_type == "mat-form-field":
                return "mat-form-field"
            elif node.component_type == "mat-select":
                return "mat-form-field"
            elif node.component_type == "mat-tab-group":
                return "mat-tab-group"
            # Añadir más componentes según sea necesario
        
        # Mapear tipos de nodo a elementos HTML
        if node.type == "TEXT":
            # Determinar el tipo de texto según el tamaño
            font_size = node.style.get("text", {}).get("fontSize", 16)
            if font_size >= 32:
                return "h1"
            elif font_size >= 24:
                return "h2"
            elif font_size >= 18:
                return "h3"
            elif font_size >= 16:
                return "p"
            else:
                return "span"
            
        elif node.component_type in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "strong", "em"]:
            return node.component_type
            
        # Por defecto, usar divs
        return "div"
    
    def _get_class_name(self, node: AngularNode) -> str:
        """Genera un nombre de clase CSS para el nodo"""
        base_class = node.name
        
        # Si no hay nombre específico, usar el tipo
        if not base_class:
            base_class = node.type.lower()
            
        return f"{base_class}-element"
    
    def _add_material_import(self, component_type: str):
        """Añade la importación necesaria para un componente de Material"""
        if component_type == "mat-button":
            self.imports.add("MatButtonModule")
        elif component_type == "mat-card":
            self.imports.add("MatCardModule")
        elif component_type == "mat-form-field":
            self.imports.add("MatFormFieldModule")
        elif component_type == "mat-select":
            self.imports.add("MatSelectModule")
            self.imports.add("MatFormFieldModule")
        elif component_type == "mat-tab-group":
            self.imports.add("MatTabsModule")
        # Añadir más importaciones según sea necesario
    
    def _generate_scss(self, nodes: List[AngularNode]) -> str:
        """
        Genera el código SCSS para los nodos proporcionados
        
        Args:
            nodes: Lista de nodos AngularNode
            
        Returns:
            String con el código SCSS
        """
        scss_parts = []
        
        # Generar variables SCSS para los colores extraídos
        if self.colors:
            scss_parts.append("// Design tokens")
            scss_parts.append("// Colors")
            for name, color in self.colors.items():
                variable_name = name.replace(" ", "-").lower()
                scss_parts.append(f"$color-{variable_name}: {color['hex']};")
            scss_parts.append("")
        
        # Estilos para el contenedor principal
        scss_parts.append(".figma-component-container {")
        scss_parts.append("  position: relative;")
        if self.responsive:
            scss_parts.append("  width: 100%;")
            scss_parts.append("  max-width: 1200px;")
            scss_parts.append("  margin: 0 auto;")
        scss_parts.append("}")
        scss_parts.append("")
        
        # Generar estilos para cada nodo
        for node in nodes:
            scss_parts.append(self._generate_node_scss(node))
        
        return "\n".join(scss_parts)
    
    def _generate_node_scss(self, node: AngularNode) -> str:
        """
        Genera el SCSS para un nodo individual
        
        Args:
            node: Nodo a procesar
            
        Returns:
            String con el SCSS para este nodo
        """
        class_name = self._get_class_name(node)
        scss_parts = [f".{class_name} {{"]
        
        # Position
        position_type = node.position.get("position", "relative")
        scss_parts.append(f"  position: {position_type};")
        
        # Si es absolute, añadir top/left
        if position_type == "absolute":
            scss_parts.append(f"  top: {node.position['y']}px;")
            scss_parts.append(f"  left: {node.position['x']}px;")
        
        # Size
        if node.size["width_type"] == "fixed":
            scss_parts.append(f"  width: {node.size['width']}px;")
        elif self.responsive:
            scss_parts.append("  width: 100%;")
        
        if node.size["height_type"] == "fixed":
            scss_parts.append(f"  height: {node.size['height']}px;")
        
        # Layout (Flex o Grid)
        if node.flex_props:
            for prop, value in node.flex_props.items():
                scss_parts.append(f"  {prop}: {value};")
        elif node.grid_props:
            for prop, value in node.grid_props.items():
                scss_parts.append(f"  {prop}: {value};")
        
        # Padding
        if node.layout["type"] == "auto-layout":
            padding = node.layout["padding"]
            if any(padding.values()):
                padding_values = []
                for side in ["top", "right", "bottom", "left"]:
                    padding_values.append(f"{padding[side]}px")
                scss_parts.append(f"  padding: {' '.join(padding_values)};")
        
        # Background
        if node.style.get("fills"):
            for fill in node.style["fills"]:
                if fill["type"] == "color":
                    color_name = None
                    # Buscar si este color está en nuestras variables
                    for name, color in self.colors.items():
                        if color["hex"] == fill["hex"]:
                            color_name = f"$color-{name.replace(' ', '-').lower()}"
                            break
                    
                    if color_name:
                        scss_parts.append(f"  background-color: {color_name};")
                    else:
                        scss_parts.append(f"  background-color: {fill['color']};")
                    break
                elif fill["type"] == "gradient" and fill["gradientType"] == "linear":
                    # Implementación básica de gradiente
                    scss_parts.append("  background: linear-gradient(to bottom, #ffffff, #f0f0f0);")
                    scss_parts.append("  // Note: Gradient implementation is approximate")
                    break
        
        # Border
        if node.style.get("strokes"):
            for stroke in node.style["strokes"]:
                scss_parts.append(f"  border: {stroke['weight']}px {stroke['style']} {stroke['color']};")
                break  # Solo usar el primer stroke
        
        # Border radius
        if isinstance(node.style["radius"], (int, float)) and node.style["radius"] > 0:
            scss_parts.append(f"  border-radius: {node.style['radius']}px;")
        elif isinstance(node.style["radius"], dict):
            radius = node.style["radius"]
            scss_parts.append(f"  border-radius: {radius['topLeft']}px {radius['topRight']}px {radius['bottomRight']}px {radius['bottomLeft']}px;")
        
        # Shadow effects
        if node.style.get("effects"):
            for effect in node.style["effects"]:
                if effect["type"] == "shadow":
                    x = effect["offset"]["x"]
                    y = effect["offset"]["y"]
                    blur = effect["radius"]
                    spread = effect.get("spread", 0)
                    color = effect["color"]
                    scss_parts.append(f"  box-shadow: {x}px {y}px {blur}px {spread}px {color};")
        
        # Text styles
        if "text" in node.style:
            text_style = node.style["text"]
            scss_parts.append(f"  font-family: {text_style['fontFamily']}, sans-serif;")
            scss_parts.append(f"  font-size: {text_style['fontSize']}px;")
            scss_parts.append(f"  font-weight: {text_style['fontWeight']};")
            scss_parts.append(f"  text-align: {text_style['textAlign']};")
            
            if text_style['fontStyle'] != "normal":
                scss_parts.append(f"  font-style: {text_style['fontStyle']};")
                
            if text_style['textDecoration'] != "none":
                scss_parts.append(f"  text-decoration: {text_style['textDecoration']};")
                
            if text_style['lineHeight'] != "auto":
                scss_parts.append(f"  line-height: {text_style['lineHeight']}px;")
                
            if text_style['letterSpacing'] != 0:
                scss_parts.append(f"  letter-spacing: {text_style['letterSpacing']}px;")
            
            # Text color
            if node.style.get("fills"):
                for fill in node.style["fills"]:
                    if fill["type"] == "color":
                        color_name = None
                        # Buscar si este color está en nuestras variables
                        for name, color in self.colors.items():
                            if color["hex"] == fill["hex"]:
                                color_name = f"$color-{name.replace(' ', '-').lower()}"
                                break
                        
                        if color_name:
                            scss_parts.append(f"  color: {color_name};")
                        else:
                            scss_parts.append(f"  color: {fill['color']};")
                        break
        
        # Media queries for responsiveness
        if self.responsive and node.is_container:
            scss_parts.append("")
            scss_parts.append("  // Responsive adjustments")
            scss_parts.append("  @media (max-width: 768px) {")
            
            # Ajustar flex direction para móvil si es horizontal
            if node.flex_props and node.flex_props.get("flex-direction") == "row":
                scss_parts.append("    flex-direction: column;")
                
            # Ajustar tamaño
            if node.size["width_type"] == "fixed" and node.size["width"] > 500:
                scss_parts.append("    width: 100%;")
                
            scss_parts.append("  }")
        
        scss_parts.append("}")
        scss_parts.append("")
        
        # Generar estilos para los hijos
        for child in node.children:
            scss_parts.append(self._generate_node_scss(child))
        
        return "\n".join(scss_parts)
    
    def _generate_typescript(self, nodes: List[AngularNode]) -> str:
        """
        Genera el código TypeScript para el componente Angular
        
        Args:
            nodes: Lista de nodos AngularNode
            
        Returns:
            String con el código TypeScript
        """
        ts_parts = [
            "import { Component, OnInit } from '@angular/core';",
        ]
        
        # Añadir importaciones de Angular Material
        if self.use_material and self.imports:
            ts_parts.append("import {")
            for imp in sorted(self.imports):
                ts_parts.append(f"  {imp},")
            ts_parts.append("} from '@angular/material';")
        
        ts_parts.append("")
        ts_parts.append("@Component({")
        ts_parts.append(f"  selector: '{self.component_selector}',")
        ts_parts.append(f"  templateUrl: './{self.component_name}.component.html',")
        ts_parts.append(f"  styleUrls: ['./{self.component_name}.component.scss']")
        ts_parts.append("})")
        ts_parts.append(f"export class {self._to_class_name(self.component_name)}Component implements OnInit {{")
        
        # Añadir propiedades para los elementos interactivos
        has_form_elements = any(node.component_type in ["mat-form-field", "mat-select"] for node in self._collect_all_nodes(nodes))
        
        if has_form_elements:
            ts_parts.append("  // Form model")
            ts_parts.append("  formData = {")
            ts_parts.append("    // Add form fields here")
            ts_parts.append("  };")
            ts_parts.append("")
        
        # Añadir método ngOnInit
        ts_parts.append("  constructor() { }")
        ts_parts.append("")
        ts_parts.append("  ngOnInit(): void {")
        ts_parts.append("    // Initialize component")
        ts_parts.append("  }")
        
        # Si hay elementos interactivos, añadir métodos
        if has_form_elements:
            ts_parts.append("")
            ts_parts.append("  onSubmit(): void {")
            ts_parts.append("    // Handle form submission")
            ts_parts.append("    console.log('Form submitted:', this.formData);")
            ts_parts.append("  }")
        
        ts_parts.append("}")
        
        return "\n".join(ts_parts)
    
    def _to_class_name(self, kebab_name: str) -> str:
        """Convierte un nombre kebab-case a PascalCase para nombres de clase"""
        return "".join(word.capitalize() for word in kebab_name.split("-"))
    
    def _collect_all_nodes(self, nodes: List[AngularNode]) -> List[AngularNode]:
        """Recopila todos los nodos (incluidos los hijos) en una lista plana"""
        all_nodes = []
        
        def collect_recursive(node_list):
            for node in node_list:
                all_nodes.append(node)
                if node.children:
                    collect_recursive(node.children)
        
        collect_recursive(nodes)
        return all_nodes