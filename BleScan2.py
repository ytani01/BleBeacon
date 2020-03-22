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
import sys
import click
from MyLogger import get_logger
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class ScanDelegate(btle.DefaultDelegate):
    _log = None

    def __init__(self, ble_scan, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self._ble_scan = ble_scan
        self._addrs = self._ble_scan._addrs

    def handleDiscovery(self, dev, isNewDev, isNewData):
        self._log.debug('%s,NewDev=%s,NewData=%s',
                        dev.addr, isNewDev, isNewData)


class BleScan:
    BASE_UUID = '0000%s-0000-1000-8000-00805f9b34fb'
    UUID_CHARA_DEVICE_NAME = BASE_UUID % '2a00'

    _log = None

    def __init__(self, addrs=(), hci=0, scan_timeout=5,
                 conn_svc=3, get_chara=3, read_chara=3,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('addrs=%s, hci=%s, scan_timeout=%s',
                        addrs, hci, scan_timeout)

        self._addrs = addrs
        self._hci = hci
        self._scan_timeout = scan_timeout
        self._conn_svc = conn_svc
        self._get_chara = get_chara
        self._read_chara = read_chara

        self._delegate = ScanDelegate(self, debug=self._dbg)
        self._scanner = btle.Scanner(self._hci).withDelegate(self._delegate)

    def end(self):
        self._log.debug('')

    def scan(self, scan_timeout=None):
        self._log.debug('scan_timeout=%s', scan_timeout)

        if scan_timeout is None:
            scan_timeout = self._scan_timeout
            self._log.debug('scan_timeout=%s', scan_timeout)

        devs = self._scanner.scan(scan_timeout, passive=True)
        return devs


class App:
    _log = None

    def __init__(self, addrs=(), hci=0, scan_timeout=5,
                 conn_svc=3, get_chara=3, read_chara=3,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('addrs=%s')

        self._addrs = addrs
        self._hci = hci
        self._scan_timeout = scan_timeout
        self._conn_svc = conn_svc
        self._get_chara = get_chara
        self._read_chara = read_chara

        self._ble_scan = BleScan(self._addrs, self._hci, self._scan_timeout,
                                 self._conn_svc, self._get_chara,
                                 self._read_chara, 
                                 debug=self._dbg)

    def main(self):
        self._log.debug('')

        devs = self._ble_scan.scan()
        self._log.debug('scan end')
        
        time.sleep(1)

        target_addr = []
        for d in devs:
            self._log.debug('[%s]', d.addr)
            if len(d.rawData) > 0:
                self._log.debug('rawData=')
                self._log.debug('%s',
                                ['%02x' % c for c in d.rawData])

                part = 'len'
                data = []
                l_ = 0
                i_ = 0
                for c in d.rawData:
                    if part == 'len':
                        l_ = int(c)
                        i_ = 0
                        data.append('%02x(%d)' % (c, l_))
                        part = 'data'
                        continue

                    data.append('%02x' % c)
                    i_ += 1
                    if i_ == l_:
                        self._log.debug('data=%s', data)
                        part = 'len'
                        data = []
                        l_ = 0
                        i_ = 0
                        
            name = None

            for (adtype, desc, val) in d.getScanData():
                self._log.debug('desc=%s, val=%s', desc, val)
                if 'Local Name' in desc:
                    name = val
                    self._log.debug('name=%s', val)

            if d.addr in self._addrs:
                target_addr.append(d.addr)
            else:
                continue

            if name in self._addrs:
                target_addr.append(d.addr)

            if not d.connectable:
                continue

            count = 0
            while count < self._conn_svc:
                try:
                    count += 1
                    self._log.debug('connecting[%d/%d] ..',
                                    count, self._conn_svc)
                    with btle.Peripheral(d.addr, d.addrType) as p:
                        self._log.debug('OK')

                        # self._log.debug('state=%s', p.getState())

                        p.discoverServices()
                        # self._log.debug('state=%s', p.getState())

                        for s in p.services:
                            self._log.debug('s:%s', s.uuid)

                            c = s.getCharacteristics()
                            for c1 in c:
                                self._log.debug('c1:%s(%s)', c1, c1.uuid)

                                if c1.uuid == BleScan.UUID_CHARA_DEVICE_NAME:
                                    name = c1.read().decode('utf-8')
                                    self._log.debug('name=%s', val)

                        break

                except btle.BTLEDisconnectError as e:
                    # self._log.debug('%s:%s', type(e).__name__, e)
                    time.sleep(1)

                except Exception as e:
                    self._log.debug('%s:%s', type(e).__name__, e)
                    time.sleep(1)

            if name in self._addrs:
                target_addr.append(d.addr)
                continue

        for t in target_addr:
            print(t)

    def end(self):
        self._log.debug('')
        self._ble_scan.end()


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BLE Device Scanner
''')
@click.argument('addrs', type=str, nargs=-1)
@click.option('--hci', '-i', 'hci', type=int, default=0,
              help='Interface number for scan')
@click.option('--scan_timeout', '-t', 'scan_timeout', type=int, default=4,
              help='scan sec, 0 for continuous')
@click.option('--conn_svc', '-s', 'conn_svc', type=int, default=3,
              help='connect service')
@click.option('--get_chara', '-c', 'get_chara', type=int, default=3,
              help='get characteristics')
@click.option('--read_chara', '-r', 'read_chara', type=int, default=3,
              help='read characteristics value')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(addrs, hci, scan_timeout, conn_svc, get_chara, read_chara, debug):
    logger = get_logger(__name__, debug)
    logger.debug('addrs=%s', addrs)
    logger.debug('hci=%s, scan_timeout=%s', hci, scan_timeout)
    logger.debug('conn_svc=%s, get_chara=%s, read_chara=%s',
                 conn_svc, get_chara, read_chara)

    app = App(addrs, hci, scan_timeout, conn_svc, get_chara, read_chara,
              debug=debug)
    try:
        app.main()
    finally:
        logger.debug('finally')
        app.end()
        logger.info('done')


if __name__ == '__main__':
    main()
