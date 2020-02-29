/*
  Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleWrite.cpp
  Ported to Arduino ESP32 by Evandro Copercini

  changed by Yoichi Tanibayashi
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define MY_NAME             "ESP32"
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

#define LED_PIN	2
#define LED_ON	HIGH
#define LED_OFF	LOW

#define DEEP_SLEEP_SEC 20

#define MODE_OFF   0
#define MODE_ON    1
#define MODE_BLINK 2
int LedMode = MODE_OFF;

#define COUNTON_MAX  20
#define COUNTOFF_MAX  5
int CountOn  = 0;
int CountOff = 0;

BLEServer      *pServer;
BLEAdvertising *pAdvertising;
BLEAddress     MyAddr = BLEAddress("00:00:00:00:00:00");

String DevID[] = {
  "30:ae:a4:99:a2:02",
  "24:0a:c4:11:e6:1a"
};
int TouchPin[] = {T0, T7};
int TouchDefaults[] = {0, 0};

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  LedMode = MODE_BLINK;

  Serial.print("Start:");
  Serial.println(MY_NAME);
  digitalWrite(LED_PIN, LED_ON);

  // init device
  BLEDevice::init(MY_NAME);
  MyAddr = BLEDevice::getAddress();
  Serial.println("MyAddr=" + String(MyAddr.toString().c_str()));
  
  // init server, service, characteristic, and start service
  pServer = BLEDevice::createServer();
  
  // start advertising
  pAdvertising = pServer->getAdvertising();
  BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
  oAdvertisementData.setName(MY_NAME);
  oAdvertisementData.setFlags(0x06);
  oAdvertisementData.setManufacturerData("all");
  
  pAdvertising->setAdvertisementData(oAdvertisementData);
  pAdvertising->start();
  
  delay(1000);
  digitalWrite(LED_PIN, LED_OFF);

  for (int i=0; i < 2; i++) {
    TouchDefaults[i] = touchRead(TouchPin[i]);
    Serial.println("TouchDefaults[" + String(i) + "]="
                   + String(TouchDefaults[i]));
  }
}

void loop() {
  bool touch_on[] = {false, false};

  Serial.print("v = ");
  for (int i=0; i < 2; i++) {
    touch_on[i] = false;
    int v = touchRead(TouchPin[i]);
    Serial.print(String(v) + " ");

    if (v < TouchDefaults[i] * 0.5) {
      touch_on[i] = true;
    }
  }
  Serial.println();

  String buf = "";
  if (touch_on[0] && touch_on[1]) {
    buf = "all";
  } else if (touch_on[0]) {
    buf = DevID[0];
  } else if (touch_on[1]) {
    buf = DevID[1];
  } else {
    buf = "";
  }
  if (buf != "") {
    Serial.println(buf);
    
    pAdvertising->stop();
    delay(500);
    BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
    oAdvertisementData.setName(MY_NAME);
    oAdvertisementData.setFlags(0x06);
    oAdvertisementData.setManufacturerData(buf.c_str());
    pAdvertising->setAdvertisementData(oAdvertisementData);
    pAdvertising->start();
    
    Serial.println(oAdvertisementData.getPayload().c_str());
  }

  while (Serial.available() > 0) {
    String buf = Serial.readStringUntil('\r');
    Serial.println(buf);
    if (buf.length() <= 2) {
      int idx = buf.toInt();
      if (idx < 2) {
        buf = DevID[idx];
      }
    }
    
    pAdvertising->stop();
    delay(500);
    BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
    oAdvertisementData.setName(MY_NAME);
    oAdvertisementData.setFlags(0x06);
    oAdvertisementData.setManufacturerData(buf.c_str());
    pAdvertising->setAdvertisementData(oAdvertisementData);
    pAdvertising->start();
    
    Serial.println(oAdvertisementData.getPayload().c_str());
  }

  if (LedMode == MODE_ON) {
    digitalWrite(LED_PIN, LED_ON);
    delay(1000);
    CountOn++;
  } else if (LedMode == MODE_BLINK) {
    digitalWrite(LED_PIN, LED_ON);
    delay(200);
    digitalWrite(LED_PIN, LED_OFF);
    delay(800);
    CountOn++;
  } else { // OFF
    digitalWrite(LED_PIN, LED_OFF);
    delay(1000);
    CountOff++;
  }
}

class MyCallbacks: public BLECharacteristicCallbacks {
  void onConnect(BLEClient *pClient) {
    Serial.println("> onConnect");
  }
  
  void OnDisconnect(BLEClient *pClient) {
    Serial.println("> onDisconnect");
  }
  
  void onWrite(BLECharacteristic *pCharacteristic) {
    Serial.println("> onWrite");
    std::string value = pCharacteristic->getValue();
    
    Serial.print("value=");
    Serial.println(value.c_str());
    if (value.length() > 0) {
      Serial.print("New value: ");
      for (int i = 0; i < value.length(); i++) {
	Serial.print(value[i]);
      }
      Serial.println();
    }
    
    if (value == "on") {
      LedMode = MODE_ON;
      CountOn = 0;
    } else if (value == "blink") {
      LedMode = MODE_BLINK;
      CountOn = 0;
    } else {
      LedMode = MODE_OFF;
      CountOff = 0;
    }
  }
};
