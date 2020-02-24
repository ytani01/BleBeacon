# setup

```bash
$ cd
$ python3 -m venv env-ble
$ . ./env-ble/bin/activate
(env-ble)$ pip install -U bluepy
(env-ble)$ sudo setcap 'cap_net_raw,cap_net_admin+eip' lib/python3.7/site-packages/bluepy/bluepy-helper
(env-ble)$ ./env-ble/lib/python3.7/site-packages/bluepy/bluepy-helper 0
# ...
le on
rsp=$mgmt code=$success
quit
(env-ble)$
```

# Reference

  * [ ] bluepy
  * [ ] https://ambidata.io/samples/temphumid/ble_gw/

