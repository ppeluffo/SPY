#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_PSENSOR:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf

        self.name = dconf.get(('PSENSOR', 'NAME'), 'X')
        self.count_min = int(dconf.get(('PSENSOR', 'COUNT_MIN'), 0))
        self.count_max = int(dconf.get(('PSENSOR', 'COUNT_MAX'), 0))
        self.p_max = float(dconf.get(('PSENSOR', 'PRESION_MAX'), 0))
        self.p_min = float(dconf.get(('PSENSOR', 'PRESION_MIN'), 0))
        self.offset = float(dconf.get(('PSENSOR', 'OFFSET'), 0))
        self.response = 'PS0:%s,%d,%d,%.01f,%.01f,%.01f:' % (self.name, int(self.count_min), int(self.count_max), float(self.p_min), float(self.p_max), float(self.offset))
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confPsensor_RSP: ({})'.format(self.response))
        pload = 'CLASS:PSENSOR;{};'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



