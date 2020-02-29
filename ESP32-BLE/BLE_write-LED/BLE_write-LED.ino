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

#define BUTTON_PIN 0

#define MODE_OFF 0
#define MODE_ON  1
#define MODE_BLINK 2

#define DEEP_SLEEP_SEC 30

int led_mode = MODE_OFF;
int on_count = 0;
int off_count = 0;
#define ON_COUNT_MAX 60
#define OFF_COUNT_MAX 60

BLEAddress my_addr = BLEAddress("00:00:00:00:00:00");

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
      led_mode = MODE_ON;
      on_count = 0;
    } else if (value == "blink") {
      led_mode = MODE_BLINK;
      on_count = 0;
    } else {
      led_mode = MODE_OFF;
      off_count = 0;
    }
  }
};

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  led_mode = MODE_BLINK;

  Serial.print("Start:");
  Serial.println(MY_NAME);
  digitalWrite(LED_PIN, LED_ON);

  // init device
  BLEDevice::init(MY_NAME);
  my_addr = BLEDevice::getAddress();
  Serial.print("my_addr=");
  Serial.println(my_addr.toString().c_str());

  // init server, service, characteristic, and start service
  BLEServer *pServer = BLEDevice::createServer();

  /*
  // init service
  BLEService *pService = pServer->createService(SERVICE_UUID);
  BLECharacteristic *pCharacteristic
    = pService->createCharacteristic(
				     CHARACTERISTIC_UUID,
				     BLECharacteristic::PROPERTY_READ |
				     BLECharacteristic::PROPERTY_WRITE
				     );
  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->setValue(my_addr.toString().c_str());
  pService->start();
  */

  // start advertising
  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
  oAdvertisementData.setName(MY_NAME);
  oAdvertisementData.setFlags(0x06);
  oAdvertisementData.setManufacturerData("abc");

  pAdvertising->setAdvertisementData(oAdvertisementData);
  pAdvertising->start();

  delay(1000);
  digitalWrite(LED_PIN, LED_OFF);
}

char buf[256];
int idx = 0;

void loop() {
  while (Serial.available() > 0) {
    buf[idx] = Serial.read();
    Serial.println(String(buf[idx]));
    idx++;
  }
  if (buf[idx - 1] == 13) {
    buf[idx] ==  0;
    Serial.println(String(buf));
    idx = 0;
  }

  if (led_mode == MODE_ON) {
    digitalWrite(LED_PIN, LED_ON);
    delay(1000);
    on_count++;
  } else if (led_mode == MODE_BLINK) {
    digitalWrite(LED_PIN, LED_ON);
    delay(300);
    digitalWrite(LED_PIN, LED_OFF);
    delay(700);
    on_count++;
  } else { // OFF
    digitalWrite(LED_PIN, LED_OFF);
    delay(1000);
    off_count++;
  }

  if (led_mode == MODE_ON || led_mode == MODE_BLINK) {
    Serial.print("on_count=");
    Serial.println(String(on_count));
    if (on_count >= ON_COUNT_MAX) {
      led_mode = MODE_OFF;
      off_count = 0;
    }
  } else { // MODE_OFF
    Serial.print("off_count=");
    Serial.println(String(off_count));
    if (off_count >= OFF_COUNT_MAX) {
      Serial.print("deep sleep:");
      Serial.print(String(DEEP_SLEEP_SEC));
      Serial.println("sec ..");
      esp_deep_sleep(DEEP_SLEEP_SEC * 1000000LL);
    }
  }
}
