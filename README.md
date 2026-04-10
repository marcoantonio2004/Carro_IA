# Carro_IA

Proyecto de control de un carro robótico con Arduino, servidor Python y modelo de IA local.

## 1) Armado del proyecto

### Compra y selección del carro

- Se compró un carro de juguete con chasis firme, tracción funcional y espacio interno para electrónica.
- Se validó que el tamaño permitiera alojar Arduino, puente H, servos, sensor y cableado.

### Desarmado y preparación

- Se desmontó la carrocería para acceder al sistema interno de motores y a la zona de puertas.
- Se retiraron piezas no necesarias para liberar espacio y facilitar el enrutado de cables.
- Se conservaron tornillos y puntos de fijación para el reensamblaje final.

### Unión de cables

- Se identificaron líneas de alimentación, tierra común y señales de control.
- Se hicieron empalmes y extensiones donde los cables originales no alcanzaban.
- Cada unión se aisló para evitar cortocircuitos y falsos contactos por vibración.

### Cortes para las puertas

- Se realizaron cortes puntuales en la carrocería para permitir el recorrido de las puertas accionadas por servos.
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
- Puente H para control de motores DC.
- 2 motores DC de tracción para 4 llantas: un motor mueve el lado derecho y otro el lado izquierdo.
- Batería independiente de 7.4 V para los motores de tracción.
- 2 servomotores para apertura/cierre de puertas.
- Sensor ultrasónico para medición de distancia frontal.
- 3 LEDs de estado: rojo, amarillo/naranja y verde.

### Funcionamiento del puente H

El puente H es el circuito que permite controlar motores DC en ambos sentidos usando señales del Arduino.
En este proyecto, se usan señales de dirección (`IN1`, `IN2`, `IN3`, `IN4`) y de velocidad (`ENA`, `ENB` mediante PWM):

- Configuración de tracción: se utilizan 2 motores DC para mover las 4 llantas (uno para el lado derecho y otro para el lado izquierdo).
- Alimentación de tracción: estos motores se alimentan con una batería independiente de 7.4 V.
- Dirección: combinando HIGH/LOW en las entradas se define si cada motor gira hacia adelante o hacia atrás.
- Velocidad: con PWM en `ENA` y `ENB` se regula la potencia entregada a cada motor.
- Frenado/paro: colocando velocidad en 0 y entradas en LOW, el carro se detiene.

### Conexión general del circuito

- Arduino genera señales de control para el puente H (dirección y velocidad PWM).
- El puente H alimenta y gobierna los dos motores de tracción.
- Los servos de puertas se controlan desde pines PWM del Arduino.
- El sensor ultrasónico se conecta a pines TRIG/ECHO para medir distancia.
- Los LEDs se conectan a salidas del Arduino para indicar estados del sistema.

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

### Cómo se conectó todo

- Se unieron todas las tierras en común para mantener referencia eléctrica estable.
- La lógica de control se gestiona con Arduino y la potencia de tracción con batería de 7.4 V.
- Cada subsistema (tracción, puertas, sensado e indicadores) se cableó por separado para facilitar pruebas y mantenimiento.

## 3) Funcionamiento sencillo del carro

- El Arduino actúa como controlador de tiempo real del carro.
- Recibe comandos por puerto serial y ejecuta acciones de actuadores (motores y servos).
- En reposo se enciende el LED rojo.
- En movimiento se enciende el LED verde.
- Cuando una puerta está abierta, el LED amarillo/naranja parpadea.
- Al avanzar, el sensor ultrasónico mide distancia frontal.
- Si detecta un obstáculo a 22 cm o menos, el sistema detiene el carro automáticamente.

### Funcionalidades del programa en Arduino (`arduino.ino`)

- Control de motores DC: avanzar, retroceder, girar derecha, girar izquierda, detener.
- Control de 2 servos (puertas): abrir/cerrar puerta 1 y puerta 2.
- Sensor ultrasónico para distancia y auto-detención al avanzar.
- Protocolo de comandos serial en texto plano.
- Consulta de distancia desde la IA, con respuesta en cm.

## 4) Comunicación Arduino + IA (LM Studio)

### Integración lograda

- Se usó LM Studio como motor de inferencia local.
- Se usó el modelo `qwen/qwen3-v1-4b`.
- El servidor `server.py` actúa como puente entre el modelo y el Arduino por puerto serial.
- La integración MCP utilizada es `mcp/robot-control`.

### Arquitectura general

1. `server.py` abre conexión serial (COM7, 9600).
2. Se envía un comando de texto (por ejemplo: `Abre la puerta 1 o 2`, `Avanza`, `Gira a la derecha o izquierda` y `A que distancia se encuentra un obstáculo`).
3. `arduino.ino` recibe el comando, ejecuta acción y responde por serial.
4. El servidor devuelve el resultado como respuesta de la tool.

### Responsabilidad del servidor (`server.py`)

- Envía comandos al Arduino por serial.
- Espera respuesta según tipo de comando (tiempos de espera distintos).
- Publica tools MCP para puertas, movimiento, distancia y estado del robot.

### Qué herramientas se usan en esa comunicación

Puertas:

- `open_door_1`: abre puerta 1.
- `close_door_1`: cierra puerta 1.
- `open_door_2`: abre puerta 2.
- `close_door_2`: cierra puerta 2.
- `open_both_doors`: abre ambas puertas.
- `close_both_doors`: cierra ambas puertas.

Movimiento:

- `move_forward`: avanza con control de seguridad por distancia.
- `move_backward`: retrocede.
- `turn_right`: gira a la derecha.
- `turn_left`: gira a la izquierda.
- `stop`: detiene el carro.

Sensado y estado:

- `get_distance`: mide y devuelve distancia frontal en cm.
- `check_robot_status`: revisa estado general del robot.
- `check_arduino_connection`: valida conexión serial con Arduino.

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

### Flujo de uso esperado

1. Cargar `arduino.ino` en la placa Arduino.
2. Conectar la placa al puerto definido en `server.py`.
3. Ejecutar el servidor Python.
4. Invocar tools para controlar el robot.

## 5) Ciclo típico de operación

1. Encender el carro y el sistema electrónico.
2. Verificar conexión con Arduino.
3. Encender indicadores según estado inicial (reposo).
4. Abrir una o ambas puertas si la instrucción lo requiere.
5. Ejecutar movimiento (avanzar, retroceder o girar).
6. Medir distancia durante el avance para evitar colisiones.
7. Detener el carro al final de la acción o por seguridad.
8. Cerrar puertas y volver a estado de reposo.

## Estructura del repositorio

- `arduino.ino`: programa principal del carro.
- `server.py`: servidor MCP que se comunica por serial con Arduino.

## Estado del proyecto

Versión funcional orientada a control físico del carro por comandos y por integración con IA local.
