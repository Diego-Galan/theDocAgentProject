"""
Este módulo contiene el Pre-Flight Check Agent, responsable de realizar
validaciones de negocio sobre los datos antes de que comience el procesamiento principal.
"""
from db import models

def run_pre_flight_checks(structured_data: dict, classification_data: dict, document_type: models.DocumentType) -> dict:
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

    # Definir Incoterms válidos
    valid_incoterms = {
        'EXW', 'FCA', 'FAS', 'FOB', 'CFR', 'CIF', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP'
    }

    # --- INICIO DE REGLAS DE NEGOCIO ---

    # Aplicar reglas específicas solo para FACTURA_COMERCIAL
    if document_type == models.DocumentType.FACTURA_COMERCIAL:
        # Regla 1: Validar la existencia del 'invoice_id'.
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

        # Regla 3: Validación de Incoterm
        incoterm = structured_data.get("incoterm")
        if incoterm and incoterm.upper() not in valid_incoterms:
            check_results["checks_passed"] = False
            check_results["errors"].append(
                "Error Crítico: El Incoterm especificado no es un Incoterm 2020 válido."
            )
        elif not incoterm: # Consider incoterm mandatory for commercial invoices
            check_results["checks_passed"] = False
            check_results["errors"].append(
                "Error Crítico: El Incoterm es un campo obligatorio para la factura comercial y no fue encontrado o está vacío."
            )

        # Regla 4: Auditoría Matemática
        line_items = structured_data.get("line_items")
        if isinstance(line_items, list) and line_items:
            calculated_total = 0.0
            for item in line_items:
                quantity = item.get("quantity")
                unit_price = item.get("unit_price")

                if isinstance(quantity, (int, float)) and isinstance(unit_price, (int, float)):
                    calculated_total += (quantity * unit_price)
                else:
                    # If any item has invalid quantity or unit_price, flag an error
                    check_results["checks_passed"] = False
                    check_results["errors"].append(
                        "Error Crítico: Uno o más ítems de línea tienen cantidad o precio unitario inválido."
                    )
                    break # No need to continue if data is malformed

            # Compare with total_amount, allowing for small floating point inaccuracies
            if isinstance(total_amount, (int, float)) and abs(calculated_total - total_amount) > 0.01:
                check_results["checks_passed"] = False
                check_results["errors"].append(
                    "Error Crítico: La suma de los ítems de línea no coincide con el monto total de la factura."
                )
        elif total_amount is not None and (not isinstance(line_items, list) or not line_items):
            # If total_amount is present but line_items are missing or empty
            check_results["checks_passed"] = False
            check_results["errors"].append(
                "Error Crítico: La factura comercial debe contener ítems de línea para la auditoría matemática."
            )


    # --- FIN DE REGLAS DE NEGOCIO ---

    if check_results["checks_passed"]:
        print("[+] (Agent: PreFlightChecker) Pre-flight checks completed successfully.")
    else:
        print(f"[!] (Agent: PreFlightChecker) Pre-flight checks failed. Errors found: {check_results['errors']}")

    return check_results
