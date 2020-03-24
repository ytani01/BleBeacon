#!/usr/bin/env python3

import serial
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
                break

        self._log.info('tag_addr=%s.', tag_addr)

    def get_tagaddr(self, repeat):
        self._log.debug('repeat=%s', self._repeat)

        dev = self.openSerial(self._dev_name_prefix, 115200, 1.0)
        if dev is None:
            self._log.error('failed to open serial')
            return

        tag_addr = None
        while True:
            try:
                li = self._ser.readline()
            except serial.serialutil.SerialException as e:
                self._log.warning('%s:%s', type(e).__name__, e)
                li = b''

            if len(li) == 0:
                continue

            try:
                li = li.decode('utf-8')
            except UnicodeDecodeError:
                li = str(li)

            li = li.replace('\r\n', '')
            self._log.debug("%s>%s", dev, li)

            if li.startswith(self.STR_MY_ADDR):
                tag_addr = li[len(self.STR_MY_ADDR):]
                self._log.debug('* tag_addr=%s.', tag_addr)

                if repeat:
                    continue

                break

        self.closeSerial()
        return tag_addr

    def end(self):
        self._log.debug('')
        self.closeSerial()
        self._log.debug('done')

    def openSerial(self, dev_prefix, speed, timeout=1.0):
        self._log.debug('dev_prefix=%s, spped=%d, timeout=%s',
                        dev_prefix, speed, timeout)

        dev = None

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
                dev = None
                continue

        return dev

    def closeSerial(self):
        self._log.debug('')
        if self._ser is not None:
            self._ser.close()
            self._ser = None


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Serial test
''')
@click.option('--dev_name_prefix', '-d', 'dev_name_prefix', type=str,
              default='/dev/ttyUSB',
              help='serial device name')
@click.option('--speed', '-s', 'speed', type=int, default=9600,
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
