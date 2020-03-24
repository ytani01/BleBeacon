#!/usr/bin/env python3

import serial
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    _log = get_logger(__name__, False)

    def __init__(self, dev_name, speed, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('dev_name=%s, speed=%s', dev_name, speed)

        self._dev_name = dev_name
        self._speed = speed

        self._ser = None

    def main(self):
        self._log.debug('')

        if self.openSerial('/dev/ttyUSB', 115200, 1.0) is None:
            self._log.error('failed to open serial')
            return

        while True:
            try:
                li = self._ser.readline()
            except serial.serialutil.SerialException:
                li = b''
                
            if len(li) == 0:
                continue

            try:
                li = li.decode('utf-8')
            except UnicodeDecodeError:
                li = str(li)

            li = li.replace('\r\n', '')

            print(li)

        self.closeSerial()

    def end(self):
        self._log.debug('')
        self.closeSerial()
        self._log.debug('done')

    def openSerial(self, dev_prefix, speed, timeout=1.0):
        self._log.debug('dev_prefix=%s, spped=%d, timeout=%s',
                        dev_prefix, speed, timeout)

        if self._ser is not None:
            self._log.warning('already opend .. close')
            self.closeSerial()

        for i in range(3):
            dev = dev_prefix + str(i)
            self._log.debug('dev=%s', dev)
            try:
                self._ser = serial.Serial(dev, speed, timeout=timeout)
                break
            except Exception as e:
                self._log.error('%s, %s', type(e).__name__, e)
                continue

        return self._ser

    def closeSerial(self):
        self._log.debug('')
        if self._ser is not None:
            self._ser.close()
            self._ser = None


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Serial test
''')
@click.option('--dev_name', '-d', 'dev_name', type=str,
              default='/dev/ttyUSB0',
              help='serial device name')
@click.option('--speed', '-s', 'speed', type=int, default=9600,
              help='serial speed')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug option')
def main(dev_name, speed, debug):
    lgr = get_logger(__name__, debug)
    lgr.debug('dev_name=%s, speed=%s', dev_name, speed)

    lgr.info('start')
    app = App(dev_name, speed, debug=debug)
    try:
        app.main()
    finally:
        app.end()


if __name__ == '__main__':
    main()
