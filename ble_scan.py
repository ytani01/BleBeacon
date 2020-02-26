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


class BleDev:
    def __init__(self, scanner=None, addr_hdr=None, data_keyword=None,
                 debug=False):
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug('scanner=%s, addr_hdr=%s, data_keyword=%s',
                        scanner, addr_hdr, data_keyword)

        self._scanner = scanner
        self._addr_hdr = addr_hdr
        self._data_keyword = data_keyword

        if self._scanner is None:
            self._scanner = bluepy.btle.Scanner(0)
            self._log.debug('_scanner=%s', self._scanner)

    def scan(self, sec=5):
        self._log.debug('sec=%s', sec)

        devs = self._scanner.scan(sec)

        dev_count = 0;
        for dev in devs:
            if self._addr_hdr is not None:
                if not dev.addr.startswith(self._addr_hdr):
                    continue

            dev_count += 1
            print('(%02d)%s' % (dev_count, dev.addr))

            for (adtype, desc, val) in dev.getScanData():
                if self._data_keyword is not None:
                    if desc != self._data_keyword:
                        continue

                print('    %02X:%s: %s' % (adtype, desc, val))

        print('')


class App:
    def __init__(self, debug=False):
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug('')

        self._bledev = BleDev(debug=self._debug)

    def main(self):
        self._log.debug('')
        while True:
            self._bledev.scan(5)
            time.sleep(0.1)

    def end(self):
        self._log.debug('')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
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
