#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 20:51:49 2019

@author: pablo
"""

from spy_log import log
from spy_utils import u_send_response,  u_get_fw_version, u_convert_fw_version_to_str

# ------------------------------------------------------------------------------

class INIT_CONF_MODBUS:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.response = ''
        self.sla = dconf.get(('BASE', 'MBUS_SLAVE_ADDR'), '0')

        self.config_modbus_old_release()
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:APP_B;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def config_modbus_old_release(self):
        self.response += 'SLA:{0};'.format(self.sla)
        for ch in ('M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11'):
            self.name = self.dconf.get((ch, 'NAME'), 'X')
            self.addr = int(self.dconf.get((ch, 'ADDR'), '0'))
            self.size = int(self.dconf.get((ch, 'SIZE'), '0'))
            self.fcode = int(self.dconf.get((ch, 'FCODE'), '0'))
            self.tipo = self.dconf.get((ch, 'TIPO'), 'F')
            if self.tipo.upper() == 'FLOAT':
                self.tipo = 'F'
            else:
                self.tipo = 'I'

            self.response += '{0}:{1},{2},{3},{4},{5};'.format(ch, self.name, self.addr, self.size, self.fcode,
                                                               self.tipo)
        return


class INIT_CONF_MBUS_LOW:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.fw_version = u_convert_fw_version_to_str(self.version)
        self.response = ''
        self.sla = dconf.get(('BASE', 'MBUS_SLAVE_ADDR'), '0')

        self.config_modbus_new_release()
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:MBUS_LOW;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def config_modbus_new_release(self):
        sla = int(self.dconf.get(('BASE', 'MBUS_SLAVE_ADDR'), '0'))
        self.response = 'SLA:{0};'.format(sla)
        mbwt = int(self.dconf.get(('BASE', 'MBUS_WAITTIME'), '1'))
        self.response += 'MBWT:{0};'.format(mbwt)
        data_format_name = self.dconf.get(('BASE', 'MBUS_FORMAT'), 'KINCO')
        self.response += 'FORMAT:{0};'.format(data_format_name)

        for ch in range(0,7):
            mbname = 'M{}'.format(ch)
            name = self.dconf.get((mbname, 'NAME'), 'X')
            addr = int(self.dconf.get((mbname, 'ADDR'), '0'))
            size = int(self.dconf.get((mbname, 'SIZE'), '1'))
            fcode = int(self.dconf.get((mbname, 'FCODE'), '3'))
            tipo = self.dconf.get((mbname, 'TYPE'), 'U16')
            pow10 = int(self.dconf.get((mbname, 'POW10'), '0'))
            if tipo == 'U16':
                self.response += 'MB%02d:%s,%d,%d,%d,U16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I16':
                self.response += 'MB%02d:%s,%d,%d,%d,I16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'U32':
                self.response += 'MB%02d:%s,%d,%d,%d,U32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I32':
                self.response += 'MB%02d:%s,%d,%d,%d,I32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'FLOAT':
                self.response += 'MB%02d:%s,%d,%d,%d,FLOAT,%d;' % (ch, name, addr, size, fcode, pow10)
        return


class INIT_CONF_MBUS_MED:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.fw_version = u_convert_fw_version_to_str(self.version)
        self.response = ''
        #
        self.config_modbus_new_release()
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:MBUS_MED;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def config_modbus_new_release(self):
        self.response = ''
        for ch in range(7,14):
            mbname = 'M{}'.format(ch)
            name = self.dconf.get((mbname, 'NAME'), 'X')
            addr = int(self.dconf.get((mbname, 'ADDR'), '0'))
            size = int(self.dconf.get((mbname, 'SIZE'), '1'))
            fcode = int(self.dconf.get((mbname, 'FCODE'), '3'))
            tipo = self.dconf.get((mbname, 'TYPE'), 'U16')
            pow10 = int(self.dconf.get((mbname, 'POW10'), '0'))
            if tipo == 'U16':
                self.response += 'MB%02d:%s,%d,%d,%d,U16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I16':
                self.response += 'MB%02d:%s,%d,%d,%d,I16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'U32':
                self.response += 'MB%02d:%s,%d,%d,%d,U32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I32':
                self.response += 'MB%02d:%s,%d,%d,%d,I32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'FLOAT':
                self.response += 'MB%02d:%s,%d,%d,%d,FLOAT,%d;' % (ch, name, addr, size, fcode, pow10)
        return


class INIT_CONF_MBUS_HIGH:

    def __init__(self, dlgid, version, dconf ):
        self.dlgid = dlgid
        self.version = version
        self.dconf = dconf
        self.fw_version = u_convert_fw_version_to_str(self.version)
        self.response = ''
        #
        self.config_modbus_new_release()
        return

    def process(self):
        '''
        El procesamiento consiste en logear el string de respuesta y enviarlo al datalogger.
        '''
        log(module=__name__, function='get_response_string', level='SELECT', dlgid=self.dlgid, msg='confModbus_RSP: ({})'.format(self.response))
        pload = 'CLASS:MBUS_HIGH;{}'.format(self.response )
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def config_modbus_new_release(self):
        self.response = ''
        for ch in range(14,20):
            mbname = 'M{}'.format(ch)
            name = self.dconf.get((mbname, 'NAME'), 'X')
            addr = int(self.dconf.get((mbname, 'ADDR'), '0'))
            size = int(self.dconf.get((mbname, 'SIZE'), '1'))
            fcode = int(self.dconf.get((mbname, 'FCODE'), '3'))
            tipo = self.dconf.get((mbname, 'TYPE'), 'U16')
            pow10 = int(self.dconf.get((mbname, 'POW10'), '0'))
            if tipo == 'U16':
                self.response += 'MB%02d:%s,%d,%d,%d,U16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I16':
                self.response += 'MB%02d:%s,%d,%d,%d,I16,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'U32':
                self.response += 'MB%02d:%s,%d,%d,%d,U32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'I32':
                self.response += 'MB%02d:%s,%d,%d,%d,I32,%d;' % (ch, name, addr, size, fcode, pow10)
            elif tipo == 'FLOAT':
                self.response += 'MB%02d:%s,%d,%d,%d,FLOAT,%d;' % (ch, name, addr, size, fcode, pow10)
        return

