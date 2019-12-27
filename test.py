#!/usr/bin/env python3

'''
from bluepy.btle import Peripheral, DefaultDelegate, Scanner, BTLEException, UUID
'''
from bluepy.btle import DefaultDelegate, Scanner, BTLEException
import bluepy.btle
import time
# import sys

from MyLogger import get_logger

class ScanDelegate(DefaultDelegate):
    ADDR_HDR = 'ac:23:3f:'
    DATA_KEYWORD = '16b Service Data'

    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        super().__init__()

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        '''
        self._logger.debug('scanEntry=%s', scanEntry)
        self._logger.debug('isNewDev=%s, isNewData=%s',
                           isNewDev, isNewData)
        print(time.strftime("%Y-%m-%d %H:%M:%s", time.gmtime()),
              scanEntry.addr, scanEntry.getScanData())
        sys.stdout.flush()
        '''
        addr = scanEntry.addr
        # self._logger.debug('addr=%s', addr)

        if not addr.startswith(self.ADDR_HDR):
            return

        scan_data = scanEntry.getScanData()
        # self._logger.debug('scan_data=%s', scan_data)

        for a in scan_data:
            if a[1] == self.DATA_KEYWORD:
                data_str = a[2]
                self._logger.debug('data_str=%s', data_str)

                batt_str = data_str[8:10]
                temp_str = data_str[10:14]
                humidity_str = data_str[14:18]
                self._logger.debug('batt_str=%s, temp_str=%s, humidity_str=%s',
                                   batt_str, temp_str, humidity_str)

                batt_val = int(batt_str, 16) / int('64', 16)
                self._logger.debug('batt_val=%s', batt_val)

                temp_val = self.hexstr2float(temp_str)
                humidity_val = self.hexstr2float(humidity_str)

                self._logger.info('%.1f C, %.1f %%', temp_val, humidity_val)

    def hexstr2float(self, val_str):
        self._logger.debug('val_str=%s', val_str)

        val = int(val_str[0:2], 16)
        val += int(val_str[2:3], 16) / 16.0
        val += int(val_str[3:4], 16) / 256.0
        self._logger.debug('val=%s', val)

        return val


class App(DefaultDelegate):
    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        delegate = ScanDelegate(debug=debug)
        self._scanner = Scanner().withDelegate(delegate)

    def main(self):
        self._logger.debug('')
        while True:
            self.scan(5.0)
            time.sleep(0.1)

    def end(self):
        self._logger.debug('')

    def scan(self, sec):
        self._logger.debug('sec=%s', sec)
        try:
            self._scanner.scan(sec, passive=True)
        except Exception as e:
            msg = '%s:%s' % (type(e), e)
            self._logger.warning(msg)


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
