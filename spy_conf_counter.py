#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_counter_channel import CounterChannel
from spy_log import log


# ------------------------------------------------------------------------------

class Confcounter:
    '''
    Un 'paquete' contador esta formado por 2 'canales counter'
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.C0 = CounterChannel(cch_id = 'C0', dlgid = dlgid)
        self.C1 = CounterChannel(cch_id = 'C1', dlgid = dlgid)
        return

    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo C0:CNTA,1.000,100,10,0;
        '''
        id_list = [ 'C0', 'C1']
        ch_list = [self.C0, self.C1 ]
        for (ch_id, ch_obj) in zip(id_list, ch_list ):
            if ch_id in d.keys():
                ch_obj.init_from_str((d.get( ch_id, 'X,0,0,0,0')), True)
            else:
                ch_obj.init_from_str((d.get( ch_id, 'X,0,0,0,0')), False)
        return


    def init_from_bd(self, d):
        self.C0.init_from_bd(d)
        self.C1.init_from_bd(d)
        return


    def log(self, tag=''):
        self.C0.log(tag)
        self.C1.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        '''
        if self.C0.presente and ( self.C0 != other.C0):
            return False
        if self.C1.presente and ( self.C1 != other.C1):
            return False
        '''
        if ( self.C0 != other.C0):
            return False
        if ( self.C1 != other.C1):
            return False

        return True


    def get_response_string(self, other):
        '''
        Genero el string que deberia mandarse al datalogger con la configuracion
        de los canales analogicos a reconfigurarse
        El objeto ( self) sobre el cual se llama debe ser la referencia de la BD.
        El other es el objeto con los datos del datalogger
        '''
        response = ''
        '''
        if other.C0.presente and (self.C0 != other.C0):
            response += self.C0.get_response_string()
        if other.C1.presente and (self.C1 != other.C1):
            response += self.C1.get_response_string()
        '''
        if (self.C0 != other.C0):
            response += self.C0.get_response_string()
        if (self.C1 != other.C1):
            response += self.C1.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confCounter_RSP: {}'.format(response))
        return (response)
