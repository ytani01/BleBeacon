#!/usr/bin/env python3

from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
import bluepy.btle
import time
import sys

from MyLogger import get_logger

ADDR_HDR = 'ac:23:3f:'

class ScanDelegate(DefaultDelegate):
    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        super().__init__()

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        self._logger.debug('scanEntry=%s', scanEntry)
        self._logger.debug('isNewDev=%s, isNewData=%s',
                           isNewDev, isNewData)
        '''
        print(time.strftime("%Y-%m-%d %H:%M:%s", time.gmtime()),
              scanEntry.addr, scanEntry.getScanData())
        sys.stdout.flush()
        '''
        addr = scanEntry.addr
        self._logger.debug('addr=%s', addr)

        if not addr.startswith(ADDR_HDR):
            return

        scan_data = scanEntry.getScanData()
        self._logger.debug('scan_data=%s', scan_data)

        print(scan_data[2][2])


class App(DefaultDelegate):
    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        delegate = ScanDelegate(debug=debug)
        self._scanner = Scanner().withDelegate(delegate)

    def main(self):
        self._logger.debug('')
        self.scan(10.0)

    def end(self):
        self._logger.debug('')

    def scan(self, sec):
        self._logger.debug('sec=%s', sec)
        self._scanner.scan(sec, passive=True)


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Beacon Scanner
''')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(debug):
    logger = get_logger(__name__, debug)
    logger.debug('')

    logger.info('start')
    app = App(debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('end')


if __name__ == '__main__':
    main()
