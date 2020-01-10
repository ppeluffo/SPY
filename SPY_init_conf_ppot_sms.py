#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response

# ------------------------------------------------------------------------------

class INIT_CONF_PPOT_SMS:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.response = ''

        level_default = 1
        for i in range(9):
            name = 'SMS{}'.format(i)
            nivel = 'NV_SMS{}'.format(i)
            nro_default = '099' + str(i) * 6

            SMS_nro = dconf.get(('PPOT', name), nro_default)
            if SMS_nro == '':
                SMS_nro = nro_default
            SMS_nivel = dconf.get(('PPOT', nivel), level_default)
            if SMS_nivel == '':
                SMS_nivel = level_default

            level_default += 1
            if level_default > 3:
                level_default = 1

            log(module=__name__, function='DEBUG PPOT SMS', dlgid=self.dlgid, msg='name={0},nivel={1},SMS_nro={2}, SMS_nivel={3}'.format(name,nivel, SMS_nro,SMS_nivel  ))
            self.response += "SMS0{0}:{1},{2};".format(i, SMS_nro, SMS_nivel)

        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confPPotSms_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_B;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



