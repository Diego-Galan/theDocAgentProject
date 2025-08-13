"""
Este módulo contiene el Pre-Flight Check Agent, responsable de realizar
validaciones de negocio sobre los datos antes de que comience el procesamiento principal.
"""
from db import models # Added import

def run_pre_flight_checks(structured_data: dict, classification_data: dict, document_type: models.DocumentType) -> dict: # Modified signature
    """
    Ejecuta una serie de validaciones de negocio sobre los datos extraídos y clasificados.

    Args:
        structured_data: El diccionario de datos extraído de la factura.
        classification_data: El diccionario con la clasificación arancelaria propuesta.
        document_type: El tipo de documento que se está procesando.

    Returns:
        Un diccionario con los resultados de las comprobaciones.
    """
    print("[+] (Agent: PreFlightChecker) Starting real pre-flight business checks...")

    # Inicializa el diccionario de resultados asumiendo que todo está bien.
    # Este es el estado por defecto.
    check_results = {
        "checks_passed": True,
        "warnings": [],
        "errors": []
    }

    # --- INICIO DE REGLAS DE NEGOCIO ---

    # Aplicar reglas específicas solo para FACTURA_COMERCIAL
    if document_type == models.DocumentType.FACTURA_COMERCIAL:
        # Regla 1: Validar la existencia del 'invoice_id'.
        # Este es un campo crítico para la auditoría y la identificación.
        invoice_id = structured_data.get("invoice_id")
        if not invoice_id: # Esta condición cubre tanto la ausencia de la clave como un valor None o vacío.
            check_results["checks_passed"] = False
            check_results["errors"].append(
                "Error Crítico: El número de factura (invoice_id) es un campo obligatorio y no fue encontrado o está vacío."
            )

        # Regla 2: Validar que el 'total_amount' sea un número válido y positivo.
        total_amount = structured_data.get("total_amount")
        if not isinstance(total_amount, (int, float)) or total_amount <= 0:
            check_results["checks_passed"] = False
            check_results["errors"].append(
                f"Error Crítico: El monto total de la factura ('{total_amount}') no es un número válido o es menor o igual a cero."
            )
    # --- FIN DE REGLAS DE NEGOCIO ---

    if check_results["checks_passed"]:
        print("[+] (Agent: PreFlightChecker) Pre-flight checks completed successfully.")
    else:
        print(f"[!] (Agent: PreFlightChecker) Pre-flight checks failed. Errors found: {check_results['errors']}")

    return check_results