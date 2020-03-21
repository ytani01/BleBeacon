# BleBeacon

## setup

```bash
$ cd
$ python3 -m venv env-ble
$ . ./env-ble/bin/activate
(env-ble)$ pip install -U bluepy
(env-ble)$ sudo setcap 'cap_net_raw,cap_net_admin+eip' lib/python3.7/site-packages/bluepy/bluepy-helper
(env-ble)$ ~/env-ble/lib/python3.7/site-packages/bluepy/bluepy-helper 0
# ...
le on
rsp=$mgmt code=$success
quit
(env-ble)$ sudo systemctl restart bluetooth.service
```


## bluepyの罠？

* scanの間隔が難しい：短すぎると見つからない。長すぎるとエラー。(5～10秒？)

* scan中に(handleDiscoveryで)、詳細情報を取得しようとすると、
scanがエラー終了することがある。
connectのリトライは1回まで？

* Peripheralへのconnectが不安定：リトライが必要

* getCharacteristics も不安定：リトライが必要

* Characteristics の read も不安定：リトライが必要

* 以上のリトライ処理をしても失敗することがある。


## pyblenoの罠

* ``Bleno.startAdvertising(name, uuids)``のnameは、
<Shortened local name>(0x08)。
<Complete local name>(0x09)には、何も入らない。

* ``ManufacturerData``を設定する関数がない。

## ESP32 BLEの罠

* ``BLEAdvertisedDevice``の``getName()``は、
<Complete local name>(0x09)。
<Shortened local name>(0x08)は取得できない。


## Reference

### BLE
* [BLE Docs](https://sites.google.com/a/gclue.jp/ble-docs/advertising-1/advertising)

* [bluetooth公式(定義済UUIDなど)](https://www.bluetooth.com/specifications/gatt/services/)

* [codes for distinct appearances](https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.gap.appearance.xml)


### ESP32

* [Arduino core for the ESP32](https://github.com/espressif/arduino-esp32)

* [ESP32による近距離無線通信の実験（2）BLE通信](http://marchan.e5.valueserver.jp/cabin/comp/jbox/arc212/index212.html)


### bluepy

* [bluepy](https://github.com/IanHarvey/bluepy)

* [bluepyで始めるBluetooth Low Energy(BLE)プログラミング](https://www.ipride.co.jp/blog/2510)

* [Bluetoothl-Low-Energy入門講座-part1](https://www.slideshare.net/edy555/ble-deospart1)

* [RPi Bluetooth LE](https://www.elinux.org/RPi_Bluetooth_LE)


### pybleno

* [pybleno](https://github.com/Adam-Langley/pybleno)


### SwitchBot

* [OpenWonderLabs](https://github.com/OpenWonderLabs/python-host/wiki/Meter-BLE-open-API)
