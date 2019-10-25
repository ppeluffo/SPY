#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log
from spy_conf_aplicacion_channel_off import APP_OFF
from spy_conf_aplicacion_channel_consigna import APP_CONSIGNA
from spy_conf_aplicacion_channel_perforacion import APP_PERFORACION
from spy_conf_aplicacion_channel_tanque import APP_TANQUE
# ------------------------------------------------------------------------------
class AplicacionChannel():

    def __init__(self, ch_id, dlgid):
        self.dlgid = dlgid
        self.app_type = ''
        self.app = None


    def init_from_payload(self,d):
        '''
        CLASS:APP
        AP0:OFF

        CLASS:APP
        AP0:CONSIGNA,0630,2345
        '''
        ( self.app_type, *r ) = d.get(('AP0'),'OFF').split(',')
        if self.app_type == 'OFF':
            self.app = APP_OFF(self.dlgid)
        elif self.app_type == 'CONSIGNA':
            self.app = APP_CONSIGNA(self.dlgid)
        elif self.app_type == 'PERFORACION':
            self.app = APP_PERFORACION(self.dlgid)
        elif self.app_type == 'TANQUE':
            self.app = APP_TANQUE(self.dlgid)

        self.app.init_from_payload(d)
        return


    def init_from_bd(self, d):

        self.app_type = d.get(('BASE','APLICACION'),'OFF')
        if self.app_type  == 'OFF':
            self.app = APP_OFF(self.dlgid)
        elif self.app_type == 'CONSIGNA':
            self.app = APP_CONSIGNA(self.dlgid)
        elif self.app_type == 'PERFORACION':
            self.app = APP_PERFORACION(self.dlgid)
        elif self.app_type == 'TANQUE':
            self.app = APP_TANQUE(self.dlgid)

        self.app.init_from_bd(d)
        return


    def log(self, tag=''):
        self.app.log(tag)
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if ( self.app_type == other.app_type ) and ( self.app == other.app ) :
            return True
        else:
            return False


    def get_response_string(self):
        response = self.app.get_response_string()
        return response

