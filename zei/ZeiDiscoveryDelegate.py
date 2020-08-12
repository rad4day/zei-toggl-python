#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from bluepy import btle
from Log import _log


class ZeiDiscoveryDelegate(btle.DefaultDelegate):
    def __init__(self, scanner, periph):
        btle.DefaultDelegate.__init__(self)
        self.scanner = scanner
        self.periph = periph

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not dev.addr == 'f1:05:a5:9c:2e:9b':
            return
        _log.info("Device %s (%s), RSSI=%d dB", dev.addr, dev.addrType, dev.rssi)
        for (_, desc, value) in dev.getScanData():
            _log.info("  %s = %s", desc, value)
        # reconnect

        # bluepy can only do one thing at a time, so stop scanning while trying to connect
        # this is not supported by bluepy
        #self.scanner.stop()

        try:
            self.periph.connect(dev)
            self.scanner.stop_scanning = True
        except:
            # re
            self.scanner.start()
            pass