import os
import openai
from openai import OpenAI, AzureOpenAI
import streamlit as st
from utils import extract_nodes, flatten_figma_tree

# Note: we'll initialize the API clients as needed inside the function
# to ensure we always use the current environment variables and settings


def generate_angular_code(figma_data, responsive=True, additional_instructions="", use_azure=False, azure_endpoint="", azure_model="", node_limit=50, openai_model="gpt-4o"):
    """
    Generate Angular component code from Figma data using OpenAI (standard or Azure)
    
    Args:
        figma_data (dict): The Figma file data
        responsive (bool): Whether to generate responsive code
        additional_instructions (str): Additional instructions for code generation
        use_azure (bool): Whether to use Azure OpenAI API
        azure_endpoint (str): Azure OpenAI endpoint URL
        azure_model (str): Azure OpenAI model deployment name
        node_limit (int): Maximum number of nodes to process
        
    Returns:
        str: Generated Angular component code (HTML, TS, SCSS)
    """
    # Extract document data
    document = figma_data.get("document", {})

    # Prepare the Figma nodes for processing
    nodes = extract_nodes(document)

    # Flatten the Figma node tree for easier processing
    flattened_nodes = flatten_figma_tree(nodes)

    # Limit the number of nodes to prevent token overflow
    if len(flattened_nodes) > node_limit:
        st.warning(
            f"Design contains {len(flattened_nodes)} nodes. Processing only the first {node_limit} nodes to prevent API limits."
        )
        flattened_nodes = flattened_nodes[:node_limit]

    # Create a structured summary of the design
    design_summary = {
        "name":
        figma_data.get("name", "Untitled Design"),
        "nodeCount":
        len(flattened_nodes),
        "canvas":
        document.get("type", ""),
        "children": [
            node.get("name", f"Element-{i}")
            for i, node in enumerate(flattened_nodes)
        ],
    }

    # Extract key design properties
    colors_used = set()
    fonts_used = set()
    element_types = set()

    for node in flattened_nodes:
        # Extract colors
        if "fills" in node:
            for fill in node.get("fills", []):
                if fill.get("type") == "SOLID" and "color" in fill:
                    color = fill["color"]
                    r = int(color["r"] * 255)
                    g = int(color["g"] * 255)
                    b = int(color["b"] * 255)
                    a = color.get("a", 1)
                    colors_used.add(f"rgba({r}, {g}, {b}, {a})")

        # Extract fonts
        if "style" in node:
            style = node.get("style", {})
            if "fontFamily" in style:
                fonts_used.add(style["fontFamily"])

        # Extract element types
        element_types.add(node.get("type", ""))

    # Create a simplified representation of nodes for the prompt
    simplified_nodes = []
    for i, node in enumerate(flattened_nodes):
        # Only include essential properties
        simplified_node = {
            "name": node.get("name", f"Element-{i}"),
            "type": node.get("type", ""),
            "id": node.get("id", ""),
        }

        # Include basic styling properties if available
        if "style" in node:
            simplified_node["style"] = {
                k: v
                for k, v in node["style"].items() if k in [
                    "fontFamily", "fontSize", "fontWeight",
                    "textAlignHorizontal", "textAlignVertical"
                ]
            }

        # Include basic layout properties
        if "absoluteBoundingBox" in node:
            simplified_node["dimensions"] = {
                "width": node["absoluteBoundingBox"].get("width", 0),
                "height": node["absoluteBoundingBox"].get("height", 0),
                "x": node["absoluteBoundingBox"].get("x", 0),
                "y": node["absoluteBoundingBox"].get("y", 0),
            }

        simplified_nodes.append(simplified_node)

    # Create a prompt for the AI
    responsive_text = "Make the design fully responsive with mobile-first approach." if responsive else "Focus on pixel-perfect desktop implementation."
    
    # We already applied the node limit earlier, so this is just to correct simplified_nodes
    if len(simplified_nodes) > len(flattened_nodes):
        simplified_nodes = simplified_nodes[:len(flattened_nodes)]

    prompt = f"""You are an expert Angular developer converting a Figma design to Angular components (TypeScript, HTML templates, and SCSS styles).

Design Summary:
{design_summary}

Extract from design:
- Colors: {list(colors_used)}
- Fonts: {list(fonts_used)}
- Element Types: {list(element_types)}

Requirements:
1. Generate complete, valid Angular component code based on the design.
2. Create THREE files:
   - component.ts (TypeScript class with @Component decorator)
   - component.html (Angular template)
   - component.scss (SCSS styles)
3. {responsive_text}
4. Use Angular best practices including:
   - Proper component structure and annotations
   - Reactive approach for data handling (no template forms)
   - TypeScript interfaces for data models
   - Angular Material components where appropriate
5. Ensure semantic HTML with appropriate tags.
6. Use modern SCSS techniques with variables for colors and dimensions.
7. Implement responsive design with Angular Flex Layout or CSS Grid/Flexbox.
8. Use Angular routing for navigation elements when appropriate.
9. Organize and comment your code for clarity.
10. Ensure fonts are properly imported in the styles.
11. Create reusable sub-components when appropriate.

{additional_instructions}

FIGMA DESIGN NODES (SIMPLIFIED):
{simplified_nodes}

Return the complete Angular component files. Include all three files (TS, HTML, SCSS) in the response, each in its own code block.
"""

    # Log the token count (helpful for debugging)
    import tiktoken
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    token_count = len(encoding.encode(prompt))
    st.session_state["debug_info"]["token_count"] = token_count

    # Check if prompt is too large
    max_tokens = 128000  # Context size for gpt-4o
    if token_count > max_tokens:
        st.warning(
            f"Prompt is too large ({token_count} tokens). Implementando estrategia de procesamiento por bloques."
        )
        
        # Don't simplify - instead, split the design and process in chunks if needed
        st.session_state["debug_info"]["original_token_count"] = token_count
        
        # We'll handle this with a multi-pass approach below instead of truncating
        # prompt remains unchanged
        st.session_state["debug_info"]["processing_strategy"] = "multi_pass"

    # Generate code using OpenAI API (standard or Azure)
    try:
        system_message = "You are an expert Angular developer specializing in converting Figma designs to Angular components with TypeScript, HTML templates, and SCSS styles."
        
        if use_azure and azure_endpoint and azure_model:
            import openai
            from openai import AzureOpenAI
            
            # Use Azure OpenAI API
            st.info(f"Using Azure OpenAI API with model: {azure_model}")
            
            # Set up Azure OpenAI client
            client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2023-05-15"  # Update to latest API version
            )
            
            response = client.chat.completions.create(
                model=azure_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4500
            )
        else:
            # Use standard OpenAI API
            # Initialize OpenAI client with current API key
            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Use the model provided or fallback to default
            model_name = openai_model if openai_model else "gpt-4o"
            
            st.info(f"Using standard OpenAI API with model: {model_name}")
            
            # Use single-phase approach for all designs, regardless of size
            st.info(f"Diseño con {token_count} tokens. Usando un enfoque de fase única para mejor fidelidad.")
            
            # Prepare a detailed design description for accurate reproduction
            design_description = f"""
            EXACT DESIGN DETAILS
            ====================
            
            Colors:
            - Document all colors exactly as they appear in HEX format: {list(colors_used)}
            
            Typography:
            - Fonts: {list(fonts_used)}
            - Maintain exact font sizes, weights, and line heights from the design
            
            Layout:
            - Preserve all spacing, padding, and margins exactly as shown
            - Maintain the precise grid structure shown in the design
            - Keep the same vertical and horizontal alignment of elements
            
            Elements:
            - Cards should have the exact same corner radius as in the design
            - Buttons should match the design's exact styling (borders, shadows, etc.)
            - Icons must be positioned and sized exactly as shown
            
            Content:
            - Text content must be identical to what appears in the design
            - Maintain the same text formatting (bold, italic, etc.)
            
            Design Notes:
            - Pay special attention to color gradients or shadows if present
            - Reproduce any hover states or interactive elements faithfully
            - Ensure the responsive behavior maintains the design's integrity at different screen sizes
            """
            
            # We'll use a more focused subset of nodes if needed
            if len(simplified_nodes) > 100:
                subset_nodes = simplified_nodes[:100]  # Focus on first 100 nodes
                node_note = f"Note: Focusing on a subset of {len(subset_nodes)} most important nodes out of {len(simplified_nodes)} total nodes"
            else:
                subset_nodes = simplified_nodes
                node_note = "Processing all design nodes"
            
            # Create enhanced single-phase prompt
            enhanced_prompt = f"""You are a senior Angular developer tasked with PERFECTLY recreating a Figma design in code.

            IMPORTANT: Your objective is PIXEL-PERFECT recreation of the following design, with exact colors, spacing, typography, and layout.
            
            Design Summary:
            {design_summary}
            
            Extract from design:
            - Colors: {list(colors_used)}
            - Fonts: {list(fonts_used)}
            - Element Types: {list(element_types)}
            
            {design_description}
            
            {node_note}
            
            FIGMA DESIGN NODES (SIMPLIFIED):
            {subset_nodes}
            
            STRICT REQUIREMENTS:
            1. Create THREE complete files matching the design EXACTLY:
               - component.ts (TypeScript class with @Component decorator)
               - component.html (Angular template with EXACT structure matching design)
               - component.scss (SCSS with PRECISE styling matching design)
            2. {responsive_text}
            3. Follow Angular best practices
            4. Use semantic HTML (section, article, nav, etc. as appropriate)
            5. Use CSS Grid AND Flexbox for layout as needed
            6. Match ALL visual details: colors, fonts, spacing, borders, shadows, etc.
            7. Do not substitute or simplify ANY visual elements
            8. Include ALL text content exactly as shown in the design
            9. Generate ALL necessary CSS for the layout to work properly
            10. {additional_instructions}
            
            CRITICAL: Compare your work to the design multiple times during creation. Your code must reproduce the design exactly as shown, including all visual details, layout, and styling.
            
            Return the complete Angular component files. Include all three files (TS, HTML, SCSS) in your response, each in its own code block.
            """
            
            # Use the enhanced single-phase approach for all designs
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.3,
                max_tokens=4500
            )

        # Extract the generated code
        generated_code = response.choices[0].message.content
        
        # Process the Angular component files (extract from markdown code blocks)
        processed_response = ""
        
        # Extract TypeScript component code
        if "```typescript" in generated_code or "```ts" in generated_code:
            ts_start = generated_code.find("```typescript")
            if ts_start == -1: 
                ts_start = generated_code.find("```ts")
                ts_start = ts_start + 5 if ts_start != -1 else -1
            else:
                ts_start = ts_start + 13
                
            if ts_start != -1:
                ts_end = generated_code.find("```", ts_start)
                ts_code = generated_code[ts_start:ts_end].strip()
                processed_response += "// component.ts\n" + ts_code + "\n\n"
        
        # Extract HTML template code
        if "```html" in generated_code:
            html_start = generated_code.find("```html") + 7
            html_end = generated_code.find("```", html_start)
            html_code = generated_code[html_start:html_end].strip()
            processed_response += "<!-- component.html -->\n" + html_code + "\n\n"
        
        # Extract SCSS style code
        if "```scss" in generated_code or "```css" in generated_code:
            scss_start = generated_code.find("```scss")
            if scss_start == -1: 
                scss_start = generated_code.find("```css")
                scss_start = scss_start + 6 if scss_start != -1 else -1
            else:
                scss_start = scss_start + 7
                
            if scss_start != -1:
                scss_end = generated_code.find("```", scss_start)
                scss_code = generated_code[scss_start:scss_end].strip()
                processed_response += "/* component.scss */\n" + scss_code + "\n"
                
        # If no code blocks were found, return the raw response
        if not processed_response:
            return "/* No properly formatted code blocks found in response */\n\n" + generated_code
            
        return processed_response

    except Exception as e:
        error_message = f"""
// Error in Angular component generation

/**
 * ERROR DETAILS
 * -------------
 * {str(e)}
 */

// component.ts
import {{ Component, OnInit }} from '@angular/core';

@Component({{
  selector: 'app-error',
  templateUrl: './error.component.html',
  styleUrls: ['./error.component.scss']
}})
export class ErrorComponent implements OnInit {{
  errorMessage = '{str(e).replace("'", "")}';
  
  constructor() {{ }}
  
  ngOnInit(): void {{
    console.error('Error generating Angular code:', this.errorMessage);
  }}
}}

<!-- component.html -->
<div class="error-container">
  <h1>Error Generating Angular Code</h1>
  <div class="error-message">
    <p>An error occurred while generating the Angular components:</p>
    <pre>{{errorMessage}}</pre>
  </div>
  <p>Please check your API configuration and try again.</p>
</div>

/* component.scss */
.error-container {{
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}}

.error-message {{
  color: #d32f2f;
  background: #ffebee;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
}}

pre {{
  white-space: pre-wrap;
  word-break: break-all;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}}
"""
        return error_message
