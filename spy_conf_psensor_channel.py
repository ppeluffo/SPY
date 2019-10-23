#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class PsensorChannel():

    def __init__(self, ch_id, dlgid):
        self.dlgid = dlgid
        self.id = ch_id
        self.name = 'X'
        self.pmin = 0
        self.pmax = 0
        self.poffset = 0

    def init_from_str(self, c_str ):
        '''
        c_str CLORO,0,0.7,0.002;
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        try:
            ( self.name, self.pmin, self.pmax, self.poffset, *s )  = re.split(':|,', c_str)
            self.pmin =float(self.pmin)
            self.pmax = float(self.pmax)
            self.poffset = float(self.poffset)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        self.name = d.get(('PSENS', 'NAME'), 'X')
        self.pmin = float(d.get(('PSENS', 'PMIN'), '0'))
        self.pmax = float(d.get(('PSENS', 'PMAX'), '0'))
        self.poffset = float(d.get(('PSENS', 'POFFSET'), '0'))
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} pmax={3} pmin={4} poffset={5}'.format(tag, self.id, self.name, self.pmin, self.pmax, self.poffset))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name and
            self.pmin == other.pmin and
            self.pmax == other.pmax and
            self.poffset == other.poffset ):
            return True
        else:
            return False


    def get_response_string(self):
        response = 'PS0:%s,%.03f,%.03f,%.03f;' % (self.name, self.pmin, self.pmax, self.poffset)
        return (response)

