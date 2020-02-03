#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from bluepy.btle import DefaultDelegate, Scanner
import bluepy.btle
import queue
import time
import click
from MyLogger import get_logger


class ScanDelegate(DefaultDelegate):
    DST_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'

    def __init__(self, app, cmd='', debug=False):
        self._debug = debug
        self._lg = get_logger(__class__.__name__, self._debug)
        self._lg.debug('cmd=%s', cmd)

        self._app = app
        self._cmd = cmd

        self.p_addr = ''
        self.p_addr_type = ''

        super().__init__()

    def handleNotification(self, handle, data):
        self._lg.debug('handle=%s, data=%s', handle, data)

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        self._lg.debug('')

        addr = scanEntry.addr
        addr_type = scanEntry.addrType

        scan_data = scanEntry.getScanData()
        for (ad_type, ad_desc, ad_value) in scan_data:
            if 'MyESP' not in ad_value:
                continue

            self._lg.debug('%s(%s)', addr, addr_type)
            self._lg.debug('%s,%s', ad_desc, ad_value)

            # time.sleep(3)

            while True:
                try:
                    self._lg.info('connecting..')
                    peri = bluepy.btle.Peripheral(addr, addr_type)
                    self._lg.info('connected')

                except bluepy.btle.BTLEDisconnectError as e:
                    self._lg.error('%s:%s.', type(e), e)
                    self._lg.info('retry!')
                    continue
                except Exception as e:
                    self._lg.error('%s:%s.', type(e), e)
                    return
                finally:
                    time.sleep(.1)

                for svc in peri.getServices():
                    self._lg.debug('Svc UUID=%s', svc.uuid)
                    for chara in svc.getCharacteristics():
                        self._lg.debug('  Chara UUID=%s', chara.uuid)
                        handle = chara.getHandle()
                        self._lg.debug('    Handle=%s', handle)
                        props = chara.propertiesToString()
                        self._lg.debug('    Props =%s', props)

                        if chara.uuid == self.DST_UUID:
                            self._lg.info('CharaUUID=%s', self.DST_UUID)
                            peri.writeCharacteristic(handle,
                                                     self._cmd.encode(
                                                         'utf-8'),
                                                     False)
                            self._lg.debug('write: done')
                            self._app._stat = 'done'

                            peri.disconnect()
                            return

                self._app._stat = 'continue'

                peri.disconnect()
                return

        self._app._stat = 'continue'


class App:
    def __init__(self, cmd, debug=False):
        self._debug = debug
        self._lg = get_logger(__class__.__name__, self._debug)
        self._lg.debug('cmd=%s', cmd)

        self._cmd = cmd

        self._stat = ''

        self._delegate = ScanDelegate(self, self._cmd,
                                      debug=self._debug)
        self._scanner = Scanner().withDelegate(self._delegate)

    def main(self):
        self._lg.debug('')

        while True:
            try:
                self._lg.info('scanning..')
                self._scanner.scan(.5, passive=False)
                self._lg.info('scan: done')
            except bluepy.btle.BTLEDisconnectError as e:
                msg = '%s:%s' % (type(e), e)
                self._lg.error(msg)
            except Exception as e:
                msg = '%s:%s' % (type(e), e)
                self._lg.error(msg)

            self._lg.debug('_stat=%s', self._stat)
            if self._stat == 'done':
                break

    def end(self):
        self._lg.debug('')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Beacon Scanner
''')
@click.argument('cmd')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(cmd, debug):
    logger = get_logger(__name__, debug)
    logger.debug('cmd=%s', cmd)

    logger.info('start')
    app = App(cmd, debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('end')


if __name__ == '__main__':
    main()
