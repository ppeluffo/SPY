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
from spy_utils import u_send_response
from spy_bd_bdspy import BDSPY
from spy import Config
from spy_utils import u_send_response, u_convert_fw_version_to_str
# ------------------------------------------------------------------------------

class INIT_CONF_AUTH:
    '''
    Esta clase toma el diccionario con los datos de la base de datos y arma la respuesta completa
    correspondiente a una configuracion BASE.
    El process se encarga de formatearla y mandarla al datalogger.
    '''

    def __init__(self, dlgid, version, uid ):
        '''
        Creo la clase y relleno los campos con los datos del diccionario de la base de datos.
        Genero la salida.
        '''
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.uid = uid
        return

    def __str__(self):
        response = 'CONF_AUTH: dlgid={0},uid={1}'.format( self.dlgid, self.uid)
        return response

    def process(self):
        '''
        El procesamiento consiste ver si en la BDSPY hay una entrada con el DLGID y el UID.
        '''
        # log(module=__name__, function='CONF_AUTH_process', level='SELECT', dlgid=self.dlgid, msg='dlgid={0},uid={1}'.format(self.dlgid,self.uid))
        log(module=__name__, function='CONF_AUTH_process', level='SELECT', dlgid='DEBUG', msg='dlgid={0},uid={1}'.format(self.dlgid, self.uid))
        bd = BDSPY(modo = Config['MODO']['modo'])
        if bd.dlg_is_defined(self.dlgid):
            '''
            Comprende los casos ( DLGID OK, UID OK ) y
            ( DLGID OK, UID err )
            En este ultimo, arregla en la BD el UID. 
            '''
            bd.update_uid(self.dlgid, self.uid)
            pload = 'CLASS:AUTH;STATUS:OK;'
            u_send_response(self.fw_version, 'INIT', pload)
            log(module=__name__, function='CONF_AUTH_send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))

        elif bd.uid_is_defined(self.uid):
            dlgid_from_bd = bd.get_dlgid_from_uid(self.uid)
            pload = 'CLASS:AUTH;STATUS:RECONF;DLGID:{};'.format(dlgid_from_bd)
            u_send_response(self.fw_version, 'INIT', pload)
            log(module=__name__, function='CONF_AUTH_send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))

        else:
            '''
            No encontramos el DLGID ni un UID que permita recuperarnos.
            ERROR
            '''
            pload = 'CLASS:AUTH;STATUS:ERROR_DS;'
            u_send_response(self.fw_version, 'INIT', pload)
            log(module=__name__, function='CONF_AUTH_send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))

        return





