#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response

# ------------------------------------------------------------------------------

class INIT_CONF_DIGITAL:
    '''
    La respuesta siempre contiene los 8 canales.
    Los dataloggers pueden descartar aquellos canales que no son para ellos.
    El SPXIO5 solo configura del D0 al D4.
    '''

    def __init__(self, dlgid, version, dconf):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.response = ''

        for ch in ('D0','D1','D2','D3','D4','D5','D6','D7'):
            self.name = dconf.get((ch, 'NAME'), 'X')
            self.modo = dconf.get((ch, 'MODO'), 'NORMAL')
            self.response += '{0}:{1},{2};'.format( ch, self.name, self.modo )

        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confDigital_RSP: ({})'.format(self.response))
        pload = 'CLASS:DIGITAL;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



