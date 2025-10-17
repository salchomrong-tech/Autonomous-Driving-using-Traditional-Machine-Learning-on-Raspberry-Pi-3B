#include <Servo.h>
Servo myServo;
#define Servo 6
#define EnA 5
#define En1 4
#define En2 3
unsigned int servoAngle = 50;
unsigned long time, lasttime = 0;
void setup(){

  Serial.begin(115200);
  pinMode(EnA, OUTPUT);
  pinMode(En2, OUTPUT);
  pinMode(En1, OUTPUT);
  pinMode(Servo, OUTPUT);
  myServo.attach(Servo);
  myServo.write(servoAngle);

}

void Forward(int speed){

  analogWrite(EnA, speed);
  digitalWrite(En1, LOW);
  digitalWrite(En2, HIGH);

}

void loop(){
  time = millis();
  if (Serial.available()) {
    servoAngle = Serial.read();
    lasttime = time;
    myServo.write(servoAngle-40);
    Forward(80);
  }
  if(time -lasttime > 3000){
    Forward(0);
  }

}
