from typing import List

def search_tariff_schedule(product_description: str) -> List[str]:
    """
    Busca información relevante en el arancel de aduanas para una descripción de producto dada.

    Args:
        product_description: La descripción del producto a buscar.

    Returns:
        Una lista de cadenas de texto con los fragmentos encontrados en el arancel.
    """
    print(f"Iniciando búsqueda en el arancel para: '{product_description}'...")

    # Lógica de búsqueda simulada
    search_results = [
        "Sección XVI, Capítulo 85: Máquinas, aparatos y material eléctrico...",
        "Partida 85.17: Teléfonos, incluidos los teléfonos móviles (celulares) y los de otras redes inalámbricas...",
        "Subpartida 8517.12.00.00: -- Teléfonos móviles (celulares) y los de otras redes inalámbricas"
    ]

    print("Búsqueda en el arancel completada con éxito.")
    return search_results
