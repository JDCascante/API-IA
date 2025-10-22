import time

from flask import Flask, request, jsonify
from google import genai
from pathlib import Path
import os
import json
import base64
import tempfile

app = Flask(__name__, static_folder='public', static_url_path='')

# Configura tu API Key aquí o usa variable de entorno
os.environ["GOOGLE_API_KEY"] = "AIzaSyB1nYcZbCYDWSWz5BeqLSweqNEHPL4dmWg"

def extract_json_from_pdf(pdf_path, prompt, max_retries=5, wait_time=10):
    """
    Extrae JSON de un PDF usando Gemini API con reintentos.

    Args:
        pdf_path: Ruta al archivo PDF
        prompt: Prompt para el modelo
        max_retries: Número máximo de intentos (default: 3)
        wait_time: Tiempo de espera entre intentos en segundos (default: 5)

    Returns:
        tuple: (data, error) donde data es el JSON o None, y error es el mensaje de error o None
    """
    client = genai.Client()

    # Subir el archivo PDF una sola vez
    try:
        sample_pdf = client.files.upload(file=Path(pdf_path))
        # Esperar a que el archivo se procese
        time.sleep(2)
    except Exception as e:
        return None, f"Error al subir el PDF: {str(e)}"

    gemini_model = "gemini-2.5-flash"

    # Intentar obtener respuesta válida
    for attempt in range(max_retries):
        try:
            print(f"Intento {attempt + 1} de {max_retries}...")

            response = client.models.generate_content(
                model=gemini_model,
                contents=[prompt, sample_pdf],
            )

            # Verificar si hay respuesta
            if not response or not response.text:
                print(f"Respuesta vacía en intento {attempt + 1}. Reintentando...")
                time.sleep(wait_time)
                continue

            text = response.text.strip()

            # Verificar que no esté vacío
            if not text or text.lower() in ['null', 'none', '']:
                print(f"Respuesta nula o vacía en intento {attempt + 1}. Reintentando...")
                time.sleep(wait_time)
                continue

            # Limpiar delimitadores de bloque de código Markdown
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Intentar convertir a JSON
            try:
                data = json.loads(text)

                # Verificar que el JSON no esté vacío
                if not data or (isinstance(data, dict) and len(data) == 0):
                    print(f"JSON vacío en intento {attempt + 1}. Reintentando...")
                    time.sleep(wait_time)
                    continue

                print(f"✓ JSON válido obtenido en intento {attempt + 1}")
                return data, None

            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                else:
                    return None, f"Respuesta no es JSON válido después de {max_retries} intentos: {str(e)}. Última respuesta: {text}"

        except Exception as e:
            print(f"Error en intento {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
                continue
            else:
                return None, f"Error al generar contenido después de {max_retries} intentos: {str(e)}"

    return None, f"No se pudo obtener una respuesta válida después de {max_retries} intentos"

@app.route('/extract-json', methods=['POST'])
def extract_json():
    data = request.get_json()
    pdf_base64 = data.get('pdf_base64')
    prompt = data.get('prompt')
    if not pdf_base64 or not prompt:
        return jsonify({'error': 'Faltan pdf_base64 o prompt'}), 400

    # Decodifica y guarda el PDF temporalmente
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(base64.b64decode(pdf_base64))
            tmp_path = tmp.name
    except Exception as e:
        return jsonify({'error': f'Error al guardar el PDF temporal: {str(e)}'}), 500

    # Procesa el PDF como antes
    result, error = extract_json_from_pdf(tmp_path, prompt)
    os.remove(tmp_path)  # Elimina el archivo temporal

    if error:
        return jsonify({'error': error}), 500
    return jsonify(result)

@app.route('/ask', methods=['POST'])
def ask_model():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Falta el prompt'}), 400

    try:
        client = genai.Client()
        gemini_model = "gemini-2.5-flash"
        response = client.models.generate_content(
            model=gemini_model,
            contents=[prompt]
        )
        text = response.text if response.text else ""
        return jsonify({'response': text})
    except Exception as e:
        return jsonify({'error': f'Error al generar contenido: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True) 