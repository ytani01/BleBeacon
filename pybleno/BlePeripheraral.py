#!/usr/bin/env python3
#
# usage:
#   sudo ./BlePeripheraral.py -d
#

from pybleno import Bleno, BlenoPrimaryService, Characteristic
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class BlePeripheral:
    def __init__(self, svcs=[], debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._svcs = svcs

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

        uuids = [u.UUID for u in self._svcs]
        self._log.debug('uuids=%s', uuids)

        if (state == 'poweredOn'):
            self._log.debug('address=%s', self._bleno.address)
            address = ':'.join(self._bleno.address.split(':')[::-1])
            self._log.debug('address=%s', address)
            
            self._bleno.startAdvertising(self.MY_NAME + '-' + address, uuids)
        else:
            self._bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        self._log.debug('error=%s', error)

        if not error:
            self._bleno.setServices(self._svcs)


class EchoCharacteristic(Characteristic):
    UUID = 'ec0F'

    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        super().__init__({
            'uuid': self.UUID,
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
        self._log.debug('data=%s, offset=%s', data, offset)

        self._value = data[offset:]
        self._log.debug('_value=%s', self._value)

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


class EchoService(BlenoPrimaryService):
    UUID = 'ec00'

    def __init__(self, charas=[], debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        # self._log.debug('charas=%s', charas)
        self._log.debug('')

        super().__init__({'uuid': self.UUID, 'characteristics': charas})


class BleEcho(BlePeripheral):
    MY_NAME = 'echo'
    #MY_NAME = 'b8:27:eb:c3:e1:7c'

    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._chara1 = EchoCharacteristic(debug=self._dbg)
        self._svc1 = EchoService([self._chara1], debug=self._dbg)

        super().__init__([self._svc1], debug=self._dbg)


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
