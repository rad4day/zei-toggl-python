#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json
from TogglDelegate import TogglDelegate
from zei.Zei import Zei
from zei.ZeiDiscovery import ZeiDiscovery
import logging

_log = logging.getLogger(__name__)
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.INFO)

def main():

    config = json.load(open("./config.json", "r"))
    zei = Zei(config["zei"]["mac"], 'random', iface=0)
    zei.withDelegate(TogglDelegate(zei, config))
    scanner = ZeiDiscovery(zei)

    while True:
        try:
             zei.waitForNotifications(timeout=None)
        except Exception as e:
            _log.exception(e)
            scanner.reconnect()

    zei.disconnect()


if __name__ == "__main__":
    main()
