#!/usr/bin/env python3

import serial
import time
import click
from MyLogger import get_logger


class App:
    def __init__(self, dev_name, speed, debug=False):
        self._dbg = debug
        self._lgr = get_logger(__class__.__name__, self._dbg)
        self._lgr.debug('dev_name=%s, speed=%s', dev_name, speed)

        self._dev_name = dev_name
        self._speed = speed

    def main(self):
        self._lgr.debug('')

        ser = serial.Serial(self._dev_name, self._speed, timeout=1)
        # ser.open()

        while True:
            buf = ''
            while True:
                ch = ser.read()
                self._lgr.debug('ch=%a', ch)
                if len(ch) == 0:
                    break

                try:
                    buf += ch.decode('utf-8')
                except UnicodeDecodeError as e:
                    self._lgr.debug('%a:%s:%s', ch, type(e), e)
                    buf += '?'
                    continue

            print(buf)

            line = input('> ')
            self._lgr.debug('line=%a', line)
            if len(line) == 0:
                break

            ser.write((line + '\r\n').encode('utf-8'))
            time.sleep(0.1)

        ser.close()

    def end(self):
        self._lgr.debug('')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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
