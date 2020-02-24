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
    def __init__(self, addrq, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        self.addrq = addrq

        self.p_addr = ''
        self.p_addr_type = ''

        super().__init__()

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        # self._logger.debug('scanEntry=%s, isNewDev=%s, isNewData=%s',
        #                    scanEntry, isNewDev, isNewData)
        #self._logger.debug('ScanData=%s', scanEntry.getScanData())
        
        if not self.addrq.empty():
            return

        addr = scanEntry.addr
        addr_type = scanEntry.addrType
        scan_data = scanEntry.getScanData()
        for (ad_type, ad_desc, ad_value) in scan_data:
            if 'MyESP' in ad_value:
                self._logger.debug('%s(%s)', addr, addr_type)
                self._logger.debug('%3s,%s,%s', ad_type, ad_desc, ad_value)

                self.addrq.put((addr, addr_type))

                return

    def hexstr2float(self, val_str):
        self._logger.debug('val_str=%s', val_str)

        val = int(val_str[0:2], 16)
        val += int(val_str[2:3], 16) / 16.0
        val += int(val_str[3:4], 16) / 256.0
        self._logger.debug('val=%s', val)

        return val


class App:
    DST_UUID = 'beb5483e-36e1-4688-b7f5-ea07361b26a8'

    def __init__(self, cmd, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('cmd=%s', cmd)

        self.cmd = cmd

        self.addrq = queue.Queue()
        self._delegate = ScanDelegate(self.addrq, debug=self._debug)
        self._scanner = Scanner().withDelegate(self._delegate)

    def main(self):
        self._logger.debug('')

        while True:
            if self.addrq.empty():
                try:
                    self._logger.info('scanning..')
                    self._scanner.scan(1, passive=False)
                except Exception as e:
                    msg = '%s:%s' % (type(e), e)
                    self._logger.error(msg)
                    return

            time.sleep(.5)

            if not self.addrq.empty():
                (addr, addr_type) = self.addrq.get()
                self.addrq.put((addr, addr_type))
                self._logger.info('addr=%s(%s)', addr, addr_type)

                while True:
                    try:
                        self._logger.info('connecting..')
                        peri = bluepy.btle.Peripheral(addr, addr_type)
                        self._logger.info('connected')
                        break

                    except Exception as e:
                        self._logger.error('%s:%s.', type(e), e)
                        self._logger.info('retry!')
                    finally:
                        time.sleep(.1)

                try:
                    for svc in peri.getServices():
                        self._logger.debug('Svc UUID=%s', svc.uuid)
                        for chara in svc.getCharacteristics():
                            self._logger.debug('  Chara UUID=%s', chara.uuid)
                            handle = chara.getHandle()
                            self._logger.debug('    Handle=%s', handle)
                            props = chara.propertiesToString()
                            self._logger.debug('    Props =%s', props)

                            if chara.uuid == self.DST_UUID:
                                self._logger.info('CharaUUID=%s',
                                                  self.DST_UUID)
                                peri.writeCharacteristic(handle,
                                                         self.cmd.encode(
                                                             'utf-8'),
                                                         False)
                                time.sleep(1.5)

                            time.sleep(.1)

                except Exception as e:
                    msg = '%s:%s.' % (type(e), e)
                    peri.disconnect()
                else:
                    peri.disconnect()
                    self._logger.info('disconnected')
                    return

            self._delegate.p_addr = ''
            time.sleep(0.1)

    def end(self):
        self._logger.debug('')


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
