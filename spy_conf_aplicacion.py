#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_aplicacion_channel import AplicacionChannel
from spy_log import log

# ------------------------------------------------------------------------------

class Confaplicacion:
    '''
    Crea la estructura y metodos para manejar la configuracion de los canales
    digitales.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.AP0 = AplicacionChannel(ch_id = 'AP0', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        self.AP0.init_from_payload(d)
        return


    def init_from_bd(self, d):
        self.AP0.init_from_bd(d)
        return


    def log(self, tag=''):
        self.AP0.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.AP0 == other.AP0:
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
        if self.AP0 != other.AP0:
            response += self.AP0.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confApp_RSP: {}'.format(response))
        return response

