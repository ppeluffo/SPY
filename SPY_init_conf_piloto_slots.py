#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, d_defaults

# ------------------------------------------------------------------------------

class INIT_CONF_PILOTO_SLOTS:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.response = ''

        hhmm_default = 0
        presion_default = 0

        hhmm0 = int(dconf.get(('PILOTO', 'HHMM0'), hhmm_default))
        if hhmm0 == '':
            hhmm0 = hhmm_default
        p0 = float(dconf.get(('PILOTO', 'P0'), presion_default))
        if p0 == '':
            p0 = presion_default
        self.response += 'SLOT0:%04d,%.02f;' % ( hhmm0, p0)

        hhmm1 = int(dconf.get(('PILOTO', 'HHMM1'), hhmm_default))
        if hhmm1 == '':
            hhmm1 = hhmm_default
        p1 = float(dconf.get(('PILOTO', 'P1'), presion_default))
        if p1 == '':
            p1 = presion_default
        self.response += 'SLOT1:%04d,%.02f;' % (hhmm1, p1)

        hhmm2 = int(dconf.get(('PILOTO', 'HHMM2'), hhmm_default))
        if hhmm2 == '':
            hhmm2 = hhmm_default
        p2 = float(dconf.get(('PILOTO', 'P2'), presion_default))
        if p2 == '':
            p2 = presion_default
        self.response += 'SLOT2:%04d,%.02f;' % (hhmm2, p2)

        hhmm3 = int(dconf.get(('PILOTO', 'HHMM3'), hhmm_default))
        if hhmm3 == '':
            hhmm3 = hhmm_default
        p3 = float(dconf.get(('PILOTO', 'P3'), presion_default))
        if p3 == '':
            p3 = presion_default
        self.response += 'SLOT3:%04d,%.02f;' % (hhmm3, p3)

        hhmm4 = int(dconf.get(('PILOTO', 'HHMM4'), hhmm_default))
        if hhmm4 == '':
            hhmm4 = hhmm_default
        p4 = float(dconf.get(('PILOTO', 'P4'), presion_default))
        if p4 == '':
            p4 = presion_default
        self.response += 'SLOT4:%04d,%.02f;' % (hhmm4, p4)

        log(module=__name__, function='DEBUG PILOTO SLOTS', dlgid=self.dlgid, msg='RSP={}'.format(self.response))
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confPilotoSlots_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_B;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



