#include <Arduino.h>
#include <BluetoothSerial.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

// Définition des broches
#define RED_PIN     13
#define GREEN_PIN   12
#define BLUE_PIN    25
#define COLD_PIN    32
#define WARM_PIN    26

// Définition des canaux PWM (0–15)
#define RED_CH      0
#define GREEN_CH    1
#define BLUE_CH     2
#define COLD_CH     3
#define WARM_CH     4

void setup() {
  // Initialisation des canaux PWM (fréquence de 5 kHz, résolution 8 bits)
  ledcSetup(RED_CH, 5000, 8);
  ledcSetup(GREEN_CH, 5000, 8);
  ledcSetup(BLUE_CH, 5000, 8);
  ledcSetup(COLD_CH, 5000, 8);
  ledcSetup(WARM_CH, 5000, 8);

  // Attacher chaque broche à un canal PWM
  ledcAttachPin(RED_PIN, RED_CH);
  ledcAttachPin(GREEN_PIN, GREEN_CH);
  ledcAttachPin(BLUE_PIN, BLUE_CH);
  ledcAttachPin(COLD_PIN, COLD_CH);
  ledcAttachPin(WARM_PIN, WARM_CH);

  Serial.begin(115200);
  SerialBT.begin("LEDstrip");
}

void decodeFrame(String frame){
  int r = 0, g = 0, b = 0, c = 0, w = 0;
  int idxR = frame.indexOf("'R': '");
  int idxG = frame.indexOf("'G': '");
  int idxB = frame.indexOf("'B': '");
  int idxC = frame.indexOf("'C': '");
  int idxW = frame.indexOf("'W': '");

  if (idxR != -1) {
    int endR = frame.indexOf("'", idxR + 6);
    String rStr = frame.substring(idxR + 6, endR);
    r = rStr.toInt();
  }
  if (r > 255 || r < 0) r = 0;
  if (idxG != -1) {
    int endG = frame.indexOf("'", idxG + 6);
    String gStr = frame.substring(idxG + 6, endG);
    g = gStr.toInt();
  }
  if (g > 255 || g < 0) g = 0;
  if (idxB != -1) {
    int endB = frame.indexOf("'", idxB + 6);
    String bStr = frame.substring(idxB + 6, endB);
    b = bStr.toInt();
  }
  if (b > 255 || b < 0) b = 0;
  if (idxC != -1) {
    int endC = frame.indexOf("'", idxC + 6);
    String cStr = frame.substring(idxC + 6, endC);
    c = cStr.toInt();
  }
  if (c > 255 || c < 0) c = 0;
  if (idxW != -1) {
    int endW = frame.indexOf("'", idxW + 6);
    String wStr = frame.substring(idxW + 6, endW);
    w = wStr.toInt();
  }
  if (w > 255 || w < 0) w = 0;

  ledcWrite(RED_CH, r);
  ledcWrite(GREEN_CH, g);
  ledcWrite(BLUE_CH, b);
  ledcWrite(COLD_CH, c);
  ledcWrite(WARM_CH, w);
}

void loop() {
  int acc = 0;
  String frameReceived = "";
  if (SerialBT.available()) {
    String input_data = String((char)SerialBT.read());
    if (input_data == "S"){
      while (acc < 120)
      {
        acc++;
        frameReceived += String((char)SerialBT.read());
      }
      decodeFrame(frameReceived);
    }
  }
  delay(10);
}