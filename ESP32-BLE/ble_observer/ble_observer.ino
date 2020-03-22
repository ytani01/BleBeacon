/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface

#define SERIAL_SPEED   115200
#define PIN_LED        2
#define SCAN_SEC       2
#define DEEP_SLEEP_MSEC_OFF 10000
#define DEEP_SLEEP_MSEC_ON 200
#define MY_NAME        "ESP32 Observer"
#define DEV_NAME       "ESP32"

#define LED_MODE_OFF   0
#define LED_MODE_ON    1
#define LED_MODE_BLINK 2
int     LedMode = LED_MODE_OFF;
#define ON_MSEC        2000

#define COUNTOFF_MAX 2
int     CountOff = 0;

BLEScan* pBLEScan;
String   MyAddrStr;

#define ALL_STR "all"

#define TAG_PREFIX "tag-"
String TargetName;

//
// setup
//
void setup() {
  Serial.begin(SERIAL_SPEED);

  CountOff = 0;

  pinMode(PIN_LED, OUTPUT);
  //digitalWrite(PIN_LED, HIGH);

  BLEDevice::init(MY_NAME);
  //Serial.println(BLEDevice::toString().c_str());
  MyAddrStr = String(BLEDevice::getAddress().toString().c_str());
  Serial.println("MyAddrStr=" + MyAddrStr);
  
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(false); // パッシブスキャン
  //pBLEScan->setActiveScan(true); // アクティブスキャン

  Serial.println("start...");
  digitalWrite(PIN_LED, LOW);

  TargetName = TAG_PREFIX + MyAddrStr;
  Serial.println("TargetName=" + TargetName);
}

//
// loop
//
void loop() {
  Serial.print("scanning ..");
  BLEScanResults foundDevices = pBLEScan->start(SCAN_SEC);
  int n_devs = foundDevices.getCount();
  Serial.println(" done. " + String(n_devs));
  
  for (int i = 0; i < n_devs; i++) {
    BLEAdvertisedDevice dev = foundDevices.getDevice(i);
    String dev_addr = String(dev.getAddress().toString().c_str());
    String dev_name = String(dev.getName().c_str());
    String manu_data = "";

    if (dev.haveManufacturerData()) {
      manu_data = String(dev.getManufacturerData().c_str());
    }
    Serial.print("*" + dev_name + ':' + dev_addr + ':');

    if (dev_name == TargetName || manu_data == TargetName) {
      Serial.println(" !!");
      LedMode = LED_MODE_ON;
      break;
    } else {
      Serial.print(" NG");
    }

    Serial.println();

    if (dev.haveServiceData()) {
      String svc_data = String(dev.getServiceData().c_str());
      Serial.println("  svc_data=" + svc_data);
    }

    if (dev.haveServiceUUID()) {
      BLEUUID svc_uuid = dev.getServiceDataUUID();
      Serial.println("  svc_uuid=" + String(svc_uuid.toString().c_str()));
    }
  } // for
  
  Serial.println("LedMode=" + String(LedMode));
  if (LedMode == LED_MODE_ON) {		// LED_MODE_ON
    digitalWrite(PIN_LED, HIGH);
    CountOff = 0;
    delay(ON_MSEC);
    Serial.println("deep sleep " + String(DEEP_SLEEP_MSEC_ON) + " msec ..");
    esp_deep_sleep(DEEP_SLEEP_MSEC_ON * 1000LL);

    // digitalWrite(PIN_LED, LOW);
    //LedMode = LED_MODE_OFF;

  } else {				// LED_MODE_OFF
    digitalWrite(PIN_LED, LOW);
    CountOff++;
    Serial.println("CountOff=" + String(CountOff));
    if (CountOff > COUNTOFF_MAX) {
      Serial.println("deep sleep " + String(DEEP_SLEEP_MSEC_OFF) + " msec ..");
      esp_deep_sleep(DEEP_SLEEP_MSEC_OFF * 1000LL);
    }
  }
}
