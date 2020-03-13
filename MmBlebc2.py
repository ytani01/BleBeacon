#!/usr/bin/env python3
#
# (c) Yoichi Tanibayashi
#
from bluepy import btle
from BleScan import BleScan, App, ScanDelegate

import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
from MyLogger import get_logger


class MmBleBc2ScanDelegate(ScanDelegate):
    '''
    exactlly same as ScanDelegate
    '''
    pass


class MmBlebc2(BleScan):
    SVC_UUID = '0000ffe1-0000-1000-8000-00805f9b34fb'

    _log = None

    def __init__(self, uuids=(), hci=0, scan_timeout=5,
                 cb_temperature=None,
                 cb_humidity=None,
                 cb_battery=None,
                 debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuids=%s, hci=%s, scan_timeout=%s',
                        uuids, hci, scan_timeout)

        self._cb_temperature = cb_temperature
        self._cb_humidity = cb_humidity
        self._cb_battery = cb_battery

        super().__init__(uuids, hci, scan_timeout,
                         conn_svc=0, get_chara=0, read_chara=0,
                         debug=self._dbg)

        self._delegate = MmBleBc2ScanDelegate(self, debug=self._dbg)
        self._scanner = btle.Scanner(self._hci).withDelegate(self._delegate)

    def cb_temperature(self, val):
        '''
        Please override
        '''
        self._log.debug('val=%s', val)

    def cb_humidity(self, val):
        '''
        Please override
        '''
        self._log.debug('val=%s', val)

    def cb_battery(self, val):
        '''
        Please override
        '''
        self._log.debug('val=%s', val)

    def dev_data(self, dev, indent=4):
        '''
        called from dev_info()
        dev_info() is called from main() and/or handleDiscovery()
        '''
        self._log.debug('indent=%s', indent)
        super().dev_data(dev, indent)

        svc_ok = False
        data = ''
        for (adtype, desc, val) in dev.getScanData():
            if desc == 'Complete 16b Services':
                if val == self.SVC_UUID:
                    svc_ok = True

            if desc == '16b Service Data':
                data = val

        self._log.debug('svc_ok=%s, data=%s', svc_ok, data)
        if len(data) == 0:
            return None

        # split
        data2 = [data[i:i+2] for i in range(0, len(data), 2)]
        self._log.debug('data2=%s', data2)

        data_battery = self.buttery_level(data2[4])
        data_temperature = self.hexstr2float(''.join(data2[5:7]))
        data_humidity = self.hexstr2float(''.join(data2[7:9]))
        print(' ' * indent, end='')
        print('----------')
        print(' ' * indent, end='')
        print('battery: %d %% ' % (data_battery), end='')
        print('temperature: %.1f \'C ' % (data_temperature), end='')
        print('humidity: %.1f %%' % (data_humidity))

        self._cb_battery(data_battery)
        self._cb_temperature(data_temperature)
        self._cb_humidity(data_humidity)

        return [data_battery, data_temperature, data_humidity]

    def buttery_level(self, data):
        self._log.debug('data=%s', data)

        return float(int(data, 16) / int('64', 16) * 100)

    @classmethod
    def hexstr2float(self, data):
        self._log.debug('data=%s', data)

        try:
            return float(int(data, 16) / 256.0)
        except Exception as e:
            self._log.warning('%s:%s', type(e).__class__, e)
            return -1


class App2(App):
    _log = None

    def __init__(self, uuids=(), hci=0, scan_timeout=5, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuids=%s, hci=%s, scan_timeout=%s',
                        uuids, hci, scan_timeout)

        self._uuids = uuids
        self._hci = hci
        self._scan_timeout = scan_timeout
        self._conn_svc = 0
        self._get_chara = 0
        self._read_chara = 0

        self._ble_scan = MmBlebc2(self._uuids, self._hci, self._scan_timeout,
                                  self.cb_t, self.cb_h, self.cb_b,
                                  debug=self._dbg)

    def cb_t(self, val):
        print(val)

    def cb_h(self, val):
        print(val)

    def cb_b(self, val):
        print(val)


@click.command(context_settings=CONTEXT_SETTINGS, help='MM-BLEBC2')
@click.argument('uuids', type=str, nargs=-1)
@click.option('--hci', '-i', 'hci', type=int, default=0,
              help='Interface number for scan')
@click.option('--scan_timeout', '-t', 'scan_timeout', type=int, default=3,
              help='scan sec, 0 for continuous')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug option')
def main(uuids, hci, scan_timeout, debug):
    log = get_logger(__name__, debug)
    log.debug('uuids=%s, hci=%s, scan_timeout=%s', uuids, hci, scan_timeout)

    app = App2(uuids, hci, scan_timeout, debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.debug('done')


if __name__ == '__main__':
    main()
