import time
import serial
import requests

# ─────────────────────────────────────────
#  CONFIGURACIÓN LM STUDIO
# ─────────────────────────────────────────
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL         = "qwen/qwen3-4b-2507"
TOKEN         = "sk-lm-oHoec2Gk:1lmL4ydO33372ADwGexN"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# ─────────────────────────────────────────
#  CONFIGURACIÓN ARDUINO
# ─────────────────────────────────────────
ARDUINO_PORT       = "COM3"
ARDUINO_BAUD       = 9600
MOVE_DURATION      = 3    # segundos de movimiento
DISTANCIA_TRIGGER  = 10   # cm — si detecta objeto a esta distancia o menos, arranca
INTERVALO_SENSOR   = 0.5  # segundos entre cada lectura del sensor en espera

arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=10)
print(f"✅ Conectado al Arduino en {arduino.port}")
time.sleep(2)
arduino.reset_input_buffer()
arduino.reset_output_buffer()


# ─────────────────────────────────────────
#  COMUNICACIÓN ARDUINO
# ─────────────────────────────────────────
def arduino_write_read(command: str) -> str:
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.write(f"{command.strip()}\n".encode())
    arduino.flush()

    cmd = command.strip().upper()
    if cmd in ("TURN_RIGHT", "TURN_LEFT"):
        wait = 3.5
    elif cmd == "GET_DISTANCE":
        wait = 0.3
    elif cmd in ("OPEN_DOOR_1", "CLOSE_DOOR_1", "OPEN_DOOR_2", "CLOSE_DOOR_2"):
        wait = 1.5
    else:
        wait = 0.5

    time.sleep(wait)
    result = arduino.readline().decode(errors="replace").strip()

    if any(x in result.upper() for x in ["MOVING", "FORWARD", "BACKWARD"]):
        arduino.reset_input_buffer()
        return "ok"

    return result if result else "no response"


def arduino_send_only(command: str):
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.write(f"{command.strip()}\n".encode())
    arduino.flush()


# ─────────────────────────────────────────
#  FUNCIÓN DE ESPERA — lee sensor hasta
#  detectar objeto a DISTANCIA_TRIGGER cm
# ─────────────────────────────────────────
def esperar_trigger():
    print(f"\n👀 En espera — acerca un objeto a {DISTANCIA_TRIGGER} cm o menos para arrancar...\n")

    while True:
        raw = arduino_write_read("GET_DISTANCE")

        try:
            distancia = int(raw.replace("cm", "").replace("Sin obstaculo detectado", "999").strip())
        except ValueError:
            distancia = 999

        print(f"   📡 Distancia actual: {raw}     ", end="\r")

        if distancia <= DISTANCIA_TRIGGER:
            print(f"\n\n🚨 Objeto detectado a {distancia} cm — ¡Arrancando secuencia!")
            time.sleep(0.5)
            return distancia

        time.sleep(INTERVALO_SENSOR)


# ─────────────────────────────────────────
#  TOOLS — funciones Python
# ─────────────────────────────────────────
def open_both_doors() -> str:
    """Abre las dos puertas del robot en secuencia."""
    arduino_write_read("OPEN_DOOR_1")
    time.sleep(0.5)
    arduino_write_read("OPEN_DOOR_2")
    return "Las dos puertas están abiertas."

def close_both_doors() -> str:
    """Cierra las dos puertas del robot en secuencia."""
    arduino_write_read("CLOSE_DOOR_1")
    time.sleep(0.5)
    arduino_write_read("CLOSE_DOOR_2")
    return "Las dos puertas están cerradas."

def move_forward_3s() -> str:
    """Avanza el robot hacia adelante durante 3 segundos y lo detiene automáticamente."""
    arduino_send_only("MOVE_FORWARD")
    time.sleep(MOVE_DURATION)
    arduino_write_read("STOP")
    return "Robot avanzó 3 segundos y se detuvo."

def move_backward_3s() -> str:
    """Retrocede el robot hacia atrás durante 3 segundos y lo detiene automáticamente."""
    arduino_send_only("MOVE_BACKWARD")
    time.sleep(MOVE_DURATION)
    arduino_write_read("STOP")
    return "Robot retrocedió 3 segundos y se detuvo."

def turn_right() -> str:
    """Gira el robot a la derecha."""
    arduino_write_read("TURN_RIGHT")
    return "Robot giró a la derecha."

def turn_left() -> str:
    """Gira el robot a la izquierda."""
    arduino_write_read("TURN_LEFT")
    return "Robot giró a la izquierda."

def get_distance() -> str:
    """Mide la distancia en centímetros al obstáculo más cercano usando el sensor ultrasónico."""
    result = arduino_write_read("GET_DISTANCE")
    return f"Distancia al obstáculo: {result}"


# ─────────────────────────────────────────
#  MAPA nombre → función Python
# ─────────────────────────────────────────
TOOL_FUNCTIONS = {
    "open_both_doors":  open_both_doors,
    "close_both_doors": close_both_doors,
    "move_forward_3s":  move_forward_3s,
    "move_backward_3s": move_backward_3s,
    "turn_right":       turn_right,
    "turn_left":        turn_left,
    "get_distance":     get_distance,
}

# ─────────────────────────────────────────
#  DEFINICIÓN DE TOOLS (formato OpenAI)
# ─────────────────────────────────────────
TOOLS = [
    {"type": "function", "function": {"name": "open_both_doors",  "description": "Abre las dos puertas del robot en secuencia.",                                          "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "close_both_doors", "description": "Cierra las dos puertas del robot en secuencia.",                                        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "move_forward_3s",  "description": "Avanza el robot hacia adelante durante 3 segundos y lo detiene automáticamente.",       "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "move_backward_3s", "description": "Retrocede el robot hacia atrás durante 3 segundos y lo detiene automáticamente.",       "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "turn_right",       "description": "Gira el robot a la derecha.",                                                           "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "turn_left",        "description": "Gira el robot a la izquierda.",                                                         "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_distance",     "description": "Mide la distancia en centímetros al obstáculo más cercano con el sensor ultrasónico.",  "parameters": {"type": "object", "properties": {}}}},
]

# ─────────────────────────────────────────
#  MISIÓN
# ─────────────────────────────────────────
MISSION = """/no_think
Ejecuta estas instrucciones EN ORDEN, una por una, usando las tools disponibles.
NO saltes ningún paso. Espera el resultado de cada tool antes de continuar.

1. Abre las dos puertas          → open_both_doors()
2. Cierra las dos puertas        → close_both_doors()
3. Avanza 3 segundos             → move_forward_3s()
4. Gira a la derecha             → turn_right()
5. Avanza 3 segundos             → move_forward_3s()
6. Gira a la izquierda           → turn_left()
7. Avanza 3 segundos             → move_forward_3s()
8. Retrocede 3 segundos          → move_backward_3s()
9. Mide la distancia             → get_distance()

Al finalizar todos los pasos, reporta únicamente a cuántos centímetros está el obstáculo.
"""


# ─────────────────────────────────────────
#  LLAMADA AL MODELO
# ─────────────────────────────────────────
def llamar_modelo(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0,
    }
    response = requests.post(LM_STUDIO_URL, headers=HEADERS, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────
#  EJECUTAR SECUENCIA CON EL MODELO
# ─────────────────────────────────────────
def ejecutar_secuencia():
    messages = [
        {"role": "system", "content": "Eres un controlador de robot. Ejecuta las tools en orden sin texto extra."},
        {"role": "user",   "content": MISSION}
    ]

    while True:
        data    = llamar_modelo(messages)
        choice  = data["choices"][0]
        message = choice["message"]

        messages.append(message)

        if choice.get("finish_reason") == "tool_calls" or message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                name = tool_call["function"]["name"]
                print(f"\n⚙️  Ejecutando: {name}()")

                if name in TOOL_FUNCTIONS:
                    resultado = TOOL_FUNCTIONS[name]()
                    print(f"   ✅ {resultado}")
                else:
                    resultado = f"Tool desconocida: {name}"
                    print(f"   ❌ {resultado}")

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_call["id"],
                    "content":      resultado
                })
        else:
            respuesta_final = message.get("content", "")
            if respuesta_final:
                print(f"\n🤖 {respuesta_final}")
            break


# ─────────────────────────────────────────
#  MAIN — loop infinito hasta Ctrl+C
# ─────────────────────────────────────────
def main():
    print("\n🤖 Robot Controller iniciado")
    print("   Presiona Ctrl+C para detener el programa")
    print("=" * 50)

    ciclo = 1

    try:
        while True:
            print(f"\n🔄 Ciclo #{ciclo}")

            # 1. Esperar trigger del sensor
            esperar_trigger()

            # 2. Ejecutar secuencia automática
            print("\n🚀 Iniciando secuencia...")
            print("=" * 50)
            ejecutar_secuencia()

            print("\n" + "=" * 50)
            print(f"✅ Secuencia #{ciclo} completada.")

            ciclo += 1

           
            print("\n⏳ Esperando...")
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n🛑 Saliendo...")
        arduino.close()


if __name__ == "__main__":
    main()