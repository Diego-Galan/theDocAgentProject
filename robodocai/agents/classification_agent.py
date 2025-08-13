"""
Este módulo contiene el agente responsable de proponer una clasificación
arancelaria (HS Code) para un producto basándose en datos estructurados.
"""
import json
import google.generativeai as genai
from core.config import settings
from agents.knowledge_agent import search_tariff_schedule

# Configurar la API de Google al inicio del módulo
genai.configure(api_key=settings.google_api_key)

def propose_tariff_classification(structured_data: dict) -> dict:
    """
    Analiza datos, consulta el arancel vía KnowledgeAgent y usa un LLM para proponer
    una clasificación arancelaria estructurada.

    Args:
        structured_data: Un diccionario con la información del producto.

    Returns:
        Un diccionario con la clasificación propuesta o un diccionario de error.
    """
    print("[+] (Agent: TariffClassifier) Starting tariff classification...")

    try:
        # Paso 1: Crear una descripción rica del producto.
        product_description = " ".join(str(v) for v in structured_data.values() if v)
        if not product_description:
            raise ValueError("No se pudo crear una descripción del producto a partir de los datos estructurados.")

        # Paso 2: Consultar al KnowledgeAgent para obtener el contexto normativo.
        print(f"[+] (Agent: TariffClassifier) Consulting Knowledge Agent for: '{product_description}'")
        tariff_context = search_tariff_schedule(product_description)
        if not tariff_context:
            raise ValueError("El Knowledge Agent no devolvió ningún contexto del arancel.")

        # Paso 3: Usar el LLM para analizar el contexto y proponer una clasificación.
        print("[+] (Agent: TariffClassifier) Calling Google Gemini for analysis...")

        # Construcción del prompt para el LLM
        prompt = f"""
        Actúa como un experto clasificador de aduanas. Tu tarea es analizar la descripción de un producto
        y, basándote EXCLUSIVAMENTE en los fragmentos del arancel de aduanas proporcionados, proponer
        la clasificación arancelaria (HS Code) más adecuada.

        **Descripción del Producto:**
        {product_description}

        **Fragmentos del Arancel de Aduanas para tu Análisis:**
        ---
        {"\n---\n".join(tariff_context)}
---
".join(tariff_context)
        ---

        **Instrucciones de Salida:**
        Devuelve tu análisis en un único objeto JSON. El JSON debe tener la siguiente estructura y campos:
        - \"hs_code\": (string) El código HS que consideres más apropiado.
        - \"description\": (string) La descripción oficial que corresponde a ese código HS, extraída del contexto.
        - \"confidence_score\": (float) Tu nivel de confianza en la clasificación, entre 0.0 y 1.0.
        - \"reasoning\": (string) Una explicación concisa de por qué elegiste ese código, citando la lógica del arancel.
        - \"source_text\": (string) El fragmento de texto exacto del arancel que usaste como evidencia principal.

        Asegúrate de que la salida sea únicamente el objeto JSON, sin ningún texto o formato adicional.
        """

        # Llamada a la API de Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        # Limpieza y parseo de la respuesta
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        classification_output = json.loads(cleaned_response)

        print("[+] (Agent: TariffClassifier) Successfully received and parsed classification from Gemini.")
        return classification_output

    except Exception as e:
        # Captura cualquier error (de red, de parseo, etc.) y lo reporta.
        print(f"[-] (Agent: TariffClassifier) An error occurred: {e}")
        return {
            "error": True,
            "message": str(e)
        }
