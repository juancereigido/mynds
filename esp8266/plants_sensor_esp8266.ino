#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>

// ---------- Configuración del Usuario ----------
const char* ssid = "TURED WiFi";
const char* password = "12345678";

// Configuración del modo de operación
const bool sendDataToServer = true;  // Cambiar a false para solo imprimir datos localmente

// URL del servidor
const char* serverName = "https://www.recordai.app/api/esp-plants";  // URL de producción (RecordAi o tu propia serverless function)

// Datos de la planta para el servidor
const char* plantName = "MyPlant"; // Nombre de la planta
const char* userPhone = "5491120221812"; // Tu número de teléfono (Con codigo de país, sin espacios ni +)

// ---------- Configuración del Sensor ----------
const int analogSensorPin = A0;   // Pin analógico para leer los valores de humedad
const int digitalSensorPin = 5;   // Pin digital para control del sensor

// ---------- Variables de Temporización ----------
const unsigned long measurementInterval = 30000;  // Intervalo de medición (En milisegundos): 30 segundos = 30000 (Atención: No bajar de 30 segundos porque el servidor no soporta menos)
unsigned long previousMillis = 0;  // Guarda el último tiempo de medición

// ---------- Estado del Sensor ----------
bool sensorError = false;  // Bandera para controlar errores del sensor

// Definimos si usamos HTTPS (Matener en true)
const bool useHTTPS = true;

void setup() {
  Serial.begin(115200);  // Iniciamos comunicación para poder leer los datos desde el monitor serial
  delay(10);
  
  // Configuramos el pin digital como entrada
  pinMode(digitalSensorPin, INPUT);
  
  // Conectamos al WiFi
  WiFi.begin(ssid, password);
  
  // Esperamos a que se conecte al WiFi
  Serial.print("Conectando al WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n¡WiFi conectado!"); // Mostramos un mensaje de éxito
  Serial.print("IP Local: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Calculamos el tiempo actual
  unsigned long currentMillis = millis();
  
  // Si el tiempo actual menos el tiempo anterior es mayor o igual al intervalo de medición, entonces medimos
  if (currentMillis - previousMillis >= measurementInterval) {
    previousMillis = currentMillis;
    
    // Leemos el valor del sensor
    int sensorValue = analogRead(analogSensorPin);

    // Mostramos el valor en el Monitor Serial
    Serial.print("Humedad del suelo: ");
    Serial.print(sensorValue);
    Serial.println(" (valor crudo)");

    // Enviamos los datos al servidor solo si sendDataToServer es true
    if (sendDataToServer) {
      sendSensorData(sensorValue);
    } else {
      Serial.println("Modo local: datos no enviados al servidor");
    }
  }
}

// Función para enviar datos al servidor
void sendSensorData(int moisture) {
  if (WiFi.status() == WL_CONNECTED) {
    
    // Creamos un cliente
    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;
    http.begin(client, serverName);

    // Armamos el documento que va a ser enviado al servidor en formato JSON
    StaticJsonDocument<200> doc;
    doc["plant_name"] = plantName;
    doc["phone"] = userPhone;
    doc["moisture"] = moisture;

    // Convertimos el documento a una cadena de caracteres
    String jsonString;
    serializeJson(doc, jsonString);

    // Agregamos los headers necesarios
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Accept", "application/json");
    http.addHeader("User-Agent", "ESP8266");
    
    // Información de debugging
    Serial.println("Enviando request a: " + String(serverName));
    Serial.println("Payload: " + jsonString);
    
    // Enviamos la request
    int httpResponseCode = http.POST(jsonString);

    // Manejamos la respuesta
    if (httpResponseCode > 0) {
      String response = http.getString();
      
      Serial.printf("Código de respuesta HTTP: %d\n", httpResponseCode);
      Serial.println("Respuesta: " + response);
      
      // Manejamos redirecciones si es necesario
      if (httpResponseCode == 308) {
        StaticJsonDocument<200> responseDoc;
        DeserializationError error = deserializeJson(responseDoc, response);
        
        // Si el documento tiene la clave "redirect", entonces intentamos redirigir
        if (!error && responseDoc.containsKey("redirect")) {
          String redirectUrl = responseDoc["redirect"].as<String>();
          Serial.println("Intentando redirección a: " + redirectUrl);
          
          // Cerramos la conexión actual
          http.end();
          
          // Iniciamos una nueva conexión con la URL de redirección
          http.begin(client, redirectUrl.c_str());
          
          // Agregamos los headers necesarios
          http.addHeader("Content-Type", "application/json");
          http.addHeader("Accept", "application/json");
          http.addHeader("User-Agent", "ESP8266");
          
          // Enviamos la request
          httpResponseCode = http.POST(jsonString);
          
          // Si la respuesta es exitosa, entonces mostramos el mensaje
          if (httpResponseCode > 0) {
            response = http.getString();
            Serial.printf("Código de respuesta de redirección: %d\n", httpResponseCode);
            Serial.println("Respuesta de redirección: " + response);
          }
        }
      }
      
      // Si llegamos al límite de requests, esperamos
      if (httpResponseCode == 429) {
        delay(10000);  // Esperamos 10 segundos si alcanzamos el rate limit
      }
    } else {
      // Si hay un error, entonces mostramos el mensaje
      Serial.printf("Error enviando POST: %d\n", httpResponseCode);
    }

    // Cerramos la conexión
    http.end();
  } else {
    // Si no hay conexión, entonces intentamos reconectarnos
    Serial.println("WiFi Desconectado - Intentando reconectar...");
    WiFi.begin(ssid, password);
  }
}