#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_conf_analog_channel import AnalogChannel
from spy_log import log


# ------------------------------------------------------------------------------

class Confanalog:
    '''
    Un 'paquete' analogico esta formado por hasta 8 'canales analogicos'

    Crea la estructura y metodos para manejar la configuracion de los canales
    analogicos.
    Los dataloggers pueden tener hasta 8 canales ( SPX_IO5, SPX_IO8)
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.A0 = AnalogChannel(ach_id = 'A0', dlgid = dlgid)
        self.A1 = AnalogChannel(ach_id = 'A1', dlgid = dlgid)
        self.A2 = AnalogChannel(ach_id = 'A2', dlgid = dlgid)
        self.A3 = AnalogChannel(ach_id = 'A3', dlgid = dlgid)
        self.A4 = AnalogChannel(ach_id = 'A4', dlgid = dlgid)
        self.A5 = AnalogChannel(ach_id = 'A5', dlgid = dlgid)
        self.A6 = AnalogChannel(ach_id = 'A6', dlgid = dlgid)
        self.A7 = AnalogChannel(ach_id = 'A7', dlgid = dlgid)
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario resultado del parseo del payload enviado por el datalogger.
        Las entradas de d son del tipo A0:PA,0,20,0.00,6.00
        '''
        id_list = [ 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
        ch_list = [self.A0, self.A1, self.A2, self.A3, self.A4, self.A5, self.A6, self.A7]
        for (ch_id, ch_obj) in zip(id_list, ch_list ):
            if ch_id in d.keys():
                ch_obj.init_from_str((d.get( ch_id, 'X,4,20,0.00,10.00,0.00')), True)
            else:
                ch_obj.init_from_str((d.get( ch_id, 'X,4,20,0.00,10.00,0.00')), False)

        return


    def init_from_bd(self, d):
        '''
        Recibo un diccionario resultado de leer la configuracion de
        Las entradas de d son del tipo A0:PA,0,20,0.00,6.00;
        '''
        self.A0.init_from_bd(d)
        self.A1.init_from_bd(d)
        self.A2.init_from_bd(d)
        self.A3.init_from_bd(d)
        self.A4.init_from_bd(d)
        self.A5.init_from_bd(d)
        self.A6.init_from_bd(d)
        self.A7.init_from_bd(d)
        return


    def log(self, tag=''):
        self.A0.log(tag)
        self.A1.log(tag)
        self.A2.log(tag)
        self.A3.log(tag)
        self.A4.log(tag)
        self.A5.log(tag)
        self.A6.log(tag)
        self.A7.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        self: conf_from_bd
        other: conf_from_dlg:
        '''
        #log(module=__name__, function='D_A0', level='SELECT', dlgid=self.dlgid, msg='A0: {}'.format(self.A0.presente))
        #self.A0.log()
        #other.A0.log()

        '''
        if self.A0.presente and ( self.A0 != other.A0):
            return False

        if self.A1.presente and ( self.A1 != other.A1):
            return False

        if self.A2.presente and ( self.A2 != other.A2):
            return False

        if self.A3.presente and ( self.A3 != other.A3):
            return False

        if self.A4.presente and ( self.A4 != other.A4):
            return False

        if self.A5.presente and ( self.A5 != other.A5):
            return False

        if self.A6.presente and ( self.A6 != other.A6):
            return False

        if self.A7.presente and ( self.A7 != other.A7):
            return False
        '''
        if self.A0 != other.A0:
            return False

        if self.A1 != other.A1:
            return False

        if self.A2 != other.A2:
            return False

        if self.A3 != other.A3:
            return False

        if self.A4 != other.A4:
            return False

        if self.A5 != other.A5:
            return False

        if self.A6 != other.A6:
            return False

        if self.A7 != other.A7:
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
        #log(module=__name__, function='DEBUG_A0', level='SELECT', dlgid=self.dlgid, msg='dlgA0: {}'.format(other.A0.presente))
        '''
        if other.A0.presente and (self.A0 != other.A0):
            response += self.A0.get_response_string()
            #log(module=__name__, function='DEBUG_A0', level='SELECT', dlgid=self.dlgid, msg='RSP: {}'.format(response))
        if other.A1.presente and (self.A1 != other.A1):
            response += self.A1.get_response_string()
        if other.A2.presente and (self.A2 != other.A2):
            response += self.A2.get_response_string()
        if other.A3.presente and (self.A3 != other.A3):
            response += self.A3.get_response_string()
        if other.A4.presente and (self.A4 != other.A4):
            response += self.A4.get_response_string()
        if other.A5.presente and (self.A5 != other.A5):
            response += self.A5.get_response_string()
        if other.A6.presente and (self.A6 != other.A6):
            response += self.A6.get_response_string()
        if self.A7.presente and (self.A7 != other.A7):
            response += self.A7.get_response_string()
        '''

        if (self.A0 != other.A0):
            response += self.A0.get_response_string()
            #log(module=__name__, function='DEBUG_A0', level='SELECT', dlgid=self.dlgid, msg='RSP: {}'.format(response))
        if (self.A1 != other.A1):
            response += self.A1.get_response_string()
        if (self.A2 != other.A2):
            response += self.A2.get_response_string()
        if (self.A3 != other.A3):
            response += self.A3.get_response_string()
        if (self.A4 != other.A4):
            response += self.A4.get_response_string()
        if (self.A5 != other.A5):
            response += self.A5.get_response_string()
        if (self.A6 != other.A6):
            response += self.A6.get_response_string()
        if (self.A7 != other.A7):
            response += self.A7.get_response_string()
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confanalog_RSP: {}'.format(response))
        return response
