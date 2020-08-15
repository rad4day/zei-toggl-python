#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from bluepy import btle


class ZeiDiscovery(btle.Scanner):
    def __init__(self, periph=None, **kwargs):
        self.zei = periph
        btle.Scanner.__init__(self, **kwargs)
        # self.withDelegate(ZeiDiscoveryDelegate(self, self.zei))
        # self.stop_scanning = False

    def reconnect(self):
        self.iface = self.zei.iface
        self.clear()
        self.start()
        while self.zei.addr not in self.scanned:
            self.process(timeout=2)
        self.stop()
        self.zei.connect(self.scanned[self.zei.addr])
