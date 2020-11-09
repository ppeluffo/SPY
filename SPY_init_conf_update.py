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
from spy_bd_gda import BDGDA
from spy import Config

# ------------------------------------------------------------------------------

class INIT_CONF_UPDATE:
    '''
    Esta clase lee del payload la configuracion que esta mandando el datalogger
    de los canales analogicos y actualiza la BD
    '''

    def __init__(self, dlgid, version, payload_dict, dlgbdconf_dict ):
        '''
        '''
        self.dlgid = dlgid
        self.version = version
        self.payload_dict = payload_dict
        self.dlgbdconf_dict = dlgbdconf_dict
        self.response = 'OK'
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='process', dlgid=self.dlgid, msg='start')
        bd = BDGDA(modo=Config['MODO']['modo'])
        for ch in ('A0','A1','A2','A3','A4','A5','A6','A7'):
            ch_str = self.payload_dict.get(ch,'X')
            if ch_str == 'X':
                continue
            (imin,imax,mmin,mmax,_) = ch_str.split(',')
            dc={'IMIN':imin,'IMAX':imax,'MMIN':mmin,'MMAX':mmax}
            bd.update_analog(self.dlgid, ch, dc)
            log(module=__name__, function='process', dlgid=self.dlgid, msg='UPDATE: CH:{0},imin={1},iMax={2},mmin={3},mMax={4}'.format(ch,imin,imax,mmin,mmax))

        log(module=__name__, function='process', level='SELECT', dlgid=self.dlgid, msg='process_RSP: ({})'.format(self.response))
        pload = 'CLASS:UPDATE;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='process', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return




