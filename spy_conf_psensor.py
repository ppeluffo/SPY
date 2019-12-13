#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_psensor_channel import PsensorChannel
from spy_log import log


# ------------------------------------------------------------------------------

class Confpsensor:
    '''
    Crea la estructura y metodos para manejar la configuracion de los canales
    digitales.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.PS0 = PsensorChannel(ch_id = 'PS0', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo PS0:CLORO,1500,7000,0.1,50.5,3.2
        '''
        self.PS0.init_from_str((d.get('PS0', 'X,0,0,0,0,0')))
        return


    def init_from_bd(self, d):
        self.PS0.init_from_bd(d)
        return


    def log(self, tag=''):
        self.PS0.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.PS0 == other.PS0:
            return True
        else:
            return False


    def get_response_string(self, other):
        '''
        Genero el string que deberia mandarse al datalogger con la configuracion
        de los canales analogicos a reconfigurarse
        El objeto ( self) sobre el cual se llama debe ser la referencia de la BD.
        El other es el objeto con los datos del datalogger
        '''
        response = ''
        if self.PS0 != other.PS0:
            response += self.PS0.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confPsensor_RSP: {}'.format(response))
        return (response)

