from flask import Flask, request, jsonify
from google import genai
from pathlib import Path
import os
import json

app = Flask(__name__)

# Configura tu API Key aquí o usa variable de entorno
os.environ["GOOGLE_API_KEY"] = "AIzaSyA0Gzgj7_7wnPysCVQXwNNQJS3L_M0jKXg"

def extract_json_from_pdf(pdf_path, prompt, formatoJSON):
    client = genai.Client()
    try:
        sample_pdf = client.files.upload(file=Path(pdf_path))
    except Exception as e:
        return None, f"Error al subir el PDF: {str(e)}"
    
    full_prompt = prompt.replace("{formatoJSON}", formatoJSON)
    gemini_model = "gemini-2.0-flash"
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=[full_prompt, sample_pdf],
        )
        text = response.text if response.text is not None else ""
        # Limpia delimitadores de bloque de código Markdown
        if text.strip().startswith("```json"):
            text = text.strip()[7:]  # Elimina '```json\n'
        if text.strip().startswith("```"):
            text = text.strip()[3:]  # Elimina '```\n'
        if text.strip().endswith("```"):
            text = text.strip()[:-3]  # Elimina '\n```'
        text = text.strip()
        # Intenta convertir a JSON
        try:
            data = json.loads(text)
            return data, None
        except Exception as e:
            return None, f"Respuesta no es JSON válido: {str(e)}. Respuesta: {text}"
    except Exception as e:
        return None, f"Error al generar contenido: {str(e)}"

# Formato JSON base (puedes moverlo a un archivo si prefieres)
formatoJSON = '''
{
  "encabezado": {
    "numConsecutivo": "número de la factura",
    "numOrdenCompra": "número de la orden relacionada a la factura",
    "cedulaProveedor": "número de identificación del proveedor",
    "nombreProveedor": "nombre del proveedor",
    "fechaEmision": "la fecha de la factura",
    "moneda": "nombre o iniciales de la moneda",
    "subtotal": "valor subtotal de la factura",
    "total": "valor total de la factura"
  },
  "lineas": [
    {
      "numero": "número de la línea",
      "descripcion": "descripción de la línea",
      "cantidad": "cantidad solicitada",
      "precioUnitario": "precio unitario del producto en línea",
      "unidMedida": "unidad de medida de la línea",
      "subtotal": "valor subtotal de la línea",
      "total": "valor total de la línea"
    }
    // (otras líneas aquí)
  ]
}
'''

@app.route('/extract-json', methods=['POST'])
def extract_json():
    data = request.get_json()
    pdf_path = data.get('pdf_path')
    prompt = data.get('prompt')
    if not pdf_path or not prompt:
        return jsonify({'error': 'Faltan pdf_path o prompt'}), 400
    
    result, error = extract_json_from_pdf(pdf_path, prompt, formatoJSON)
    if error:
        return jsonify({'error': error}), 500
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 