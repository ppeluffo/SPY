#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class OutputsChannel():

    def __init__(self, ch_id, dlgid):
        self.dlgid = dlgid
        self.modo = ''
        self.output_channel = ''


    def init_from_payload(self,d):
        '''
        CLASS:OUTPUTS
        MODO:OFF

        CLASS:OUTPUTS
        MODO:CONSIGNA
        CHH1:06
        CMM1:30
        CHH2:23
        CMM2:45

        CLASS:OUTPUTS
        MODO:PERF

        CLASS:OUTPUTS
        MODO:PILOTO
        STEPS:6
        BAND:0.02
        SLOT0:06,30,3.45
        SLOT1:07,30,2.45
        SLOT2:10,30,1.45
        SLOT3:12,30,2.45
        SLOT4:14,30,3.45;
        '''
        self.modo = d['MODO']
        if d['MODO'] == 'OFF':
            return
        elif d['MODO'] == 'CONSIGNA':
            from spy_conf_outputs_channel_consigna import OutConsigna
            self.output_channel = OutConsigna(self.dlgid)
            self.output_channel.init_from_payload(d)
            return

        return


    def init_from_bd(self, d):

        self.modo = d['MODO']
        if d['MODO'] == 'OFF':
            return
        elif d['MODO'] == 'CONSIGNA':
            from spy_conf_outputs_channel_consigna import OutConsigna
            self.output_channel = OutConsigna(self.dlgid)
            self.output_channel.init_from_bd(d)
            return

        return


    def log(self, tag=''):
        self.output_channel.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if self.output_channel == other.output_channel:
            return True
        else:
            return False


    def get_response_string(self):
        response = self.output_channel.response()
        return response

