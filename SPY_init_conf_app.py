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
        # log(module=__name__, function='DEBUG init APP', dlgid=self.dlgid, msg='aplicacion:{0}'.format(self.aplicacion))
        #
        if self.fw_version >= 400:
            self.init_app_v400()
        else:
            self.init_app_old()
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
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def init_app_v400(self):
        '''
        Procesa la configuracion de aplicacion en la version 4.0.0
        En esta solo puede ser: OFF,CONSIGNA,PILOTO
        '''
        if self.aplicacion == 'OFF':
            self.init_app_v400_off()
        elif self.aplicacion == 'CONSIGNA':
            self.init_app_v400_consigna()
        elif self.aplicacion == 'PILOTO':
            self.init_app_v400_piloto()
        elif self.aplicacion == 'GENPULSOS':
            self.init_app_v400_genpulsos()
        else:
            self.init_app_v400_off()

    def init_app_v400_off(self):
        self.response = "OFF;"
        return

    def init_app_v400_consigna(self):
        cons_hhmm1 = int(self.dconf.get(('CONS', 'HHMM1'), '0000'))
        cons_hhmm2 = int(self.dconf.get(('CONS', 'HHMM2'), '0000'))
        self.response = "CONSIGNA;HHMM1:%04d;HHMM2:%04d;" % ( cons_hhmm1, cons_hhmm2)
        return

    def init_app_v400_genpulsos(self):
        log(module=__name__, function='init_app_v400_genpulsos', dlgid=self.dlgid, msg='aplicacion:{}'.format(self.aplicacion))
        pulsosXmt3 = int(self.dconf.get(('GENPULSOS', 'PULSOSXMT3'), '10'))
        pulso_width = int(self.dconf.get(('GENPULSOS', 'PULSOWIDTH'), '10'))
        self.response = "GENPULSOS;PULSOSXMT3:%d;PULSOWIDTH:%d;" % ( pulsosXmt3, pulso_width)
        return

    def init_app_v400_piloto(self):
        self.response = "PILOTO;"
        #
        pulseXrev =  int(self.dconf.get(('PILOTO', 'PulseXrev'), 3000))
        pwidth = int(self.dconf.get(('PILOTO', 'pwidth'), 20))
        self.response += 'PPR:%d;PWIDTH:%d;' % (pulseXrev, pwidth)
        #
        for slot in range(0,12):
            sHHMM = 'HHMM{}'.format(slot)
            hhmm =  self.dconf.get(('PILOTO', sHHMM), '0000')
            hhmm = hhmm.replace(":", "")
            hhmm = int(hhmm)
            sPRES = 'P{}'.format(slot)
            pres = float(self.dconf.get(('PILOTO', sPRES), '0'))
            if pres == '':
                pres = 0.0
            self.response += 'SLOT%d:%04d,%.02f;' % (slot, hhmm, pres)

        log(module=__name__, function='DEBUG PILOTO SLOTS', dlgid=self.dlgid, msg='RSP={}'.format(self.response))
        return

    def init_app_old(self):
        '''
        En las versiones anteriores, el paso de la aplicacion era solo un swithc a otras configuraciones
        '''
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

