import streamlit as st
import json
import requests
from figma_api import FigmaAPI

def export_to_json(figma_data, output_path="exported_figma.json"):
    """
    Export Figma data to a JSON file in a format suitable for .jam imports
    
    Args:
        figma_data (dict): The Figma file data
        output_path (str): Where to save the exported JSON
        
    Returns:
        str: Path to the exported file
    """
    try:
        # Prepare the data structure for .jam format
        jam_data = {
            "document": figma_data.get("document", {}),
            "name": figma_data.get("name", "Figma Export"),
            "lastModified": figma_data.get("lastModified", ""),
            "version": figma_data.get("version", ""),
            "exportSource": "FigmaToCode"
        }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(jam_data, f, indent=2)
            
        return output_path
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None
        
def extract_specific_nodes(figma_data, node_types=None, max_depth=3):
    """
    Extract only specific node types from Figma data
    
    Args:
        figma_data (dict): The Figma file data
        node_types (list): List of node types to extract (e.g., ["FRAME", "TEXT"])
        max_depth (int): Maximum depth to traverse
        
    Returns:
        list: Extracted nodes of the specified types
    """
    if node_types is None:
        node_types = ["FRAME", "RECTANGLE", "TEXT", "GROUP", "COMPONENT"]
        
    extracted_nodes = []
    
    def traverse_node(node, current_depth=0):
        if current_depth > max_depth:
            return
            
        # Check if this node matches the requested types
        if "type" in node and node["type"] in node_types:
            extracted_nodes.append(node)
            
        # Traverse children
        if "children" in node:
            for child in node["children"]:
                traverse_node(child, current_depth + 1)
    
    # Start traversal from the document
    document = figma_data.get("document", {})
    traverse_node(document)
    
    return extracted_nodes
    
def get_figma_node_structure(figma_api, file_key, node_id=None):
    """
    Get a structured representation of Figma nodes similar to what v0/Lovable use
    
    Args:
        figma_api (FigmaAPI): Initialized Figma API client
        file_key (str): Figma file key
        node_id (str, optional): Specific node ID to focus on
        
    Returns:
        dict: Structured node data
    """
    try:
        # Get the file data
        file_data = figma_api.get_file(file_key, node_id)
        
        # Extract specific nodes
        frames = extract_specific_nodes(file_data, ["FRAME", "COMPONENT", "COMPONENT_SET"], max_depth=2)
        
        # Create a structure similar to what v0/Lovable might use
        structured_data = {
            "name": file_data.get("name", "Untitled"),
            "frames": [],
            "components": [],
            "styles": {}
        }
        
        # Process frames
        for frame in frames:
            frame_data = {
                "id": frame.get("id", ""),
                "name": frame.get("name", "Untitled Frame"),
                "type": frame.get("type", ""),
                "width": frame.get("absoluteBoundingBox", {}).get("width", 0),
                "height": frame.get("absoluteBoundingBox", {}).get("height", 0),
                "childCount": len(frame.get("children", [])),
                "hasAutoLayout": "layoutMode" in frame
            }
            
            if frame["type"] == "COMPONENT" or frame["type"] == "COMPONENT_SET":
                structured_data["components"].append(frame_data)
            else:
                structured_data["frames"].append(frame_data)
                
        # Get style metadata if available
        try:
            style_metadata = figma_api.get_style_metadata(file_key)
            if style_metadata and "meta" in style_metadata and "styles" in style_metadata["meta"]:
                structured_data["styles"] = style_metadata["meta"]["styles"]
        except:
            # Style metadata is not critical, so continue even if it fails
            pass
            
        return structured_data
    
    except Exception as e:
        st.error(f"Error getting node structure: {str(e)}")
        return None