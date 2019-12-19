#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class APP_CONSIGNA():


    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.chhmm1 = ''
        self.chhmm2 = ''


    def init_from_payload(self, d):
        '''
        CLASS:APP
        AP0:CONSIGNA,0630,2340
         '''
        (self.app_type, self.chhmm1, self.chhmm2, *r) = d.get(('AP0'), 'CONSIGNA,0000,0000').split(',')
        return


    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        self.chhmm1 = d.get(('CONS', 'HHMM1'), '0000')
        self.chhmm2 = d.get(('CONS', 'HHMM2'), '0000')
        return


    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid, msg='{0} hhmm1={1},hhmm2={2}'.format(tag, self.chhmm1, self.chhmm2))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if ( int(self.chhmm1) == int(other.chhmm1) ) and ( int(self.chhmm2) == int(other.chhmm1) ):
            return True
        else:
            return False


    def get_response_string(self):
        response = 'AP0:CONSIGNA,{0},{1};'.format(self.chhmm1,self.chhmm2)
        return response

