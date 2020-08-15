#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from . import ZeiCharBase


def _ZEI_UUID(short_uuid):
    return "c7e7%04X-c847-11e6-8175-8c89a55d403c" % (short_uuid)


class ZeiOrientationChar(ZeiCharBase.ZeiCharBase):
    svcUUID = _ZEI_UUID(0x0010)
    charUUID = _ZEI_UUID(0x0012)

    def __init__(self, periph):
        ZeiCharBase.ZeiCharBase.__init__(self, periph)
