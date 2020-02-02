#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from bluepy.btle import DefaultDelegate, Scanner, BTLEException
import bluepy.btle
import time
import click
from MyLogger import get_logger


class ScanDelegate(DefaultDelegate):
    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        self._addr = {}

        super().__init__()

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        #self._logger.debug('scanEntry=%s, isNewDev=%s, isNewData=%s',
        #                   scanEntry, isNewDev, isNewData)

        addr = scanEntry.addr
        scan_data = scanEntry.getScanData()

        for (ad_type, ad_desc, ad_value) in scan_data:
            #self._logger.debug('%3s,%s,%s', ad_type, ad_desc, ad_value)
            if 'MyESP' in ad_value:
                print('%s %s: %s.' % (addr, ad_desc, ad_value))

                peri = bluepy.btle.Peripheral()
                try:
                    ret = peri.connect(addr)
                    # peri.connect(addr, bluepy.btle.ADDR_TYPE_RANDOM)
                    print('connect:ret=', ret)
                    time.sleep(5)
                    ret = peri.disconnect()
                    print('disconnect:ret=', ret)
                except Exception as e:
                    print('%s:%s.' % (type(e), e))
                    return

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
            self._scanner.scan(sec, passive=False)
        except Exception as e:
            msg = '%s:%s' % (type(e), e)
            self._logger.warning(msg)


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
