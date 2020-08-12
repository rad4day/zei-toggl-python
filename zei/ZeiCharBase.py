#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from bluepy import btle
import struct


class ZeiCharBase(object):

    def __init__(self, periph):
        self.periph = periph
        self.hndl = None
        #self.svcUUID = None
        #self.charUUID = None

    # pylint: disable=E1101
    def enable(self):
        _svc = self.periph.getServiceByUUID(self.svcUUID)
        _chr = _svc.getCharacteristics(self.charUUID)[0]
        self.hndl = _chr.getHandle()

        # this is uint16_t - see: https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
        _cccd = _chr.getDescriptors(btle.AssignedNumbers.client_characteristic_configuration)[0]
        _cccd.write(struct.pack("<H", 2), withResponse=True)
