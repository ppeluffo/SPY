#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response,  u_get_fw_version

# ------------------------------------------------------------------------------

class INIT_CONF_MODBUS:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.response = ''

        self.sla = dconf.get(('BASE', 'MBUS_SLAVE_ADDR'), '0')
        self.response += 'SLA:{0};'.format(self.sla)

        for ch in ('M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11'):
            self.name = dconf.get((ch, 'NAME'), 'X')
            self.addr = int(dconf.get((ch, 'ADDR'), '0'))
            self.size = int(dconf.get((ch, 'SIZE'), '0'))
            self.fcode = int(dconf.get((ch, 'FCODE'), '0'))
            self.tipo = dconf.get((ch, 'TIPO'), 'F')
            if self.tipo.upper() == 'FLOAT':
                self.tipo = 'F'
            else:
                self.tipo = 'I'

            self.response += '{0}:{1},{2},{3},{4},{5};'.format(ch, self.name, self.addr,self.size,self.fcode,self.tipo)

        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_B;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



