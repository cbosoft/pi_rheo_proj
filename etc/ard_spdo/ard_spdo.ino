int count;
void incr();


void setup() {
  //Setup serial (USB/TTY) communication
  Serial.begin(9600);
  while (!Serial) {
    ;
  }

  //Setup interrupt on pin 3
  attachInterrupt(digitalPinToInterrupt(3), incr, RISING);
}

void loop() {
  // put your main code here, to run repeatedly:
  long tbt = millis();
  delay(100);
  long diff = millis() - tbt;
  long spd = count / (diff / (60000)); //spd in RPM
  count = 0;
  //send to rpi
  Serial.write(spd);
}

void incr(){
  count += 1;
}

