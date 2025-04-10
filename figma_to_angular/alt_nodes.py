"""
Módulo para la representación intermedia de nodos (similar a AltNodes)
Basado en el concepto de FigmaToCode pero implementado específicamente para Angular
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple


class AngularNode:
    """
    Nodo intermedio para optimización y procesamiento antes de la conversión a Angular
    """
    def __init__(self, figma_node: Dict, parent=None):
        self.id = figma_node.get("id", "")
        self.name = self._clean_name(figma_node.get("name", ""))
        self.type = figma_node.get("type", "")
        self.parent = parent
        self.children: List['AngularNode'] = []
        
        # Propiedades específicas extraídas del nodo Figma
        self.position = self._extract_position(figma_node)
        self.size = self._extract_size(figma_node)
        self.style = self._extract_style(figma_node)
        self.layout = self._extract_layout(figma_node)
        self.content = self._extract_content(figma_node)
        
        # Propiedades para la conversión a Angular
        self.component_type = self._detect_component_type(figma_node)
        self.is_container = self._determine_if_container(figma_node)
        self.flex_props = {}  # Se llenará durante el análisis de layout
        self.grid_props = {}  # Se llenará durante el análisis de layout
        self.warnings = []
        
    def _clean_name(self, name: str) -> str:
        """Limpia el nombre para usarlo como identificador"""
        if not name:
            return "element"
        
        # Reemplazar espacios y caracteres especiales
        clean = re.sub(r'[^a-zA-Z0-9_\-\s]', '', name)
        clean = re.sub(r'\s+', '-', clean).lower()
        
        # Asegurar que comienza con una letra
        if clean and not clean[0].isalpha():
            clean = "el-" + clean
            
        return clean or "element"
    
    def _extract_position(self, node: Dict) -> Dict:
        """Extrae información de posición del nodo"""
        position = {"x": 0, "y": 0, "position": "relative"}
        
        if "absoluteBoundingBox" in node:
            bbox = node["absoluteBoundingBox"]
            position["x"] = bbox.get("x", 0)
            position["y"] = bbox.get("y", 0)
        
        # Verificar si el nodo tiene posición absoluta
        if node.get("constraints", {}).get("horizontal") == "LEFT_RIGHT" or node.get("constraints", {}).get("vertical") == "TOP_BOTTOM":
            position["position"] = "absolute"
        
        return position
    
    def _extract_size(self, node: Dict) -> Dict:
        """Extrae información de tamaño del nodo"""
        size = {"width": "auto", "height": "auto"}
        
        if "absoluteBoundingBox" in node:
            bbox = node["absoluteBoundingBox"]
            size["width"] = bbox.get("width", 0)
            size["height"] = bbox.get("height", 0)
        
        # Verificar restricciones de tamaño
        if node.get("constraints", {}).get("width") == "FIXED":
            size["width_type"] = "fixed"
        else:
            size["width_type"] = "flexible"
            
        if node.get("constraints", {}).get("height") == "FIXED":
            size["height_type"] = "fixed"
        else:
            size["height_type"] = "flexible"
        
        return size
    
    def _extract_style(self, node: Dict) -> Dict:
        """Extrae información de estilo del nodo"""
        style = {
            "fills": [],
            "strokes": [],
            "effects": [],
            "opacity": node.get("opacity", 1),
            "radius": self._extract_radius(node),
            "visible": node.get("visible", True)
        }
        
        # Procesar fills (colores/gradientes)
        if "fills" in node and isinstance(node["fills"], list):
            for fill in node["fills"]:
                if fill.get("visible", True):
                    if fill["type"] == "SOLID":
                        color = fill.get("color", {})
                        r = int(color.get("r", 0) * 255)
                        g = int(color.get("g", 0) * 255)
                        b = int(color.get("b", 0) * 255)
                        a = fill.get("opacity", 1) * color.get("a", 1)
                        
                        style["fills"].append({
                            "type": "color",
                            "color": f"rgba({r}, {g}, {b}, {a})",
                            "hex": f"#{r:02x}{g:02x}{b:02x}"
                        })
                    elif fill["type"] == "IMAGE":
                        style["fills"].append({
                            "type": "image",
                            "imageRef": fill.get("imageRef", "")
                        })
                    elif fill["type"] == "GRADIENT_LINEAR":
                        style["fills"].append({
                            "type": "gradient",
                            "gradientType": "linear",
                            "gradientHandlePositions": fill.get("gradientHandlePositions", []),
                            "gradientStops": fill.get("gradientStops", [])
                        })
        
        # Procesar strokes (bordes)
        if "strokes" in node and isinstance(node["strokes"], list) and node["strokes"]:
            for stroke in node["strokes"]:
                if stroke.get("visible", True) and stroke["type"] == "SOLID":
                    color = stroke.get("color", {})
                    r = int(color.get("r", 0) * 255)
                    g = int(color.get("g", 0) * 255)
                    b = int(color.get("b", 0) * 255)
                    a = stroke.get("opacity", 1) * color.get("a", 1)
                    
                    style["strokes"].append({
                        "color": f"rgba({r}, {g}, {b}, {a})",
                        "hex": f"#{r:02x}{g:02x}{b:02x}",
                        "weight": node.get("strokeWeight", 1),
                        "align": node.get("strokeAlign", "INSIDE"),
                        "style": node.get("strokeDashes", []) and "dashed" or "solid"
                    })
        
        # Procesar efectos (sombras)
        if "effects" in node and isinstance(node["effects"], list):
            for effect in node["effects"]:
                if effect.get("visible", True):
                    if effect["type"] == "DROP_SHADOW":
                        color = effect.get("color", {})
                        r = int(color.get("r", 0) * 255)
                        g = int(color.get("g", 0) * 255)
                        b = int(color.get("b", 0) * 255)
                        a = effect.get("opacity", 1) * color.get("a", 1)
                        
                        style["effects"].append({
                            "type": "shadow",
                            "color": f"rgba({r}, {g}, {b}, {a})",
                            "offset": {
                                "x": effect.get("offset", {}).get("x", 0),
                                "y": effect.get("offset", {}).get("y", 0)
                            },
                            "radius": effect.get("radius", 0),
                            "spread": effect.get("spread", 0)
                        })
        
        # Procesar propiedades de texto
        if node.get("type") == "TEXT" and "style" in node:
            text_style = node["style"]
            style["text"] = {
                "content": node.get("characters", ""),
                "fontSize": text_style.get("fontSize", 14),
                "fontFamily": text_style.get("fontFamily", "Roboto"),
                "fontWeight": text_style.get("fontWeight", 400),
                "textAlign": text_style.get("textAlignHorizontal", "LEFT").lower(),
                "fontStyle": text_style.get("italic", False) and "italic" or "normal",
                "textDecoration": text_style.get("textDecoration", "NONE").lower(),
                "lineHeight": text_style.get("lineHeightPx", "auto"),
                "letterSpacing": text_style.get("letterSpacing", 0)
            }
        
        return style
    
    def _extract_radius(self, node: Dict) -> Union[float, Dict]:
        """Extrae información de border radius del nodo"""
        if "cornerRadius" in node:
            return float(node["cornerRadius"])
        
        # Radios individuales por esquina
        if "rectangleCornerRadii" in node:
            radii = node["rectangleCornerRadii"]
            if len(radii) == 4:
                return {
                    "topLeft": radii[0],
                    "topRight": radii[1],
                    "bottomRight": radii[2],
                    "bottomLeft": radii[3]
                }
        
        return 0
    
    def _extract_layout(self, node: Dict) -> Dict:
        """Extrae información de layout del nodo"""
        layout = {
            "type": "default",  # default, auto-layout, grid
            "direction": None,  # horizontal, vertical
            "spacing": 0,
            "padding": {
                "top": 0,
                "right": 0,
                "bottom": 0,
                "left": 0
            },
            "alignment": {
                "horizontal": "NONE",
                "vertical": "NONE"
            },
            "constraints": node.get("constraints", {})
        }
        
        # Detectar Auto Layout
        if "layoutMode" in node:
            layout["type"] = "auto-layout"
            layout["direction"] = node["layoutMode"].lower()
            layout["spacing"] = node.get("itemSpacing", 0)
            
            # Extraer padding
            if "paddingLeft" in node:
                layout["padding"]["left"] = node["paddingLeft"]
            if "paddingRight" in node:
                layout["padding"]["right"] = node["paddingRight"] 
            if "paddingTop" in node:
                layout["padding"]["top"] = node["paddingTop"]
            if "paddingBottom" in node:
                layout["padding"]["bottom"] = node["paddingBottom"]
                
            # Extraer alineación
            if "primaryAxisAlignItems" in node:
                layout["alignment"]["primary"] = node["primaryAxisAlignItems"]
            if "counterAxisAlignItems" in node:
                layout["alignment"]["counter"] = node["counterAxisAlignItems"]
        
        return layout
    
    def _extract_content(self, node: Dict) -> Dict:
        """Extrae el contenido específico del nodo según su tipo"""
        content = {}
        
        if node.get("type") == "TEXT":
            content["text"] = node.get("characters", "")
        elif node.get("type") == "VECTOR":
            content["vector_paths"] = node.get("vectorPaths", [])
        elif node.get("type") == "INSTANCE":
            content["component_id"] = node.get("componentId", "")
        
        return content
    
    def _detect_component_type(self, node: Dict) -> str:
        """
        Detecta si el nodo puede mapearse a un componente de Angular Material
        """
        name = node.get("name", "").lower()
        
        # Detección basada en nombre
        if "button" in name or name.endswith("btn"):
            return "mat-button"
        elif "card" in name:
            return "mat-card"
        elif "input" in name or "textfield" in name:
            return "mat-form-field"
        elif "select" in name or "dropdown" in name:
            return "mat-select"
        elif "checkbox" in name:
            return "mat-checkbox"
        elif "radio" in name:
            return "mat-radio"
        elif "tab" in name and node.get("type") == "FRAME":
            return "mat-tab-group"
        elif "dialog" in name or "modal" in name:
            return "mat-dialog"
        elif "menu" in name:
            return "mat-menu"
        elif "toolbar" in name:
            return "mat-toolbar"
        elif "icon" in name:
            return "mat-icon"
        elif "chip" in name or "tag" in name:
            return "mat-chip"
        elif "progress" in name:
            if "circular" in name or "spinner" in name:
                return "mat-progress-spinner"
            return "mat-progress-bar"
        
        # Detección basada en apariencia
        if node.get("type") == "TEXT" and "style" in node:
            if node["style"].get("fontSize", 0) > 24:
                return "h1"
            elif node["style"].get("fontSize", 0) > 20:
                return "h2"
            elif node["style"].get("fontSize", 0) > 16:
                return "h3"
            elif node["style"].get("fontWeight", 0) > 500:
                return "strong"
        
        # Por defecto, usar el tipo de nodo de Figma
        return node.get("type", "div").lower()
    
    def _determine_if_container(self, node: Dict) -> bool:
        """Determina si el nodo es un contenedor de otros elementos"""
        container_types = ["FRAME", "GROUP", "COMPONENT", "INSTANCE"]
        return node.get("type") in container_types or "children" in node
    
    def add_child(self, child: 'AngularNode'):
        """Añade un nodo hijo"""
        self.children.append(child)
        child.parent = self
    
    def to_dict(self) -> Dict:
        """Convierte el nodo a un diccionario para depuración"""
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "component_type": self.component_type,
            "is_container": self.is_container,
            "position": self.position,
            "size": self.size,
            "layout": self.layout,
            "has_parent": self.parent is not None,
            "children_count": len(self.children)
        }
        
        if self.warnings:
            result["warnings"] = self.warnings
            
        return result


def convert_to_angular_nodes(figma_nodes: List[Dict]) -> List[AngularNode]:
    """
    Convierte los nodos de Figma a nuestra representación intermedia AngularNode
    
    Args:
        figma_nodes: Lista de nodos Figma
        
    Returns:
        Lista de AngularNode
    """
    # Verificación de entrada
    if not figma_nodes:
        print("Warning: No se proporcionaron nodos Figma para convertir")
        return []
        
    node_map = {}  # Mapeo de ID a nodo para mantener la estructura
    root_nodes = []
    
    # Para prevenir errores por nodos malformados
    valid_nodes = []
    for node in figma_nodes:
        if not isinstance(node, dict) or "id" not in node:
            print(f"Warning: Ignorando nodo sin ID: {type(node)}")
            continue
        valid_nodes.append(node)
    
    # Primera pasada: crear los nodos
    try:
        for node in valid_nodes:
            try:
                angular_node = AngularNode(node)
                node_map[angular_node.id] = angular_node
                
                # Si no tiene parent_id, es un nodo raíz
                if "parent_id" not in node:
                    root_nodes.append(angular_node)
            except Exception as e:
                print(f"Error al convertir nodo {node.get('id', 'unknown')}: {str(e)}")
    except Exception as e:
        print(f"Error en primera pasada: {str(e)}")
    
    # Segunda pasada: establecer relaciones padre-hijo
    try:
        for node in valid_nodes:
            try:
                if "parent_id" in node and node["parent_id"] in node_map:
                    parent = node_map[node["parent_id"]]
                    if node["id"] in node_map:
                        child = node_map[node["id"]]
                        parent.add_child(child)
            except Exception as e:
                print(f"Error al establecer relación para nodo {node.get('id', 'unknown')}: {str(e)}")
    except Exception as e:
        print(f"Error en segunda pasada: {str(e)}")
    
    # En caso de que no se hayan detectado nodos raíz, buscar el primero
    if not root_nodes and node_map:
        first_node = list(node_map.values())[0]
        root_nodes.append(first_node)
        print(f"No se detectaron nodos raíz, usando el primer nodo como raíz: {first_node.id}")
    
    return root_nodes


def analyze_layout(nodes: List[AngularNode]):
    """
    Analiza y mejora la información de layout en los nodos
    
    Args:
        nodes: Lista de nodos AngularNode raíz
    """
    if not nodes:
        print("Warning: No hay nodos para analizar layout")
        return
        
    try:
        for node in nodes:
            try:
                _analyze_node_layout(node)
                
                # Procesar hijos recursivamente
                for child in node.children:
                    analyze_layout([child])
            except Exception as e:
                print(f"Error al analizar layout de nodo {node.id}: {str(e)}")
    except Exception as e:
        print(f"Error general en analyze_layout: {str(e)}")


def _analyze_node_layout(node: AngularNode):
    """
    Analiza el layout de un nodo y sus hijos para detectar patrones
    
    Args:
        node: Nodo a analizar
    """
    # Si no es un contenedor o no tiene hijos, no hay nada que analizar
    if not node.is_container or not node.children:
        return
        
    # Verificar si los hijos están alineados horizontal o verticalmente
    if _children_aligned_horizontally(node.children):
        node.layout["type"] = "auto-layout"
        node.layout["direction"] = "horizontal"
        node.flex_props = {"display": "flex", "flex-direction": "row"}
        
        # Calcular spacing promedio entre elementos
        spacing = _calculate_horizontal_spacing(node.children)
        if spacing > 0:
            node.layout["spacing"] = spacing
            node.flex_props["gap"] = f"{spacing}px"
            
        # Detectar alineación vertical
        v_alignment = _detect_vertical_alignment(node.children)
        if v_alignment:
            node.flex_props["align-items"] = v_alignment
            
    elif _children_aligned_vertically(node.children):
        node.layout["type"] = "auto-layout"
        node.layout["direction"] = "vertical"
        node.flex_props = {"display": "flex", "flex-direction": "column"}
        
        # Calcular spacing promedio entre elementos
        spacing = _calculate_vertical_spacing(node.children)
        if spacing > 0:
            node.layout["spacing"] = spacing
            node.flex_props["gap"] = f"{spacing}px"
            
        # Detectar alineación horizontal
        h_alignment = _detect_horizontal_alignment(node.children)
        if h_alignment:
            node.flex_props["align-items"] = h_alignment
    
    # Si tenemos una cuadrícula (grid)
    elif _appears_to_be_grid(node.children):
        node.layout["type"] = "grid"
        cols, rows = _detect_grid_dimensions(node.children)
        node.grid_props = {
            "display": "grid",
            "grid-template-columns": f"repeat({cols}, 1fr)",
            "grid-template-rows": f"repeat({rows}, auto)"
        }
        
        # Calcular gaps para grid
        h_gap, v_gap = _calculate_grid_gaps(node.children, cols, rows)
        if h_gap > 0:
            node.grid_props["column-gap"] = f"{h_gap}px"
        if v_gap > 0:
            node.grid_props["row-gap"] = f"{v_gap}px"
    
    # Buscar elementos que están posicionados absolutamente
    positioned_elements = [c for c in node.children if c.position["position"] == "absolute"]
    if positioned_elements:
        # Si es un contenedor con posicionamiento absoluto, debemos asegurarnos de que sea relativo
        if not node.flex_props and not node.grid_props:
            node.position["position"] = "relative"


def _children_aligned_horizontally(children: List[AngularNode]) -> bool:
    """Verifica si los hijos están principalmente alineados horizontalmente"""
    if not children or len(children) < 2:
        return False
        
    # Verificar si todos los elementos están aproximadamente a la misma altura (Y)
    y_positions = [c.position["y"] for c in children]
    y_avg = sum(y_positions) / len(y_positions)
    max_deviation = 5  # Permitir pequeñas desviaciones (5px)
    
    aligned = all(abs(y - y_avg) <= max_deviation for y in y_positions)
    
    # Verificar que los elementos están distribuidos horizontalmente
    if aligned:
        x_positions = [c.position["x"] for c in children]
        return max(x_positions) - min(x_positions) > 20  # Desviación significativa en X
        
    return False


def _children_aligned_vertically(children: List[AngularNode]) -> bool:
    """Verifica si los hijos están principalmente alineados verticalmente"""
    if not children or len(children) < 2:
        return False
        
    # Verificar si todos los elementos están aproximadamente a la misma posición X
    x_positions = [c.position["x"] for c in children]
    x_avg = sum(x_positions) / len(x_positions)
    max_deviation = 5  # Permitir pequeñas desviaciones (5px)
    
    aligned = all(abs(x - x_avg) <= max_deviation for x in x_positions)
    
    # Verificar que los elementos están distribuidos verticalmente
    if aligned:
        y_positions = [c.position["y"] for c in children]
        return max(y_positions) - min(y_positions) > 20  # Desviación significativa en Y
        
    return False


def _calculate_horizontal_spacing(children: List[AngularNode]) -> float:
    """Calcula el espaciado horizontal promedio entre elementos"""
    if len(children) < 2:
        return 0
        
    # Ordenar por posición X
    sorted_children = sorted(children, key=lambda c: c.position["x"])
    
    # Calcular diferencias entre elementos adyacentes
    spacings = []
    for i in range(len(sorted_children) - 1):
        curr_right = sorted_children[i].position["x"] + sorted_children[i].size["width"]
        next_left = sorted_children[i+1].position["x"]
        spacings.append(next_left - curr_right)
    
    # Devolver promedio si hay valores positivos
    positive_spacings = [s for s in spacings if s > 0]
    if positive_spacings:
        return sum(positive_spacings) / len(positive_spacings)
    return 0


def _calculate_vertical_spacing(children: List[AngularNode]) -> float:
    """Calcula el espaciado vertical promedio entre elementos"""
    if len(children) < 2:
        return 0
        
    # Ordenar por posición Y
    sorted_children = sorted(children, key=lambda c: c.position["y"])
    
    # Calcular diferencias entre elementos adyacentes
    spacings = []
    for i in range(len(sorted_children) - 1):
        curr_bottom = sorted_children[i].position["y"] + sorted_children[i].size["height"]
        next_top = sorted_children[i+1].position["y"]
        spacings.append(next_top - curr_bottom)
    
    # Devolver promedio si hay valores positivos
    positive_spacings = [s for s in spacings if s > 0]
    if positive_spacings:
        return sum(positive_spacings) / len(positive_spacings)
    return 0


def _detect_vertical_alignment(children: List[AngularNode]) -> Optional[str]:
    """Detecta la alineación vertical de los elementos"""
    if not children:
        return None
        
    # Verificar alineación al inicio (top)
    y_positions = [c.position["y"] for c in children]
    if all(abs(y - min(y_positions)) < 5 for y in y_positions):
        return "flex-start"
        
    # Verificar alineación al final (bottom)
    bottom_positions = [c.position["y"] + c.size["height"] for c in children]
    if all(abs(b - max(bottom_positions)) < 5 for b in bottom_positions):
        return "flex-end"
    
    # Verificar alineación central
    parent_height = max(bottom_positions) - min(y_positions)
    centers = [c.position["y"] + c.size["height"]/2 for c in children]
    center_avg = sum(centers) / len(centers)
    if all(abs(c - center_avg) < 10 for c in centers):
        return "center"
    
    # Espaciado uniforme
    if len(set(y_positions)) > 1 and len(children) > 2:
        return "space-between"
        
    return None


def _detect_horizontal_alignment(children: List[AngularNode]) -> Optional[str]:
    """Detecta la alineación horizontal de los elementos"""
    if not children:
        return None
        
    # Verificar alineación al inicio (left)
    x_positions = [c.position["x"] for c in children]
    if all(abs(x - min(x_positions)) < 5 for x in x_positions):
        return "flex-start"
        
    # Verificar alineación al final (right)
    right_positions = [c.position["x"] + c.size["width"] for c in children]
    if all(abs(r - max(right_positions)) < 5 for r in right_positions):
        return "flex-end"
    
    # Verificar alineación central
    parent_width = max(right_positions) - min(x_positions)
    centers = [c.position["x"] + c.size["width"]/2 for c in children]
    center_avg = sum(centers) / len(centers)
    if all(abs(c - center_avg) < 10 for c in centers):
        return "center"
    
    # Espaciado uniforme
    if len(set(x_positions)) > 1 and len(children) > 2:
        return "space-between"
        
    return None


def _appears_to_be_grid(children: List[AngularNode]) -> bool:
    """Verifica si los elementos parecen estar en una cuadrícula"""
    if len(children) < 4:  # Una cuadrícula debe tener al menos 4 elementos
        return False
        
    # Detectar posibles columnas
    x_positions = set()
    for child in children:
        x_positions.add(round(child.position["x"] / 10) * 10)  # Redondear a decenas para agrupar
    
    # Detectar posibles filas
    y_positions = set()
    for child in children:
        y_positions.add(round(child.position["y"] / 10) * 10)  # Redondear a decenas para agrupar
    
    # Si hay múltiples columnas y filas, podría ser una cuadrícula
    return len(x_positions) > 1 and len(y_positions) > 1


def _detect_grid_dimensions(children: List[AngularNode]) -> Tuple[int, int]:
    """Detecta las dimensiones aproximadas de la cuadrícula (columnas, filas)"""
    # Detectar columnas distintivas
    x_positions = set()
    for child in children:
        x_positions.add(round(child.position["x"] / 10) * 10)  # Redondear a decenas
    
    # Detectar filas distintivas
    y_positions = set()
    for child in children:
        y_positions.add(round(child.position["y"] / 10) * 10)  # Redondear a decenas
    
    return len(x_positions), len(y_positions)


def _calculate_grid_gaps(children: List[AngularNode], cols: int, rows: int) -> Tuple[float, float]:
    """Calcula los espacios entre columnas y filas en una cuadrícula"""
    # Agrupar por columnas aproximadas
    column_positions = {}
    for child in children:
        col_key = round(child.position["x"] / 10) * 10
        if col_key not in column_positions:
            column_positions[col_key] = []
        column_positions[col_key].append(child)
    
    # Ordenar las columnas por posición
    sorted_cols = sorted(column_positions.keys())
    
    # Calcular gaps horizontales
    h_gaps = []
    for i in range(len(sorted_cols) - 1):
        col = sorted_cols[i]
        next_col = sorted_cols[i+1]
        
        # Tomar el elemento más a la derecha de la columna actual
        rightmost = max(column_positions[col], key=lambda c: c.position["x"] + c.size["width"])
        # Tomar el elemento más a la izquierda de la columna siguiente
        leftmost = min(column_positions[next_col], key=lambda c: c.position["x"])
        
        h_gaps.append(leftmost.position["x"] - (rightmost.position["x"] + rightmost.size["width"]))
    
    # Agrupar por filas aproximadas
    row_positions = {}
    for child in children:
        row_key = round(child.position["y"] / 10) * 10
        if row_key not in row_positions:
            row_positions[row_key] = []
        row_positions[row_key].append(child)
    
    # Ordenar las filas por posición
    sorted_rows = sorted(row_positions.keys())
    
    # Calcular gaps verticales
    v_gaps = []
    for i in range(len(sorted_rows) - 1):
        row = sorted_rows[i]
        next_row = sorted_rows[i+1]
        
        # Tomar el elemento más abajo de la fila actual
        bottommost = max(row_positions[row], key=lambda c: c.position["y"] + c.size["height"])
        # Tomar el elemento más arriba de la fila siguiente
        topmost = min(row_positions[next_row], key=lambda c: c.position["y"])
        
        v_gaps.append(topmost.position["y"] - (bottommost.position["y"] + bottommost.size["height"]))
    
    # Calcular promedios
    h_gap = sum(h_gaps) / len(h_gaps) if h_gaps else 0
    v_gap = sum(v_gaps) / len(v_gaps) if v_gaps else 0
    
    return h_gap, v_gap