#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
from MmBlebc2 import MmBlebc2
from ytBeeboote import Beebotte
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    def __init__(self, uuids, user, topics, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuid=%s, user=%s, topic=%s',
                        uuuid, user, topic)

        self._uuids = uuids
        self._user = user
        self._topics = topics
        
        self._dev = MmBlebc2(self._uuids, 0, 0,
                             self.cb_t, self._cb_h, self._cb_b,
                             debug=self._dbg)

    def main(self):
        self._log.debug('')

        devs = self._dev.scan()

        self._log.debug('done')

    def end(self):
        self._log.debug('')

        self._log.debug('done')

    def cb_t(self, val):
        print(val)

    def cb_h(self, val):
        print(val)

    def cb_b(self, val):
        print(val)


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Environment data publisher
temperature, humidity ..
''')
@click.argument('uuid1', type=str)
@click.argument('user', type=str, nargs=-1)
@click.argument('topic1', type=str, nargs=-1)
@click.option('--debugg', '-d', 'debug', is_flag=True, default=False,
              help='debug option')
def main(uuid1, user, topic1, debug):
    log = get_logger(__name__, debug)
    log.debug('uuid1=%s, user=%s, topic1=%s', uuid1, user, topic1)

    app = App([uuid1], user, [topic1], debug=debug)
    try:
        app.main()
    finally:
        app.end()

if __name__ == '__main__':
    main()
