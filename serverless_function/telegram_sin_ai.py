import json
import os
import requests

# 📌 Obtiene el token del bot de Telegram desde las variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ID del chat donde queremos mandar los mensajes

# 📌 Umbral de humedad mínima para activar la alerta
MOISTURE_THRESHOLD = 500  

def send_telegram_message(plant_name, moisture_value):
    try:
        # 🔹 Armamos el mensaje
        message = f"🪴 ¡Ojo! La planta '{plant_name}' necesita agua\n💧 Nivel de humedad: {moisture_value}"
        
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

def lambda_handler(event, context):
    try:
        # 📌 Leemos los datos que mandó el ESP8266
        body = json.loads(event['body'])
        plant_name = body.get("plant_name", "Planta Desconocida")
        moisture_value = int(body.get("moisture", -1))

        # 📌 Mostramos los datos que llegaron
        print(f"📥 Llegaron datos nuevos - Planta: {plant_name}, Humedad: {moisture_value}")

        # 📌 Si la humedad está muy baja, mandamos el mensaje
        if moisture_value < MOISTURE_THRESHOLD:
            send_telegram_message(plant_name, moisture_value)

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