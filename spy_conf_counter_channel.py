#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class CounterChannel():

    def __init__(self, cch_id, dlgid):
        self.dlgid = dlgid
        self.id = cch_id
        self.name = 'X'
        self.magpp = 0
        self.pwidth = 0
        self.period = 0
        self.speed = ''
        self.presente = False


    def init_from_str(self, c_str, presente ):
        '''
        c_str C0:CNTA,1.000,100,10,LS;
        Primero vemos que no sea vacio.
        Luego lo parseamos y rellenamos los campos del self.
        '''
        self.presente = presente
        try:
            ( self.name, self.magpp, self.period, self.pwidth, self.speed, *s ) = re.split(':|,', c_str)
            self.magpp = float(self.magpp)
            self.pwidth = int(self.pwidth)
            self.period = int(self.period)
        except Exception as err_var:
            log(module=__name__, function='init_from_str', level='INFO', dlgid=self.dlgid, msg='ERROR: {0}_unpack {1}'.format(self.id, c_str))
            log(module=__name__, function='init_from_str', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto CounterChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        CH = self.id
        if (CH, 'NAME') in d.keys():
            self.presente = True
        else:
            self.presente = False
        self.name = d.get((CH, 'NAME'), 'X')
        self.magpp = float(d.get((CH, 'MAGPP'), 0.100))
        self.pwidth = int(d.get((CH, 'PWIDTH'), 10))
        self.period = int(d.get((CH, 'PERIOD'), 100))
        self.speed = d.get((CH, 'SPEED'), 'LS')
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2}, magpp={3}, pwidth={4}, period={5}, speed={6} pres={7}'.format(tag, self.id, self.name,
                                                                                            self.magpp, self.pwidth,
                                                                                            self.period, self.speed, self.presente))
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
                self.magpp == other.magpp and
                self.pwidth == other.pwidth and
                self.period == other.period and
                self.speed == other.speed):
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
                self.magpp != other.magpp or
                self.pwidth != other.pwidth or
                self.period != other.period or
                self.speed != other.speed):
            return True
        else:
            return False


    def get_response_string(self):
        response = '%s:%s,%s,%s,%s,%s;' % (
        self.id, self.name, self.magpp, self.pwidth, self.period, self.speed)
        return response


