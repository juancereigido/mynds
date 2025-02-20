import json
import os
import requests

# 📌 Variables de entorno - Las claves API se cargan desde las variables de AWS Lambda
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 📌 Definimos el valor mínimo de humedad - Si baja de este número, mandamos el aviso
MOISTURE_THRESHOLD = 500

# 📌 Esta función se conecta con ChatGPT para armar un mensaje copado
def generate_message_content(plant_name, moisture_value):
    try:
        # 🔹 Armamos el encabezado del request - Esto le dice a OpenAI quiénes somos
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # 🔹 Preparamos los datos que le vamos a mandar a ChatGPT
        data = {
            "model": "gpt-4o-mini",  # Usamos este modelo porque es rápido y económico. En un futuro pueden haber modelos más avanzados!
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"""
                Sos un asistente IoT argentino. La humedad de la planta '{plant_name}' ha caído a {moisture_value}. 
                Escribí un mensaje corto y divertido para Juan avisándole sobre esto, y sugiriéndole que la riegue.
                Incluí emojis copados. No uses más de 200 caracteres.
                """}
            ],
            "temperature": 0.7  # Esto controla qué tan creativo es el mensaje (0 es muy creativo, 1 es muy conservador)
        }

        # 🔹 Hacemos el POST a la API de OpenAI
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        # 🔹 Chequeamos si todo salió bien
        if response.status_code == 200:
            message_content = response.json()["choices"][0]["message"]["content"].strip()
            return message_content
        else:
            print(f"❌ Uh, hubo un error con la API de OpenAI: {response.status_code} - {response.text}")
            return f"🪴 ¡Ojo! La planta '{plant_name}' necesita agua\n💧 Nivel de humedad: {moisture_value}"

    except Exception as e:
        print(f"❌ Che, algo salió mal generando el mensaje con OpenAI: {e}")
        return f"🪴 ¡Ojo! La planta '{plant_name}' necesita agua\n💧 Nivel de humedad: {moisture_value}"

# 📌 Esta función usa Telegram para mandar el mensaje
def send_telegram_message(plant_name, moisture_value):
    try:
        # 🔹 Primero generamos el contenido del mensaje usando ChatGPT
        message = generate_message_content(plant_name, moisture_value)
        
        # 🔹 Hacemos el POST a la API de Telegram
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Mensaje de Telegram enviado con éxito!")
        else:
            print(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Che, hubo un problema con Telegram: {e}")

# 📌 Esta es la función principal que AWS Lambda va a ejecutar
def lambda_handler(event, context):
    try:
        # 🔹 Leemos los datos que mandó el ESP8266
        body = json.loads(event['body'])
        plant_name = body.get("plant_name", "Planta Desconocida")
        moisture_value = int(body.get("moisture", -1))

        # 🔹 Mostramos los datos que llegaron (re útil para debuggear)
        print(f"📥 Llegaron datos nuevos - Planta: {plant_name}, Humedad: {moisture_value}")

        # 🔹 Si la humedad está muy baja, mandamos el aviso
        if moisture_value < MOISTURE_THRESHOLD:
            send_telegram_message(plant_name, moisture_value)

        # 🔹 Devolvemos una respuesta
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Datos recibidos correctamente", 
                "moisture": moisture_value
            })
        }

    except Exception as e:
        print(f"❌ Uh, se rompió algo: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }