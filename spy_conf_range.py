#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_range_channel import RangeChannel
from spy_log import log

# ------------------------------------------------------------------------------

class Confrange:
    '''
    Crea la estructura y metodos para manejar la configuracion de los canales
    digitales.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.R0 = RangeChannel(rch_id = 'R0', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo R0:DIST1;
        '''
        self.R0.init_from_str((d.get('R0', 'X,0')))
        return


    def init_from_bd(self, d):
        '''
        Recibo un diccionario resultado de leer la configuracion de
        Las entradas de d son del tipo D0:Q
        '''
        self.R0.init_from_bd(d)
        return


    def log(self, tag=''):
        self.R0.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.R0 == other.R0:
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
        if self.R0 != other.R0:
            response += self.R0.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confRange_RSP: {}'.format(response))
        return (response)

