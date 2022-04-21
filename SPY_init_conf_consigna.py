#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 21:43:48 2019

@author: pablo

    - El parametros DIST el datalogger lo manda como ON u OFF.
    - En la base de datos esta 0 (OFF) o 1 (ON)
    - Idem con PWRS
    * OJO con los types: Tanto al leer de la BD como del QS debo convertirlos
      al mismo tipo para que anden las comparaciones
"""

from spy_log import log
from spy_utils import u_send_response
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_CONSIGNA:
    '''
    Esta clase toma el diccionario con los datos de la base de datos y arma la respuesta completa
    correspondiente a una configuracion BASE.
    El process se encarga de formatearla y mandarla al datalogger.
    '''

    def __init__(self, dlgid, version, dconf ):
        '''
        Creo la clase y relleno los campos con los datos del diccionario de la base de datos.
        Genero la salida.
        '''
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.cons_hhmm1 = int(dconf.get(('CONS', 'HHMM1'), '0000'))
        self.cons_hhmm2 = int(dconf.get(('CONS', 'HHMM2'), '0000'))

        self.response = "HHMM1:%04d;HHMM2:%04d;" % (self.cons_hhmm1, self.cons_hhmm2)
        return


    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confConsigna_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_B;{}'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return




