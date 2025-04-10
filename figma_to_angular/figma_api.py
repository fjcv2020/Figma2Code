import requests
import json
import streamlit as st

class FigmaAPI:
    """
    Class to interact with the Figma API
    """
    def __init__(self, access_token):
        """
        Initialize the Figma API with the access token
        
        Args:
            access_token (str): Figma personal access token
        """
        self.access_token = access_token
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.access_token
        }
    
    def get_file(self, file_key, node_id=None):
        """
        Get a Figma file data
        
        Args:
            file_key (str): The key of the Figma file
            node_id (str, optional): The ID of a specific node to retrieve
            
        Returns:
            dict: The Figma file data in JSON format
        """
        try:
            # Construct the API URL
            url = f"{self.base_url}/files/{file_key}"
            
            # Add node_id parameter if provided
            if node_id:
                url += f"?ids={node_id}"
            
            # Log the request for debugging
            st.session_state['debug_info'] = {
                "request_url": url,
                "headers": {"X-Figma-Token": "****" + self.access_token[-4:] if self.access_token else "None"}
            }
            
            # Make the API request
            response = requests.get(url, headers=self.headers)
            
            # Save response info for debugging
            st.session_state['debug_info']["response_status"] = response.status_code
            st.session_state['debug_info']["response_text"] = response.text[:500] + "..." if len(response.text) > 500 else response.text
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse and return the JSON data
                file_data = response.json()
                
                # Process and clean up the data
                return self._process_file_data(file_data, node_id)
            elif response.status_code == 404:
                # Not Found - Common issue with file key or permissions
                error_msg = f"Figma API Error: 404 - File Not Found\n\nPossible reasons:\n"
                error_msg += "1. The file key is incorrect\n"
                error_msg += "2. The file doesn't exist\n"
                error_msg += "3. You don't have permission to access this file\n"
                error_msg += "\nEnsure your Figma access token has 'files:read' permission"
                st.error(error_msg)
                return None
            elif response.status_code == 403:
                # Forbidden - Usually a permission issue
                error_msg = f"Figma API Error: 403 - Access Forbidden\n\nPossible reasons:\n"
                error_msg += "1. Your access token doesn't have sufficient permissions\n"
                error_msg += "2. The access token has expired\n"
                error_msg += "\nCreate a new Personal Access Token with 'files:read' permission"
                st.error(error_msg)
                return None
            elif response.status_code == 401:
                # Unauthorized - Invalid token
                error_msg = f"Figma API Error: 401 - Unauthorized\n\nPossible reasons:\n"
                error_msg += "1. Invalid access token\n"
                error_msg += "2. The access token has been revoked\n"
                error_msg += "\nCreate a new Personal Access Token with 'files:read' permission"
                st.error(error_msg)
                return None
            else:
                # Handle other API errors
                error_msg = f"Figma API Error: {response.status_code} - {response.text}"
                st.error(error_msg)
                return None
                
        except Exception as e:
            st.error(f"Error fetching Figma file: {str(e)}")
            return None
    
    def get_image_urls(self, file_key, ids, scale=1):
        """
        Get URLs for images in the Figma document
        
        Args:
            file_key (str): The key of the Figma file
            ids (list): List of node IDs to get images for
            scale (int, optional): Scale factor for the images (default: 1)
            
        Returns:
            dict: Dictionary mapping node IDs to image URLs
        """
        try:
            # Construct the API URL
            url = f"{self.base_url}/images/{file_key}"
            
            # Prepare the query parameters
            params = {
                "ids": ",".join(ids),
                "scale": scale,
                "format": "svg"
            }
            
            # Make the API request
            response = requests.get(url, headers=self.headers, params=params)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse and return the JSON data
                return response.json().get("images", {})
            else:
                # Handle API errors
                error_msg = f"Figma API Error (images): {response.status_code} - {response.text}"
                st.error(error_msg)
                return {}
                
        except Exception as e:
            st.error(f"Error fetching Figma images: {str(e)}")
            return {}
    
    def _process_file_data(self, file_data, node_id=None):
        """
        Process and clean up the Figma file data
        
        Args:
            file_data (dict): The raw Figma file data
            node_id (str, optional): The ID of a specific node being processed
            
        Returns:
            dict: Processed Figma file data
        """
        # Extract the document data
        document = file_data.get("document", {})
        
        # If a specific node ID was requested, extract only that node
        if node_id:
            # Find the specific node in the document
            nodes = file_data.get("nodes", {})
            if node_id in nodes:
                node_data = nodes[node_id]
                return {
                    "name": node_data.get("document", {}).get("name", "Unknown"),
                    "document": node_data.get("document", {}),
                    "components": file_data.get("components", {}),
                    "styles": file_data.get("styles", {}),
                    "node_id": node_id
                }
        
        # Return the full document data
        return {
            "name": document.get("name", "Unknown"),
            "document": document,
            "components": file_data.get("components", {}),
            "styles": file_data.get("styles", {}),
        }
    
    def get_style_metadata(self, file_key):
        """
        Get style metadata for a Figma file
        
        Args:
            file_key (str): The key of the Figma file
            
        Returns:
            dict: Style metadata
        """
        try:
            url = f"{self.base_url}/files/{file_key}/styles"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Figma API Error (styles): {response.status_code} - {response.text}"
                st.error(error_msg)
                return {"meta": {"styles": []}}
                
        except Exception as e:
            st.error(f"Error fetching style metadata: {str(e)}")
            return {"meta": {"styles": []}}
    
    def extract_colors(self, document):
        """
        Extract color styles from a Figma document
        
        Args:
            document (dict): The Figma document data
            
        Returns:
            dict: Dictionary of color styles
        """
        colors = {}
        
        def traverse_node(node):
            # Check for fills with solid colors
            if "fills" in node and node["fills"]:
                for fill in node["fills"]:
                    if fill["type"] == "SOLID" and "color" in fill:
                        color = fill["color"]
                        # Convert RGB values (0-1) to hex
                        r = int(color["r"] * 255)
                        g = int(color["g"] * 255)
                        b = int(color["b"] * 255)
                        opacity = color.get("a", 1)
                        
                        hex_color = f"#{r:02x}{g:02x}{b:02x}"
                        
                        # Add to colors dict if it has a name
                        if "name" in node:
                            colors[node["name"]] = {
                                "hex": hex_color,
                                "rgba": f"rgba({r}, {g}, {b}, {opacity})"
                            }
            
            # Recursively traverse children
            if "children" in node:
                for child in node["children"]:
                    traverse_node(child)
        
        # Start traversal from the document root
        traverse_node(document)
        return colors
