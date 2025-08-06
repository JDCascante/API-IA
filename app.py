from flask import Flask, request, jsonify
from google import genai
from pathlib import Path
import os
import json
import base64
import tempfile

app = Flask(__name__)

# Configura tu API Key aquí o usa variable de entorno
os.environ["GOOGLE_API_KEY"] = "AIzaSyA0Gzgj7_7wnPysCVQXwNNQJS3L_M0jKXg"

def extract_json_from_pdf(pdf_path, prompt):
    client = genai.Client()
    try:
        sample_pdf = client.files.upload(file=Path(pdf_path))
    except Exception as e:
        return None, f"Error al subir el PDF: {str(e)}"
    
    gemini_model = "gemini-2.0-flash"
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=[prompt, sample_pdf],
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
        gemini_model = "gemini-2.0-flash"
        response = client.models.generate_content(
            model=gemini_model,
            contents=[prompt]
        )
        text = response.text if response.text else ""
        return jsonify({'response': text})
    except Exception as e:
        return jsonify({'error': f'Error al generar contenido: {str(e)}'}), 500
        
if __name__ == '__main__':
    app.run(debug=True) 