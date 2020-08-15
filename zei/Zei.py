#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from bluepy import btle
from . import ZeiOrientationChar
from . import ZeiDelegate


class Zei(btle.Peripheral):
    def __init__(self, *args, **kwargs):
        btle.Peripheral.__init__(self, *args, **kwargs)
        self.withDelegate(ZeiDelegate.ZeiDelegate(self))

        # activate notifications about turn
        self.orientation = ZeiOrientationChar.ZeiOrientationChar(self)
        self.orientation.enable()
