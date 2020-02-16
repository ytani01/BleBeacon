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

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

#define LED_PIN	2
#define LED_ON	HIGH
#define LED_OFF	LOW

#define MODE_OFF 0
#define MODE_ON  1
#define MODE_BLINK 2

int led_mode = MODE_OFF;

class MyCallbacks: public BLECharacteristicCallbacks {
  void onConnect(BLEClient *pClient) {
    Serial.println('> onConnect');
  }

  void OnDisconnect(BLEClient *pClient) {
    Serial.println('> onDisconnect');
  }

  void onWrite(BLECharacteristic *pCharacteristic) {
    std::string value = pCharacteristic->getValue();
    
    if (value == "on") {
      led_mode = MODE_ON;
      digitalWrite(LED_PIN, LED_ON);
    } else if (value == "blink") {
      led_mode = MODE_BLINK;
    } else {
      led_mode = MODE_OFF;
      digitalWrite(LED_PIN, LED_OFF);
    }
      
    if (value.length() > 0) {
      Serial.println("*********");
      Serial.print("New value: ");
      for (int i = 0; i < value.length(); i++)
	Serial.print(value[i]);

      Serial.println();
      Serial.println("*********");
    }
  }
};

void setup() {
  Serial.begin(115200);

  Serial.println("1- Download and install an BLE scanner app in your phone");
  Serial.println("2- Scan for BLE devices in the app");
  Serial.println("3- Connect to MyESP32");
  Serial.println("4- Go to CUSTOM CHARACTERISTIC in CUSTOM SERVICE and write something");
  Serial.println("5- See the magic =)");

  led_mode = MODE_OFF;
  pinMode(LED_PIN, OUTPUT);

  BLEDevice::init("MyESP32");
  BLEServer *pServer = BLEDevice::createServer();

  BLEService *pService = pServer->createService(SERVICE_UUID);

  BLECharacteristic *pCharacteristic
    = pService->createCharacteristic(
				     CHARACTERISTIC_UUID,
				     BLECharacteristic::PROPERTY_READ |
				     BLECharacteristic::PROPERTY_WRITE
				     );

  pCharacteristic->setCallbacks(new MyCallbacks());

  pCharacteristic->setValue("Hello World");
  pService->start();

  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->start();
}

void loop() {
  if (led_mode == MODE_ON) {
    digitalWrite(LED_PIN, LED_ON);
    delay(1000);
  } else if (led_mode == MODE_BLINK) {
    digitalWrite(LED_PIN, LED_ON);
    delay(300);
    digitalWrite(LED_PIN, LED_OFF);
    delay(300);
  } else {
    digitalWrite(LED_PIN, LED_OFF);
    delay(1000);
  }
}
