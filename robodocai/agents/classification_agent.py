"""
Este módulo contiene el agente responsable de proponer una clasificación
arancelaria (HS Code) para un producto basándose en datos estructurados.
"""
from agents.knowledge_agent import search_tariff_schedule

def propose_tariff_classification(structured_data: dict) -> dict:
    """
    Analiza los datos estructurados, consulta al KnowledgeAgent y propone una
    clasificación arancelaria, con manejo de errores específico.

    Args:
        structured_data: Un diccionario con la información del producto.

    Returns:
        Un diccionario con la clasificación propuesta o un diccionario de error.
    """
    print("[+] (Agent: TariffClassifier) Starting tariff classification...")

    try:
        # Paso 1: Crear una descripción rica del producto uniendo todos los datos disponibles.
        # Esto proporciona un contexto mucho mejor para la búsqueda semántica.
        product_description = " ".join(str(v) for v in structured_data.values() if v)
        if not product_description:
            raise ValueError("No se pudo crear una descripción del producto a partir de los datos estructurados.")

        # Paso 2: Consultar al KnowledgeAgent para obtener el contexto normativo.
        print(f"[+] (Agent: TariffClassifier) Consulting Knowledge Agent for: '{product_description}'")
        tariff_context = search_tariff_schedule(product_description)
        if not tariff_context:
            raise ValueError("El Knowledge Agent no devolvió ningún contexto del arancel.")

        # Paso 3: Formular la propuesta (lógica aún simulada, pero informada por el contexto).
        classification_output = {
            "hs_code": "8517.12.00.00",  # Simulado
            "description": "Teléfonos móviles (celulares) y los de otras redes inalámbricas",
            "confidence_score": 0.95,
            "reasoning": f"La clasificación se basa en el contexto recuperado del arancel: '{tariff_context[-1]}'",
            "source": "Knowledge Agent Search"
        }

        print("[+] (Agent: TariffClassifier) Successfully proposed a classification.")
        return classification_output

    except Exception as e:
        # Captura cualquier error, incluidos los ValueError que definimos, y lo reporta.
        print(f"[-] (Agent: TariffClassifier) An error occurred: {e}")
        return {
            "error": True,
            "message": str(e)
        }
