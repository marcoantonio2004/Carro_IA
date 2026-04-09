import logging
import time
import serial
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("robot_control")

ARDUINO_BOOT_DELAY_SECONDS = 2

arduino = serial.Serial('COM7', 9600, timeout=10)
logger.info("Connected to Arduino on %s", arduino.port)

time.sleep(ARDUINO_BOOT_DELAY_SECONDS)
arduino.reset_input_buffer()
arduino.reset_output_buffer()


# ---------------- COMUNICACIÓN ----------------
def arduino_write_read(command: str) -> str:
    payload = f"{command.strip()}\n"
    logger.debug("Sending: %s", command)

    # Limpiar buffer antes de enviar
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()

    arduino.write(payload.encode())
    arduino.flush()

    cmd = command.strip().upper()
    if cmd in ("TURN_RIGHT", "TURN_LEFT"):
        wait = 3.5
    elif cmd == "GET_DISTANCE":
        wait = 0.3
    elif cmd in ("OPEN_DOOR_1", "CLOSE_DOOR_1", "OPEN_DOOR_2", "CLOSE_DOOR_2"):
        wait = 1.5  # tiempo suficiente para que el servo termine
    else:
        wait = 0.5

    time.sleep(wait)

    # Limpiar cualquier basura que haya llegado durante la espera
    result = arduino.readline().decode(errors="replace").strip()

    # Si el resultado parece un comando de motor, ignorarlo
    if any(x in result.upper() for x in ["MOVING", "FORWARD", "BACKWARD"]):
        logger.warning("Respuesta inesperada ignorada: %s", result)
        arduino.reset_input_buffer()
        return "ok"

    logger.debug("Response: %s", result)
    return result if result else "no response"


def arduino_send_only(command: str):
    """Envía un comando sin leer respuesta — útil para secuencias."""
    payload = f"{command.strip()}\n"
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    arduino.write(payload.encode())
    arduino.flush()


# ---------------- FAST MCP ----------------
app = FastMCP(
    name="Robot Control Tools",
    instructions="""
/no_think
Eres un controlador de robot conectado a un Arduino.

REGLAS ABSOLUTAS:
1. SIEMPRE ejecuta la tool correspondiente al comando.
2. NUNCA respondas con texto antes de ejecutar la tool.
3. Después de ejecutar la tool, responde ÚNICAMENTE con el resultado, sin agregar frases como "¡Claro!", "Por supuesto", "El robot está activo", ni nada extra.
4. Si el resultado es exitoso, responde solo con el mensaje de éxito. Ejemplo: "Ambas puertas cerradas exitosamente."
5. NUNCA confirmes que estás listo, activo o disponible. Solo ejecuta y reporta el resultado.

MAPEO DE COMANDOS:

"abre la puerta 1" / "abre puerta 1"            → open_door_1()
"cierra la puerta 1" / "cierra puerta 1"        → close_door_1()
"abre la puerta 2" / "abre puerta 2"            → open_door_2()
"cierra la puerta 2" / "cierra puerta 2"        → close_door_2()
"abre las dos puertas" / "abre ambas puertas"   → open_both_doors()
"cierra las dos puertas" / "cierra ambas puertas" → close_both_doors()

"avanza" / "ve hacia adelante"                  → move_forward()
"retrocede" / "ve hacia atrás"                  → move_backward()
"gira a la derecha" / "dobla a la derecha"      → turn_right()
"gira a la izquierda" / "dobla a la izquierda"  → turn_left()
"detente" / "para" / "stop"                     → stop()

"distancia" / "¿hay algo enfrente?"
"¿a qué distancia hay un obstáculo?"            → get_distance()

"¿el carro está activo?" / "¿estás activo?"
"¿está funcionando?" / "¿robot activo?"         → check_robot_status()

"¿estás conectado?" / "¿arduino conectado?"
"¿hay conexión?" / "¿está conectado el arduino?" → check_arduino_connection()
"""
)


# ---------------- TOOLS PUERTAS ----------------

@app.tool
def open_door_1() -> dict:
    """Abre la puerta 1."""
    return {"status": arduino_write_read("OPEN_DOOR_1")}

@app.tool
def close_door_1() -> dict:
    """Cierra la puerta 1."""
    return {"status": arduino_write_read("CLOSE_DOOR_1")}

@app.tool
def open_door_2() -> dict:
    """Abre la puerta 2."""
    return {"status": arduino_write_read("OPEN_DOOR_2")}

@app.tool
def close_door_2() -> dict:
    """Cierra la puerta 2."""
    return {"status": arduino_write_read("CLOSE_DOOR_2")}

@app.tool
def open_both_doors() -> dict:
    """Abre las dos puertas en secuencia de forma segura."""
    arduino_write_read("OPEN_DOOR_1")
    time.sleep(0.5)
    arduino_write_read("OPEN_DOOR_2")
    return {"status": "Las dos puertas se han abierto exitosamente."}

@app.tool
def close_both_doors() -> dict:
    """Cierra las dos puertas en secuencia de forma segura."""
    arduino_write_read("CLOSE_DOOR_1")
    time.sleep(0.5)
    arduino_write_read("CLOSE_DOOR_2")
    return {"status": "Las dos puertas se han cerrado exitosamente."}


# ---------------- TOOLS MOTORES ----------------

@app.tool
def move_forward() -> dict:
    """Avanza el robot de forma continua. Se detiene automáticamente si hay un obstáculo a 7cm."""
    result = arduino_write_read("MOVE_FORWARD")
    if "Obstaculo" in result or "Obstáculo" in result:
        return {"status": result}
    return {"status": "Avanzando"}

@app.tool
def move_backward() -> dict:
    """Retrocede el robot de forma continua hasta recibir stop."""
    return {"status": arduino_write_read("MOVE_BACKWARD")}

@app.tool
def turn_right() -> dict:
    """Gira el robot a la derecha."""
    arduino_write_read("TURN_RIGHT")
    return {"status": "Ha girado exitosamente"}

@app.tool
def turn_left() -> dict:
    """Gira el robot a la izquierda."""
    arduino_write_read("TURN_LEFT")
    return {"status": "Ha girado exitosamente"}

@app.tool
def stop() -> dict:
    """Detiene todos los motores inmediatamente."""
    return {"status": arduino_write_read("STOP")}


# ---------------- TOOL SENSOR ----------------

@app.tool
def get_distance() -> dict:
    """Mide la distancia al obstáculo más cercano en centímetros usando el sensor ultrasónico."""
    result = arduino_write_read("GET_DISTANCE")
    return {"distancia": result}


# ---------------- TOOLS ESTADO ----------------

@app.tool
def check_robot_status() -> dict:
    """Verifica si el robot está activo y funcionando correctamente."""
    result = arduino_write_read("PING")
    if result == "pong":
        return {"status": "El carro está activo y funcionando correctamente."}
    return {"status": "El carro no responde."}

@app.tool
def check_arduino_connection() -> dict:
    """Verifica si el Arduino está conectado y respondiendo."""
    try:
        if arduino.is_open:
            result = arduino_write_read("PING")
            if result == "pong":
                return {"status": f"El Arduino está conectado correctamente en el puerto {arduino.port}."}
            return {"status": "El Arduino está conectado pero no responde."}
        return {"status": "El Arduino no está conectado."}
    except Exception as e:
        return {"status": f"Error de conexión con el Arduino: {str(e)}"}


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()