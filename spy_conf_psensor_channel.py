#!/usr/bin/python3 -u
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
        self.name = ''
        self.count_min = 0
        self.count_max = 0
        self.p_min = 0.0
        self.p_max = 0.0
        self.offset = 0.0


    def init_from_str(self, c_str ):
        '''
        c_str PS0:CLORO,1500,7000,0.1,50.5,3.2;
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        try:
            ( self.name, self.count_min, self.count_max, self.p_min, self.p_max, self.offset, *s )  = re.split(':|,', c_str)
            self.p_min = float(self.p_min)
            self.p_max = float(self.p_max)
            self.offset = float(self.offset)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        self.name = d.get(('PSENSOR', 'NAME'), 'X')
        self.count_min = int(d.get(('PSENSOR', 'COUNT_MIN'), 0))
        self.count_max = int(d.get(('PSENSOR', 'COUNT_MAX'), 0))
        self.p_max = float(d.get(('PSENSOR', 'PRESION_MAX'), 0))
        self.p_min = float(d.get(('PSENSOR', 'PRESION_MIN'), 0))
        self.offset = float(d.get(('PSENSOR', 'OFFSET'), 0))
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} cMin={3} cMax={4} pMin={5} pMax={6} offset={7}'.format(tag, self.id, self.name, self.count_min, self.count_max, self.p_min, self.p_max, self.offset ))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name and
            self.count_min == other.count_min and
            self.count_max == other.count_max and
            self.p_min == other.p_min and
            self.p_max == other.p_max and
            self.offset == other.offset):
            return True
        else:
            return False


    def get_response_string(self):
        response = 'PS0:%s,%d,%d,%.01f,%.01f,%.01f:' % (self.name, int(self.count_min), int(self.count_max), float(self.p_min), float(self.p_max), float(self.offset))
        return response

