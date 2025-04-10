import os
import re

def save_file(file_path, content):
    """
    Save content to a file
    
    Args:
        file_path (str): Path to save the file
        content (str): Content to save
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return False

def read_file(file_path):
    """
    Read content from a file
    
    Args:
        file_path (str): Path of the file to read
        
    Returns:
        str: File content or empty string if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        return ""
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return ""

def validate_inputs(file_key, access_token, openai_api_key):
    """
    Validate the required inputs
    
    Args:
        file_key (str): Figma file key
        access_token (str): Figma access token
        openai_api_key (str): OpenAI API key
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not file_key:
        return False, "Figma file key is required"
    
    if not access_token:
        return False, "Figma access token is required"
    
    if not openai_api_key:
        return False, "OpenAI API key is required"
    
    # Check if file_key is in valid format
    if not re.match(r'^[a-zA-Z0-9_-]+$', file_key):
        return False, "Invalid Figma file key format"
    
    return True, ""

def extract_nodes(document):
    """
    Extract nodes from Figma document
    
    Args:
        document (dict): Figma document data
        
    Returns:
        list: List of extracted nodes
    """
    nodes = []
    
    def traverse_node(node):
        # Skip nodes without type
        if "type" not in node:
            return
        
        # Add current node to the list
        nodes.append(node)
        
        # Recursively traverse children
        if "children" in node:
            for child in node["children"]:
                traverse_node(child)
    
    # Start traversal from root
    if document:
        traverse_node(document)
    
    return nodes

def flatten_figma_tree(nodes):
    """
    Flatten the Figma node tree into a simple list
    
    Args:
        nodes (list): Hierarchical list of Figma nodes
        
    Returns:
        list: Flattened list of nodes with parent references
    """
    flattened = []
    
    def process_node(node, parent=None):
        # Create a copy to avoid modifying the original
        node_copy = node.copy()
        
        # Add parent reference
        if parent:
            node_copy["parent_id"] = parent.get("id")
            node_copy["parent_type"] = parent.get("type")
        
        # Remove children to keep the node simple
        if "children" in node_copy:
            children = node_copy.pop("children")
            # Process children
            for child in children:
                process_node(child, node_copy)
        
        # Add to flattened list
        flattened.append(node_copy)
    
    # Process each root node
    for node in nodes:
        if node.get("type") in ["CANVAS", "FRAME", "GROUP", "COMPONENT"]:
            process_node(node)
    
    return flattened

def rgb_to_hex(r, g, b):
    """
    Convert RGB values to hex color
    
    Args:
        r (float): Red (0-1)
        g (float): Green (0-1)
        b (float): Blue (0-1)
        
    Returns:
        str: Hex color code
    """
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def extract_text_styles(nodes):
    """
    Extract text styles from Figma nodes
    
    Args:
        nodes (list): List of Figma nodes
        
    Returns:
        dict: Dictionary of text styles
    """
    text_styles = {}
    
    for node in nodes:
        if node.get("type") == "TEXT" and "style" in node:
            style = node["style"]
            style_name = node.get("name", f"text-style-{len(text_styles)}")
            
            text_styles[style_name] = {
                "fontFamily": style.get("fontFamily", "sans-serif"),
                "fontSize": style.get("fontSize", 16),
                "fontWeight": style.get("fontWeight", 400),
                "lineHeight": style.get("lineHeightPercent", 100),
                "letterSpacing": style.get("letterSpacing", 0),
                "textCase": style.get("textCase", "ORIGINAL"),
            }
    
    return text_styles
