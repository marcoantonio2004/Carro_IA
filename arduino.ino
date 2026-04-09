#include <Servo.h>

// ---------------- PINES SERVO ----------------
const int servoPin1 = 3;
const int servoPin2 = 2;
Servo puerta1;
Servo puerta2;

// ---------------- PINES MOTORES ----------------
const int IN1 = 7;
const int IN2 = 8;
const int IN3 = 12;
const int IN4 = 13;
const int ENA = 5;
const int ENB = 6;

const int velMotor1 = 220;
const int velMotor2 = 220;

// ---------------- PINES ULTRASONICO ----------------
const int TRIG = 9;
const int ECHO = 10;
const int DISTANCIA_MINIMA = 25;

// ---------------- PINES LEDS ----------------
const int LED_ROJO     = A0;
const int LED_AMARILLO = A1;
const int LED_VERDE    = A2;

// ---------------- ESTADO PUERTAS ----------------
bool puerta1Abierta = false;
bool puerta2Abierta = false;

// ---------------- ESTADO MOTORES ----------------
bool motorMoviendo = false;

// ---------------- PARPADEO AMARILLO ----------------
unsigned long ultimoParpadeo = 0;
bool estadoAmarillo = false;
const int intervaloParpadeo = 400; // ms

// ---------------- LEER DISTANCIA ----------------
long leerDistancia() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duracion = pulseIn(ECHO, HIGH, 30000);
  if (duracion == 0) return 999;
  return duracion * 0.034 / 2;
}

// ---------------- ACTUALIZAR LEDS ----------------
void actualizarLeds() {
  // LED VERDE y ROJO segun movimiento
  if (motorMoviendo) {
    digitalWrite(LED_ROJO, LOW);
    digitalWrite(LED_VERDE, HIGH);
  } else {
    digitalWrite(LED_ROJO, HIGH);
    digitalWrite(LED_VERDE, LOW);
  }

  // LED AMARILLO parpadea si alguna puerta esta abierta
  if (puerta1Abierta || puerta2Abierta) {
    unsigned long ahora = millis();
    if (ahora - ultimoParpadeo >= intervaloParpadeo) {
      ultimoParpadeo = ahora;
      estadoAmarillo = !estadoAmarillo;
      digitalWrite(LED_AMARILLO, estadoAmarillo ? HIGH : LOW);
    }
  } else {
    estadoAmarillo = false;
    digitalWrite(LED_AMARILLO, LOW);
  }
}

// ---------------- COMANDOS ----------------
typedef String (*CommandFunc)(String args);

String cmdPing(String _args) {
  return "pong";
}

String cmdOpenDoor1(String _args) {
  puerta1.attach(servoPin1);
  puerta1.write(180);
  delay(200);
  puerta1.write(90);
  delay(500);
  puerta1.detach();
  puerta1Abierta = true;
  return "Door 1 opened";
}

String cmdCloseDoor1(String _args) {
  puerta1.attach(servoPin1);
  puerta1.write(0);
  delay(200);
  puerta1.write(90);
  delay(500);
  puerta1.detach();
  puerta1Abierta = false;
  return "Door 1 closed";
}

String cmdOpenDoor2(String _args) {
  puerta2.attach(servoPin2);
  puerta2.write(100);
  delay(450);
  puerta2.detach();
  puerta2Abierta = true;
  return "Door 2 opened";
}

String cmdCloseDoor2(String _args) {
  puerta2.attach(servoPin2);
  puerta2.write(81);
  delay(380);
  puerta2.detach();
  puerta2Abierta = false;
  return "Door 2 closed";
}

String cmdGetDistance(String _args) {
  long distancia = leerDistancia();
  if (distancia >= 999) return "Sin obstaculo detectado";
  return String(distancia) + " cm";
}

String cmdMoveForward(String _args) {
  long distancia = leerDistancia();
  if (distancia <= DISTANCIA_MINIMA) {
    detener();
    return "Obstaculo a " + String(distancia) + " cm - detenido";
  }

  analogWrite(ENA, velMotor1);
  analogWrite(ENB, velMotor2);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  motorMoviendo = true;
  return "Moving forward";
}

String cmdMoveBackward(String _args) {
  analogWrite(ENA, velMotor1);
  analogWrite(ENB, velMotor2);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  motorMoviendo = true;
  return "Moving backward";
}

String cmdTurnRight(String _args) {
  motorMoviendo = true;
  actualizarLeds();

  analogWrite(ENA, velMotor1);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENB, 255);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  delay(2500);
  detener();
  return "Turned right";
}

String cmdTurnLeft(String _args) {
  motorMoviendo = true;
  actualizarLeds();

  analogWrite(ENB, velMotor2);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 255);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  delay(2400);
  detener();
  return "Turned left";
}

String cmdStop(String _args) {
  detener();
  return "Stopped";
}

// ---------------- REGISTRO ----------------
struct Command {
  const char*  name;
  CommandFunc  func;
};

Command commands[] = {
  {"PING",          cmdPing},
  {"OPEN_DOOR_1",   cmdOpenDoor1},
  {"CLOSE_DOOR_1",  cmdCloseDoor1},
  {"OPEN_DOOR_2",   cmdOpenDoor2},
  {"CLOSE_DOOR_2",  cmdCloseDoor2},
  {"GET_DISTANCE",  cmdGetDistance},
  {"MOVE_FORWARD",  cmdMoveForward},
  {"MOVE_BACKWARD", cmdMoveBackward},
  {"TURN_RIGHT",    cmdTurnRight},
  {"TURN_LEFT",     cmdTurnLeft},
  {"STOP",          cmdStop}
};

const int numCommands = sizeof(commands) / sizeof(commands[0]);

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  pinMode(LED_ROJO,     OUTPUT);
  pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_VERDE,    OUTPUT);

  detener(); // rojo ON al iniciar
}

// ---------------- LOOP ----------------
void loop() {
  static String input = "";

  // Monitoreo automatico si esta avanzando
  bool avanzando = (digitalRead(IN1) == HIGH && digitalRead(IN2) == LOW &&
                    digitalRead(IN3) == HIGH && digitalRead(IN4) == LOW);

  if (avanzando) {
    long distancia = leerDistancia();
    if (distancia <= DISTANCIA_MINIMA) {
      detener();
      Serial.println("AUTO_STOP:" + String(distancia) + "cm");
    }
  }

  // Actualizar LEDs en cada ciclo (parpadeo amarillo)
  actualizarLeds();

  // Leer comandos serial
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (input.length() > 0) {
        processCommand(input);
        input = "";
      }
    } else {
      input += c;
    }
  }
}

// ---------------- PROCESAR ----------------
void processCommand(String line) {
  line.trim();
  int    spaceIdx = line.indexOf(' ');
  String cmdName  = (spaceIdx == -1) ? line : line.substring(0, spaceIdx);
  String args     = (spaceIdx == -1) ? ""   : line.substring(spaceIdx + 1);

  for (int i = 0; i < numCommands; ++i) {
    if (cmdName.equalsIgnoreCase(commands[i].name)) {
      Serial.println(commands[i].func(args));
      return;
    }
  }
  Serial.println("Unknown command");
}

// ---------------- DETENER ----------------
void detener() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  motorMoviendo = false;
}