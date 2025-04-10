import os
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

def encode_image_to_base64(image_file):
    """
    Encode an image file to base64 string
    
    Args:
        image_file: Uploaded image file (BytesIO object)
        
    Returns:
        str: Base64 encoded string
    """
    if hasattr(image_file, "read"):
        # If it's a file-like object
        img_data = image_file.read()
    else:
        # If it's a path
        with open(image_file, "rb") as f:
            img_data = f.read()
            
    # Convert to base64
    base64_encoded = base64.b64encode(img_data).decode("utf-8")
    return base64_encoded

def resize_image_if_needed(image_file, max_size=10*1024*1024):
    """
    Resize an image if it's too large (for API limits)
    
    Args:
        image_file: Image file (BytesIO or path)
        max_size: Maximum file size in bytes
        
    Returns:
        BytesIO: Processed image in BytesIO object
    """
    # Read the image
    if hasattr(image_file, "read"):
        image_file.seek(0)  # Reset file pointer to beginning
        img = Image.open(image_file)
    else:
        img = Image.open(image_file)
    
    # Check file size with BytesIO
    temp_buffer = BytesIO()
    img.save(temp_buffer, format=img.format or "PNG")
    current_size = temp_buffer.tell()
    
    # If the image is already small enough, return it
    if current_size <= max_size:
        temp_buffer.seek(0)
        return temp_buffer
    
    # Calculate scale factor to reduce size
    scale_factor = (max_size / current_size) ** 0.5 * 0.9  # 0.9 is a safety factor
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    
    # Resize the image
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Save to buffer
    output_buffer = BytesIO()
    resized_img.save(output_buffer, format=img.format or "PNG")
    output_buffer.seek(0)
    
    return output_buffer

def generate_angular_from_image(image_file, responsive=True, additional_instructions="", use_azure=False, azure_endpoint="", azure_model="", openai_model="gpt-4o"):
    """
    Generate Angular component code from an image using OpenAI Vision API
    
    Args:
        image_file: The uploaded image file
        responsive: Whether to make the component responsive
        additional_instructions: Additional instructions for code generation
        use_azure: Whether to use Azure OpenAI
        azure_endpoint: Azure endpoint URL
        azure_model: Azure model name
        openai_model: OpenAI model to use
        
    Returns:
        str: Generated Angular component code (HTML, TS, SCSS)
    """
    try:
        # Process the image (resize if needed)
        processed_image = resize_image_if_needed(image_file)
        
        # Convert the image to base64
        base64_image = encode_image_to_base64(processed_image)
        
        # Responsive text for the prompt
        responsive_text = "Ensure the layout is fully responsive and works well on all screen sizes." if responsive else "Focus on pixel-perfect implementation for desktop screens."
        
        # Build system message
        system_message = "You are an expert Angular developer specializing in converting designs to Angular components with TypeScript, HTML templates, and SCSS styles."
        
        # Build the user prompt
        prompt = f"""Please convert this image into Angular component code.

EXACT DESIGN DETAILS:
Focus on creating a pixel-perfect recreation of the design shown in the image.

Requirements:
1. Generate complete, valid Angular component code based on the design.
2. Create THREE files:
   - component.ts (TypeScript class with @Component decorator)
   - component.html (Angular template with EXACT structure matching design)
   - component.scss (SCSS with PRECISE styling matching design)
3. {responsive_text}
4. Follow Angular best practices
5. Use semantic HTML (section, article, nav, etc. as appropriate)
6. Use CSS Grid AND Flexbox for layout as needed
7. Match ALL visual details: colors, fonts, spacing, borders, shadows, etc.
8. Do not substitute or simplify ANY visual elements
9. Include ALL text content exactly as shown in the design
10. Generate ALL necessary CSS for the layout to work properly

{additional_instructions}

Return the complete Angular component files. Include all three files (TS, HTML, SCSS) in your response, each in its own code block.
"""
        
        # Generate code using OpenAI API (standard or Azure)
        if use_azure and azure_endpoint and azure_model:
            import openai
            from openai import AzureOpenAI
            
            # Use Azure OpenAI API
            st.info(f"Using Azure OpenAI API with model: {azure_model}")
            
            # Set up Azure OpenAI client
            client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2023-05-15"  # Update to the latest API version
            )
            
            # Azure OpenAI call with vision capabilities
            response = client.chat.completions.create(
                model=azure_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
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
            
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
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
// Error in Angular component generation from image

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
    console.error('Error generating Angular code from image:', this.errorMessage);
  }}
}}

<!-- component.html -->
<div class="error-container">
  <h1>Error Generating Angular Code from Image</h1>
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