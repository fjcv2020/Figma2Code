"""
Módulo para integrar la nueva generación de código optimizada con el flujo existente
"""

import os
import openai
from openai import OpenAI, AzureOpenAI
import streamlit as st
from utils import extract_nodes, flatten_figma_tree
from alt_nodes import convert_to_angular_nodes, analyze_layout, AngularNode
from angular_generator import AngularGenerator


def generate_enhanced_angular_code(figma_data, responsive=True, use_material=True, additional_instructions="", node_limit=50):
    """
    Genera código Angular usando nuestro nuevo sistema de procesamiento intermedio
    
    Args:
        figma_data (dict): Los datos del archivo Figma
        responsive (bool): Si el código debe ser responsive
        use_material (bool): Si se deben usar componentes de Angular Material
        additional_instructions (str): Instrucciones adicionales
        node_limit (int): Límite de nodos a procesar
        
    Returns:
        str: Código Angular generado (HTML, SCSS, TS)
    """
    try:
        # Añadir logs para debugging
        st.info(f"Iniciando generación de código con {node_limit} nodos límite, Material UI: {use_material}")
        
        # Extraer document data
        document = figma_data.get("document", {})
        if not document:
            st.error("No se pudo obtener el documento de Figma")
            return "// Error: No se encontró documento en los datos de Figma"
        
        # Extraer los nodos del documento
        st.info("Extrayendo nodos del documento...")
        figma_nodes = extract_nodes(document)
        st.info(f"Se extrajeron {len(figma_nodes)} nodos iniciales")
        
        # Aplanar los nodos para mejor procesamiento
        st.info("Aplanando árbol de nodos...")
        flattened_nodes = flatten_figma_tree(figma_nodes)
        st.info(f"Árbol aplanado: {len(flattened_nodes)} nodos")
        
        # Limitar la cantidad de nodos para prevenir problemas de memoria
        max_safe_nodes = min(node_limit, 500)  # Limitar a un máximo seguro
        if len(flattened_nodes) > max_safe_nodes:
            st.warning(
                f"Diseño contiene {len(flattened_nodes)} nodos. Procesando solo los primeros {max_safe_nodes} para prevenir problemas de memoria."
            )
            flattened_nodes = flattened_nodes[:max_safe_nodes]
        
        # Guardar información para debugging
        st.session_state["debug_info"] = {
            "node_count": len(flattened_nodes),
            "processing_strategy": "enhanced",
            "uses_material": use_material,
            "nodes_procesados": min(len(flattened_nodes), max_safe_nodes)
        }
        
        # Convertir a nodos intermedios (AltNodes)
        st.info("Convirtiendo nodos de Figma a representación intermedia...")
        angular_nodes = convert_to_angular_nodes(flattened_nodes)
        st.info(f"Se convirtieron {len(angular_nodes)} nodos raíz")
        
        # Analizar layout para detectar estructuras como flexbox y grid
        st.info("Analizando layout y optimizando estructura...")
        analyze_layout(angular_nodes)
        
        # Generar código Angular
        st.info("Generando código Angular optimizado...")
        generator = AngularGenerator(use_material=use_material, responsive=responsive)
        
        # Obtener el nombre del componente del documento
        component_name = figma_data.get("name", "figma-component").lower().replace(" ", "-")
        st.info(f"Generando componente: {component_name}")
        
        # Generar el código
        options = {"component_name": component_name}
        st.info("Llamando al generador...")
        code_files = generator.generate(angular_nodes, options)
        
        # Verificar resultado
        if not code_files or not isinstance(code_files, dict):
            st.error(f"Error: El generador devolvió un resultado inválido: {type(code_files)}")
            return "// Error: Formato de código generado inválido"
        
        # Formatear el resultado para la interfaz
        st.info("Formateando resultado final...")
        ts_code = code_files.get("ts", "// No se generó código TypeScript")
        html_code = code_files.get("html", "<!-- No se generó código HTML -->")
        scss_code = code_files.get("scss", "/* No se generó código SCSS */")
        
        # Crear el resultado final
        result = ""
        result += f"// component.ts\n{ts_code}\n\n"
        result += f"<!-- component.html -->\n{html_code}\n\n"
        result += f"/* component.scss */\n{scss_code}\n"
        
        # Añadir comentario con instrucciones adicionales procesadas
        if additional_instructions:
            result += f"\n/* \nInstrucciones adicionales aplicadas:\n{additional_instructions}\n*/\n"
        
        st.success("Código generado correctamente")
        return result
        
    except MemoryError:
        st.error("Error de memoria: El procesamiento requiere demasiados recursos")
        return "// Error: Se produjo un error de memoria durante la generación de código.\n// Intente reducir el límite de nodos o utilizar un diseño más simple."
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Error en la generación de código: {str(e)}")
        st.info(f"Detalles del error: {error_details}")
        return f"// Error durante la generación de código: {str(e)}\n// Consulte la consola para más detalles"


def process_figma_with_mixed_approach(figma_data, openai_api_key, responsive=True, 
                              additional_instructions="", use_azure=False, 
                              azure_endpoint="", azure_model="", 
                              node_limit=50, openai_model="gpt-4o", 
                              use_material=True):
    """
    Función que determina qué enfoque usar para procesar el diseño Figma
    
    Args:
        figma_data (dict): Los datos del archivo Figma
        openai_api_key (str): La API key de OpenAI
        responsive (bool): Si el código debe ser responsive
        additional_instructions (str): Instrucciones adicionales
        use_azure (bool): Si se debe usar Azure OpenAI
        azure_endpoint (str): El endpoint de Azure OpenAI
        azure_model (str): El modelo de Azure OpenAI
        node_limit (int): Límite de nodos a procesar
        openai_model (str): El modelo de OpenAI a usar
        use_material (bool): Si se deben usar componentes de Angular Material
        
    Returns:
        str: Código Angular generado
    """
    try:
        # Importar aquí para evitar problemas de importación circular
        from code_generator import generate_angular_code
        
        # Verificar datos de Figma
        if not figma_data or not isinstance(figma_data, dict):
            st.error(f"Datos de Figma inválidos: {type(figma_data)}")
            return "// Error: Formato de datos de Figma inválido"
            
        # Extraer document data para análisis
        document = figma_data.get("document", {})
        if not document:
            st.error("No se pudo obtener el documento de Figma")
            return "// Error: No se encontró documento en los datos de Figma"
            
        st.info("Analizando estructura del documento...")
        
        # Extraer y aplanar nodos con manejo de errores
        try:
            extracted_nodes = extract_nodes(document)
            st.info(f"Extracción inicial: {len(extracted_nodes)} nodos")
            
            # Limitar número de nodos antes de aplanar para evitar problemas de memoria
            if len(extracted_nodes) > 1000:  # Umbral arbitrario para protección
                st.warning(f"Demasiados nodos extraídos ({len(extracted_nodes)}), truncando a 1000")
                extracted_nodes = extracted_nodes[:1000]
                
            flattened_nodes = flatten_figma_tree(extracted_nodes)
            st.info(f"Nodos aplanados: {len(flattened_nodes)}")
        except Exception as e:
            st.error(f"Error al procesar nodos: {str(e)}")
            return f"// Error al procesar nodos del documento: {str(e)}"
        
        # Guardar información para debugging
        st.session_state["debug_info"] = {
            "node_count": len(flattened_nodes),
            "node_limit": node_limit,
            "use_material": use_material,
            "modo_enhanced": False
        }
        
        # Calcular complejidad aproximada
        st.info("Calculando métricas de complejidad...")
        complexity_factors = {
            "node_count": len(flattened_nodes),
            "has_auto_layout": any("layoutMode" in node for node in flattened_nodes[:100]),  # Muestreo
            "has_constraints": any("constraints" in node for node in flattened_nodes[:100]),  # Muestreo
            "has_vector_nodes": any(node.get("type") == "VECTOR" for node in flattened_nodes),
            "has_text_nodes": any(node.get("type") == "TEXT" for node in flattened_nodes),
        }
        
        # Actualizar información de debugging
        st.session_state["debug_info"].update(complexity_factors)
        
        # Decidir la estrategia basada en la complejidad
        use_enhanced = (
            complexity_factors["has_auto_layout"] or 
            complexity_factors["has_constraints"] or
            "material" in additional_instructions.lower() or
            "angular material" in additional_instructions.lower()
        )
        
        # Si el usuario especificó el uso de Material en instrucciones, actualizar la variable
        use_material_from_instructions = (
            "material" in additional_instructions.lower() or
            "angular material" in additional_instructions.lower()
        )
        
        # Combinar la opción del usuario con las instrucciones
        if use_material_from_instructions:
            use_material = True
            
        # Actualizar información de debugging
        st.session_state["debug_info"]["use_enhanced"] = use_enhanced
        st.session_state["debug_info"]["use_material"] = use_material
        
        # Configurar límite de nodos seguro
        safe_node_limit = min(node_limit, 500)  # Limitar para prevenir problemas de memoria
        
        if use_enhanced:
            st.info(f"Utilizando generador optimizado con representación intermedia (nodos: {safe_node_limit})...")
            st.session_state["debug_info"]["modo_enhanced"] = True
            return generate_enhanced_angular_code(
                figma_data, 
                responsive=responsive,
                use_material=use_material,
                additional_instructions=additional_instructions,
                node_limit=safe_node_limit  # Usar límite seguro
            )
        else:
            st.info(f"Utilizando generador basado en OpenAI (nodos: {safe_node_limit})...")
            # Configurar variable de entorno para la API key
            os.environ["OPENAI_API_KEY"] = openai_api_key
            
            return generate_angular_code(
                figma_data,
                responsive=responsive,
                additional_instructions=additional_instructions,
                use_azure=use_azure,
                azure_endpoint=azure_endpoint,
                azure_model=azure_model,
                node_limit=safe_node_limit,  # Usar límite seguro
                openai_model=openai_model
            )
            
    except MemoryError:
        st.error("Error de memoria: El procesamiento requiere demasiados recursos")
        return "// Error: Se produjo un error de memoria durante la generación de código.\n// Intente reducir el límite de nodos o utilizar un diseño más simple."
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Error en el procesamiento: {str(e)}")
        st.info(f"Detalles del error: {error_details}")
        return f"// Error durante el procesamiento: {str(e)}\n// Consulte la consola para más detalles"