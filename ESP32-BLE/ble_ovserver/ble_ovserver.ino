/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface

#define SERIAL_SPEED   115200
#define PIN_LED        2
#define SCAN_SEC       2
#define DEEP_SLEEP_SEC 20
#define DEV_NAME       "ESP32"

#define LED_MODE_OFF 0
#define LED_MODE_ON  1
#define LED_MODE_BLINK 2
int LedMode = LED_MODE_OFF;

#define COUNTOFF_MAX 2
int CountOff = 0;

BLEScan*    pBLEScan;
std::string MyAddrStr;

//
// setup
//
void setup() {
  Serial.begin(SERIAL_SPEED);

  CountOff = 0;

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();

  MyAddrStr = BLEDevice::getAddress().toString();
  Serial.println(("MyAddrStr=" + MyAddrStr).c_str());
  //Serial.println(MyAddrStr.substr(0,9).c_str());
    
  pBLEScan->setActiveScan(false); // パッシブスキャン
  Serial.println("start...");
  digitalWrite(PIN_LED, LOW);
}

//
// loop
//
void loop() {
  BLEScanResults foundDevices = pBLEScan->start(SCAN_SEC);
  int count = foundDevices.getCount();
  
  if (LedMode == LED_MODE_ON) {
    digitalWrite(PIN_LED, LOW);
    delay(1000);
  }
  
  LedMode = LED_MODE_OFF;
  for (int i = 0; i < count; i++) {
    BLEAdvertisedDevice dev = foundDevices.getDevice(i);
    std::string dev_addr = dev.getAddress().toString();
    std::string dev_name = dev.getName();

    Serial.print(dev.toString().c_str());

    if (dev_name == DEV_NAME && dev.haveManufacturerData()) {
      std::string data = dev.getManufacturerData();
      Serial.print((" / data=" + data).c_str());

      if (data == "abc") {
        Serial.print(" !!");
        LedMode = LED_MODE_ON;
      }
    } // for

    Serial.println();
  }
  
  Serial.println("LedMode=" + String(LedMode));
  if (LedMode == LED_MODE_ON) {
    digitalWrite(PIN_LED, HIGH);
    CountOff = 0;
  } else { // LED_MODE_OFF
    digitalWrite(PIN_LED, LOW);
    CountOff++;
    Serial.println("CountOff=" + String(CountOff));
    if (CountOff > COUNTOFF_MAX) {
      Serial.println("deep sleep " + String(DEEP_SLEEP_SEC) + " sec ..");
      esp_deep_sleep(DEEP_SLEEP_SEC * 1000000LL);
    }
  }
  Serial.println();
}
