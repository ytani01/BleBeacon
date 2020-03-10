#! /usr/bin/env python3

from pybleno import Bleno, Characteristic, BlenoPrimaryService
import time

FOO_SERVICE_UUID = '13A28130-8883-49A8-8BDB-42BC1A7107F4'
FOO_CHARACTERISTIC_UUID = 'A2935077-201F-44EB-82E8-10CC02AD8CE1'


class FooCharacteristic(Characteristic):

    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': FOO_CHARACTERISTIC_UUID,
            'properties': ['read', 'notify'],
            'value': None
        })

        self._value = 0
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        print('onReadRequest:value=%s' % (self._value))
        callback(Characteristic.RESULT_SUCCESS, self._value)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('FooCharacteristic - onSubscribe')

        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('FooCharacteristic - onUnsubscribe')

        self._updateValueCallback = None


def onStateChange(state):
    print('on -> stateChange: ' + state)

    if (state == 'poweredOn'):
        bleno.startAdvertising('Foo', [FOO_SERVICE_UUID])
    else:
        bleno.stopAdvertising()


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + (
        'error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': FOO_SERVICE_UUID,
                'characteristics': [
                    fooCharacteristic
                ]
            })
        ])


counter = 0


def task():
    global counter
    counter += 1
    fooCharacteristic._value = counter
    if fooCharacteristic._updateValueCallback:

        print('Sending notification with value : ' + str(
            fooCharacteristic._value))

        notificationBytes = str(fooCharacteristic._value).encode()
        fooCharacteristic._updateValueCallback(notificationBytes)


bleno = Bleno()
fooCharacteristic = FooCharacteristic()
bleno.on('stateChange', onStateChange)
bleno.on('advertisingStart', onAdvertisingStart)
bleno.start()

while True:
    task()
    time.sleep(1)
