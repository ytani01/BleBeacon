#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
get Tag's BLE MAC address
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import serial
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    STR_MY_ADDR = 'MyAddrStr='

    _log = get_logger(__name__, False)

    def __init__(self, dev_name_prefix, speed, repeat=False, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('dev_name_prefix=%s, speed=%s, repeat=%s',
                        dev_name_prefix, speed, repeat)

        self._dev_name_prefix = dev_name_prefix
        self._speed = speed
        self._repeat = repeat

        self._ser = None

    def main(self):
        self._log.debug('')

        while True:
            tag_addr = self.get_tagaddr(self._repeat)
            if tag_addr is not None:
                self._log.info('tag_addr=%s.', tag_addr)
                if not self._repeat:
                    break

    def get_tagaddr(self, repeat):
        """
        Returns
        -------
        str
            Tag's MAC address
        None
            error
        """
        self._log.debug('repeat=%s', self._repeat)

        tag_addr = None

        dev = None
        while dev is None:
            try:
                dev = self.openSerial(self._dev_name_prefix, self._speed, 0.1)
            except Exception as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                time.sleep(1)

        while True:
            try:
                lines = self._ser.readlines()
            except serial.serialutil.SerialException as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                # lines = []
                return None

            if len(lines) == 0:
                continue

            for li in lines:
                try:
                    li = li.decode('utf-8')
                except UnicodeDecodeError:
                    li = str(li)

                li = li.replace('\r\n', '')
                self._log.debug("%s> %s", dev, li)

                if li.startswith(self.STR_MY_ADDR):
                    tag_addr = li[len(self.STR_MY_ADDR):]
                    self._log.debug('* tag_addr=%s.', tag_addr)

                    if not repeat:
                        break

            if tag_addr is not None:
                break

        self.closeSerial()
        return tag_addr

    def end(self):
        self._log.debug('')
        self.closeSerial()
        self._log.debug('done')

    def openSerial(self, dev_prefix, speed, timeout=1.0):
        """
        Parameters
        ----------
        dev_prefix: str
            device name prefix (ex. '/dev/USB')
        speed: int

        timeout: float

        Returns
        -------
        str
            device name (ex. '/dev/USB0')
        """
        self._log.debug('dev_prefix=%s, spped=%d, timeout=%s',
                        dev_prefix, speed, timeout)

        dev = None

        if self._ser is not None:
            self._log.warning('already opend .. close')
            self.closeSerial()

        for i in range(10):
            dev = dev_prefix + str(i)
            self._log.debug('dev=%s', dev)
            try:
                self._ser = serial.Serial(dev, speed, timeout=timeout)
                return dev
            except Exception as e:
                self._log.debug('%s:%s', type(e).__name__, e)
                dev = None

        raise Exception('openSerial(%s,%d,%.1f)' % (dev_prefix, speed,
                                                    timeout))

    def closeSerial(self):
        self._log.debug('')
        if self._ser is not None:
            self._ser.close()
            self._ser = None


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Serial test
''')
@click.option('--dev_name_prefix', '-p', 'dev_name_prefix', type=str,
              default='/dev/ttyUSB',
              help='serial device name')
@click.option('--speed', '-s', 'speed', type=int, default=115200,
              help='serial speed')
@click.option('--repeat', '-r', 'repeat', is_flag=True, default=False,
              help='repeat flag')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug option')
def main(dev_name_prefix, speed, repeat, debug):
    log = get_logger(__name__, debug)
    log.debug('dev_name_prefix=%s, speed=%s, repeat=%s',
              dev_name_prefix, speed, repeat)

    app = App(dev_name_prefix, speed, repeat, debug=debug)
    try:
        app.main()
    finally:
        app.end()


if __name__ == '__main__':
    main()
