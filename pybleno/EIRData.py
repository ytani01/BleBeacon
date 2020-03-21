#!/usr/bin/env python3
#
# (c) Yoichi Tanibayashi
#
from MyLogger import get_logger


class EIRDataEnt:
    AD_TYPE_FLAGS = 0x01
    AD_TYPE_SHORTED_LOCAL_NAME = 0x08
    AD_TYPE_COMPLETE_LOCAL_NAME = 0x09
    AD_TYPE_MANU_DATA = 0xff  # Manufacturer Specific Data

    _log = get_logger(__name__, False)

    def __init__(self, type, data, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('type=%X, data=%a', type, data)

        self._type = type
        self._data = data

        self._data_ent = bytearray(b'  ' + self._data)
        self._log.debug('_data_ent=%a', self._data_ent)

        ad_len = len(self._data) + 1
        self._data_ent[0] = ad_len

        self._data_ent[1] = self._type

        self._data_ent = bytes(self._data_ent)
        self._log.debug('_data_ent=%s',
                        ['%02x' % c for c in self._data_ent])

    def get_data(self):
        self._log.debug('')
        return self._data_ent

    @classmethod
    def str2data(cls, str_data):
        cls._log.debug('str_data=%a', str_data)


class Flags(EIRDataEnt):
    _log = get_logger(__name__, False)

    def __init__(self, flags, debug=False):
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('flags=%x', flags)

        data = bytearray(1)
        data[0] = flags

        super().__init__(EIRDataEnt.AD_TYPE_FLAGS, bytes(data))


class ShortedLocalName(EIRDataEnt):

    def __init__(self, name, debug=False):
        super().__init__(EIRDataEnt.AD_TYPE_SHORTED_LOCAL_NAME,
                         name.encode('utf-8'), debug=debug)


class CompleteLocalName(EIRDataEnt):

    def __init__(self, name, debug=False):
        super().__init__(EIRDataEnt.AD_TYPE_COMPLETE_LOCAL_NAME,
                         name.encode('utf-8'), debug=debug)
