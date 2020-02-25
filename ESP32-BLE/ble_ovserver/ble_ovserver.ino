/*
 * -*- coding: utf-8 -*-
 */
#include <BLEDevice.h>
#include <Wire.h>                   // I2C interface

/* 基本属性定義  */
#define SERIAL_SPEED   115200          // SERIAL通信速度

/* スキャン制御用 */
#define DEV_NAME "ESP32"         // 対象デバイス名
#define MAX_DEVICES  32              // 最大デバイス数
#define ManufacturerId 0xffff       // 既定のManufacturer ID
const int scanning_time = 5;        // スキャン時間（秒）
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

    for (int i = 0; i < count; i++) {     // 受信したアドバタイズデータを調べて
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
	Serial.println();
	continue;
	
        if (dev_name == DEV_NAME 
                && dev.haveManufacturerData()) {   // デバイス名が一致しManufacturer dataがあって
            std::string data = dev.getManufacturerData();
            int manu_code = data[1] << 8 | data[0];
            int dev_number = data[2];
            int seq_number = data[4];

            // デバイス識別番号が有効かつシーケンス番号が更新されていたら
            if (dev_number >= 1 && dev_number <= MAX_DEVICES
                      && seq_number != prev_seq[dev_number - 1]) {
                // 受信データを取り出す
                prev_seq[dev_number - 1] = seq_number;
                td.dev_number = dev_number;
                td.abnormal = (bool)data[3];
                td.seq_number = seq_number;
                td.temperature = (float)(data[6] << 8 | data[5]) / 100.00;
                td.humidity = (float)(data[8] << 8 | data[7]) / 100.00;
                if (!td.abnormal) {
                    displayData(&td);
                } else {
                    displayAlarm(&td);
                }
            }
        }
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
