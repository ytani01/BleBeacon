#!/usr/bin/env python3

from pybleno import Bleno, BlenoPrimaryService, Characteristic
import time
import click
from MyLogger import get_logger


class BleEcho:
    MY_NAME = 'echo'
    UUID_SERVICE1 = 'ec00'
    UUID_CHARACTERISTIC1 = 'ec0F'

    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._bleno = Bleno()
        self._bleno.on('stateChange', self.onStateChange)
        self._bleno.on('advertisingStart', self.onAdvertisingStart)

    def start(self):
        self._log.debug('')
        self._bleno.start()

    def end(self):
        self._log.debug('')
        self._bleno.stopAdvertising()
        self._bleno.disconnect()

    def onStateChange(self, state):
        self._log.debug('state=%s', state)

        if (state == 'poweredOn'):
            self._bleno.startAdvertising(self.MY_NAME, [
                self.UUID_SERVICE1
            ])
        else:
            self._bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        self._log.debug('error=%s', error)

        chara = EchoCharacteristic(self.UUID_CHARACTERISTIC1, debug=self._dbg)
        svc = BlenoPrimaryService({'uuid': self.UUID_SERVICE1,
                                   'characteristics': [chara]})
        if not error:
            self._bleno.setServices([svc])


class EchoCharacteristic(Characteristic):
    def __init__(self, uuid, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s', uuid)

        super().__init__({
            'uuid': uuid,
            'properties': ['read', 'write', 'notify'],
            'value': None
        })

        self._value = ''
        self._updateValueCallback = None

    def onReadRequest(self, offset, callback):
        self._log.debug('offset=%s', offset)
        self._log.debug('_value=%s', self._value)

        callback(Characteristic.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._log.debug('data=%s', data)

        self._value = data

        if self._updateValueCallback:
            self._log.info('notifying')
            self._updateValueCallback(self._value)

        callback(Characteristic.RESULT_SUCCESS)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('onSubscribe')
        self._log.debug('maxValueSize=%s', maxValueSize)
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        self._log.debug('')
        self._updateValueCallback = None


class App:
    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._ble_echo = BleEcho(debug=self._dbg)

    def main(self):
        self._log.debug('')

        self._ble_echo.start()

        while True:
            time.sleep(10)

    def end(self):
        self._log.debug('')
        self._ble_echo.end()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(debug):
    log = get_logger(__name__, debug)

    app = App(debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('done')


if __name__ == '__main__':
    main()
