import json
# import google.generativeai as genai  <-- Comentado temporalmente
# from core.config import settings     <-- Comentado temporalmente

# genai.configure(api_key=settings.google_api_key) <-- Comentado temporalmente

def extract_data_from_text(text_content: str) -> dict:
    """
    [MODO DE PRUEBA] Simula una extracción de datos exitosa sin llamar a la API.

    Esto nos permite probar el resto del pipeline (Pre-Flight Check, Supervisor)
    mientras se resuelve el acceso a la API.

    Args:
        text_content: El texto crudo de un documento.

    Returns:
        Un diccionario con datos estructurados de prueba.
    """
    print("[+] (Agent: DataExtractor) [MODO DE PRUEBA] Bypassing API call and returning simulated data.")

    # Este es el resultado que simularemos.
    # Puedes cambiar los valores para probar diferentes escenarios.
    # Por ejemplo, para probar nuestra regla de Pre-Flight, elimina la clave "invoice_id".
    structured_data = {
        "invoice_id": "INV-TEST-123",
        "seller_name": "Test Seller Inc.",
        "buyer_name": "Test Buyer Corp.",
        "total_amount": -1500.75,
        "currency": "USD"
    }
    
    return structured_data
