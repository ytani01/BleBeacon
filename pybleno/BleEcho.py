#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
from BlePeripheral import BlePeripheral, BleService, BleCharacteristic
from BlePeripheral import BlePeripheralApp
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class BleEcho(BlePeripheral):
    MY_NAME = 'BleEcho'

    _log = get_logger(__name__, False)

    def __init__(self, name=MY_NAME, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('name=%s', name)

        self._name = name

        self._chara1 = EchoCharacteristic(debug=self._dbg)
        self._svc1 = EchoService(charas=[self._chara1],
                                 debug=self._dbg)

        super().__init__(self._name, [self._svc1], debug=self._dbg)


class EchoService(BleService):
    UUID = 'ec00'

    _log = get_logger(__name__, False)

    def __init__(self, uuid=UUID, charas=[], debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s', uuid)

        super().__init__(uuid, charas, debug=self._dbg)


class EchoCharacteristic(BleCharacteristic):
    UUID = 'ec0F'

    _log = get_logger(__name__, False)

    def __init__(self, uuid=UUID, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s', uuid)

        super().__init__(uuid, ['read', 'write', 'notify'],
                         debug=debug)


class BleEchoApp(BlePeripheralApp):
    def __init__(self, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._ble = BleEcho(debug=self._dbg)


@click.command(context_settings=CONTEXT_SETTINGS, help='')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(debug):
    log = get_logger(__name__, debug)

    app = BleEchoApp(debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('done')


if __name__ == '__main__':
    main()
