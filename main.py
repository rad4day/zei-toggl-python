#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from bluepy import btle
from toggl.TogglPy import Toggl
import struct
import json
import dateutil.parser
from datetime import datetime, timezone

import logging
_log = logging.getLogger(__name__)
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.INFO)


def _ZEI_UUID(short_uuid):
    print( 'c7e7%04X-c847-11e6-8175-8c89a55d403c' % (short_uuid))
    return 'c7e7%04X-c847-11e6-8175-8c89a55d403c' % (short_uuid)


class ZeiCharBase:

    def __init__(self, periph):
        self.periph = periph
        self.hndl = None

    def enable(self):
        _svc = self.periph.getServiceByUUID(self.svcUUID)
        _chr = _svc.getCharacteristics(self.charUUID)[0]
        self.hndl = _chr.getHandle()

        # this is uint16_t - see: https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
        _cccd = _chr.getDescriptors(btle.AssignedNumbers.client_characteristic_configuration)[0]
        _cccd.write(struct.pack("<H", 2), withResponse=True)


class ZeiOrientationChar(ZeiCharBase):
    svcUUID = _ZEI_UUID(0x0010)
    charUUID = _ZEI_UUID(0x0012)

    def __init__(self, periph):
        ZeiCharBase.__init__(self, periph)


class BatteryLevelChar(ZeiCharBase):
    svcUUID = btle.AssignedNumbers.battery_service
    charUUID = btle.AssignedNumbers.battery_level

    def __init__(self, periph):
        ZeiCharBase.__init__(self, periph)


class Zei(btle.Peripheral):

    def __init__(self, *args, **kwargs):
        btle.Peripheral.__init__(self, *args, **kwargs)
        self.withDelegate(ZeiDelegate(self))

        # activate notifications about turn
        self.orientation = ZeiOrientationChar(self)
        self.orientation.enable()


class ZeiDelegate(btle.DefaultDelegate):

    def __init__(self, periph):
        btle.DefaultDelegate.__init__(self)
        self.parent = periph

    def handleNotification(self, cHandle, data):
        if cHandle == 38:
            side = struct.unpack('B', data)[0]
            _log.info("Current side up is %s", side )
        else:
            _log.info("Notification from hndl: %s - %r", cHandle, data)


class ZeiDiscoveryDelegate(btle.DefaultDelegate):
    def __init__(self, scanner, periph):
        btle.DefaultDelegate.__init__(self)
        self.scanner = scanner
        self.periph = periph

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if not dev.addr == 'f1:05:a5:9c:2e:9b':
            return
        _log.info("Device %s (%s), RSSI=%d dB", dev.addr, dev.addrType, dev.rssi)
        for (adtype, desc, value) in dev.getScanData():
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


class ZeiDiscovery(btle.Scanner):

    def __init__(self, periph=None, **kwargs):
        self.zei = periph
        btle.Scanner.__init__(self, **kwargs)
        #self.withDelegate(ZeiDiscoveryDelegate(self, self.zei))
        #self.stop_scanning = False

    def reconnect(self):
        self.iface=self.zei.iface
        self.clear()
        self.start()
        while self.zei.addr not in self.scanned:
            self.process(timeout=2)
        self.stop()
        self.zei.connect(self.scanned[self.zei.addr])



class TogglDelegate(ZeiDelegate):

    def __init__(self, periph, config):
        self.config = config
        self.toggl = Toggl()
        self.toggl.setAPIKey(self.config['toggl']['settings']['token'])

        self._populateProjects()
        super().__init__(periph)

    def handleNotification(self, cHandle, data):
        if cHandle == 38:
            side = struct.unpack('B', data)[0]
            self._trackProject(self._getDescriptionBySide(side), self._getIdBySide(side), self._getTagsBySide(side))
        else:
            _log.info("Notification from hndl: %s - %r", cHandle, data)

    def _getIdBySide(self, side: int):
 
        if str(side) in self.config['mappings']:
            return self.config['mappings'][str(side)]['id']
        else:
            return 0

    def _getTagsBySide(self, side: int):
        if str(side) in self.config['mappings'] and 'tags' in self.config['mappings'][str(side)]:
            return self.config['mappings'][str(side)]['tags']
        else:
            return None

    def _getDescriptionBySide(self, side: int):
 
        if str(side) in self.config['mappings'] and 'description' in self.config['mappings'][str(side)]:
            return self.config['mappings'][str(side)]['description']
        else:
            return ''

    def _getProjectById(self, id: int):
        return self.projects[int(id)]

    def _populateProjects(self):
        self.projects = {}
        proj = (self.toggl.getWorkspaceProjects(self.config['toggl']['settings']['workspace_id']))
        NoneProj = {'id': 0, 'wid': int(self.config['toggl']['settings']['workspace_id']), 'name': 'None', 'billable': False, 'is_private': True, 'active': True, 'template': False, 'at': '2020-06-09T04:02:38+00:00', 'created_at': '2019-12-09T16:36:28+00:00', 'color': '9', 'auto_estimates': False, 'actual_hours': 0, 'hex_color': '#990099'}

        self.projects[0] = NoneProj
        for i in proj:
            self.projects[i['id']] = i

    def _trackProject(self, description: str, pid: int, tags: list):
        current = self.toggl.currentRunningTimeEntry()['data']

        if current is not None:
            if (datetime.now(timezone.utc) - dateutil.parser.isoparse(current['start'])).total_seconds() < 20:
                # Delete entry if not older than 20s
                _log.info("Abort currently running entry")
                self.toggl.deleteTimeEntry(current['id'])
            else:
                _log.info("Stopping currently running entry")
                self.toggl.stopTimeEntry(current['id'])


        _log.info("Now tracking project %s: %s (%s)", self._getProjectById(pid)['name'], description, ', '.join(tags if tags else []))
        if pid == 0:
            return
        
        self.toggl.startTimeEntry(description, pid=pid, tags=tags )
        


def main():

    # config = {
    #     'toggl': {
    #         'settings': {
    #             'token': 'XXXXX',
    #             'user_agent': 'Toggl-Zei-Py',
    #             'workspace_id': '2629429'
    #         }
    #     },
    #     'mappings': {
    #         "7": {
    #             'id': '157907853',
    #             'description': 'Test'
    #         }            
    #     }

    # }
    #json.dump(config, open('./config.json', 'w'), sort_keys=True, indent=4)
    
    config = json.load(open("./config.json", "r"))
    zei = Zei('c5:58:ed:89:90:ba', 'random', iface=0)
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
