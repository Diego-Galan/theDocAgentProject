import fitz  # PyMuPDF
import pydantic
from typing import List, Optional

# --- Modelos de Datos Pydantic para la Factura Comercial ---

class LineItemData(pydantic.BaseModel):
    """
    Define la estructura de un único ítem dentro de la factura.
    """
    item_description: Optional[str] = pydantic.Field(
        None, description="Descripción detallada del producto o servicio."
    )
    quantity: Optional[float] = pydantic.Field(
        None, description="Cantidad del producto (puede ser decimal)."
    )
    unit_price: Optional[float] = pydantic.Field(
        None, description="Precio por unidad del producto."
    )
    total_price: Optional[float] = pydantic.Field(
        None, description="Precio total para este ítem (cantidad * precio unitario)."
    )
    hs_code: Optional[str] = pydantic.Field(
        None, description="Código arancelario (HS Code) si está especificado en la línea."
    )

class CommercialInvoiceData(pydantic.BaseModel):
    """
    Define la estructura completa de los datos que se extraerán de una Factura Comercial.
    Está alineado con los estándares del comercio exterior.
    """
    invoice_id: Optional[str] = pydantic.Field(None, description="Número o ID único de la factura.")
    issue_date: Optional[str] = pydantic.Field(None, description="Fecha de emisión de la factura (YYYY-MM-DD).")
    
    seller_name: Optional[str] = pydantic.Field(None, description="Nombre o razón social del vendedor/exportador.")
    seller_address: Optional[str] = pydantic.Field(None, description="Dirección completa del vendedor.")
    seller_tax_id: Optional[str] = pydantic.Field(None, description="ID fiscal o NIT del vendedor.")
    
    buyer_name: Optional[str] = pydantic.Field(None, description="Nombre o razón social del comprador/importador.")
    buyer_address: Optional[str] = pydantic.Field(None, description="Dirección completa del comprador.")
    buyer_tax_id: Optional[str] = pydantic.Field(None, description="ID fiscal o NIT del comprador.")
    
    incoterm: Optional[str] = pydantic.Field(None, description="Incoterm acordado (ej. FOB, CIF, EXW).")
    currency: Optional[str] = pydantic.Field(None, description="Moneda de la transacción (código ISO, ej. USD, EUR).")
    
    subtotal_amount: Optional[float] = pydantic.Field(None, description="Suma de los precios de todos los ítems.")
    total_amount: Optional[float] = pydantic.Field(None, description="Monto total de la factura después de impuestos/descuentos.")
    
    country_of_origin: Optional[str] = pydantic.Field(None, description="País de origen de las mercancías.")
    
    line_items: List[LineItemData] = pydantic.Field(
        default_factory=list, description="Lista detallada de los productos en la factura."
    )


class DataExtractorAgent:
    """
    Agente responsable de extraer texto de un documento y usar un LLM
    para estructurarlo en un modelo Pydantic validado.
    """
    def __init__(self, model_llm=None):
        """
        Inicializa el agente.
        Args:
            model_llm: Una instancia de un modelo de lenguaje generativo (como Gemini).
                       Se pasa como argumento para facilitar las pruebas y la flexibilidad.
        """
        # self.llm = model_llm # <-- Descomentaremos esto cuando integremos el LLM real
        pass

    def _get_extraction_prompt(self, raw_text: str) -> str:
        """
        Genera el prompt para guiar al LLM en la extracción de datos.
        """
        prompt = f"""
        Actúa como un sistema experto en extracción de datos de documentos de comercio exterior.
        Tu tarea es analizar el siguiente texto extraído de una factura comercial y convertirlo en un objeto JSON estructurado.

        **Texto Crudo del Documento:**
        ---
        {raw_text}
        ---

        **Instrucciones de Salida:**
        Devuelve un único objeto JSON que se ajuste a la siguiente estructura. Si un campo no se encuentra en el texto, omítelo del JSON (no uses valores nulos o "N/A").
        - **invoice_id**: (string) El número de la factura.
        - **issue_date**: (string) La fecha de emisión en formato YYYY-MM-DD.
        - **seller_name**: (string) El nombre del vendedor.
        - **seller_address**: (string) La dirección del vendedor.
        - **seller_tax_id**: (string) El ID fiscal del vendedor.
        - **buyer_name**: (string) El nombre del comprador.
        - **buyer_address**: (string) La dirección del comprador.
        - **buyer_tax_id**: (string) El ID fiscal del comprador.
        - **incoterm**: (string) El Incoterm (ej. FOB, CIF).
        - **currency**: (string) La moneda (ej. USD).
        - **subtotal_amount**: (float) El subtotal antes de impuestos.
        - **total_amount**: (float) El total final.
        - **country_of_origin**: (string) El país de origen.
        - **line_items**: (array de objetos) Una lista de los productos, donde cada objeto tiene:
          - **item_description**: (string) La descripción del producto.
          - **quantity**: (float) La cantidad.
          - **unit_price**: (float) El precio por unidad.
          - **total_price**: (float) El precio total del ítem.

        Asegúrate de que la salida sea únicamente el objeto JSON, sin texto o formato adicional.
        """
        return prompt

    def extract_from_commercial_invoice(self, file_path: str) -> Optional[CommercialInvoiceData]:
        """
        Orquesta la extracción de datos de una factura comercial en PDF.

        Args:
            file_path: La ruta al archivo PDF.

        Returns:
            Una instancia del modelo Pydantic CommercialInvoiceData con los datos extraídos,
            o None si ocurre un error.
        """
        print(f"[+] (Agent: DataExtractor) Procesando factura: {file_path}")
        try:
            # 1. Extraer texto crudo del PDF usando PyMuPDF
            doc = fitz.open(file_path)
            raw_text = ""
            for page in doc:
                raw_text += page.get_text("text")
            doc.close()

            if not raw_text.strip():
                print("[-] (Agent: DataExtractor) Advertencia: No se extrajo texto del documento.")
                return None

            # --- AQUI IRÁ LA LLAMADA AL LLM ---
            # Por ahora, simularemos la respuesta del LLM para poder seguir desarrollando
            
            # 1. Generar el prompt
            prompt = self._get_extraction_prompt(raw_text)
            print("\n--- PROMPT PARA EL LLM (SIMULADO) ---")
            print(prompt)
            print("--------------------------------------\n")
            
            # 2. Simular la respuesta JSON del LLM
            simulated_llm_json_response = {
                "invoice_id": "FAC-2024-08-13",
                "issue_date": "2024-08-13",
                "seller_name": "Componentes Electrónicos de Colombia S.A.S.",
                "seller_address": "Zona Franca, Bodega 5, Cartagena, Colombia",
                "seller_tax_id": "900.123.456-7",
                "buyer_name": "Tech Imports LLC",
                "buyer_address": "123 Tech Way, Miami, FL 33101, USA",
                "buyer_tax_id": "US-59-1234567",
                "incoterm": "FOB Cartagena",
                "currency": "USD",
                "country_of_origin": "Colombia",
                "line_items": [
                    {
                        "item_description": "Microcontrolador ATmega328P-PU",
                        "quantity": 1500.0,
                        "unit_price": 2.50,
                        "total_price": 3750.0
                    },
                    {
                        "item_description": "Sensor de Humedad y Temperatura DHT22",
                        "quantity": 500.0,
                        "unit_price": 4.15,
                        "total_price": 2075.0
                    }
                ],
                "subtotal_amount": 5825.0,
                "total_amount": 5825.0
            }

            # 3. Validar y crear el objeto Pydantic a partir de la respuesta (real o simulada)
            invoice_data = CommercialInvoiceData(**simulated_llm_json_response)
            
            print("[+] (Agent: DataExtractor) Datos estructurados y validados exitosamente.")
            return invoice_data

        except Exception as e:
            print(f"[-] (Agent: DataExtractor) Ocurrió un error al extraer datos: {e}")
            return None

