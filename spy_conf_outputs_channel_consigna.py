#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class OutConsigna():


    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.chhmm1 = ''
        self.chhmm2 = ''


    def init_from_payload(self, d):
        '''
         CLASS:OUTPUTS
        MODO:CONSIGNA
        CHH1:06
        CMM1:30
        CHH2:23
        CMM2:45
        '''
        self.chh1 = d['CHH1']
        self.cmm1 = d['CMM1']
        self.chh2 = d['CHH2']
        self.cmm2 = d['CMM2']
        return

    def init_from_bd(self, d):
        '''
        self apunta a un objeto DigitalChannel
        Por defecto si el canal no esta definido lo tomo como 'X'
        '''
        self.chhmm1 = d.get(('CONS', 'HHMM1'), '0000')
        self.chhmm2 = d.get(('CONS', 'HHMM2'), '0000')
        self.cmm2 = ''

        self.name = d.get(('PSENS', 'NAME'), 'X')
        self.pmin = float(d.get(('PSENS', 'PMIN'), '0'))
        self.pmax = float(d.get(('PSENS', 'PMAX'), '0'))
        self.poffset = float(d.get(('PSENS', 'POFFSET'), '0'))
        return

    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} id={1}: name={2} pmax={3} pmin={4} poffset={5}'.format(tag, self.id, self.name, self.pmin,
                                                                            self.pmax, self.poffset))
        return

    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if (self.name == other.name and
                self.pmin == other.pmin and
                self.pmax == other.pmax and
                self.poffset == other.poffset):
            return True
        else:
            return False

    def get_response_string(self):
        response = 'PS0:%s,%.03f,%.03f,%.03f;' % (self.name, self.pmin, self.pmax, self.poffset)
        return (response)

