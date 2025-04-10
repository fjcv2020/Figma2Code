import os
import streamlit as st
import time
import json
from figma_api import FigmaAPI
from code_generator import generate_angular_code
from image_to_code import generate_angular_from_image
from utils import save_file, read_file, validate_inputs
from cost_estimator import estimate_cost

# Set page configuration
st.set_page_config(
    page_title="FigmaToCode - Convert Figma Designs to Angular",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state variables
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []
if 'file_key' not in st.session_state:
    st.session_state.file_key = ""
if 'node_id' not in st.session_state:
    st.session_state.node_id = ""
if 'access_token' not in st.session_state:
    st.session_state.access_token = ""
if 'preview_url' not in st.session_state:
    st.session_state.preview_url = ""
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = {
        "token_count": 0,
        "reduced_token_count": 0
    }
if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False

# Main page header
st.title("🎨 FigmaToCode")
st.subheader("Convert Figma Designs to Angular Components")

# Sidebar for settings and instructions
with st.sidebar:
    st.header("Settings")
    
    # API Key tabs for OpenAI vs Azure OpenAI
    api_tabs = st.tabs(["OpenAI API", "Azure OpenAI API"])
    
    with api_tabs[0]:
        # Standard OpenAI API Key
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password",
            help="Your OpenAI API key to use for code generation"
        )
        
        openai_model = st.selectbox(
            "OpenAI Model",
            ["gpt-4o", "gpt-4o-mini"],
            index=0,
            help="Select the model to use for code generation. gpt-4o ofrece mejor calidad pero gpt-4o-mini es más económico."
        )
        
        st.info("The API key is used for generating Angular code from the design.")
        
    with api_tabs[1]:
        # Azure OpenAI API settings
        azure_api_key = st.text_input(
            "Azure OpenAI API Key",
            value=os.environ.get("AZURE_OPENAI_API_KEY", ""),
            type="password",
            help="Your Azure OpenAI API key"
        )
        
        azure_endpoint = st.text_input(
            "Azure API Endpoint",
            placeholder="https://your-resource-name.openai.azure.com",
            help="Your Azure OpenAI API endpoint URL"
        )
        
        azure_model = st.text_input(
            "Azure Model Deployment Name",
            placeholder="e.g. gpt-4o-deployment",
            help="The deployment name of your model in Azure"
        )
        
        st.info("These settings are only needed if you want to use Azure OpenAI instead of standard OpenAI.")
    
    # Figma access token
    st.subheader("Figma Settings")
    access_token = st.text_input(
        "Figma Access Token", 
        value=os.environ.get("ACCESS_TOKEN", st.session_state.access_token),
        type="password",
        help="Your Figma personal access token"
    )
    
    # Node limit settings
    st.subheader("Performance & Cost")
    node_limit = st.slider(
        "Node Limit",
        min_value=10,
        max_value=10000,
        value=50,
        step=50,
        help="Limit the number of nodes to process (higher = more complete design but higher cost)"
    )
    
    # Store model choice in session state
    selected_model = azure_model if azure_api_key and azure_endpoint and azure_model else openai_model
    
    # Show cost estimate
    if node_limit > 0:
        cost_estimate = estimate_cost(node_limit, selected_model)
        st.info(f"Estimated cost: {cost_estimate['formatted_total']} USD")
        with st.expander("Cost details"):
            st.write(f"Model: {cost_estimate['model']}")
            st.write(f"Input tokens: {cost_estimate['input_tokens']} (${cost_estimate['input_cost']:.4f})")
            st.write(f"Output tokens: {cost_estimate['output_tokens']} (${cost_estimate['output_cost']:.4f})")
            st.write(f"Total cost: ${cost_estimate['total_cost']:.4f}")
            
    # Set environment variables
    if azure_api_key:
        os.environ["AZURE_OPENAI_API_KEY"] = azure_api_key
    
    # Instructions
    st.markdown("---")
    st.subheader("Instructions")
    st.markdown("""
    1. **Get Figma File Key**: The key in the URL after /file/ (e.g., figma.com/file/**key**/...)
    2. **Get Node ID**: Select an element and get the node ID from the URL or Share menu
    3. **Generate Access Token**: From Figma menu: Help → Account settings → Personal access tokens
    4. Click "Convert to Code" to generate Angular components
    """)
    
    st.markdown("---")
    
    # About section
    st.markdown("### About")
    st.markdown("""
    This app converts Figma designs to Angular components using AI technology.
    It processes the design structure, styles, and layout to generate 
    responsive and clean Angular code (TypeScript, HTML, and SCSS).
    """)

# Main content area - tabs for different input methods
input_method = st.radio("Choose Input Method", ["Figma API", "Upload Image (New!)"], horizontal=True)

# Angular Material option
use_material = st.checkbox("Use Angular Material Components", 
                           value=True, 
                           help="When enabled, the generator will detect and create Angular Material components when appropriate")

# Main content area - split into two columns
col1, col2 = st.columns([1, 1])

with col1:
    if input_method == "Figma API":
        st.subheader("Figma Design Input")
        
        # File Key and Node ID inputs
        file_key = st.text_input(
            "Figma File Key",
            value=st.session_state.file_key,
            help="The key in the URL after /file/ (e.g., figma.com/file/**key**/...)"
        )
        
        node_id = st.text_input(
            "Node ID (Optional)",
            value=st.session_state.node_id,
            help="ID of specific node to convert (leave empty for entire file)"
        )
        
        if not st.session_state.access_token:
            st.warning("⚠️ Please set your Figma Personal Access Token in the sidebar")
        
        # Design specifications and details
        st.subheader("Design Specifications")
        
        # Options for responsiveness and additional features
        responsive = st.checkbox("Generate Responsive Layout", value=True)
        
        additional_instructions = st.text_area(
            "Additional Instructions",
            placeholder="Describe any specific styling, behavior, or features you want in the generated Angular components...",
            height=150
        )
        
        # Conversion button
        if st.button("Convert to Angular"):
            # Validate Figma API inputs
            valid, error_message = validate_inputs(file_key, access_token, openai_api_key)
            
            if not valid:
                st.error(error_message)
            else:
                # Save to session state
                st.session_state.file_key = file_key
                st.session_state.node_id = node_id
                st.session_state.access_token = access_token
                
                # Set environment variables for API keys
                os.environ["OPENAI_API_KEY"] = openai_api_key
                
                # Show progress
                with st.spinner("Fetching design from Figma..."):
                    # Initialize Figma API
                    figma_api = FigmaAPI(access_token)
                    
                    try:
                        # Get Figma file data
                        file_data = figma_api.get_file(file_key, node_id)
                        
                        if file_data:
                            # Show a preview of the design
                            try:
                                # Get the first node ID if not specified
                                preview_node_id = node_id if node_id else file_data["document"]["id"]
                                images = figma_api.get_image_urls(file_key, [preview_node_id])
                                
                                if images and preview_node_id in images:
                                    st.session_state.preview_url = images[preview_node_id]
                                    st.success("Preview obtained successfully!")
                                    
                                    # Download button for the preview image
                                    import requests
                                    st.download_button(
                                        "Download Preview Image",
                                        data=requests.get(st.session_state.preview_url).content,
                                        file_name="figma_preview.png",
                                        mime="image/png"
                                    )
                                else:
                                    st.warning("Preview not available for this node")
                            except Exception as e:
                                st.warning(f"Couldn't generate preview: {str(e)}")
                                
                            # Display the preview if available
                            if "preview_url" in st.session_state and st.session_state.preview_url:
                                st.subheader("Design Preview")
                                st.image(st.session_state.preview_url, use_container_width=True)
                            
                            # Continue with code generation
                            # Progress indicator for code generation
                            with st.spinner("Generating Angular components..."):
                                # Determine which API to use
                                use_azure = bool(azure_api_key and azure_endpoint and azure_model)
                                
                                # Import the mixed approach generator
                                from enhanced_generator import process_figma_with_mixed_approach
                                
                                # Generate Angular code using the mixed approach
                                code = process_figma_with_mixed_approach(
                                    file_data,
                                    openai_api_key=openai_api_key,
                                    responsive=responsive,
                                    additional_instructions=additional_instructions,
                                    use_azure=use_azure,
                                    azure_endpoint=azure_endpoint,
                                    azure_model=azure_model,
                                    node_limit=node_limit,
                                    openai_model=openai_model,
                                    use_material=use_material
                                )
                                
                                # Save generated code
                                st.session_state.generated_code = code
                                
                                # Add to conversion history
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                                history_item = {
                                    "timestamp": timestamp,
                                    "file_key": file_key,
                                    "node_id": node_id,
                                    "code": code
                                }
                                st.session_state.conversion_history.insert(0, history_item)
                                
                                # Save to file
                                save_file("output_angular.txt", code)
                                
                                st.success("Angular components generated successfully!")
                        else:
                            st.error("Failed to retrieve Figma file data. Please check your file key and access token.")
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    else:  # Image upload method
        st.subheader("Upload Design Image")
        st.info("📸 ¡Nueva funcionalidad! Convierte imágenes PNG/JPG directamente a código Angular")
        
        # Image uploader
        uploaded_file = st.file_uploader("Upload a design image (PNG, JPG)", type=["png", "jpg", "jpeg"])
        
        # Design specifications
        st.subheader("Design Specifications")
        responsive_img = st.checkbox("Generate Responsive Layout", value=True, key="responsive_img")
        
        additional_instructions_img = st.text_area(
            "Additional Instructions",
            placeholder="Describe any specific styling, behavior, or features you want in the generated Angular components...",
            height=150,
            key="additional_instructions_img"
        )
        
        # Process image button
        if st.button("Convert Image to Angular"):
            if not openai_api_key and not (azure_api_key and azure_endpoint and azure_model):
                st.error("Please provide an OpenAI API key or Azure OpenAI credentials")
            elif not uploaded_file:
                st.error("Please upload an image file")
            else:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                
                # Display the uploaded image
                st.subheader("Uploaded Design")
                st.image(uploaded_file, use_container_width=True)
                
                # Process the image
                with st.spinner("Generating Angular components from image..."):
                    # Determine which API to use
                    use_azure = bool(azure_api_key and azure_endpoint and azure_model)
                    
                    try:
                        # Generate Angular code from image
                        code = generate_angular_from_image(
                            uploaded_file,
                            responsive=responsive_img,
                            additional_instructions=additional_instructions_img,
                            use_azure=use_azure,
                            azure_endpoint=azure_endpoint,
                            azure_model=azure_model,
                            openai_model=openai_model
                        )
                        
                        # Save generated code
                        st.session_state.generated_code = code
                        
                        # Add to conversion history
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        history_item = {
                            "timestamp": timestamp,
                            "file_key": "image_upload",
                            "node_id": "",
                            "code": code
                        }
                        st.session_state.conversion_history.insert(0, history_item)
                        
                        # Save to file
                        save_file("output_angular.txt", code)
                        
                        st.success("Angular components generated successfully from image!")
                    except Exception as e:
                        st.error(f"An error occurred processing the image: {str(e)}")

with col2:
    st.subheader("Generated Angular Components")
    
    # Tabs for code view, preview, history and debug
    code_tab, preview_tab, history_tab, debug_tab = st.tabs(["Code", "Preview", "History", "Debug"])
    
    with code_tab:
        # Show generated code with syntax highlighting
        if st.session_state.generated_code:
            st.code(st.session_state.generated_code, language="typescript")
            
            # Download button for the code
            st.download_button(
                "Download Angular Components",
                st.session_state.generated_code,
                file_name="figma_to_angular.txt",
                mime="text/plain"
            )
        else:
            st.info("Generated Angular components will appear here after conversion.")
    
    with preview_tab:
        # Show a preview of the generated HTML
        if st.session_state.generated_code:
            # Extract the HTML part from the code
            html_start = st.session_state.generated_code.find("<!-- component.html -->")
            if html_start != -1:
                html_end = st.session_state.generated_code.find("/* component.scss */") if "/* component.scss */" in st.session_state.generated_code else -1
                if html_end == -1:  # If scss not found, try to find next code block
                    html_end = st.session_state.generated_code.find("\n\n", html_start + 20)
                
                # Extract HTML code
                if html_end > html_start:
                    html_code = st.session_state.generated_code[html_start:html_end].strip()
                    html_code = html_code.replace("<!-- component.html -->", "").strip()
                    
                    # Extract SCSS styles
                    scss_start = st.session_state.generated_code.find("/* component.scss */")
                    if scss_start != -1:
                        scss_code = st.session_state.generated_code[scss_start:].replace("/* component.scss */", "").strip()
                    else:
                        scss_code = ""
                    
                    # Create a preview HTML with the styles and enhanced display
                    preview_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Angular Component Preview</title>
                        <!-- Include fonts if needed -->
                        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
                        <link href="https://fonts.googleapis.com/css2?family=Material+Icons&display=swap" rel="stylesheet">
                        <!-- Base styles to improve rendering -->
                        <style>
                            body {{
                                font-family: 'Roboto', Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                                box-sizing: border-box;
                                background-color: #f5f5f5;
                            }}
                            .component-preview {{
                                background-color: white;
                                padding: 20px;
                                border-radius: 8px;
                                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                                margin: 20px auto;
                                max-width: 1200px;
                                overflow: auto;
                            }}
                            /* Angular Material mock styles */
                            .mat-button {{
                                display: inline-block;
                                padding: 8px 16px;
                                border-radius: 4px;
                                background-color: #3f51b5;
                                color: white;
                                font-weight: 500;
                                text-align: center;
                                text-decoration: none;
                                cursor: pointer;
                            }}
                            .mat-card {{
                                background-color: #fff;
                                border-radius: 4px;
                                box-shadow: 0 2px 1px -1px rgba(0,0,0,.2), 0 1px 1px 0 rgba(0,0,0,.14), 0 1px 3px 0 rgba(0,0,0,.12);
                                padding: 16px;
                                margin-bottom: 16px;
                            }}
                            /* Custom SCSS from generated code */
                            {scss_code}
                        </style>
                    </head>
                    <body>
                        <div class="component-preview">
                            {html_code}
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Save the preview HTML to a file
                    save_file("output.html", preview_html)
                    
                    # Display preview using HTML component
                    st.components.v1.html(preview_html, height=600, scrolling=True)
                    
                    # Download button for HTML preview
                    st.download_button(
                        "Download HTML Preview",
                        preview_html,
                        file_name="angular_preview.html",
                        mime="text/html"
                    )
                else:
                    st.info("No se pudo extraer el código HTML para la vista previa.")
            else:
                st.info("No se encontró código HTML en los componentes generados.")
        else:
            st.info("La vista previa del código aparecerá aquí después de la conversión.")
    
    with history_tab:
        # Show conversion history
        if st.session_state.conversion_history:
            for i, item in enumerate(st.session_state.conversion_history):
                with st.expander(f"{item['timestamp']} - {item['file_key']}"):
                    st.code(item['code'], language="typescript")
                    
                    st.download_button(
                        f"Download #{i+1}",
                        item['code'],
                        file_name=f"figma_angular_{i+1}.txt",
                        mime="text/plain"
                    )
        else:
            st.info("Conversion history will be shown here.")
    
    with debug_tab:
        # Toggle for debug info
        show_debug = st.checkbox("Show Debug Info", value=st.session_state.show_debug)
        st.session_state.show_debug = show_debug
        
        if st.session_state.show_debug:
            st.subheader("Debug Information")
            st.json(st.session_state.debug_info)
            
            # Only show this if we have generated code
            if st.session_state.generated_code:
                st.subheader("Token Usage")
                st.write(f"Prompt Tokens: {st.session_state.debug_info.get('token_count', 'N/A')}")
                if 'reduced_token_count' in st.session_state.debug_info:
                    st.write(f"Reduced Tokens: {st.session_state.debug_info['reduced_token_count']}")
                if 'original_token_count' in st.session_state.debug_info:
                    st.write(f"Original Token Count: {st.session_state.debug_info['original_token_count']}")
                if 'processing_strategy' in st.session_state.debug_info:
                    st.subheader("Processing Strategy")
                    if st.session_state.debug_info['processing_strategy'] == 'multi_pass':
                        st.info("""
                        Se utilizó un enfoque multi-fase para procesar este diseño:
                        
                        1. **Fase 1**: Análisis de estructura - Identificar componentes principales
                        2. **Fase 2**: Planificación de componentes - Decidir cómo implementarlos
                        3. **Fase 3**: Generación de código - Producir el código Angular
                        
                        Este enfoque permite manejar diseños complejos más eficientemente.
                        """)
                    else:
                        st.info("""
                        Se utilizó un enfoque de una fase única para procesar este diseño, 
                        lo que generalmente produce resultados con mayor fidelidad visual
                        al mantener todo el contexto del diseño en un solo prompt.
                        """)

# Show OpenAI API key warning if it's not set and user is trying to convert
if not openai_api_key and not azure_api_key and st.button("I need an API key"):
    st.info("""
    You need an OpenAI API key to use this application. You can get one by:
    
    1. Going to [OpenAI API](https://platform.openai.com/signup)
    2. Creating an account or signing in
    3. Navigate to API Keys section
    4. Generate a new API key
    
    Or if you prefer to use Azure OpenAI:
    
    1. Set up an Azure OpenAI resource
    2. Deploy a model
    3. Get your endpoint and API key from the Azure portal
    """)

# Optional: Debug tools section at the bottom (hidden by default)
if st.session_state.show_debug:
    st.markdown("---")
    st.subheader("Advanced Debug Tools")
    
    # Test API connection
    if st.button("Test API Connection"):
        try:
            if openai_api_key:
                import openai
                openai.api_key = openai_api_key
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello!"}],
                    max_tokens=5
                )
                st.success(f"API connection successful. Model: {response.model}")
            elif azure_api_key and azure_endpoint:
                st.info("Testing Azure OpenAI connection...")
                # Azure connection test would go here
                st.success("Azure API connection test not implemented yet.")
            else:
                st.error("No API keys provided.")
        except Exception as e:
            st.error(f"API connection failed: {str(e)}")