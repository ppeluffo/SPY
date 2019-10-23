#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_outputs_channel import OutputsChannel
from spy_log import log


# ------------------------------------------------------------------------------

class Confoutputs:
    '''
    Crea la estructura y metodos para manejar la configuracion de los canales
    digitales.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.OUT0 = OutputsChannel(ch_id = 'OUT0', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo
        CLASS:OUTPUTS
        MODO:OFF

        CLASS:OUTPUTS
        MODO:CONSIGNA
        CHH1:06
        CMM1:30
        CHH2:23
        CMM2:45

        CLASS:OUTPUTS
        MODO:PERF

        CLASS:OUTPUTS
        MODO:PILOTO
        STEPS:6
        BAND:0.02
        SLOT0:06,30,3.45
        SLOT1:07,30,2.45
        SLOT2:10,30,1.45
        SLOT3:12,30,2.45
        SLOT4:14,30,3.45;

        '''
        self.OUT0.init_from_payload(d)
        return


    def init_from_bd(self, d):
        self.OUT0.init_from_bd(d)
        return


    def log(self, tag=''):
        self.OUT0.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.OUT0 == other.OUT0:
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
        if self.OUT0 != other.OUT0:
            response += self.OUT0.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confOutputs_RSP: {}'.format(response))
        return response

