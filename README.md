# Carro_IA

Proyecto de control de un carro robótico con Arduino + servidor Python (FastMCP).

## Descripción del sistema

Este proyecto parte de un carro de control remoto comercial que fue modificado para actuar con IA.
La IA envía órdenes de movimiento y consulta de estado a través de un servidor Python, y el Arduino ejecuta
las acciones físicas en el vehículo.

El carro integra:

- 2 servomotores para abrir y cerrar las puertas.
- 1 LED rojo que indica reposo (carro estático).
- 1 LED verde que indica movimiento.
- 1 LED naranja (amarillo en pines A1) que indica puertas abiertas (parpadeo mientras permanezcan abiertas).
- 1 sensor de distancia para medir obstáculos y responder en centímetros (cm).

## Objetivo

Este repositorio separa el sistema en dos partes:

- Firmware en Arduino para mover motores, controlar puertas (servos), leer distancia y responder comandos por serial.
- Servidor en Python que envía comandos al Arduino y expone herramientas para controlarlo desde un flujo de IA.

## Estructura del repositorio

- `arduino.ino`: firmware principal del robot.
- `server.py`: servidor MCP que se comunica por puerto serial con el Arduino.

## Arquitectura general

1. `server.py` abre conexión serial (COM7, 9600).
2. Se envía un comando de texto (por ejemplo: `MOVE_FORWARD`).
3. `arduino.ino` recibe el comando, ejecuta acción y responde por serial.
4. El servidor devuelve el resultado como respuesta de la tool.

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

- `PING`
- `OPEN_DOOR_1`
- `CLOSE_DOOR_1`
- `OPEN_DOOR_2`
- `CLOSE_DOOR_2`
- `GET_DISTANCE`
- `MOVE_FORWARD`
- `MOVE_BACKWARD`
- `TURN_RIGHT`
- `TURN_LEFT`
- `STOP`

## Servidor Python (`server.py`)

### Responsabilidad

- Envía comandos al Arduino por serial.
- Espera respuesta según tipo de comando (tiempos de espera distintos).
- Publica tools MCP para puertas, movimiento, distancia y estado del robot.

### Tools principales

Puertas:

- `open_door_1`
- `close_door_1`
- `open_door_2`
- `close_door_2`
- `open_both_doors`
- `close_both_doors`

Movimiento:

- `move_forward`
- `move_backward`
- `turn_right`
- `turn_left`
- `stop`

Sensado y estado:

- `get_distance`
- `check_robot_status`
- `check_arduino_connection`

## Flujo de uso esperado

1. Cargar `arduino.ino` en la placa Arduino.
2. Conectar la placa al puerto definido en `server.py`.
3. Ejecutar el servidor Python.
4. Invocar tools para controlar el robot.

## Notas de comportamiento

- Al avanzar, el firmware revisa distancia frontal y detiene el carro si detecta un obstáculo por debajo del umbral de seguridad documentado (22 cm).
- Los giros tienen duración fija y luego ejecutan `STOP`.
- El servidor filtra respuestas seriales inesperadas para mantener consistencia en la respuesta final.

## Funcionamiento del puente H

El puente H es el circuito que permite controlar motores DC en ambos sentidos usando señales del Arduino.
En este proyecto, se usan señales de dirección (`IN1`, `IN2`, `IN3`, `IN4`) y de velocidad (`ENA`, `ENB` mediante PWM):

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

En resumen, la IA toma decisiones de alto nivel, y el Arduino materializa esas decisiones en control físico del vehículo.

## Estado del proyecto

Versión inicial funcional orientada a control remoto por comandos y exposición de tools para integración con agentes IA.
