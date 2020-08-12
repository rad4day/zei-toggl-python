#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from bluepy import btle
import ZeiCharBase


# pylint: disable=E1101
class BatteryLevelChar(ZeiCharBase.ZeiCharBase):
    svcUUID = btle.AssignedNumbers.battery_service
    charUUID = btle.AssignedNumbers.battery_level

    def __init__(self, periph):
        super.__init__(self, periph)