import struct
from toggl.TogglPy import Toggl
from zei.ZeiDelegate import ZeiDelegate
from datetime import datetime, timezone
from Mapping import Mapping

import dateutil.parser
import logging

_log = logging.getLogger(__name__)
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.INFO)

class TogglDelegate(ZeiDelegate):

    def __init__(self, periph, config):
        self.config = config
        self.toggl = Toggl()
        self.toggl.setAPIKey(self.config['toggl']['settings']['token'])
        self._populateProjects()
        self._populateMappings(self.config['mappings'])
        super().__init__(periph)

    def handleNotification(self, cHandle, data):
        if cHandle == 38: # Side Change Notification
            side = struct.unpack('B', data)[0]
            self._trackProjectByMapping(self.mappings[side])
        else:
            _log.info("Notification from hndl: %s - %r", cHandle, data)

    def _trackProjectByMapping(self, mapping: Mapping):
        self._trackProject(description=mapping.description, pid=mapping.id, tags=mapping.tags)

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


        _log.info("Now tracking project %s: %s (%s)", self.projects[pid]['name'], description, ', '.join(tags if tags else []))
        if pid == 0:
            return
        
        self.toggl.startTimeEntry(description, pid=pid, tags=tags)
        
    def _populateMappings(self, mappings: dict):
        self.mappings = { 0: Mapping(0, 0)}
        for i in mappings:
            self.mappings[int(i)] = Mapping(int(i), int(mappings[i]["id"]))
            if "description" in mappings[i]:
                self.mappings[int(i)].description = mappings[i]["description"]
            if "tags" in mappings[i]:
                self.mappings[int(i)].tags = mappings[i]["tags"]

    def _populateProjects(self):
        self.projects = {}
        proj = (self.toggl.getWorkspaceProjects(self.config['toggl']['settings']['workspace_id']))
        NoneProj = {'id': 0, 'wid': int(self.config['toggl']['settings']['workspace_id']), 'name': 'None', 'billable': False, 'is_private': True, 'active': True, 'template': False, 'at': '2020-06-09T04:02:38+00:00', 'created_at': '2019-12-09T16:36:28+00:00', 'color': '9', 'auto_estimates': False, 'actual_hours': 0, 'hex_color': '#990099'}

        self.projects[0] = NoneProj
        for i in proj:
            self.projects[i['id']] = i