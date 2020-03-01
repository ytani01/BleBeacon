/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface

#define SERIAL_SPEED   115200
#define PIN_LED        2
#define SCAN_SEC       2
#define DEEP_SLEEP_SEC 20
#define MY_NAME        "ESP32 Observer"
#define DEV_NAME       "ESP32"

#define LED_MODE_OFF   0
#define LED_MODE_ON    1
#define LED_MODE_BLINK 2
int     LedMode = LED_MODE_OFF;
#define ON_MSEC        800

#define COUNTOFF_MAX 2
int     CountOff = 0;

BLEScan* pBLEScan;
String   MyAddrStr;

#define ALL_STR "all"

//
// setup
//
void setup() {
  Serial.begin(SERIAL_SPEED);

  CountOff = 0;

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, HIGH);

  BLEDevice::init(MY_NAME);
  //Serial.println(BLEDevice::toString().c_str());
  
  MyAddrStr = String(BLEDevice::getAddress().toString().c_str());
  Serial.println("MyAddrStr=" + MyAddrStr);
    
  pBLEScan = BLEDevice::getScan();
  //pBLEScan->setActiveScan(false); // パッシブスキャン
  pBLEScan->setActiveScan(true); // アクティブスキャン

  Serial.println("start...");
  digitalWrite(PIN_LED, LOW);
}

//
// loop
//
void loop() {
  Serial.print("scanning ..");
  BLEScanResults foundDevices = pBLEScan->start(SCAN_SEC);
  Serial.println(" done.");
  int n_devs = foundDevices.getCount();
  
  for (int i = 0; i < n_devs; i++) {
    BLEAdvertisedDevice dev = foundDevices.getDevice(i);
    String dev_addr = String(dev.getAddress().toString().c_str());
    String dev_name = String(dev.getName().c_str());

    // Serial.print(dev.toString().c_str());

    if (dev_name == DEV_NAME && dev.haveManufacturerData()) {
      String data = String(dev.getManufacturerData().c_str());
      Serial.print(dev_addr + ": " + data);

      if (data == ALL_STR || data == MyAddrStr) {
        Serial.print(" !!");
        LedMode = LED_MODE_ON;
      } else {
        Serial.print(" NG");
      }

      Serial.println();
    } // for
  }
  
  Serial.println("LedMode=" + String(LedMode));
  if (LedMode == LED_MODE_ON) {		// LED_MODE_ON
    digitalWrite(PIN_LED, HIGH);
    CountOff = 0;
    delay(ON_MSEC);
    digitalWrite(PIN_LED, LOW);
    LedMode = LED_MODE_OFF;
  } else {				// LED_MODE_OFF
    digitalWrite(PIN_LED, LOW);
    CountOff++;
    Serial.println("CountOff=" + String(CountOff));
    if (CountOff > COUNTOFF_MAX) {
      Serial.println("deep sleep " + String(DEEP_SLEEP_SEC) + " sec ..");
      esp_deep_sleep(DEEP_SLEEP_SEC * 1000000LL);
    }
  }
}
