#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
from BlePeripheral import BlePeripheral, BlePeripheralApp
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class TagPublisher(BlePeripheral):
    TAGID_PREFIX = 'tag-'

    _log = get_logger(__name__, False)

    def __init__(self, tagid, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('tagid=%s', tagid)

        self._tagid = tagid

        self._myname = self.TAGID_PREFIX + self._tagid
        self._svcs = []

        super().__init__(self._myname, self._svcs, debug=self._dbg)


class TagPublisherApp(BlePeripheralApp):
    _log = get_logger(__name__, False)

    def __init__(self, tagid, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('tagid=%s', tagid)

        self._ble = TagPublisher(tagid, debug=self._dbg)


@click.command(context_settings=CONTEXT_SETTINGS, help='')
@click.argument('tagid', type=str)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(tagid, debug):
    log = get_logger(__name__, debug)

    app = TagPublisherApp(tagid, debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('done')


if __name__ == '__main__':
    main()
