#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response,  u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_COUNTER:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.response = ''

        for ch in ('C0','C1' ):
            self.name = dconf.get((ch, 'NAME'), 'X')
            self.magpp = float(dconf.get((ch, 'MAGPP'), 0.100))
            self.pwidth = int(dconf.get((ch, 'PWIDTH'), 10))
            self.period = int(dconf.get((ch, 'PERIOD'), 100))
            self.speed = dconf.get((ch, 'SPEED'), 'LS')
            self.edge = dconf.get((ch, 'EDGE'), 'RISE')

            if self.fw_version >= 400:
                self.response += '{0}:{1},{2},{3},{4},{5};'.format(ch, self.name, self.magpp, self.pwidth, self.period, self.edge)
            else:
                self.response += '{0}:{1},{2},{3},{4},{5},{6};'.format( ch, self.name, self.magpp, self.pwidth, self.period, self.speed,self.edge )


        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confCounter_RSP: ({})'.format(self.response))
        pload = 'CLASS:COUNTER;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



