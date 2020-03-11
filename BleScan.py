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
        self._uuids = self._ble_scan.uuids

    def handleDiscovery(self, dev, isNewDev, isNewData):
        self._log.debug('isNewDev=%s, isNewData=%s', isNewDev, isNewData)

        target = False
        newflag = '[-]'
        if isNewData:
            newflag = '[U]'
            if len(self._uuids) == 0 or dev.addr in self._uuids:
                target = True
        if isNewDev:
            newflag = '[N]'
            if len(self._uuids) == 0 or dev.addr in self._uuids:
                self._ble_scan.devs.append(dev)

        # print(self._ble_scan.dev2string(dev))
        # self._ble_scan.dev_info(dev, conn_retry=5, get_chara=5, read_chara=5)
        if target and isNewData and self._ble_scan.scan_timeout == 0:
            print('')
            print('%s ' % (newflag), end='')
            self._ble_scan.dev_info(dev, conn_svc=self._ble_scan._conn_svc)
        elif self._ble_scan.scan_timeout != 0:
            print('%s ' % (newflag), end='')
            self._ble_scan.dev_info(dev, dev_data=False, conn_svc=0)


class BleScan:
    _log = None

    def __init__(self, uuids=(), hci=0, scan_timeout=5,
                 conn_svc=3, get_chara=3, read_chara=3,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuids=%s, hci=%s, scan_timeout=%s',
                        uuids, hci, scan_timeout)

        self.uuids = uuids
        self._hci = hci
        self.scan_timeout = scan_timeout
        self._conn_svc = conn_svc
        self._get_chara = get_chara
        self._read_chara = read_chara

        self._delegate = ScanDelegate(self, debug=self._dbg)
        self._scanner = btle.Scanner(self._hci).withDelegate(self._delegate)

        self.devs = []

    def end(self):
        self._log.debug('')

    def scan(self, scan_timeout=None):
        self._log.debug('scan_timeout=%s', scan_timeout)

        if scan_timeout is None:
            scan_timeout = self.scan_timeout
            self._log.debug('scan_timeout=%s', scan_timeout)

        devs = self._scanner.scan(scan_timeout, passive=False)
        return devs

    def dev_info(self, dev, dev_data=True,
                 conn_svc=None, get_chara=None, read_chara=None):
        self._log.debug('dev_data=%s', dev_data)
        self._log.debug('conn_svc=%s, get_chara=%s, read_chara=%s',
                        conn_svc, get_chara, read_chara)

        if conn_svc is None:
            conn_svc = self._conn_svc
            self._log.debug('conn_svc=%s', conn_svc)

        if get_chara is None:
            get_chara = self._get_chara
            self._log.debug('get_chara=%s', get_chara)

        if read_chara is None:
            read_chara = self._read_chara
            self._log.debug('read_chara=%s', read_chara)

        print(self.dev2string(dev))

        if dev_data:
            self.dev_data(dev, indent=4)

        if not dev.connectable:
            return None

        if conn_svc < 1:
            return None

        count = 0  # < 0: OK
        while count < conn_svc:
            try:
                with btle.Peripheral(dev, dev.addrType) as peri:
                    self._log.debug('Connection: OK .. %d/%d',
                                    count + 1, conn_svc)
                    ret = self.dump_svc(peri, get_chara, read_chara, indent=2)
                    self._log.debug('dump_svc()> %s', ret)
                    count = -1

                return 'OK'

            except btle.BTLEDisconnectError as e:
                self._log.debug('%s:%s', type(e).__name__, e)
                self._log.warning('Connection: NG .. %d/%d',
                                  count + 1, conn_svc)
                count += 1
            except Exception as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                self._log.warning('Connection: NG .. %d/%d',
                                  count + 1, conn_svc)
                count += 1

        return 'Error'

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

        ret += '[%s](%s) %s dBm connectable:%s' % (dev.addr, dev.addrType,
                                                   dev.rssi, dev.connectable)
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

    def dump_svc(self, peri, get_chara=None, read_chara=None, indent=2):
        self._log.debug('read_chara=%s, indent=%d', read_chara, indent)

        if get_chara is None:
            get_chara = self._get_chara
            self._log.debug('get_chara=%s', get_chara)

        if read_chara is None:
            read_chara = self._read_chara
            self._log.debug('read_chara=%s', read_chara)

        indent_str = ' ' * indent

        svcs = sorted(peri.services, key=lambda s: s.hndStart)
        for s in svcs:
            # print('%s%3d:Service[%s]' % (indent_str, i, s.uuid))
            print(indent_str, end='')
            print('Service [%s]' % (s.uuid))
            ret = self.dump_chara(s, get_chara, read_chara, indent=indent+2)
            self._log.debug('dump_chara()> %s', ret)

        return len(svcs)

    def dump_chara(self, svc, get_chara=3, read_chara=3, indent=8):
        self._log.debug('get_chara=%s, read_chara=%d, indent=%d',
                       get_chara, read_chara, indent)

        if get_chara is None:
            get_chara = self._get_chara
            self._log.debug('get_chara=%s', get_chara)

        if read_chara is None:
            read_chara = self._read_chara
            self._log.debug('read_chara=%s', read_chara)

        if get_chara < 1:
            return None

        indent_str = ' ' * indent

        count = 0
        while count < get_chara:
            try:
                chara = svc.getCharacteristics()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                raise e
            except Exception as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                time.sleep(1)
                count += 1

        if count >= 0:  # failed
            print('%s(getCharacteristics: failed)' % (indent_str))
            raise RuntimeError('getCharacteristics: failed')

        for c in chara:
            # print('%s%3d:%s' % (indent_str, i, c))
            print('%s%s' % (indent_str, c))
            print('%s  Properties: %s' %
                  (indent_str, c.propertiesToString()))

            if c.supportsRead():
                ret = self.chara_read(c, read_chara=read_chara,
                                      indent=indent+2)
                self._log.debug('chara_read()> %s', ret)

        return len(chara)

    def chara_read(self, chara, read_chara=5, indent=10):
        self._log.debug('read_chara=%d, indent=%d', read_chara, indent)

        if read_chara is None:
            read_chara = self._read_chara
            self._log.debug('read_chara=%s', read_chara)

        if read_chara < 1:
            return None

        indent_str = ' ' * indent

        count = 0
        while count < read_chara:
            try:
                val = chara.read()
                count = -1
                break
            except btle.BTLEDisconnectError as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                raise e
            except Exception as e:
                self._log.warning('%s:%s', type(e).__name__, e)
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

        return val

class App:
    _log = None

    def __init__(self, uuids=(), hci=0, scan_timeout=5,
                 conn_svc=3, get_chara=3, read_chara=3,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('hci=%s, scan_timeout=%s', hci, scan_timeout)
        self._log.debug('conn_svc=%s,get_chara=%s,read_chara=%s',
                        conn_svc, get_chara, read_chara)

        self._uuids = uuids
        self._hci = hci
        self._scan_timeout = scan_timeout
        self._conn_svc = conn_svc
        self._get_chara = get_chara
        self._read_chara = read_chara

        self._ble_scan = BleScan(self._uuids, self._hci, self._scan_timeout,
                                 self._conn_svc, self._get_chara,
                                 self._read_chara, 
                                 debug=self._dbg)

    def main(self):
        self._log.debug('')

        print('=====< Scan start >=====')
        devs = self._ble_scan.scan()
        devs2 = self._ble_scan.devs
        print('=====< Scan end: %d devices >=====' % len(devs2))
        self._log.debug('len(devs)=%d, len(dev2)=%d', len(devs), len(devs2))

        for d in devs2:
            print('')
            self._ble_scan.dev_info(d, dev_data=True,
                                    conn_svc=self._conn_svc,
                                    get_chara=self._get_chara,
                                    read_chara=self._read_chara)

    def end(self):
        self._log.debug('')
        self._ble_scan.end()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
''')
@click.argument('uuids', type=str, nargs=-1)
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
def main(uuids, hci, scan_timeout, conn_svc, get_chara, read_chara, debug):
    logger = get_logger(__name__, debug)
    logger.debug('uuids=%s', uuids)
    logger.debug('hci=%s, scan_timeout=%s', hci, scan_timeout)
    logger.debug('conn_svc=%s, get_chara=%s, read_chara=%s',
                 conn_svc, get_chara, read_chara)

    app = App(uuids, hci, scan_timeout, conn_svc, get_chara, read_chara,
              debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('done')


if __name__ == '__main__':
    main()
