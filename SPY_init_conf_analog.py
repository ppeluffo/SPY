#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_ANALOG:
    '''
    La respuesta siempre contiene los 8 canales.
    Los dataloggers pueden descartar aquellos canales que no son para ellos.
    El SPXIO5 solo configura del A0 al A4.
    '''

    def __init__(self, dlgid, version, dconf):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.response = ''

        for ch in ('A0','A1','A2','A3','A4','A5','A6','A7'):
            self.name = dconf.get((ch, 'NAME'), 'X')
            self.imin = int(dconf.get((ch, 'IMIN'), 4))
            self.imax = int(dconf.get((ch, 'IMAX'), 20))
            self.mmin = float(dconf.get((ch, 'MMIN'), 0.00))
            self.mmax = float(dconf.get((ch, 'MMAX'), 10.00))
            self.offset = float(dconf.get((ch, 'OFFSET'), 0.00))

            self.response += '{0}:{1},{2},{3},{4},{5},{6};'.format( ch, self.name, int(self.imin), int(self.imax), self.mmin, self.mmax, self.offset)

            if self.fw_version >= 400 and ch == 'A4':
                break


        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confAnalog_RSP: ({})'.format(self.response))
        pload = 'CLASS:ANALOG;{}'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



