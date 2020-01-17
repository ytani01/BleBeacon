#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
BLE Beacon
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import bluepy
import time
from MyLogger import get_logger


class BleBeacon:
    def __init__(self, scanner=None, addr_hdr=None, data_keyword=None,
                 debug=False):
        self._debug = debug
        self._lg = get_logger(__class__.__name__, self._debug)
        self._lg.debug('scanner=%s, addr_hdr=%s, data_keyword=%s',
                       scanner, addr_hdr, data_keyword)

        self._scanner = scanner
        self._addr_hdr = addr_hdr
        self._data_keyword = data_keyword

        if self._scanner is None:
            self._scanner = bluepy.btle.Scanner(0)
            self._lg.debug('_scanner=%s', self._scanner)

    def scan(self, sec=5):
        self._lg.debug('sec=%s', sec)

        devs = self._scanner.scan(sec)

        for dev in devs:
            if self._addr_hdr is not None:
                if not dev.addr.startswith(self._addr_hdr):
                    continue

            self._lg.debug('addr=%s', dev.addr)

            for (adtype, desc, val) in dev.getScanData():
                if self._data_keyword is not None:
                    if desc != self._data_keyword:
                        continue

                batt_str     = val[8:10]
                temp_str     = val[10:14]
                humidity_str = val[14:18]
                self._lg.debug('batt_str=%s, temp_str=%s, humidity_str=%s',
                               batt_str, temp_str, humidity_str)

                batt_val = int(batt_str, 16) / int('64', 16)
                temp_val = self.hexstr2float(temp_str)
                humidity_val = self.hexstr2float(humidity_str)
                self._lg.debug('batt=%d %%, temp=%.1f C, humidity=%d %%',
                               round(batt_val*100),
                               temp_val, int(humidity_val))


class MMBLEBC2:
    ADDR_HDR = 'ac:23:3f:'
    DATA_KEYWORD = '16b Service Data'

    def __init__(self, scanner=None, debug=False):
        self._debug = debug
        self._lg = get_logger(__class__.__name__, self._debug)
        self._lg.debug('scanner=%s', scanner)

        self._scanner = scanner
        if self._scanner is None:
            self._scanner = bluepy.btle.Scanner(0)
            self._lg.debug('_scanner=%s', self._scanner)

    def scan(self, sec=5):
        self._lg.debug('sec=%s', sec)

        devs = self._scanner.scan(sec)

        for dev in devs:
            """
            if not dev.addr.startswith(self.ADDR_HDR):
                continue
            """

            self._lg.debug('addr=%s', dev.addr)

            for (adtype, desc, val) in dev.getScanData():
                self._lg.debug('%s: %s', desc, val)
                print('%s %s:%s.' % (dev.addr, desc, val))
                """
                if desc == self.DATA_KEYWORD:
                    batt_str     = val[8:10]
                    temp_str     = val[10:14]
                    humidity_str = val[14:18]
                    self._lg.debug('batt_str=%s, temp_str=%s, humidity_str=%s',
                                   batt_str, temp_str, humidity_str)

                    batt_val = int(batt_str, 16) / int('64', 16)
                    temp_val = self.hexstr2float(temp_str)
                    humidity_val = self.hexstr2float(humidity_str)
                    self._lg.debug('batt=%d %%, temp=%.1f C, humidity=%d %%',
                                   round(batt_val*100),
                                   temp_val, int(humidity_val))
                """
            print()

    def hexstr2float(self, val_str):
        self._lg.debug('val_str=%s', val_str)

        val = int(val_str[0:2], 16)
        val += int(val_str[2:3], 16) / 16.0
        val += int(val_str[3:4], 16) / 256.0
        self._lg.debug('val=%s', val)

        return val


class App:
    def __init__(self, debug=False):
        self._debug = debug
        self._lg = get_logger(__class__.__name__, self._debug)
        self._lg.debug('')

        self._bledev = MMBLEBC2(debug=self._debug)

    def main(self):
        self._lg.debug('')
        while True:
            self._bledev.scan(5)
            time.sleep(0.1)

    def end(self):
        self._lg.debug('')


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
