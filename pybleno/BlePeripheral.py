#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
# usage:
#   sudo ./BlePeripheraral.py myname -d
#

from pybleno import Bleno, BlenoPrimaryService, Characteristic
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class BlePeripheral:
    _log = get_logger(__name__, False)

    def __init__(self, name, svcs=[], debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('name=%s', name)

        self._name = name
        self._svcs = svcs

        self._bleno = Bleno()
        self._bleno.on('stateChange', self.onStateChange)
        self._bleno.on('advertisingStart', self.onAdvertisingStart)

        self._address = None
        self._log.debug('_address=%s', self._address)

    def start(self):
        self._log.debug('')
        self._bleno.start()

    def end(self):
        self._log.debug('')
        self._bleno.stopAdvertising()
        self._bleno.disconnect()
        self._log.debug('done')

    def onStateChange(self, state):
        self._log.debug('state=%s', state)

        uuids = [u.UUID for u in self._svcs]
        self._log.debug('service uuids=%s', uuids)

        if (state == 'poweredOn'):
            # reverse MAC address
            self._address = ':'.join(
                self._bleno.address.split(':')[::-1]
            )
            self._log.debug('_address=%s', self._address)

            self._log.info('start Advertising(%s) ..', self._name)
            self._bleno.startAdvertising(self._name, uuids)
        else:
            self._log.info('stop Advertising ..')
            self._bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        self._log.debug('error=%s', error)

        if not error:
            self._bleno.setServices(self._svcs)


class BleService(BlenoPrimaryService):
    _log = get_logger(__name__, False)

    def __init__(self, uuid, charas=[], debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s', uuid)

        self._uuid = uuid
        self._charas = charas

        super().__init__({
            'uuid': self._uuid,
            'characteristic': self._charas
        })


class BleCharacteristic(Characteristic):
    _log = get_logger(__name__, False)

    def __init__(self, uuid, properties=[], debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s, properties=%s', uuid, properties)

        self._uuid = uuid
        self._properties = properties

        super().__init__({
            'uuid': self._uuid,
            'properties': self._properties,
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
        self._log.debug('maxValueSize=%s', maxValueSize)
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        self._log.debug('')
        self._updateValueCallback = None


class BlePeripheralApp:
    _log = get_logger(__name__, False)

    def __init__(self, name, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('name=%s', name)

        self._name = name

        self._ble = BlePeripheral(self._name, debug=self._dbg)

    def main(self):
        self._log.debug('')

        self._ble.start()

        while True:
            time.sleep(10)

    def end(self):
        self._log.debug('')
        self._ble.end()
        self._log.debug('done')


@click.command(context_settings=CONTEXT_SETTINGS, help='')
@click.argument('name', type=str)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(name, debug):
    log = get_logger(__name__, debug)

    app = BlePeripheralApp(name, debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('done')


if __name__ == '__main__':
    main()
