#!/usr/bin/env python3
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

# ------------------------------------------------------------------------------

class Confbase:
    '''
    Crea la estructura y metodos para manejar la configuracion base de todo
    datalogger.
    imei
    version
    uid
    '''

    def __init__(self, dlgid):
        self.dlgid = dlgid
        self.timerpoll = 0
        self.timerdial = 0
        self.aplicacion = ''
        self.pwrs_modo = ''
        self.pwrs_start = 0
        self.pwrs_end = 0
        return


    def init_from_payload(self, d):
        '''
        Recibo un diccionario con los datos de la configuracion base que trae el datalogger en el payload.
        TDIAL:1800;
        TPOLL:60;
        PWRS_MODO:ON;
        PWRS_START:2330;
        PWRS_END:645
        '''
        self.timerpoll = int(d.get('TPOLL', '0'))
        self.timerdial = int(d.get('TDIAL', '0'))
        self.aplicacion = d.get('APP', 'OFF')
        self.pwrs_modo = d.get('PWRS_MODO','OFF')           # El datalogger manda ON u OFF
        self.pwrs_start = int(d.get('PWRS_START','0'))
        self.pwrs_end = int(d.get('PWRS_END','0'))


    def init_from_bd(self, d):
        self.timerpoll = int(d.get(('BASE', 'TPOLL'), 0))
        self.timerdial = int(d.get(('BASE', 'TDIAL'), 0))
        self.aplicacion = d.get(('BASE', 'APLICACION'), 'OFF')

        self.pwrs_modo = int(d.get(('BASE', 'PWRS_MODO'), 0))   # En la BD se almacena 0(off) o 1 (on). Convierto !!!
        if self.pwrs_modo == 0:
            self.pwrs_modo = 'OFF'
        else:
            self.pwrs_modo = 'ON'

        self.pwrs_start = int(d.get(('BASE', 'PWRS_HHMM1'), 0))
        self.pwrs_end = int(d.get(('BASE', 'PWRS_HHMM2'), 0))


    def __str__(self):
        response = 'CONF_BASE: dlgid={0},tpoll={1},tdial={2},app={3},pws={4},{5},{6}'.format( self.dlgid, self.timerpoll,self.timerdial,self.aplicacion, self.pwrs_modo,self.pwrs_start,self.pwrs_end )
        return response


    def log(self, tag=''):
        '''
        Los datos de un frame init ya sean del query string o de la BD quedan
        en un dict.
        Aqui los logueo en 2 formatos:
            corto: solo los parametros que se van a usar para reconfigurar
            largo: todos los parametros ( incluso los que son solo informativos )
        '''
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} tpoll={1}'.format(tag, self.timerpoll))
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} tdial={1}'.format(tag, self.timerdial))
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} app={1}'.format(tag, self.aplicacion))
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} pwrs_modo={1}'.format(tag, self.pwrs_modo))
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} pwrs_start={1}'.format(tag, self.pwrs_start))
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid,
            msg='{0} pwrs_end={1}'.format(tag, self.pwrs_end))
        return


    def __eq__(self, other):
        '''
        Overload de la comparacion donde solo comparo los elementos necesarios
        '''
        if ( self.timerpoll == other.timerpoll and
                self.timerdial == other.timerdial and
                self.aplicacion == other.aplicacion and
                self.pwrs_modo == other.pwrs_modo and
                self.pwrs_start == other.pwrs_start and
                self.pwrs_end == other.pwrs_end ):
            return True
        else:
            return False


    def get_response_string(self, other):
        '''
        Genero el string que deberia mandarse al datalogger con la configuracion
        en la BD del piloto para ese dlgid
        El objeto sobre el cual se llama debe ser la referencia de la BD.
        El 'other' es el objeto con los datos del datalogger
        '''
        response = ''
        if self.timerpoll != other.timerpoll:
            response += ';TPOLL:%s' % self.timerpoll

        if self.timerdial != other.timerdial:
            response += ';TDIAL:%s' % self.timerdial

        if self.aplicacion != other.aplicacion:
            response += ';APP:%s' % self.aplicacion

        if (self.pwrs_modo != other.pwrs_modo or
                self.pwrs_start != other.pwrs_start or
                self.pwrs_end != other.pwrs_end):
            response += ';PWRS:%s,%d,%d' % (self.pwrs_modo, self.pwrs_start, self.pwrs_end)

        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confbase_RSP: {}'.format(response))
        return response




