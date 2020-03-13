#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
from MmBlebc2 import MmBlebc2
from ytBeebotte import Beebotte
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    def __init__(self, uuids, user, topics,
                 cb_t=None, cb_h=None, cb_b=None, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('uuids=%s, user=%s, topics=%s',
                        uuids, user, topics)

        self._uuids = uuids
        self._user = user
        self._topics = topics
        
        self._dev = MmBlebc2(self._uuids, 0, 0,
                             self.cb_t, self.cb_h, self.cb_b,
                             debug=self._dbg)

        self._mqtt = Beebotte(self._topics, self._user, debug=self._dbg)
        

    def main(self):
        self._log.debug('')

        self._mqtt.start()
        devs = self._dev.scan()

        self._log.debug('done')

    def end(self):
        self._log.debug('')

        self._mqtt.end()
        
        self._log.debug('done')

    def cb_t(self, val):
        print(val)

        val2 = float('%.2f' % val)
        self._mqtt.send_data(self._topics[0], val2)
        self._log.info('published: %.2f C', val2)

    def cb_h(self, val):
        print(val)

        val2 = float('%.2f' % val)
        self._mqtt.send_data('env1/humidity1', val2)
        self._log.info('published: %.2f %%', val2)

    def cb_b(self, val):
        print(val)


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Environment data publisher
temperature, humidity ..
''')
@click.argument('uuid1', type=str)
@click.argument('user', type=str)
@click.argument('topic1', type=str)
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
