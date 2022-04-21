#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, d_defaults, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_PPOT_LEVELS:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.response = ''

        for ch in range(6):
            CH = 'CH{}'.format(ch)
            self.response += ';{}:'.format(CH)
            for level in range(1,4):
                LVL_INF = 'A{}_INF'.format(level)
                LVL_SUP = 'A{}_SUP'.format(level)
                def_val_inf = d_defaults[CH][LVL_INF]
                def_val_sup = d_defaults[CH][LVL_SUP]

                val_inf = dconf.get((CH, LVL_INF), def_val_inf )
                if val_inf == '':
                    val_inf = def_val_inf

                val_sup = dconf.get((CH, LVL_SUP), def_val_sup )
                if val_sup == '':
                    val_sup = def_val_sup

                self.response += '{0},{1},'.format(val_inf, val_sup)

        log(module=__name__, function='DEBUG PPOT LEVELS', dlgid=self.dlgid, msg='RSP={}'.format(self.response))
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confPPotLevels_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_C{0};'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



