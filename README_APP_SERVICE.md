# Despliegue en Azure App Service - Web Service Flask

## Descripción
Este proyecto es un web service Flask que extrae información de facturas PDF usando la API de Google Gemini y devuelve los datos en formato JSON.

## Estructura del Proyecto

```
proyecto/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias de Python
├── startup.txt           # Comando de inicio para Azure
├── test_post.py          # Script de prueba
├── media/                # Carpeta con PDFs de ejemplo
│   └── example3.pdf
└── README_APP_SERVICE.md # Este archivo
```

## Archivos Requeridos

### 1. `app.py` - Aplicación Principal
```python
from flask import Flask, request, jsonify
from google import genai
import os
import json
import base64
import tempfile

app = Flask(__name__)

# Configuración de API Key
os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI"

@app.route('/extract-json', methods=['POST'])
def extract_json():
    data = request.get_json()
    pdf_base64 = data.get('pdf_base64')
    prompt = data.get('prompt')
    
    # Decodifica y procesa el PDF
    # ... código de procesamiento ...
    
    return jsonify(result)
```

### 2. `requirements.txt` - Dependencias
```
flask
gunicorn
google-genai
requests
```

### 3. `startup.txt` - Comando de Inicio
```
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

## Pasos para Desplegar en Azure App Service

### 1. Preparar el Proyecto

1. **Asegúrate de tener todos los archivos requeridos:**
   - `app.py`
   - `requirements.txt`
   - `startup.txt`

2. **No incluyas archivos innecesarios en el ZIP:**
   - Evita carpetas como `__pycache__`, `.git`, `.venv`
   - No incluyas PDFs de ejemplo grandes
   - No incluyas logs o archivos temporales

### 2. Crear el Paquete ZIP

1. **Selecciona solo los archivos necesarios:**
   ```
   app.py
   requirements.txt
   startup.txt
   test_post.py (opcional)
   ```

2. **Comprime desde la raíz del proyecto** (no desde una subcarpeta)

3. **Verifica que el ZIP no sea muy grande** (< 50MB recomendado)

### 3. Crear Azure App Service

1. **Ve al Portal de Azure:** [portal.azure.com](https://portal.azure.com)

2. **Crear nuevo recurso:**
   - Busca "App Service"
   - Haz clic en "Crear"

3. **Configuración básica:**
   - **Suscripción:** Tu suscripción
   - **Grupo de recursos:** Crear nuevo o usar existente
   - **Nombre:** `tu-app-service-name`
   - **Publicar:** Código
   - **Pila de runtime:** Python 3.11
   - **Sistema operativo:** Linux
   - **Región:** La más cercana a ti

4. **Haz clic en "Revisar + crear"** → **Crear**

### 4. Desplegar el Código

#### Opción A: Desde el Portal de Azure
1. Ve a tu App Service creado
2. **Centro de despliegue** → **Código fuente**
3. Selecciona tu método (GitHub, Azure Repos, etc.)
4. Sube tu código o conecta tu repositorio

#### Opción B: ZIP Deploy
1. Ve a tu App Service
2. **Centro de despliegue** → **Código fuente**
3. Selecciona "Código fuente externo"
4. Sube tu archivo ZIP

### 5. Configurar Variables de Entorno (Opcional)

1. Ve a tu App Service → **Configuración** → **Configuración de la aplicación**
2. Agrega variables de entorno:
   - `GOOGLE_API_KEY` = tu API key de Google

### 6. Verificar el Despliegue

1. Ve a la URL de tu App Service
2. Deberías ver un mensaje de Flask o el endpoint funcionando

## Uso del Web Service

### Endpoint
```
POST https://tu-app-service.azurewebsites.net/extract-json
```

### Formato de la Petición
```json
{
  "pdf_base64": "JVBERi0xLjQKJcfs...",
  "prompt": "Tu prompt aquí..."
}
```

### Script de Prueba
```python
import requests
import base64

# Convierte PDF a base64
with open("media/example3.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

# URL de tu App Service
url = "https://tu-app-service.azurewebsites.net/extract-json"

data = {
    "pdf_base64": pdf_base64,
    "prompt": "Hola, tengo una aplicación que extrae la información de una factura como texto puro, pero necesito dicha información en formato JSON, el cual debe tener el siguiente formato: {formatoJSON} ..."
}

response = requests.post(url, json=data)
print("Status code:", response.status_code)
print("Response:", response.json())
```

## Troubleshooting

### Error: "Failed to deploy web package"
- **Causa:** ZIP muy grande o estructura incorrecta
- **Solución:** 
  - Verifica que solo incluyas archivos necesarios
  - Comprime desde la raíz del proyecto
  - Revisa los logs de despliegue en Azure

### Error: "Module not found"
- **Causa:** Faltan dependencias en `requirements.txt`
- **Solución:** Agrega la dependencia faltante al archivo

### Error: "500 Internal Server Error"
- **Causa:** Error en el código de la aplicación
- **Solución:** 
  - Revisa los logs de la aplicación en Azure
  - Ve a **Herramientas de desarrollo** → **Logs de consola**

### Error: "405 Method Not Allowed"
- **Causa:** Haciendo GET en lugar de POST
- **Solución:** Asegúrate de usar POST para el endpoint

### Error: "Timeout"
- **Causa:** Procesamiento muy lento
- **Solución:** 
  - Aumenta el timeout en `startup.txt`
  - Optimiza el procesamiento del PDF

## Logs y Monitoreo

### Ver Logs de la Aplicación
1. Ve a tu App Service
2. **Herramientas de desarrollo** → **Logs de consola**
3. O **Diagnóstico y solución de problemas** → **Logs de aplicación**

### Métricas de Rendimiento
1. Ve a tu App Service
2. **Supervisión** → **Métricas**
3. Monitorea CPU, memoria, tiempo de respuesta

## Escalabilidad

### Escalar Horizontalmente
1. Ve a tu App Service
2. **Escalar** → **Escalar horizontalmente**
3. Configura el número de instancias

### Escalar Verticalmente
1. Ve a tu App Service
2. **Escalar** → **Escalar verticalmente**
3. Cambia el plan de servicio

## Seguridad

### Variables de Entorno
- Nunca incluyas API keys en el código
- Usa variables de entorno en Azure

### HTTPS
- Azure App Service incluye SSL gratuito
- Tu URL será `https://tu-app.azurewebsites.net`

### Autenticación (Opcional)
- Puedes agregar autenticación con Azure Active Directory
- O implementar tu propio sistema de autenticación

## Costos

### Planes de Azure App Service
- **F1 (Gratuito):** Para desarrollo y pruebas
- **B1 (Básico):** Para producción pequeña 13.14 USD
- **S1 (Estándar):** Para producción con escalabilidad 
- **P1 (Premium):** Para alta disponibilidad

### Factores que Afectan el Costo
- Plan de servicio seleccionado
- Número de instancias
- Tráfico de datos
- Tiempo de ejecución

## Ventajas de Azure App Service

✅ **No necesitas configurar servidores**  
✅ **Escalabilidad automática**  
✅ **SSL gratuito**  
✅ **Integración con CI/CD**  
✅ **Monitoreo integrado**  
✅ **Backup automático**  
✅ **Múltiples entornos (dev, staging, prod)**  

---

**¡Tu web service está listo para producción en Azure App Service!** 