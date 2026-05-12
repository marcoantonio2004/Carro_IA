# Carro_IA

Proyecto de control de un carro robótico con Arduino, servidor Python y modelo de IA local.

## 1) Armado del proyecto

### Compra y selección del carro

- Se compró un carro de juguete con chasis firme, tracción funcional y espacio interno para electrónica.
- Se validó que el tamaño permitiera alojar Arduino, puente H, servos, sensor y cableado.

### Desarmado y preparación

- Se desmontó la carrocería para acceder al sistema interno de motores y ubicación de las puertas.
- Se retiraron piezas no necesarias para liberar espacio y facilitar el enrutado de cables.
- Se conservaron tornillos y puntos de fijación para el reensamblaje final.

### Unión de cables

- Se identificaron líneas de alimentación (7.4 V para tracción, 5 V lógica), tierra común y señales de control.
- Se hicieron extensiones donde los cables originales no alcanzaban.
- Cada unión se aisló con cinta y/o termorretráctil para evitar cortocircuitos y falsos contactos.
- Las tierras de todos los subsistemas se unieron en un punto común para mantener referencia eléctrica estable.

### Cortes para las puertas

- Se realizaron cortes en la carrocería para permitir la apertura de las puertas accionadas por servos.
- Se verificó que los cortes no afectaran la estructura principal ni rozaran el cableado interno.

### Ensamble final

- Se montó nuevamente la carrocería con todos los módulos en posición.
- Se probaron puertas, movimiento, lectura de distancia y respuesta por serial.

## 2) Herramientas, componentes y circuito

### Descripción del sistema

Este proyecto parte de un carro de control remoto de juguete que fue modificado para actuar con IA.
La IA envía órdenes de movimiento y el Arduino ejecuta las acciones físicas en el vehículo.

### Objetivo

Este repositorio separa el sistema en dos partes:

- Programa en Arduino para mover motores, controlar puertas (servos), leer distancia y responder comandos por serial.
- Servidor en Python que envía comandos al Arduino y expone herramientas para controlarlo desde un flujo de IA.

### Elementos principales

- Carrito base de juguete modificado.
- Placa Arduino como controlador principal.
- Puente H para control de motores DC (corriente directa).
- 2 motores DC de tracción para 4 llantas: un motor mueve el lado derecho y otro el lado izquierdo.
- Batería independiente de 7.4 V para los motores de tracción.
- 2 servomotores para apertura/cierre de puertas.
- Sensor ultrasónico HC-SR04 para medición de distancia frontal.
- 3 LEDs de estado: rojo, naranja y verde.

### Funcionamiento del puente H

El puente H es el circuito que permite controlar motores DC en ambos sentidos usando señales del Arduino.
En este proyecto, se usan señales de dirección (`IN1`, `IN2`, `IN3`, `IN4`) y de velocidad (`ENA`, `ENB`):

- Dirección: combinando HIGH/LOW en las entradas se define si cada motor gira hacia adelante o hacia atrás.
- Velocidad: con PWM (modulación por ancho de pulso) en `ENA` y `ENB` se regula la potencia entregada a cada motor.
- Frenado: colocando velocidad en 0 y entradas en LOW, el carro se detiene.

### Conexión general del circuito

- Arduino genera señales de control para el puente H (dirección y velocidad).
- El puente H alimenta y gobierna los dos motores de tracción.
- Los servos de puertas se controlan desde pines PWM del Arduino.
- El sensor ultrasónico se conecta a pines TRIG/ECHO para medir distancia.
- Los LEDs se conectan a salidas del Arduino para indicar estados del sistema.
- Todas las tierras se unieron en común para mantener referencia eléctrica estable.

### Mapa de pines

Servos:

- Servo puerta 1: pin 3
- Servo puerta 2: pin 2

Motores (puente H):

- IN1: 7
- IN2: 8
- IN3: 12
- IN4: 13
- ENA: 5
- ENB: 6

Ultrasónico:

- TRIG: 9
- ECHO: 10

LEDs:

- LED rojo: A0
- LED amarillo: A1
- LED verde: A2

### Notas de conexión

- La lógica de control se gestiona con Arduino y la potencia de tracción con batería de 7.4 V.
- Cada subsistema (tracción, puertas, sensado e indicadores) se cableó por separado para facilitar pruebas y mantenimiento.

## 3) Funcionamiento sencillo del carro

- El Arduino actúa como controlador de tiempo real del carro.
- Recibe comandos por puerto serial y ejecuta acciones de actuadores (motores y servos).
- En reposo se enciende el LED rojo.
- En movimiento se enciende el LED verde.
- Cuando una puerta está abierta o ambas, el LED naranja parpadea.
- El sensor ultrasónico mide distancia frontal.
- Si detecta un obstáculo a 22 cm o menos, el sistema detiene el carro automáticamente.

### Funcionalidades del programa en Arduino (`arduino.ino`)

- Ejecuta comandos de movimiento: avanzar, retroceder, girar derecha, girar izquierda y detener.
- Controla 2 servos para abrir y cerrar puerta 1 y puerta 2.
- Lee el sensor ultrasónico para medir distancia y activar detención automática al avanzar.
- Usa protocolo de comandos serial en texto plano y devuelve respuesta al servidor.

## 4) Comunicación Arduino + IA (LM Studio)

### Integración lograda

- Se usó LM Studio como motor de inferencia local.
- Se usó el modelo `qwen/qwen3-v1-4b` (también referenciado como `qwen/qwen3-4b-2507`).
- El servidor `server.py` actúa como puente entre el modelo y el Arduino por puerto serial.
- La integración MCP utilizada es `mcp/robot-control`.

### Arquitectura general

El sistema opera de forma completamente autónoma:

1. `server.py` abre conexión serial (COM3, 9600 bps).
2. El script Python se conecta directamente a la API local de LM Studio en http://localhost:1234.
3. El modelo de lenguaje se consume a través de la API local sin requerir que el usuario abra LM Studio ni dé instrucciones manualmente.
4. Se envía un comando de texto (por ejemplo: `Abre la puerta 1 o 2`, `Avanza`, `Gira a la derecha o izquierda` y `A qué distancia se encuentra un obstáculo`).
5. `arduino.ino` recibe el comando, ejecuta acción y responde por serial.
6. El servidor devuelve el resultado como respuesta de la tool (función o acción).

### Responsabilidad del servidor (`server.py`)

- Envía comandos al Arduino por serial.
- Espera respuesta según tipo de comando (tiempos de espera distintos).
- Publica tools MCP para puertas, movimiento, distancia y estado del robot.

### Parámetros de configuración

| Parámetro | Valor |
|-----------|-------|
| LM_STUDIO_URL | http://localhost:1234/v1/chat/completions |
| MODEL | qwen/qwen3-4b-2507 |
| ARDUINO_PORT | COM3 |
| ARDUINO_BAUD | 9600 bps |
| MOVE_DURATION | 3 segundos por movimiento |
| DISTANCIA_TRIGGER | 10 cm (dispara la secuencia autónoma) |
| INTERVALO_SENSOR | 0.5 s entre lecturas en espera |

### Flujo de operación autónoma

Al ejecutar el script, el sistema entra en un loop infinito con el siguiente ciclo:

1. **Espera activa**: El sensor ultrasónico se consulta cada 0.5 s. Si detecta un objeto a 10 cm o menos, se dispara la secuencia.
2. **Consulta al LLM**: Se envía la misión completa al modelo Qwen3-4b a través de la API local. El modelo decide qué herramientas invocar y en qué orden.
3. **Ejecución de tools**: Por cada tool_call que devuelve el modelo, Python ejecuta la función correspondiente, envía el comando al Arduino por serial y espera su respuesta.
4. **Reporte final**: Al completar los 9 pasos, el modelo reporta la distancia al obstáculo medida en el último paso.
5. **Reinicio del ciclo**: Tras 3 segundos de pausa, el sistema vuelve al paso 1 a esperar el siguiente trigger.

### Comunicación serial con Arduino

Los tiempos de espera son adaptativos según el tipo de comando:

| Comando | Tiempo de espera |
|---------|------------------|
| TURN_RIGHT / TURN_LEFT | 3.5 segundos (giro completo) |
| OPEN_DOOR_x / CLOSE_DOOR_x | 1.5 segundos (servo) |
| GET_DISTANCE | 0.3 segundos (lectura rápida) |
| STOP y otros | 0.5 segundos |
| MOVE_FORWARD / MOVE_BACKWARD | Envío sin espera + 3 s + STOP |

### Qué herramientas se usan en esa comunicación

El sistema define 7 tools que el modelo de IA puede invocar autónomamente. Estas se declaran en formato de function calling compatible con la API de OpenAI:

**Puertas:**

- `open_door_1`: abre puerta 1.
- `close_door_1`: cierra puerta 1.
- `open_door_2`: abre puerta 2.
- `close_door_2`: cierra puerta 2.
- `open_both_doors`: abre ambas puertas en secuencia (OPEN_DOOR_1 → espera → OPEN_DOOR_2).
- `close_both_doors`: cierra ambas puertas en secuencia (CLOSE_DOOR_1 → espera → CLOSE_DOOR_2).

**Movimiento:**

- `move_forward`: avanza con control de seguridad por distancia.
- `move_forward_3s()`: Envía MOVE_FORWARD, espera 3 s y luego envía STOP automáticamente.
- `move_backward`: retrocede.
- `move_backward_3s()`: Envía MOVE_BACKWARD, espera 3 s y luego envía STOP automáticamente.
- `turn_right`: gira a la derecha (envía TURN_RIGHT y espera 3.5 s para completar el giro).
- `turn_left`: gira a la izquierda (envía TURN_LEFT y espera 3.5 s para completar el giro).
- `stop`: detiene el carro.

**Sensado y estado:**

- `get_distance`: mide y devuelve distancia frontal en cm.
- `check_robot_status`: revisa estado general del robot.
- `check_arduino_connection`: valida conexión serial con Arduino.

### Misión autónoma de 9 pasos

Al dispararse el trigger (objeto detectado a ≤10 cm), el modelo recibe una misión estructurada que debe ejecutar en orden estricto:

1. Abre las dos puertas → `open_both_doors()`
2. Cierra las dos puertas → `close_both_doors()`
3. Avanza 3 segundos → `move_forward_3s()`
4. Gira a la derecha → `turn_right()`
5. Avanza 3 segundos → `move_forward_3s()`
6. Gira a la izquierda → `turn_left()`
7. Avanza 3 segundos → `move_forward_3s()`
8. Retrocede 3 segundos → `move_backward_3s()`
9. Mide la distancia → `get_distance()`
   → Reportar distancia final al obstáculo en cm.

El modelo opera con temperatura 0 para garantizar determinismo total en el orden de ejecución. El flag `/no_think` suprime el razonamiento extendido de Qwen3, haciendo la respuesta más directa y rápida.

### Bucle principal (main)

La función `main()` mantiene el sistema vivo indefinidamente. Muestra en consola el número de ciclo, el estado del sensor en tiempo real y cada tool que el modelo va ejecutando. El programa termina limpiamente con Ctrl+C, cerrando la conexión serial con el Arduino.

### Comandos serial soportados por Arduino

- `PING`: verifica comunicación con Arduino.
- `OPEN_DOOR_1`: abre la puerta 1 (servo 1).
- `CLOSE_DOOR_1`: cierra la puerta 1.
- `OPEN_DOOR_2`: abre la puerta 2 (servo 2).
- `CLOSE_DOOR_2`: cierra la puerta 2.
- `GET_DISTANCE`: devuelve la distancia frontal medida en cm.
- `MOVE_FORWARD`: avanza mientras no haya obstáculo cercano.
- `MOVE_BACKWARD`: retrocede el carro.
- `TURN_RIGHT`: gira a la derecha por un tiempo fijo.
- `TURN_LEFT`: gira a la izquierda por un tiempo fijo.
- `STOP`: detiene el movimiento de los motores.

### Configuración de LM Studio

**Servidor activo:**
- Estado: Running ✓
- Dirección: http://127.0.0.1:1234
- Modelo cargado: qwen/qwen3-v1-4b
- Tamaño del modelo: 3.33 GB
- Paralelismo: 4 hilos

**Parámetros del servidor:**
- Server Port: 1234
- Require Authentication: Activado
- Serve on Local Network: Desactivado (solo localhost)
- Allow per-request MCPs: Activado
- Allow calling from mcp.json: Activado
- Enable CORS: Desactivado
- Just-in-Time Model Loading: Activado
- Auto unload unused JIT models: Activado
- Max idle TTL: 60 minutos
- Only Keep Last JIT Loaded Model: Activado

**Token de autenticación:**
Se generó un token de API dedicado para el proyecto (nombre: "carro"). Este token se incluye en cada request que el script Python hace al servidor local, en el header `Authorization`.

### Flujo de uso esperado

1. Cargar `arduino.ino` en la placa Arduino.
2. Conectar la placa al puerto definido en `server.py` (COM3).
3. Iniciar LM Studio con el modelo qwen/qwen3-4b-2507 cargado.
4. Ejecutar el servidor Python.
5. El sistema operará autónomamente, esperando que el sensor detecte objetos a ≤10 cm para ejecutar la secuencia de 9 pasos.

## 5) Dependencias y requisitos

### Librerías Python

```bash
pip install pyserial requests
```

| Librería | Uso |
|----------|-----|
| pyserial | Comunicación serial con el Arduino (COM3, 9600 bps) |
| requests | Llamadas HTTP a la API local de LM Studio |
| time | Control de tiempos de espera entre comandos |

### Requisitos de Hardware

- Arduino (compatible con serial a 9600 bps)
- Sensor ultrasónico HC-SR04 (pines TRIG:9, ECHO:10)
- Puente H con 2 motores DC (ENA:5, ENB:6, IN1-4: 7,8,12,13)
- 2 servomotores para puertas (pins 3 y 2)
- 3 LEDs de estado (A0 rojo, A1 amarillo, A2 verde)
- Batería 7.4 V independiente para tracción
- Conexión USB al puerto COM3
- PC con LM Studio corriendo el modelo qwen/qwen3-4b-2507

## Estructura del repositorio

| Archivo | Descripción |
|---------|-------------|
| `arduino.ino` | Firmware del Arduino: comandos seriales, motores, servos, sensor y LEDs |
| `server.py` | Script de control autónomo con LLM + tools + loop principal |

## Estado del proyecto

Versión funcional orientada a control físico del carro por comandos y por integración con IA local.

El sistema opera completamente autónomo: detecta objetos con el sensor, consulta al modelo de IA, recibe instrucciones y las ejecuta físicamente en el Arduino — sin ninguna intervención manual.
