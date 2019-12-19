#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class RangeChannel():

    def __init__(self, rch_id, dlgid):
        self.dlgid = dlgid
        self.id = rch_id
        self.name = 'X'


    def init_from_str(self, c_str ):
        '''
        c_str D0:Q0,0
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        try:
            ( self.name, *s )  = re.split(':|,', c_str)
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
        self.name = d.get(('RANGE', 'NAME'), 'X')
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2}'.format(tag, self.id, self.name))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.name == other.name:
            return True
        else:
            return False


    def __ne__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name == 'X'):
            return False

        # Para el caso general
        if self.name != other.name:
            return True
        else:
            return False

    def get_response_string(self):
        response = '%s:%s;' % (self.id, self.name)
        return response

