#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_digital_channel import DigitalChannel
from spy_log import log


# ------------------------------------------------------------------------------

class Confdigital:
    '''
    Crea la estructura y metodos para manejar la configuracion de los canales
    digitales.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.D0 = DigitalChannel(dch_id = 'D0', dlgid = dlgid)
        self.D1 = DigitalChannel(dch_id = 'D1', dlgid = dlgid)
        self.D2 = DigitalChannel(dch_id = 'D2', dlgid = dlgid)
        self.D3 = DigitalChannel(dch_id = 'D3', dlgid = dlgid)
        self.D4 = DigitalChannel(dch_id = 'D4', dlgid = dlgid)
        self.D5 = DigitalChannel(dch_id = 'D5', dlgid = dlgid)
        self.D6 = DigitalChannel(dch_id = 'D6', dlgid = dlgid)
        self.D7 = DigitalChannel(dch_id = 'D7', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo D0:Q0,NORMAL
        '''
        id_list = [ 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
        ch_list = [self.D0, self.D1, self.D2, self.D3, self.D4, self.D5, self.D6, self.D7]
        for (ch_id, ch_obj) in zip(id_list, ch_list ):
            if ch_id in d.keys():
                ch_obj.init_from_str((d.get( ch_id, 'X,NORMAL')), True)
            else:
                ch_obj.init_from_str((d.get( ch_id, 'X,NORMAL')), False)

        return


    def init_from_bd(self, d):
        '''
        Recibo un diccionario resultado de leer la configuracion de
        Las entradas de d son del tipo D0:Q
        '''
        self.D0.init_from_bd(d)
        self.D1.init_from_bd(d)
        self.D2.init_from_bd(d)
        self.D3.init_from_bd(d)
        self.D4.init_from_bd(d)
        self.D5.init_from_bd(d)
        self.D6.init_from_bd(d)
        self.D7.init_from_bd(d)
        return


    def log(self, tag=''):
        self.D0.log(tag)
        self.D1.log(tag)
        self.D2.log(tag)
        self.D3.log(tag)
        self.D4.log(tag)
        self.D5.log(tag)
        self.D6.log(tag)
        self.D7.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        '''
        if self.D0.presente and ( self.D0 != other.D0):
            return False
        if self.D1.presente and ( self.D1 != other.D1):
            return False
        if self.D2.presente and ( self.D2 != other.D2):
            return False
        if self.D3.presente and ( self.D3 != other.D3):
            return False
        if self.D4.presente and ( self.D4 != other.D4):
            return False
        if self.D5.presente and ( self.D5 != other.D5):
            return False
        if self.D6.presente and ( self.D6 != other.D6):
            return False
        if self.D7.presente and ( self.D7 != other.D7):
            return False
        '''
        if ( self.D0 != other.D0):
            return False
        if ( self.D1 != other.D1):
            return False
        if ( self.D2 != other.D2):
            return False
        if ( self.D3 != other.D3):
            return False
        if ( self.D4 != other.D4):
            return False
        if ( self.D5 != other.D5):
            return False
        if  (self.D6 != other.D6):
            return False
        if ( self.D7 != other.D7):
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
        if other.D0.presente and (self.D0 != other.D0):
            response += self.D0.get_response_string()
        if other.D1.presente and (self.D1 != other.D1):
            response += self.D1.get_response_string()
        if other.D2.presente and (self.D2 != other.D2):
            response += self.D2.get_response_string()
        if other.D3.presente and (self.D3 != other.D3):
            response += self.D3.get_response_string()
        if other.D4.presente and (self.D4 != other.D4):
            response += self.D4.get_response_string()
        if other.D5.presente and (self.D5 != other.D5):
            response += self.D5.get_response_string()
        if other.D6.presente and (self.D6 != other.D6):
            response += self.D6.get_response_string()
        if other.D7.presente and (self.D7 != other.D7):
            response += self.D7.get_response_string()
        '''
        if (self.D0 != other.D0):
            response += self.D0.get_response_string()
        if (self.D1 != other.D1):
            response += self.D1.get_response_string()
        if (self.D2 != other.D2):
            response += self.D2.get_response_string()
        if (self.D3 != other.D3):
            response += self.D3.get_response_string()
        if (self.D4 != other.D4):
            response += self.D4.get_response_string()
        if (self.D5 != other.D5):
            response += self.D5.get_response_string()
        if (self.D6 != other.D6):
            response += self.D6.get_response_string()
        if (self.D7 != other.D7):
            response += self.D7.get_response_string()

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid,
            msg='confbase_RSP: {}'.format(response))
        return (response)

