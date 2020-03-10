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
import click
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

        if self._ble_scan.scan_timeout == 0:
            print('')

        newflag = '[-]'

        if isNewData:
            newflag = '[U]'
        if isNewDev:
            self._ble_scan.devs.append(dev)
            newflag = '[N]'
        print('%s ' % (newflag), end='')

        # print(self._ble_scan.dev2string(dev))
        # self._ble_scan.dev_info(dev, conn_retry=5, get_chara=5, read_chara=5)
        if isNewData and self._ble_scan.scan_timeout == 0:
            self._ble_scan.dev_info(dev, conn_retry=2)
        else:
            self._ble_scan.dev_info(dev, dev_data=False, conn_retry=0)

class BleScan:
    _log = None

    def __init__(self, hci=0, scan_timeout=5, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('hci=%s, scan_timeout=%s', hci, scan_timeout)

        self._hci = hci
        self.scan_timeout = scan_timeout

        self._delegate = ScanDelegate(self, debug=self._dbg)
        self._scanner = btle.Scanner(self._hci).withDelegate(self._delegate)

        self.devs = []

    def scan(self, scan_timeout=None):
        self._log.debug('scan_timeout=%s', scan_timeout)

        if scan_timeout is None:
            scan_timeout = self.scan_timeout
            self._log.debug('scan_timeout=%s', scan_timeout)

        devs = self._scanner.scan(scan_timeout, passive=False)
        return devs

    def dev_info(self, dev, dev_data=True,
                 conn_retry=3, get_chara=3, read_chara=3):
        self._log.debug('dev_data=%s', dev_data)
        self._log.debug('conn_retry=%s, get_chara=%s, read_chara=%s',
                        conn_retry, get_chara, read_chara)

        print(self.dev2string(dev))

        if dev_data:
            self.dev_data(dev, indent=4)

        if not dev.connectable:
            return

        if conn_retry < 1:
            return

        count = 0  # < 0: OK
        while count < conn_retry:
            try:
                with btle.Peripheral(dev, dev.addrType) as peri:
                    self._log.debug('Connection: OK .. %d/%d',
                                    count + 1, conn_retry)
                    self.dump_svc(peri, get_chara, read_chara, indent=2)
                    count = -1
                break
            except btle.BTLEDisconnectError as e:
                self._log.debug('%s:%s', type(e).__name__, e)
                self._log.warning('Connection: NG .. %d/%d',
                                  count + 1, conn_retry)
                count += 1
            except Exception as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                self._log.warning('Connection: NG .. %d/%d',
                                  count + 1, conn_retry)
                count += 1

    def end(self):
        self._log.debug('')

    @classmethod
    def dev2string(cls, dev):
        cls._log.debug('')

        ret = 'Device '

        name = ''
        for (adtype, desc, val) in dev.getScanData():
            if 'Local Name' in desc:
                name = val
        if name != '':
            ret += '"' + name + '"'

        ret += '[%s](%s) %s dBm connectable:%s' % (dev.addr,
                                                   dev.addrType,
                                                   dev.rssi,
                                                   dev.connectable)
        return ret

    @classmethod
    def dev_data(cls, dev, indent=4):
        cls._log.debug('indent=%d', indent)

        indent_str = ' ' * indent

        for (adtype, desc, val) in dev.getScanData():
            # print('%s%3d:%s: "%s"' % (indent_str, adtype, desc, val))
            print('%s%s: "%s"' % (indent_str, desc, val))
        if not dev.scanData:
            print('%s(no data)' % (indent_str))

    @classmethod
    def dump_svc(cls, peri, get_chara=3, read_chara=3, indent=2):
        cls._log.debug('read_chara=%s, indent=%d', read_chara, indent)

        indent_str = ' ' * indent

        svcs = sorted(peri.services, key=lambda s: s.hndStart)
        for i, s in enumerate(svcs):
            # print('%s%3d:Service[%s]' % (indent_str, i, s.uuid))
            print(indent_str, end='')
            print('Service [%s]' % (s.uuid))
            cls.dump_chara(s, get_chara, read_chara, indent=indent+2)

    @classmethod
    def dump_chara(cls, svc, get_chara=3, read_chara=3, indent=8):
        cls._log.debug('get_chara=%s, read_chara=%d, indent=%d',
                       get_chara, read_chara, indent)

        if get_chara < 1:
            return

        indent_str = ' ' * indent

        count = 0
        while count < get_chara:
            try:
                chara = svc.getCharacteristics()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                cls._log.warning('%s:%s', type(e).__name__, e)
                raise e
            except Exception as e:
                cls._log.warning('%s:%s', type(e).__name__, e)
                time.sleep(1)
                count += 1

        if count >= 0:  # failed
            print('%s(getCharacteristics: failed)' % (indent_str))
            raise RuntimeError('getCharacteristics: failed')

        for i, c in enumerate(chara):
            # print('%s%3d:%s' % (indent_str, i, c))
            print('%s%s' % (indent_str, c))
            print('%s  Properties: %s' %
                  (indent_str, c.propertiesToString()))

            if c.supportsRead():
                cls.chara_read(c, retry=read_chara, indent=indent+2)

    @classmethod
    def chara_read(cls, chara, retry=5, indent=10):
        cls._log.debug('retry=%d, indent=%d', retry, indent)

        if retry < 1:
            return

        indent_str = ' ' * indent

        count = 0
        while count < retry:
            try:
                val = chara.read()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                cls._log.warning('%s:%s', type(e).__name__, e)
                raise e
            except Exception as e:
                cls._log.warning('%s:%s', type(e).__name__, e)
                time.sleep(1)
                count += 1

        if count >= 0:  # read failed
            print('%s(read: failed)', indent_str)
            raise RuntimeError('read: failed')

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


class App:
    _log = None

    def __init__(self, hci=0, scan_timeout=5,
                 conn_svc=3, get_chara=3, read_chara=3,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('hci=%s, scan_timeout=%s', hci, scan_timeout)
        self._log.debug('conn_svc=%s,get_chara=%s,read_chara=%s',
                        conn_svc, get_chara, read_chara)

        self._hci = hci
        self._scan_timeout = scan_timeout
        self._conn_svc = conn_svc
        self._get_chara = get_chara
        self._read_chara = read_chara

        self._ble_scan = BleScan(self._hci, self._scan_timeout, debug)

    def main(self):
        self._log.debug('')


        '''
        d = btle.Peripheral('b8:27:eb:cd:1b:ee')
        for s in d.services:
            print(str(s))
        return
        '''
    
        print('=====< Scan start >=====')
        devs = self._ble_scan.scan()
        print('=====< Scan end >=====')
        devs2 = self._ble_scan.devs
        self._log.debug('len(devs)=%d, len(dev2)=%d', len(devs), len(devs2))

        for d in devs2:
            print('')
            self._ble_scan.dev_info(d, dev_data=True,
                                    conn_retry=self._conn_svc,
                                    get_chara=self._get_chara,
                                    read_chara=self._read_chara)

    def end(self):
        self._log.debug('')
        self._ble_scan.end()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
''')
@click.option('--hci', '-i', 'hci', type=int, default=0,
              help='Interface number for scan')
@click.option('--scan_timeout', '-t', 'scan_timeout', type=int, default=3,
              help='scan sec, 0 for continuous')
@click.option('--conn_svc', '-s', 'conn_svc', type=int, default=3,
              help='connect service')
@click.option('--get_chara', '-c', 'get_chara', type=int, default=3,
              help='get characteristics')
@click.option('--read_chara', '-r', 'read_chara', type=int, default=3,
              help='read characteristics value')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(hci, scan_timeout, conn_svc, get_chara, read_chara, debug):
    logger = get_logger(__name__, debug)
    logger.debug('hci=%s, scan_timeout=%s', hci, scan_timeout);
    logger.debug('conn_svc=%s, get_chara=%s, read_chara=%s',
                 conn_svc, get_chara, read_chara)

    app = App(hci, scan_timeout, conn_svc, get_chara, read_chara, debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('done')


if __name__ == '__main__':
    main()
