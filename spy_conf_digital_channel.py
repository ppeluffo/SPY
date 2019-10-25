#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class DigitalChannel():

    def __init__(self, dch_id, dlgid):
        self.dlgid = dlgid
        self.id = dch_id
        self.name = 'X'
        self.tipo = 0
        self.presente = False


    def init_from_str(self, c_str, presente ):
        '''
        c_str D0:Q0,0
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        self.presente = presente
        try:
            ( self.name, self.tipo, *s )  = re.split(':|,', c_str)
            self.tipo =int(self.tipo)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        CH = self.id
        if (CH, 'NAME') in d.keys():
            self.presente = True
        else:
            self.presente = False
        self.name = d.get((CH, 'NAME'), 'X')
        self.tipo = int(d.get((CH, 'TIPO'), 0))
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} tipo={3} pres={4}'.format(tag, self.id, self.name, self.tipo, self.presente))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name and
                self.tipo == other.tipo ):
            return True
        else:
            return False


    def __ne__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        #if (self.name == other.name == 'X'):
        #    return False

        # Para el caso general
        if (self.name != other.name or
                self.tipo != other.tipo):
            return True
        else:
            return False

    def get_response_string(self):
        response = '%s:%s,%s;' % (self.id, self.name, self.tipo)
        return (response)

