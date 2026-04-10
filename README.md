# Carro_IA

Proyecto de control de un carro robótico con Arduino + servidor Python (FastMCP).

## Descripción del sistema

Este proyecto parte de un carro de control remoto de juguete que fue modificado para actuar con IA.
La IA envía órdenes de movimiento y el Arduino ejecuta las acciones físicas en el vehículo.

El carro integra:

- 2 motores de tracción para las 4 llantas: un motor mueve el lado derecho y otro motor mueve el lado izquierdo.
- Alimentación independiente de 7.4 V para los motores de tracción.
- 2 servomotores para abrir y cerrar las puertas.
- 1 LED rojo que indica reposo (carro estático).
- 1 LED verde que indica movimiento.
- 1 LED naranja que indica puertas abiertas (parpadeo mientras permanezcan abiertas).
- 1 sensor de distancia para detener el carro al estar en un rango de 22 centímetros o menos y consultar distancia.

## Objetivo

Este repositorio separa el sistema en dos partes:

- Programa en Arduino para mover motores, controlar puertas (servos), leer distancia y responder comandos por serial.
- Servidor en Python que envía comandos al Arduino y expone herramientas para controlarlo desde un flujo de IA.

## Estructura del repositorio

- `arduino.ino`: Código principal del carro.
- `server.py`: servidor MCP que se comunica por puerto serial con el Arduino.

## Arquitectura general

1. `server.py` abre conexión serial (COM7, 9600).
2. Se envía un comando de texto (por ejemplo: `Abre la puerta 1 o 2`, `Avanza`, `Gira a la derecha o izquierda` y `A que distancia se encuentra un obstáculo`).
3. `arduino.ino` recibe el comando, ejecuta acción y responde por serial.
4. El servidor devuelve el resultado como respuesta de la tool.

## Integración con IA (LM Studio)

El control del carro también se realiza mediante IA local usando LM Studio.

- Motor de inferencia: LM Studio.
- Modelo utilizado: `qwen/qwen3-v1-4b`.
- Integración: plugin MCP `mcp/robot-control` conectado al servidor `server.py`.

Con esta integración, se envían instrucciones en lenguaje natural (por ejemplo: "cierra las dos puertas", "gira a la derecha" o "gira a la izquierda") y el modelo invoca la tool correspondiente para ejecutar la acción en el carro.

## Firmware Arduino (`arduino.ino`)

### Funcionalidades

- Control de motores DC: avanzar, retroceder, girar derecha, girar izquierda, detener.
- Control de 2 servos (puertas): abrir/cerrar puerta 1 y puerta 2.
- Sensor ultrasónico para distancia y auto-detención al avanzar.
- Lógica de LEDs de estado:
- Rojo: reposo o estado estático.
- Verde: carro en movimiento.
- Naranja/amarillo: puertas abiertas (parpadeo mientras estén abiertas).
- Protocolo de comandos serial en texto plano.
- Consulta de distancia desde la IA, con respuesta en cm.

### Mapa de pines

#### Servos

- Servo puerta 1: pin 3
- Servo puerta 2: pin 2

#### Motores

- IN1: 7
- IN2: 8
- IN3: 12
- IN4: 13
- ENA: 5
- ENB: 6

#### Ultrasónico

- TRIG: 9
- ECHO: 10

#### LEDs

- LED rojo: A0
- LED amarillo: A1
- LED verde: A2

### Comandos serial soportados

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

## Servidor Python (`server.py`)

### Responsabilidad

- Envía comandos al Arduino por serial.
- Espera respuesta según tipo de comando (tiempos de espera distintos).
- Publica tools MCP para puertas, movimiento, distancia y estado del robot.

### Tools principales

Puertas:

- `open_door_1`: solicita abrir la puerta 1.
- `close_door_1`: solicita cerrar la puerta 1.
- `open_door_2`: solicita abrir la puerta 2.
- `close_door_2`: solicita cerrar la puerta 2.
- `open_both_doors`: abre ambas puertas en secuencia.
- `close_both_doors`: cierra ambas puertas en secuencia.

Movimiento:

- `move_forward`: ordena avanzar con control de seguridad por distancia.
- `move_backward`: ordena retroceder.
- `turn_right`: ordena giro hacia la derecha.
- `turn_left`: ordena giro hacia la izquierda.
- `stop`: ordena detención inmediata del carro.

Sensado y estado:

- `get_distance`: consulta y devuelve la distancia frontal actual.
- `check_robot_status`: resume estado de movimiento, puertas y sensores.
- `check_arduino_connection`: valida si el enlace serial está operativo.

## Flujo de uso esperado

1. Cargar `arduino.ino` en la placa Arduino.
2. Conectar la placa al puerto definido en `server.py`.
3. Ejecutar el servidor Python.
4. Invocar tools para controlar el robot.

## Elaboración del proyecto

Este apartado resume cómo se construyó el prototipo físico antes de la integración con Arduino e IA.

### 1) Compra y selección del carro base

- Se seleccionó un carro de juguete con chasis firme, espacio interno para electrónica y sistema de tracción funcional.
- Se verificó que el tamaño permitiera alojar placa, puente H, servos, cableado y batería sin comprometer estabilidad.

### 2) Desarmado inicial

- Se desmontó la carcasa para acceder a los motores internos del carroy cortar la zona de las puertas.
- Se retiraron piezas no necesarias para liberar espacio y facilitar el paso de cables.
- Se dejo la posición original de tornillos y piezas para simplificar el reensamblaje.

### 3) Unión de cables y adaptación eléctrica

- Se identificaron líneas de alimentación, tierra común y señales de control para motores, servos, LEDs y sensor ultrasónico.
- Se realizaron empalmes y extensiones de cable con jumpers donde el cable original no alcanzaba la nueva distribución.
- Se aisló cada unión para evitar cortocircuitos y falsos contactos por vibración del carro.

### 4) Cortes y adaptación de puertas

- Se hicieron cortes puntuales en la carrocería para permitir el recorrido mecánico de las puertas accionadas por servos.
- Se verificó que los cortes no afectaran la estructura principal ni rozaran con el cableado interno.

### 5) Ensamble final y pruebas

- Se volvió a montar la carrocería con los módulos electrónicos ya fijados.
- Se probó movimiento, apertura/cierre de puertas, lectura de distancia y respuesta por comandos serial.
- Se realizaron ajustes de posición de cables y servos para mejorar confiabilidad en operación continua.

## Notas de comportamiento

- Al avanzar, el servidor revisa distancia frontal y detiene el carro si detecta un obstáculo por debajo de los 22 centímetros permitidos
- Los giros tienen duración fija y luego ejecutan `STOP`.
- El servidor filtra respuestas seriales inesperadas para mantener consistencia en la respuesta final.

## Funcionamiento del puente H

El puente H es el circuito que permite controlar motores DC en ambos sentidos usando señales del Arduino.
En este proyecto, se usan señales de dirección (`IN1`, `IN2`, `IN3`, `IN4`) y de velocidad (`ENA`, `ENB` mediante PWM):

- Configuración de tracción: se utilizan 2 motores DC para mover las 4 llantas (uno para el lado derecho y otro para el lado izquierdo).
- Alimentación de tracción: estos motores se alimentan con una batería independiente de 7.4 V.
- Dirección: combinando HIGH/LOW en las entradas se define si cada motor gira hacia adelante o hacia atrás.
- Velocidad: con PWM en `ENA` y `ENB` se regula la potencia entregada a cada motor.
- Frenado/paro: colocando velocidad en 0 y entradas en LOW, el carro se detiene.

Gracias al puente H, el sistema puede avanzar, retroceder y girar variando sentido y potencia de cada motor.

## Funcionamiento del Arduino en el proyecto

El Arduino actúa como controlador de tiempo real del carro:

- Recibe comandos por puerto serial (enviados por `server.py`).
- Ejecuta acciones de actuadores (motores y servos).
- Lee sensores (ultrasónico) para estimar distancia en cm.
- Aplica reglas de seguridad (detención automática ante obstáculo cercano).
- Devuelve respuestas seriales al servidor para que la IA informe el resultado.


## Estado del proyecto

Versión inicial funcional orientada a control remoto por comandos y exposición de tools para integración con agentes IA.
