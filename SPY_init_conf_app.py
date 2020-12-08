#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response

# ------------------------------------------------------------------------------

class INIT_CONF_APP:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.aplicacion = dconf.get(('BASE', 'APLICACION'), 'OFF')
        self.response = ''

        # log(module=__name__, function='DEBUG init APP', dlgid=self.dlgid, msg='aplicacion:{}'.format(self.aplicacion))

        if self.aplicacion == 'OFF':
            self.response = 'AP0:OFF;'
        elif self.aplicacion == 'PERFORACION':
            self.response = 'AP0:PERFORACION;'
        elif self.aplicacion == 'TANQUE':
            self.response = 'AP0:TANQUE;'
        elif self.aplicacion == 'CONSIGNA':
            self.response = 'AP0:CONSIGNA;'
        elif self.aplicacion == 'PLANTAPOT':
            self.response = 'AP0:PLANTAPOT;'
        elif self.aplicacion == 'EXTPOLL':
            self.response = 'AP0:EXTPOLL;'
        else:
            self.response = 'AP0:OFF;'

        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confApp_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_A;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



