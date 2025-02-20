# API de Plantas con ESP8266 - Documentación

¡Hola! �� Esta documentación describe la API para acceder a los datos de humedad de plantas monitoreadas con sensores ESP8266.

## 🌱 Información General

- **Base URL**: `https://www.recordai.app/api/esp-plants`
- **Formato**: JSON
- **Autenticación**: No requiere (solo necesitás el número de teléfono y nombre de planta correctos)
- **Rate Limit**: 1 request cada 30 segundos por IP
- **Caché**: 1 minuto

## 📡 Endpoints

### Obtener Datos de una Planta

```http
GET /api/esp-plants
```

#### Parámetros de Query

| Parámetro   | Tipo   | Requerido | Descripción                                                |
|-------------|---------|-----------|-----------------------------------------------------------|
| phone       | string  | Sí        | Número de teléfono (formato: 5491118122022)              |
| plant_name  | string  | Sí        | Nombre de la planta                                       |

> ⚠️ **Importante**: El número de teléfono debe estar en formato internacional, sin espacios ni símbolos. Ejemplo: 5491118122022 (no incluir el +)

#### Ejemplo de Request

```javascript
// Usando fetch (JavaScript)
const getPlantData = async (phone, plantName) => {
  try {
    const response = await fetch(
      `https://www.recordai.app/api/esp-plants?phone=${phone}&plant_name=${plantName}`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};
```

```python
# Usando requests (Python)
import requests

def get_plant_data(phone, plant_name):
    url = 'https://www.recordai.app/api/esp-plants'
    params = {
        'phone': phone,
        'plant_name': plant_name
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

#### Respuesta Exitosa

```json
{
  "plant_name": "MyPlant",
  "phone": "5491118122022",
  "data": [
    {
      "timestamp": "2024-02-15T12:00:00Z",
      "moisture": 512,
      "moisture_percentage": 50
    },
    {
      "timestamp": "2024-02-15T11:50:00Z",
      "moisture": 600,
      "moisture_percentage": 59
    }
  ]
}
```

#### Detalles de la Respuesta

| Campo               | Tipo    | Descripción                                               |
|--------------------|---------|----------------------------------------------------------|
| timestamp          | string  | Fecha y hora en formato ISO 8601 (UTC)                   |
| moisture           | integer | Valor crudo del sensor (0-1024)                          |
| moisture_percentage| integer | Porcentaje de humedad calculado (0-100%)                 |

## ⚠️ Manejo de Errores

| Código | Descripción                     | Solución                                          |
|--------|----------------------------------|--------------------------------------------------|
| 400    | Parámetros inválidos            | Verificá el formato del teléfono y nombre        |
| 429    | Rate limit excedido             | Esperá 30 segundos antes de reintentar           |
| 500    | Error interno                    | Contactá al soporte                              |

### Ejemplo de Error

```json
{
  "error": "Invalid phone number format",
  "details": "Phone number must be numeric and include country code"
}
```

## 💡 Tips y Buenas Prácticas

1. **Rate Limiting**: Respetá el límite de requests (1 cada 30 segundos)
2. **Timezone**: Los timestamps están en UTC
3. **Valores**: El campo `moisture_percentage` está normalizado (0-100%)

## 🤝 Soporte

¿Tenés dudas o problemas?
1. Revisá que los parámetros estén correctos
2. Verificá la conexión a internet
3. Consultá con el soporte técnico

¡Éxitos con tu proyecto! 🌱 