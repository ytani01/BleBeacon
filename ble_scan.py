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
import sys
import time
from MyLogger import get_logger


class BleDev:
    def __init__(self, scanner=None, addr_hdr=None, val_keyword=None,
                 debug=False):
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug('scanner=%s, addr_hdr=%s, val_keyword=%s',
                        scanner, addr_hdr, val_keyword)

        self._scanner = scanner
        self._addr_hdr = addr_hdr
        self._val_keyword = val_keyword

        if self._scanner is None:
            self._scanner = bluepy.btle.Scanner(0)
            self._log.debug('_scanner=%s', self._scanner)

    def scan(self, sec=5):
        self._log.debug('sec=%s', sec)

        devs = self._scanner.scan(sec)

        dev_count = 0
        for dev in devs:
            if self._addr_hdr is not None:
                if not dev.addr.startswith(self._addr_hdr):
                    continue

            dev_count += 1
            print('----------')
            print('|%02d|%s|%s|' % (dev_count, dev.addr, dev.addrType))
            sys.stdout.flush()

            # if dev.addrType != bluepy.btle.ADDR_TYPE_PUBLIC:
            #     continue

            conn_flag = False
            for (adtype, desc, val) in dev.getScanData():
                print(' |%02X|%s|%s|' % (adtype, desc, val))
                sys.stdout.flush()

                if self._val_keyword is not None:
                    if self._val_keyword in val:
                        conn_flag = True
                    else:
                        pass
                else:
                    conn_flag = True

            if conn_flag:
                try:
                    peri = bluepy.btle.Peripheral(dev.addr)
                    self._log.debug('connected')
                    sys.stdout.flush()

                    for svc in peri.getServices():
                        print('  |svc|%s|' % (svc.uuid))

                        desc = svc.getDescriptors()
                        """
                        for d in svc.getDescriptors():
                            print('   |desc|%s|%s|%s|' % (d.handle, d.uuid,
                                                          str(d)))
                        sys.stdout.flush()
                        """
                        for chara in svc.getCharacteristics():
                            print('   |chara|%s|' % chara.uuid)
                            print('    |handle    |%s|' % chara.getHandle())
                            print('    |properties|%s|' %
                                  chara.propertiesToString())
                            for d in desc:
                                if chara.uuid == d.uuid:
                                    print('    |%s|' % str(d))
                                    
                            sys.stdout.flush()

                    peri.disconnect()

                except bluepy.btle.BTLEDisconnectError as e:
                    self._log.error('%s:%s', type(e), e)
                    continue

                except Exception as e:
                    self._log.error('%s:%s', type(e), e)

        print('')


class App:
    DEF_SCAN_SEC = 3
    
    def __init__(self, val_keyword=None, debug=False):
        self._debug = debug
        self._log = get_logger(__class__.__name__, self._debug)
        self._log.debug('')

        self._bledev = BleDev(val_keyword=val_keyword, debug=self._debug)

    def main(self):
        self._log.debug('')
        while True:
            self._bledev.scan(self.DEF_SCAN_SEC)
            time.sleep(0.1)

    def end(self):
        self._log.debug('')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
''')
@click.option('--val_keyword', '-v', 'val_keyword', type=str, default=None,
              help="value keyword")
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(val_keyword, debug):
    logger = get_logger(__name__, debug)
    logger.debug('val_keyword=%s', val_keyword)

    logger.info('start')
    app = App(val_keyword=val_keyword, debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('end')


if __name__ == '__main__':
    main()
