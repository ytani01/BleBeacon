#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
from MmBlebc2 import MmBlebc2
from Mqtt import BeebottePublisher
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    def __init__(self, addrs, token, channel, res_t, res_h, res_b, res_msg,
                 ave_n, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('addrs=%s, token=%s', addrs, token)
        self._log.debug('channel=%s', channel)
        self._log.debug('res_t=%s, res_h=%s, res_b=%s, res_msg=%s',
                        res_t, res_h, res_b, res_msg)
        self._log.debug('ave_n=%s', ave_n)

        self._addrs = addrs
        self._token = token
        self._channel = channel
        self._res_t = res_t
        self._res_h = res_h
        self._res_b = res_b
        self._res_msg = res_msg
        self._ave_n = ave_n

        self._topic_t = '%s/%s' % (self._channel, self._res_t)
        self._topic_h = '%s/%s' % (self._channel, self._res_h)
        self._topic_b = '%s/%s' % (self._channel, self._res_b)
        self._topic_msg = '%s/%s' % (self._channel, self._res_msg)

        self._t = None
        self._h = None
        self._b = None
        self._msg = None

        self._hist_t = []
        self._hist_h = []
        self._hist_b = []

        self._dev = MmBlebc2(self._addrs, 0, 0, self.cb, debug=self._dbg)
        self._mqtt = BeebottePublisher(self._token, debug=self._dbg)

    def main(self):
        self._log.debug('')

        self._mqtt.start()

        # scan forever
        devs = self._dev.scan()
        self._log.debug('devs=%s', devs)

        self._log.debug('done')

    def end(self):
        self._log.debug('')
        self._mqtt.end()
        self._log.debug('done')

    def cb(self, t, h, b):
        self._log.debug('%s C, %s %%, %s %%', t, h, b)

        self._hist_t.append(t)
        while len(self._hist_t) > self._ave_n:
            self._hist_t.pop(0)
        t = float('%.2f' % (sum(self._hist_t) / len(self._hist_t)))
        self._log.info('t=%s %s', t, self._hist_t)

        self._hist_h.append(h)
        while len(self._hist_h) > self._ave_n:
            self._hist_h.pop(0)
        h = float('%.1f' % (sum(self._hist_h) / len(self._hist_h)))
        self._log.info('h=%s %s', h, self._hist_h)

        self._hist_b.append(b)
        while len(self._hist_b) > self._ave_n:
            self._hist_b.pop(0)
        b = int(round(sum(self._hist_b) / len(self._hist_b)))
        self._log.info('b=%s %s', b, self._hist_b)

        msg = 'Temperature: %s C  Humidity: %s %% Battery: %s %%' % (
            t, h, b)
        self._mqtt.send_data(str(t), self._topic_t)
        self._mqtt.send_data(str(h), self._topic_h)
        self._mqtt.send_data(str(b), self._topic_b)
        self._mqtt.send_data(msg, self._topic_msg)


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Environment data publisher
temperature, humidity ..
''')
@click.argument('addr', type=str)
@click.argument('token', type=str)
@click.argument('channel', type=str)
@click.argument('res_temperature', type=str)
@click.argument('res_humidity', type=str)
@click.argument('res_battery', type=str)
@click.argument('res_msg', type=str)
@click.option('--ave_n', '-a', 'ave_n', type=int, default=1,
              help='average N')
@click.option('--debugg', '-d', 'debug', is_flag=True, default=False,
              help='debug option')
def main(addr, token, channel,
         res_temperature, res_humidity, res_battery, res_msg, ave_n,
         debug):
    log = get_logger(__name__, debug)
    log.debug('addr=%s, token=%s, channel=%s', addr, token, channel)
    log.debug('res_temperature=%s,res_humidity=%s,res_battery=%s,res_msg=%s',
              res_temperature, res_humidity, res_battery, res_msg)

    app = App([addr], token, channel,
              res_temperature, res_humidity, res_battery, res_msg,
              ave_n, debug=debug)
    try:
        app.main()
    finally:
        app.end()

if __name__ == '__main__':
    main()
