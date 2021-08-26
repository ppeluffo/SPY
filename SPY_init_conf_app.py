#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_APP:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.aplicacion = dconf.get(('BASE', 'APLICACION'), 'OFF')
        self.response = ''

        # log(module=__name__, function='DEBUG init APP', dlgid=self.dlgid, msg='aplicacion:{}'.format(self.aplicacion))

        if self.fw_version >= 400:
            if self.aplicacion == 'OFF':
                self.response_app_off()
            elif self.aplicacion == 'CONSIGNA':
                self.response_app_consigna()
            elif self.aplicacion == 'PILOTO':
                self.response_app_piloto()
        else:
            # Versiones anteriores.
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
            elif self.aplicacion == 'PILOTO':
                self.response = 'AP0:PILOTO;'
            elif self.aplicacion == 'MODBUS':
                self.response = 'AP0:MODBUS;'
            else:
                self.response = 'AP0:OFF;'

        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confApp_RSP: ({})'.format(self.response))
        if self.fw_version >= 400:
            pload = 'CLASS:APP;{}'.format(self.response)
        else:
            pload = 'CLASS:APP_A;{}'.format(self.response )
        #
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def response_app_off(self):
        self.response = "OFF;"
        return

    def response_app_consigna(self):
        cons_hhmm1 = int(self.dconf.get(('CONS', 'HHMM1'), '0000'))
        cons_hhmm2 = int(self.dconf.get(('CONS', 'HHMM2'), '0000'))
        self.response = "CONSIGNA;HHMM1:%04d;HHMM2:%04d;" % ( cons_hhmm1, cons_hhmm2)
        return

    def response_app_piloto(self):
        self.response = "PILOTO;"
        hhmm_default = 0
        presion_default = 0
        #
        pulseXrev =  int(self.dconf.get(('PILOTO', 'PulseXrev'), 3000))
        pwidth = int(self.dconf.get(('PILOTO', 'pwidth'), 20))
        self.response += 'PPR:%d;PWIDTH:%d;' % (pulseXrev, pwidth)
        #
        hhmm0 = int(self.dconf.get(('PILOTO', 'HHMM0'), hhmm_default))
        if hhmm0 == '':
            hhmm0 = hhmm_default
        p0 = float(self.dconf.get(('PILOTO', 'P0'), presion_default))
        if p0 == '':
            p0 = presion_default
        self.response += 'SLOT0:%04d,%.02f;' % ( hhmm0, p0)

        hhmm1 = int(self.dconf.get(('PILOTO', 'HHMM1'), hhmm_default))
        if hhmm1 == '':
            hhmm1 = hhmm_default
        p1 = float(self.dconf.get(('PILOTO', 'P1'), presion_default))
        if p1 == '':
            p1 = presion_default
        self.response += 'SLOT1:%04d,%.02f;' % (hhmm1, p1)

        hhmm2 = int(self.dconf.get(('PILOTO', 'HHMM2'), hhmm_default))
        if hhmm2 == '':
            hhmm2 = hhmm_default
        p2 = float(self.dconf.get(('PILOTO', 'P2'), presion_default))
        if p2 == '':
            p2 = presion_default
        self.response += 'SLOT2:%04d,%.02f;' % (hhmm2, p2)

        hhmm3 = int(self.dconf.get(('PILOTO', 'HHMM3'), hhmm_default))
        if hhmm3 == '':
            hhmm3 = hhmm_default
        p3 = float(self.dconf.get(('PILOTO', 'P3'), presion_default))
        if p3 == '':
            p3 = presion_default
        self.response += 'SLOT3:%04d,%.02f;' % (hhmm3, p3)

        hhmm4 = int(self.dconf.get(('PILOTO', 'HHMM4'), hhmm_default))
        if hhmm4 == '':
            hhmm4 = hhmm_default
        p4 = float(self.dconf.get(('PILOTO', 'P4'), presion_default))
        if p4 == '':
            p4 = presion_default
        self.response += 'SLOT4:%04d,%.02f;' % (hhmm4, p4)

        log(module=__name__, function='DEBUG PILOTO SLOTS', dlgid=self.dlgid, msg='RSP={}'.format(self.response))
        return

