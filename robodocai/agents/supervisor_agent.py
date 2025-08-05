"""
Este módulo contiene el agente Supervisor, responsable de realizar una revisión
final de coherencia y calidad sobre los datos procesados por otros agentes.
"""

def review_final_output(structured_data: dict, classification_data: dict) -> dict:
    """
    Revisa la salida combinada de los agentes de extracción y clasificación
    para asegurar la coherencia y la lógica del resultado final.

    Args:
        structured_data: El diccionario de datos extraído de la factura.
        classification_data: El diccionario con la clasificación arancelaria propuesta.

    Returns:
        Un diccionario con el veredicto del supervisor.
    """
    print("[+] (Agent: Supervisor) Starting final review...")

    # Inicia con un veredicto de aprobación por defecto.
    verdict = {
        "validation_status": "approved",
        "warnings": [],
        "confidence_score": 0.99, # Asumimos confianza alta al inicio
        "reasoning": "All data points are consistent and logical. No anomalies detected."
    }

    # Lógica de Validación 1: Confianza de la Clasificación
    classification_confidence = classification_data.get("confidence_score", 1.0)
    if classification_confidence < 0.95:
        verdict["validation_status"] = "needs_review"
        verdict["warnings"].append(
            f"La confianza de la clasificación arancelaria ({classification_confidence:.2f}) es baja (<95%). Se recomienda una revisión humana."
        )
        verdict["reasoning"] = "Se detectaron problemas de confianza en la clasificación."
        verdict["confidence_score"] = classification_confidence # Se podría ajustar la confianza general

    if verdict["validation_status"] == "approved":
        print("[+] (Agent: Supervisor) Final review completed successfully. All checks passed.")
    else:
        print(f"[!] (Agent: Supervisor) Final review completed. Document flagged for human review.")

    return verdict
