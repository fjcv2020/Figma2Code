import math


def estimate_cost_per_thousand_tokens(model):
    """
    Returns the cost in USD per 1000 tokens for different models
    
    Args:
        model (str): The model name
        
    Returns:
        tuple: (input_cost, output_cost) in USD per 1000 tokens
    """
    models = {
        # Modelos estándar de OpenAI
        "gpt-4o":
        (0.005, 0.015
         ),  # $5/M input, $15/M output (precios hipotéticos, no confirmados)
        "gpt-4o-mini": (0.00015, 0.0006),  # $0.15/M input, $0.60/M output
        "gpt-3.5-turbo": (0.0015, 0.002),  # $1.5/M input, $2/M output

        # Modelos de Azure - pueden variar según el acuerdo
        "gpt-4o": (0.03, 0.06),  # Tarifa típica de Azure
        "gpt-4o-mini":
        (0.00015,
         0.0006),  # Tarifa típica de Azure (asumiendo similar al de OpenAI)
        "gpt-35-turbo": (0.0015, 0.002),  # Tarifa típica de Azure
    }

    # Default to GPT-4 pricing if model not found
    return models.get(model.lower(), (0.01, 0.03))


def estimate_tokens_from_nodes(node_count, avg_complexity=1.0):
    """
    Estimates the number of tokens required based on node count
    
    Args:
        node_count (int): Number of Figma nodes
        avg_complexity (float): Complexity multiplier (1.0 = average)
        
    Returns:
        int: Estimated number of tokens for prompt
    """
    # Base tokens for system message + fixed parts of prompt
    base_tokens = 1000

    # For very large node counts, apply a diminishing return curve
    # This simulates token compression or summarization for large designs
    if node_count > 1000:
        effective_nodes = 1000 + (node_count - 1000) * 0.3  # 30% efficiency after 1000 nodes
    elif node_count > 500:
        effective_nodes = 500 + (node_count - 500) * 0.5  # 50% efficiency after 500 nodes
    else:
        effective_nodes = node_count
        
    # Tokens per node (varies by complexity)
    tokens_per_node = 100 * avg_complexity

    # Calculate total
    total_tokens = base_tokens + (effective_nodes * tokens_per_node)

    # Cap at model context limit
    return min(math.ceil(total_tokens), 128000)  # gpt-4o context limit


def estimate_cost(node_count, model, avg_complexity=1.0):
    """
    Estimate the cost of generating code for a design with the given number of nodes
    
    Args:
        node_count (int): Number of Figma nodes
        model (str): Model name to use for generation
        avg_complexity (float): Complexity multiplier (1.0 = average)
        
    Returns:
        dict: Cost estimate with details
    """
    # Get cost rates
    input_rate, output_rate = estimate_cost_per_thousand_tokens(model)

    # Estimate tokens
    input_tokens = estimate_tokens_from_nodes(node_count, avg_complexity)

    # Estimate output tokens with diminishing returns for large designs
    # For very large designs, the output doesn't scale linearly
    if node_count > 1000:
        effective_output_nodes = 1000 + (node_count - 1000) * 0.2  # 20% efficiency after 1000 nodes
    elif node_count > 500:
        effective_output_nodes = 500 + (node_count - 500) * 0.4  # 40% efficiency after 500 nodes
    else:
        effective_output_nodes = node_count
        
    # Angular components are verbose (TypeScript, HTML, and SCSS)
    output_tokens = min(effective_output_nodes * 250, 64000)  # Cap at 64k for response

    # Calculate costs
    input_cost = (input_tokens / 1000) * input_rate
    output_cost = (output_tokens / 1000) * output_rate
    total_cost = input_cost + output_cost

    # Return detailed breakdown
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4),
        "total_cost": round(total_cost, 4),
        "formatted_total": f"${total_cost:.4f}"
    }
