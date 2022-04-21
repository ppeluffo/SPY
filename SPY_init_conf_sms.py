#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_SMS:

    def __init__(self, dlgid, version, dconf ):
        '''
        Creo la clase y relleno los campos con los datos del diccionario de la base de datos.
        Genero la salida.
        '''
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.response = ''

        # Numeros autorizados
        sms_auth_nbr0 = dconf.get(('SMS', 'SMS_AUTH_00'), '99000000')
        sms_auth_nbr1 = dconf.get(('SMS', 'SMS_AUTH_01'), '99000001')
        sms_auth_nbr2 = dconf.get(('SMS', 'SMS_AUTH_02'), '99000002')
        self.response += "NRO0:{0};NRO1:{1};NRO2:{2};".format(sms_auth_nbr0, sms_auth_nbr1, sms_auth_nbr2)
        # Diccionario de ordenes
        for i in range(1,10):
            sms_chmbus = dconf.get(('SMS','SMS_O0{}_CHMBUS'.format(i)), '-1')
            sms_text = dconf.get(('SMS', 'SMS_O0{}_TEXTO'.format(i)),'X')
            self.response += "DICT{0}:{1},{2};".format(i,sms_chmbus, sms_text )
        log(module=__name__, function='DEBUG SMS', dlgid=self.dlgid, msg='RSP:{}'.format(self.response))
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confPPotSms_RSP: ({})'.format(self.response))
        pload = 'CLASS:SMS;{}'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return



