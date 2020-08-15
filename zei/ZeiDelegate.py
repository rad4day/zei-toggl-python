#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import struct
from bluepy import btle
from .Log import _log


class ZeiDelegate(btle.DefaultDelegate):
    def __init__(self, periph):
        btle.DefaultDelegate.__init__(self)
        self.parent = periph

    def handleNotification(self, cHandle, data):
        if cHandle == 38:
            side = struct.unpack("B", data)[0]
            _log.info("Current side up is %s", side)
        else:
            _log.info("Notification from hndl: %s - %r", cHandle, data)
