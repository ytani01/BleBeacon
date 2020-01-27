#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from bluepy.btle import DefaultDelegate, Scanner, BTLEException
import bluepy.btle
import time

from MyLogger import get_logger


class ScanDelegate(DefaultDelegate):
    ADDR_HDR = 'ac:23:3f:'
    DATA_KEYWORD = '16b Service Data'

    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        self._addr = {}

        super().__init__()

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        """
        self._logger.debug('scanEntry=%s, isNewDev=%s, isNewData=%s',
                           scanEntry, isNewDev, isNewData)
        """
        if not isNewDev:
            return

        addr = scanEntry.addr

        if addr in self._addr.keys():
            return
        self._addr[addr] = True
        print(addr)
        return

        """
        if not addr.startswith(self.ADDR_HDR):
            return
        """

        self._logger.debug('========================================')
        self._logger.debug('addr=%s', addr)

        scan_data = scanEntry.getScanData()
        self._logger.debug('scan_data=[')

        for (ad_type, ad_desc, ad_value) in scan_data:
            self._logger.debug('%3s,%s,%s', ad_type, ad_desc, ad_value)

            if ad_desc == 'Manufacturer':
                co_id = ad_value[0:4]
                self._logger.debug('  co_id=%s', co_id)
                
            """
            if a[1] == self.DATA_KEYWORD:
                data_str = a[2]
                self._logger.debug('data_str=%s', data_str)

                batt_str = data_str[8:10]
                temp_str = data_str[10:14]
                humidity_str = data_str[14:18]
                self._logger.debug('batt_str=%s, temp_str=%s, humidity_str=%s',
                                   batt_str, temp_str, humidity_str)

                batt_val = int(batt_str, 16) / int('64', 16)
                self._logger.debug('batt_val=%s', batt_val)

                temp_val = self.hexstr2float(temp_str)
                self._logger.debug('temp_val=%.1f C', temp_val)

                humidity_val = self.hexstr2float(humidity_str)
                self._logger.debug('humidity_val=%.1f %%', humidity_val)
            """
        self._logger.debug(']')

    def hexstr2float(self, val_str):
        self._logger.debug('val_str=%s', val_str)

        val = int(val_str[0:2], 16)
        val += int(val_str[2:3], 16) / 16.0
        val += int(val_str[3:4], 16) / 256.0
        self._logger.debug('val=%s', val)

        return val


class App(DefaultDelegate):
    def __init__(self, debug=False):
        self._debug = debug
        self._logger = get_logger(__class__.__name__, self._debug)
        self._logger.debug('')

        delegate = ScanDelegate(debug=debug)
        self._scanner = Scanner().withDelegate(delegate)

    def main(self):
        self._logger.debug('')
        while True:
            self.scan(5.0)
            time.sleep(0.1)

    def end(self):
        self._logger.debug('')

    def scan(self, sec):
        self._logger.debug('sec=%s', sec)
        try:
            self._scanner.scan(sec, passive=True)
        except Exception as e:
            msg = '%s:%s' % (type(e), e)
            self._logger.warning(msg)


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
