#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
BLE Beacon
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from bluepy import btle
import time
import binascii
from MyLogger import get_logger


class ScanDelegate(btle.DefaultDelegate):
    _log = None

    def __init__(self, ble_scan, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._ble_scan = ble_scan

    def handleDiscovery(self, dev, isNewDev, isNewData):
        self._log.debug('isNewDev=%s, isNewData=%s', isNewDev, isNewData)

        self._ble_scan.devs.append(dev)

        name = ''
        for (adtype, desc, val) in dev.getScanData():
            if 'Local Name' in desc:
                name = val
        self._ble_scan.dev_name[str(dev.addr)] = name

        print('Device ', end='')
        if name != '':
            print('"%s" ' % (name), end='')
        print('[%s](%s) %s dBm connectable:%s' %
              (dev.addr, dev.addrType, dev.rssi, dev.connectable))


class BleScan:
    _log = None

    def __init__(self, hci=0, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('hci=%s', hci)

        self._hci = hci

        self._delegate = ScanDelegate(self, debug=self._dbg)
        self._scanner = btle.Scanner(self._hci).withDelegate(self._delegate)

        self.devs = []
        self.dev_name = {}

    @classmethod
    def dump_dev(cls, dev, indent=4):
        cls._log.debug('indent=%d', indent)

        indent_str = ' ' * indent

        for (adtype, desc, val) in dev.getScanData():
            # print('%s%3d:%s: "%s"' % (indent_str, adtype, desc, val))
            print('%s%s: "%s"' % (indent_str, desc, val))
        if not dev.scanData:
            print('%s(no data)' % (indent_str))

    @classmethod
    def dump_svc(cls, peri, indent=2):
        cls._log.debug('indent=%d', indent)

        indent_str = ' ' * indent

        svcs = sorted(peri.services, key=lambda s: s.hndStart)
        for i, s in enumerate(svcs):
            # print('%s%3d:Service[%s]' % (indent_str, i, s.uuid))
            print('%sService [%s]' % (indent_str, s.uuid))
            cls.dump_chara(s, chara_retry=5, indent=indent+2)

    @classmethod
    def dump_chara(cls, svc, chara_retry=5, indent=8):
        cls._log.debug('chara_retry=%d, indent=%d',
                       chara_retry, indent)

        indent_str = ' ' * indent

        count = 0
        while count < chara_retry:
            try:
                chara = svc.getCharacteristics()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                cls._log.warning('%s:%s', type(e), e)
                raise e
            except Exception as e:
                cls._log.warning('%s:%s', type(e), e)
                time.sleep(1)
                count += 1

        if count >= 0:  # failed
            print('%s(getCharacteristics: failed)' % (indent_str))
            raise RuntimeError

        for i, c in enumerate(chara):
            # print('%s%3d:%s' % (indent_str, i, c))
            print('%s%s' % (indent_str, c))
            print('%s  Properties: %s' %
                  (indent_str, c.propertiesToString()))

            if c.supportsRead():
                cls.chara_read(c, retry=5, indent=indent+2)

    @classmethod
    def chara_read(cls, chara, retry=5, indent=10):
        cls._log.debug('retry=%d, indent=%d', retry, indent)

        indent_str = ' ' * indent

        count = 0
        while count < retry:
            try:
                val = chara.read()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                cls._log.warning('%s:%s', type(e), e)
                raise e
            except Exception as e:
                cls._log.warning('%s:%s', type(e), e)
                time.sleep(1)
                count += 1

        if count >= 0:  # read failed
            print('%s(read: failed)', indent_str)
            raise RuntimeError

        val_str1 = ''
        val_str2 = ''
        if chara.uuid == btle.AssignedNumbers.device_name:
            val_str1 = '"' + val.decode('utf-8') + '"'
        elif chara.uuid == btle.AssignedNumbers.device_information:
            val_str1 = '|' + repr(val) + '|'
        else:
            val_str1 = '%a' % val
            # val_str2 = '<' + binascii.b2a_hex(val).decode('utf-8') + '>'
            s = binascii.b2a_hex(val).decode('utf-8')
            val_str2 = ' '.join([s[i:i+2] for i in range(0, len(s), 2)])
            val_str2 = '<' + val_str2 + '>'

        print('%sValue: %s' % (indent_str, val_str1))
        if val_str2 != '':
            print('%s       %s' % (indent_str, val_str2))

    def scan(self, timeout=5):
        self._log.debug('timeout=%s', timeout)

        print('=====< Scan start >=====')
        devs = self._scanner.scan(timeout)
        print('=====< Scan end >=====')
        return devs

    def scan_svc(self, devs, conn_retry=1):
        self._log.debug('conn_retry=%s', conn_retry)

        if conn_retry < 1:
            self._log.warning('conn_retry=%s .. ??', conn_retry)
            return

        for i, d in enumerate(devs):
            # print('%3d:Device ' % (i), end='')
            print('Device ', end='')

            name = self.dev_name[d.addr]
            if name != '':
                print('"%s" ' % (name), end='')

            print('[%s](%s) connectable:%s %s dBm' %
                  (d.addr, d.addrType, d.connectable, d.rssi))

            self.dump_dev(d, indent=4)

            if not d.connectable:
                print('')
                continue

            count = 0  # < 0: OK
            while count < conn_retry:
                try:
                    with btle.Peripheral(d) as peri:
                        print('    ===< Connection: OK .. %d/%d >===' %
                              (count + 1, conn_retry))
                        self.dump_svc(peri, indent=2)
                        count = -1
                    break
                except btle.BTLEDisconnectError as e:
                    self._log.debug('%s:%s', type(e), e)
                    print('    ===< Connection: NG .. %d/%d >===' %
                          (count + 1, conn_retry))
                    count += 1
                except Exception as e:
                    self._log.warning('%s:%s', type(e), e)
                    print('    ===< Connection: NG .. %d/%d >===' %
                          (count + 1, conn_retry))
                    count += 1

            print('')

    def end(self):
        self._log.debug('')


class App:
    _log = None

    def __init__(self, hci=0, timeout=5, conn_retry=0, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('hci=%s, timeout=%s', hci, timeout)

        self._hci = hci
        self._timeout = timeout
        self._conn_retry = conn_retry

        self._ble_scan = BleScan(self._hci, debug)

    def main(self):
        self._log.debug('')

        devs = self._ble_scan.scan(self._timeout)
        devs2 = self._ble_scan.devs
        self._log.debug('len(devs)=%d, len(dev2)=%d', len(devs), len(devs2))
        self._log.debug('dev_name=%s', self._ble_scan.dev_name)

        self._ble_scan.scan_svc(devs2, self._conn_retry)

    def end(self):
        self._log.debug('')
        self._ble_scan.end()


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
''')
@click.option('--hci', '-i', 'hci', type=int, default=0,
              help='Interface number for scan')
@click.option('--timout', '-t', 'timeout', type=int, default=3,
              help='timeout sec, 0 for continuous')
@click.option('--conn_retry', '-c', 'conn_retry', type=int, default=3,
              help='conn_retry count')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(hci, timeout, conn_retry, debug):
    logger = get_logger(__name__, debug)
    logger.debug('hci=%s, timeout=%s, conn_retry=%s', hci, timeout, conn_retry)

    logger.info('start')
    app = App(hci, timeout, conn_retry, debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('done')


if __name__ == '__main__':
    main()
