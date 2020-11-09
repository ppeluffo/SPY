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
        self.response = 'SLA:0x%02x;' % int( dconf.get(('BASE','MBUS_SLAVE_ADDR'),'0'),16)
        self.response += 'M0:%s,' % (dconf.get(('M0', 'NAME'), 'X'))
        self.response += '0x%04x,' % ( int(dconf.get(('M0', 'ADDR'), '0x00'), 16) )
        self.response += '0x%02x,' % (  int(dconf.get(('M0', 'SIZE'), '0'), 16) )
        self.response += '0x%02x;' % ( int(dconf.get(('M0', 'FCODE'), '0'),16) )
        self.response += 'M1:%s,' % (dconf.get(('M1', 'NAME'), 'X'))
        self.response += '0x%04x,' % ( int(dconf.get(('M1', 'ADDR'), '0x00'), 16) )
        self.response += '0x%02x,' % (  int(dconf.get(('M1', 'SIZE'), '0'), 16) )
        self.response += '0x%02x;' % ( int(dconf.get(('M1', 'FCODE'), '0'),16) )
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:MODBUS;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



