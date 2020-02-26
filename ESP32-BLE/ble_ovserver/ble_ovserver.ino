/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface

#define SERIAL_SPEED   115200          // SERIAL通信速度

#define DEV_NAME "ESP32"         // 対象デバイス名
#define MAX_DEVICES  32              // 最大デバイス数
#define ManufacturerId 0xffff       // 既定のManufacturer ID
const int scanning_time = 3;        // スキャン時間（秒）
BLEScan* pBLEScan;                  // Scanオブジェクトへのポインター
int prev_seq[MAX_DEVICES] = {
  -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1
};

/* 受信データ構造体 */
struct tmpData {
    int     dev_number;          // デバイス識別番号
    bool    abnormal;               // デバイス異常
    int     seq_number;             // シーケンス番号
    float   temperature;            // 温度
    float   humidity;               // 湿度
};

/* LEDピン */
const int ledPin = 2;              // LEDの接続ピン

/* プッシュボタン */
const int buttonPin = 32;           // プッシュボタンの接続ピン

/*****************************************************************************
 *                          Predetermined Sequence                           *
 *****************************************************************************/
void setup() {
    doInitialize();                             // 初期化処理をして
    BLEDevice::init("");                        // BLEデバイスを作成する
    Serial.println("Client application start...");
    pBLEScan = BLEDevice::getScan();            // Scanオブジェクトを取得して、
    pBLEScan->setActiveScan(false);             // パッシブスキャンに設定する
}

void loop() {
    struct tmpData td;

    BLEScanResults foundDevices = pBLEScan->start(scanning_time);
    int count = foundDevices.getCount();

    for (int i = 0; i < count; i++) {
        BLEAdvertisedDevice dev = foundDevices.getDevice(i);
	std::string dev_addr = dev.getAddress().toString();
        std::string dev_name = dev.getName();

        Serial.print(dev.toString().c_str());

        /*
	Serial.print(dev_addr.c_str());
	Serial.print(" ");
  	Serial.print(dev_name.c_str());
	Serial.print(" ");

	std::string dev_svcdata = dev.getServiceData();
	String s = dev_svcdata.c_str();
        Serial.print(s);
        */
        
        /*
	for (int j = 0; j < dev_svcdata.size(); j++) {
	  Serial.print(sprintf("%02X ", (const char)s[j]));
	}
        */
	
        if (dev_name == DEV_NAME && dev.haveManufacturerData()) {
            std::string data = dev.getManufacturerData();
            Serial.print(" / data=");

            for (int i=0; i < data.length(); i++) {
              Serial.print(data[i]);
            }
            Serial.print(" / ");
            Serial.print(data.c_str());
        }

        Serial.println();
    } // for
    Serial.println();

    // プッシュボタン押下でLEDを消灯してディスプレイ表示を消去する
    int buttonState = digitalRead(buttonPin);
    if (buttonState == HIGH) {
        digitalWrite(ledPin, LOW);
    }
}

/*  初期化処理  */
void doInitialize() {
    Serial.begin(SERIAL_SPEED);
    pinMode(buttonPin, INPUT);        // GPIO設定：プッシュボタン        
    pinMode(ledPin, OUTPUT);          // GPIO設定：LED
    digitalWrite(ledPin, LOW);

    Serial.println("BLE Client start ...");
}

/*****************************< Other functions >*****************************/
/* 受信データを表示する */
void displayData(struct tmpData* td) {
    char sTemp[10], sHumd[10];
    sprintf(sTemp, "%5.2fC", td->temperature);
    sprintf(sHumd, "%5.2f%%", td->humidity);
    Serial.print("Received from device ");  Serial.print(td->dev_number);
    Serial.print("  Data No.");             Serial.print(td->seq_number);
    Serial.print("  Temperature: ");        Serial.print(sTemp);
    Serial.print(",  Humidity: ");          Serial.println(sHumd);
}

/* デバイス異常を表示する */
void displayAlarm(struct tmpData* td) {
    Serial.print("*Device error No.");   Serial.println(td->dev_number);
    digitalWrite(ledPin, HIGH);
    char device[10];
    sprintf(device, "  (%d)", td->dev_number);
}
