import json
import google.generativeai as genai
from core.config import settings

# Configurar la API de Google al inicio
genai.configure(api_key=settings.google_api_key)

def extract_data_from_text(text_content: str) -> dict:
    """
    Utiliza la API de Google Gemini para extraer datos estructurados de un texto.

    Args:
        text_content: El texto crudo de un documento (ej. una factura).

    Returns:
        Un diccionario con los datos estructurados o un diccionario de error.
    """
    print("[+] (Agent: DataExtractor) Starting REAL data extraction with Google Gemini...")

    # Prompt detallado que le indica al LLM qué hacer y qué formato de salida se espera.
    prompt = f"""
    Analiza el siguiente texto de una factura y extrae la siguiente información:
    - invoice_id: El número o identificador de la factura.
    - seller_name: El nombre de la empresa o persona que vende.
    - buyer_name: El nombre de la empresa o persona que compra.
    - total_amount: El monto total de la factura (debe ser un número).
    - currency: La moneda del monto total (ej. USD, EUR, MXN).

    Devuelve el resultado exclusivamente en formato JSON con las claves mencionadas.

    Texto para analizar:
    ---
    {text_content}
    ---
    """

    try:
        # Crear el modelo y generar la respuesta
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        # Limpiar la respuesta para asegurarse de que es un JSON válido
        # Los LLMs a veces envuelven el JSON en ```json ... ```
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        # Convertir la cadena de texto JSON en un diccionario de Python
        structured_data = json.loads(cleaned_response)
        print("[+] (Agent: DataExtractor) Successfully extracted and parsed data from Gemini.")
        return structured_data

    except Exception as e:
        print(f"[-] (Agent: DataExtractor) An error occurred: {e}")
        return {
            "error": True,
            "message": str(e),
            "original_response": response.text if 'response' in locals() else "No response"
        }