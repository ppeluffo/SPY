#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 21:43:48 2019

@author: pablo

    - El parametros DIST el datalogger lo manda como ON u OFF.
    - En la base de datos esta 0 (OFF) o 1 (ON)
    - Idem con PWRS
    * OJO con los types: Tanto al leer de la BD como del QS debo convertirlos
      al mismo tipo para que anden las comparaciones
"""

from spy_log import log
from spy_utils import u_send_response, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_BASE:
    '''
    Esta clase toma el diccionario con los datos de la base de datos y arma la respuesta completa
    correspondiente a una configuracion BASE.
    El process se encarga de formatearla y mandarla al datalogger.
    '''

    def __init__(self, dlgid, version, dconf ):
        '''
        Creo la clase y relleno los campos con los datos del diccionario de la base de datos.
        Genero la salida.
        '''
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.dconf = dconf
        self.timerpoll = int( dconf.get(('BASE', 'TPOLL'), 0))
        self.timerdial = int( dconf.get(('BASE', 'TDIAL'), 0))
        self.timepwrsensor = int( dconf.get(('BASE', 'TIMEPWRSENSOR'), 1))
        self.reporta_bateria = dconf.get(('BASE', 'BAT'), 'OFF')
        self.pwrs_modo = int( dconf.get(('BASE', 'PWRS_MODO'), 0))  # En la BD se almacena 0(off) o 1 (on). Convierto !!!
        if self.pwrs_modo == 0:
            self.pwrs_modo = 'OFF'
        else:
            self.pwrs_modo = 'ON'

        self.pwrs_start = int( dconf.get(('BASE', 'PWRS_HHMM1'), 0))
        self.pwrs_end = int( dconf.get(('BASE', 'PWRS_HHMM2'), 0))
        self.counters_hw = dconf.get(('BASE', 'HW_CONTADORES'),'OPTO')
        # Nuevos parametros incorporados en version 4.0.1a
        self.mb_ctrl_slave = int(dconf.get(('BASE', 'MBUS_CTL_SLAVE'), '0'))
        self.mb_ctrl_address = int(dconf.get(('BASE', 'MBUS_CTL_ADDR'), '0'))

        if self.fw_version >= 401:
            self.response = "TDIAL:{0};TPOLL:{1};PWST:{2};HW_CNT:{3};CTRL_SLA:{4};CTRL_ADDR:{5};".format(self.timerdial, self.timerpoll, self.timepwrsensor, self.counters_hw, self.mb_ctrl_slave, self.mb_ctrl_address)
        elif self.fw_version >= 400:
            self.response = "TDIAL:{0};TPOLL:{1};PWST:{2};HW_CNT:{3};".format(self.timerdial, self.timerpoll, self.timepwrsensor,self.counters_hw )
        else:
            self.response = "TDIAL:{0};TPOLL:{1};PWST:{2};PWRS:{3},{4},{5};HW_CNT:{6};BAT:{7}".format(self.timerdial,self.timerpoll,self.timepwrsensor,self.pwrs_modo, self.pwrs_start, self.pwrs_end, self.counters_hw,self.reporta_bateria )

        return


    def __str__(self):
        response = 'CONF_BASE: dlgid={0},tpoll={1},tdial={2},pws={3},{4},{5},timepwrsensor={6}, hw_counters={7}'.format( self.dlgid, self.timerpoll,self.timerdial,self.pwrs_modo,self.pwrs_start,self.pwrs_end,self.timepwrsensor, self.counters_hw )
        return response


    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confbase_RSP: ({})'.format(self.response))
        pload = 'CLASS:BASE;{}'.format(self.response )
        u_send_response(self.fw_version, 'INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return




