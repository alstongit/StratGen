import google.generativeai as genai
from config.settings import settings
import json
from typing import Optional, Dict, Any

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Initialize model - THIS is what should be exported as gemini_client
gemini_client = genai.GenerativeModel('gemini-2.0-flash-lite')

async def generate_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Generate text using Gemini 2.0 Flash.
    
    Args:
        prompt: The user prompt
        system_instruction: System instructions for the model
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text response
    """
    try:
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Combine system instruction with prompt if provided
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"
        
        response = gemini_client.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        raise

async def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    """
    Generate JSON response using Gemini 2.0 Flash.
    Ensures the response is valid JSON.
    
    Args:
        prompt: The user prompt
        system_instruction: System instructions for the model
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Parsed JSON response as dictionary
    """
    try:
        # Add JSON formatting instruction
        json_instruction = "\nYou must respond with valid JSON only. No markdown, no explanations, just pure JSON."
        
        full_system_instruction = system_instruction or ""
        full_system_instruction += json_instruction
        
        response_text = await generate_text(
            prompt=prompt,
            system_instruction=full_system_instruction,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Clean response (remove markdown code blocks if present)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        return json.loads(response_text)
    
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Response text: {response_text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    
    except Exception as e:
        print(f"Error generating JSON with Gemini: {e}")
        raise