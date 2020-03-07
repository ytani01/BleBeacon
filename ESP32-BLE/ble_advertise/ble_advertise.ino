/*
 * by Yoichi Tanibayashi
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


void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  LedMode = MODE_BLINK;

  Serial.print("Start:");
  Serial.println(MY_NAME);
  digitalWrite(LED_PIN, LED_ON);
  Serial.println(String(sizeof(DevID)/sizeof(DevID[0])));

  // init device
  BLEDevice::init("aaaaa");
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
}

void loop() {
  static char buf[32];
  String buf_str;
  static int buf_i = 0;
  int ch;
  static bool eol = false;
  static bool num = true;

  eol = false;
  while (Serial.available() > 0) {
    ch = Serial.read();
    Serial.println("ch=" + String(ch, HEX));
    if (ch == -1) {
      break;
    }
    if (ch == '\r' || ch == '\n') {
      ch = NULL;
      eol = true;
    }
      
    buf[buf_i++] = ch;
    if (ch == NULL) {
      buf_i = 0;
      break;
    }
  } // while

  if (eol) {
    buf_str = String(buf);
    Serial.println("buf=" + buf_str + ".");
    eol = false;

    if (buf[0] != NULL) {
      if (buf_str != "all") {
        if (buf_str.length() != MyAddr.toString().length()) {
          bool num = true;
          for (int i=0; i < buf_str.length(); i++) {
            if (! isDigit(buf_str[i])) {
              num = false;
              break;
            }
          }
          if (num) {
            int idx = buf_str.toInt();
            buf_str = DevID[idx];
          } else {
            buf_str = "xxx";
          }
        }
      }
    
      pAdvertising->stop();
      delay(500);

      BLEAdvertisementData oAdvertisementData = BLEAdvertisementData();
      oAdvertisementData.setName(MY_NAME);
      oAdvertisementData.setFlags(0x06);
      oAdvertisementData.setManufacturerData(buf_str.c_str());

      pAdvertising->setAdvertisementData(oAdvertisementData);
      pAdvertising->start();
      
      Serial.println(oAdvertisementData.getPayload().c_str());
    }
  } // if (eol)

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
