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
        self.modo = 'NORMAL'
        self.presente = False


    def init_from_str(self, c_str, presente ):
        '''
        c_str D0:Q0,NORMAL
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        self.presente = presente
        try:
            ( self.name, self.modo, *s )  = re.split(':|,', c_str)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        [D0][MODO]=[NORMAL]]
        [D0][NAME]=[DIN0]]
        [D1][MODO]=[TIMER]]
        [D1][NAME]=[DIN1]]
        '''
        CH = self.id
        if (CH, 'NAME') in d.keys():
            self.presente = True
        else:
            self.presente = False
        self.name = d.get((CH, 'NAME'), 'X')
        self.modo = d.get((CH, 'MODO'), 'NORMAL')
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} modo={3} pres={4}'.format(tag, self.id, self.name, self.modo, self.presente))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name and
                self.modo == other.modo ):
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
                self.modo != other.modo):
            return True
        else:
            return False

    def get_response_string(self):
        response = '%s:%s,%s;' % (self.id, self.name, self.modo)
        return (response)

