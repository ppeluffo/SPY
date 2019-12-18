#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class AnalogChannel():

    def __init__(self, ach_id, dlgid):
        self.dlgid = dlgid
        self.id = ach_id
        self.presente = False
        self.name = 'X'
        self.imin = 0
        self.imax = 0
        self.mmin = 0
        self.mmax = 0
        self.offset = 0

    def init_from_str(self, c_str, presente ):
        '''
        c_str A1:PA,0,20,0.00,6.00,0;
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        self.presente = presente
        try:
            ( self.name, self.imin, self.imax, self.mmin, self.mmax, self.offset, *s ) = re.split(':|,', c_str)
            self.imin = int(self.imin)
            self.imax = int(self.imax)
            self.mmin = float(self.mmin)
            self.mmax = float(self.mmax)
            self.offset = float(self.offset)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return

    def init_from_bd(self, d):
        '''
        self apunta a un objeto AnalogChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        CH = self.id
        if (CH, 'NAME') in d.keys():
            self.presente = True
        else:
            self.presente = False

        self.name = d.get((CH, 'NAME'), 'X')
        self.imin = int(d.get((CH, 'IMIN'), 4))
        self.imax = int(d.get((CH, 'IMAX'), 20))
        self.mmin = float(d.get((CH, 'MMIN'), 0.00))
        self.mmax = float(d.get((CH, 'MMAX'), 10.00))
        self.offset = float(d.get((CH, 'OFFSET'), 0.00))
        return

    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} imin={3} imax={4} mmin={5} mmax={6} offset={7} pres={8}'.format(tag, self.id, self.name, self.imin,
                                                                                  self.imax, self.mmin, self.mmax, self.offset, self.presente))
        return

    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        # Para los casos en que no estan definidos los canales
        #if (self.name == other.name == 'X'):
        #    return True

       # Para el caso general
        if (self.name == other.name and
                self.imin == other.imin and
                self.imax == other.imax and
                self.mmin == other.mmin and
                self.mmax == other.mmax and
                self.offset == other.offset):
            return True
        else:
            return False

    def __ne__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        # Para los casos en que no estan definidos los canales
        #if (self.name == other.name == 'X'):
        #    return False

        # Para el caso general
        if (self.name != other.name or
                self.imin != other.imin or
                self.imax != other.imax or
                self.mmin != other.mmin or
                self.mmax != other.mmax or
                self.offset != other.offset):
            return True
        else:
            return False


    def get_response_string(self):
        response = '%s:%s,%s,%s,%s,%s,%s;' % (self.id, self.name, int(self.imin), int(self.imax), self.mmin, self.mmax, self.offset )
        return (response)
