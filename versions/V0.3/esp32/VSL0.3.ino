#include <SCServo.h>

SMS_STS st;

#define S_RXD 18
#define S_TXD 19

const int OUTPUT_PIN = 4;

// 舵机信息
byte servo_ID[2];
s16 servo_position[2];
u16 servo_speed[2];
byte servo_accels[2];

// HOME 位置
const s16 SERVO0_HOME = 2500;
const s16 SERVO1_HOME = 2400;

// 步长
const int STEP_SIZE = 100;


void triggerOutput(unsigned long duration_ms = 1000) {    //激光开关函数
  digitalWrite(OUTPUT_PIN, HIGH);
  delay(duration_ms);
  digitalWrite(OUTPUT_PIN, LOW);
}

void sendAck(const String& cmd) {   //正确回应树莓派函数
  Serial.print("Received: ");
  Serial.println(cmd);

  Serial.print("OK: ");
  Serial.println(cmd);
}

void sendError(const String& cmd) {   //错误回应树莓派函数
  Serial.print("ERR: ");
  Serial.println(cmd);
}

void moveServos() {
  st.SyncWritePosEx(servo_ID, 2, servo_position, servo_speed, servo_accels);    //移动舵机函数
}

void setup() {
  Serial.begin(115200);   // 树莓派 <-> ESP32 USB 串口
  Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD);  // ESP32 <-> 舵机总线
  st.pSerial = &Serial1;

  delay(500);

  Serial.println("ESP32 ready");
  Serial.println("Servo ready");

  servo_ID[0] = 1;
  servo_ID[1] = 2;

  servo_speed[0] = 3400;
  servo_speed[1] = 3400;

  servo_accels[0] = 50;
  servo_accels[1] = 50;

  servo_position[0] = SERVO0_HOME;
  servo_position[1] = SERVO1_HOME;

  pinMode(OUTPUT_PIN, OUTPUT);
  digitalWrite(OUTPUT_PIN, LOW);

  moveServos();   //初始化舵机

  delay(1000);
}

void loop() {
  if (Serial.available()) {   //串口收到信息
    String cmd = Serial.readStringUntil('\n');    //读取信息
    cmd.trim();

    bool servoMoved = false;

    if (cmd == "RIGHT") {
      servo_position[0] += STEP_SIZE;
      servoMoved = true;
      sendAck(cmd);
    }
    else if (cmd == "LEFT") {
      servo_position[0] -= STEP_SIZE;
      servoMoved = true;
      sendAck(cmd);
    }
    else if (cmd == "UP") {
      servo_position[1] -= STEP_SIZE;
      servoMoved = true;
      sendAck(cmd);
    }
    else if (cmd == "DOWN") {
      servo_position[1] += STEP_SIZE;
      servoMoved = true;
      sendAck(cmd);
    }
    else if (cmd == "HOME") {
      servo_position[0] = SERVO0_HOME;
      servo_position[1] = SERVO1_HOME;
      servoMoved = true;
      sendAck(cmd);
    }
    else if (cmd == "OUT") {
      triggerOutput();
      sendAck(cmd);
    }
    else {
      sendError(cmd);
    }

    if (servoMoved) {   //如果收到信号则移动
      moveServos();
    }
  }
}
