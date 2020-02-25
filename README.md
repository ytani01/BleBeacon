# setup

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


# Reference

* [Arduino core for the ESP32](https://github.com/espressif/arduino-esp32)
* [ESP32による近距離無線通信の実験（2） BLE通信](http://marchan.e5.valueserver.jp/cabin/comp/jbox/arc212/index212.html)
* [BLE環境センサー・ゲートウェイ(Raspberry Pi編)](https://ambidata.io/samples/temphumid/ble_gw/)

