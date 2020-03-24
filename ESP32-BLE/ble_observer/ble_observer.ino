/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface
#include <FS.h>
#include <SPIFFS.h>

#define FORMAT_ON_FAIL true

#define ON_FILE "/tag_on"

#define SERIAL_SPEED   115200
#define PIN_LED        2  // GPIO pin
#define SCAN_SEC       2  // sec
#define DEEP_SLEEP_MSEC_OFF 10000  // ms
#define DEEP_SLEEP_MSEC_ON 100     // ms
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

#define PUB_NAME "Yt"

#define TAG_PREFIX "T"
String TargetName;

//
// setup
//
void setup() {
  Serial.begin(SERIAL_SPEED);

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  Serial.println("----- File system");
  if (!SPIFFS.begin(FORMAT_ON_FAIL)) {
    Serial.println("SPIFFS.begin(): failed");
  }

  File rootfs = SPIFFS.open("/");
  Serial.println("/");

  File file;
  while ( file = rootfs.openNextFile() ) {
    String name = file.name();
    Serial.print("+- " + name);

    if (file.isDirectory()) {
      Serial.print("/");
    }
    file.close();

    if (name == ON_FILE) {
      Serial.println(" .. found .. LED_ON");
      digitalWrite(PIN_LED, HIGH);
    } else {
      Serial.println();
    }
  }
  rootfs.close();

  Serial.println("-----");

  CountOff = 0;

  BLEDevice::init(MY_NAME);
  MyAddrStr = String(BLEDevice::getAddress().toString().c_str());
  Serial.println("MyAddrStr=" + MyAddrStr);
  
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(false); // パッシブスキャン
  //pBLEScan->setActiveScan(true); // アクティブスキャン

  Serial.println("start...");
  // digitalWrite(PIN_LED, LOW);

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
  
  LedMode = LED_MODE_OFF;
  for (int i = 0; i < n_devs; i++) {
    BLEAdvertisedDevice dev = foundDevices.getDevice(i);
    String dev_addr = String(dev.getAddress().toString().c_str());
    String dev_name = String(dev.getName().c_str());
    String ms_data = "";

    if (dev.haveManufacturerData()) {
      ms_data = String(dev.getManufacturerData().c_str());
    }

    if (dev_name == PUB_NAME && ms_data == TargetName) {
      Serial.println("*" + dev_name + "[" + dev_addr + "] " + ms_data + " !!");
      LedMode = LED_MODE_ON;
      break;
    }

    /*
    if (dev.haveServiceData()) {
      String svc_data = String(dev.getServiceData().c_str());
      Serial.println("  svc_data=" + svc_data);
    }

    if (dev.haveServiceUUID()) {
      BLEUUID svc_uuid = dev.getServiceDataUUID();
      Serial.println("  svc_uuid=" + String(svc_uuid.toString().c_str()));
    }
    */
  } // for
  
  Serial.println("LedMode=" + String(LedMode));
  if (LedMode == LED_MODE_ON) {		// LED_MODE_ON
    digitalWrite(PIN_LED, HIGH);

    // create ON_FILE
    File f = SPIFFS.open(ON_FILE, "w");
    f.close();

    CountOff = 0;

    /*
    delay(ON_MSEC);
    Serial.println("deep sleep " + String(DEEP_SLEEP_MSEC_ON) + " msec ..");
    Serial.println();
    esp_deep_sleep(DEEP_SLEEP_MSEC_ON * 1000LL);
    */
    // digitalWrite(PIN_LED, LOW);
    //LedMode = LED_MODE_OFF;

  } else {				// LED_MODE_OFF
    digitalWrite(PIN_LED, LOW);

    SPIFFS.remove(ON_FILE);

    CountOff++;
    Serial.println("CountOff=" + String(CountOff));
    if (CountOff > COUNTOFF_MAX) {
      Serial.println("deep sleep " + String(DEEP_SLEEP_MSEC_OFF) + " msec ..");
      esp_deep_sleep(DEEP_SLEEP_MSEC_OFF * 1000LL);
    }
  }
}
