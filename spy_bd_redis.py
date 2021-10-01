#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:37:29 2019

@author: pablo

Importar el modulo redis a python
pip3 install redis

"""

import redis
from spy_log import log
from spy_config import Config

# ------------------------------------------------------------------------------

class Redis():

    def __init__(self, dlgid):
        '''
        Me conecto a la redis local y dejo el conector en un objeto local
        '''
        self.dlgid = dlgid
        self.connected = ''
        self.rh = ''
        try:
            self.rh = redis.Redis(host=Config['REDIS']['host'], port=Config['REDIS']['port'], db=Config['REDIS']['db'])
            self.connected = True
        except Exception as err_var:
            log(module=__name__, function='__init__', dlgid=self.dlgid, msg='Redis init ERROR !!')
            log(module=__name__, function='__init__', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
            self.connected = False

    def create_rcd(self):
        if self.connected:
            if not self.rh.hexists(self.dlgid, 'LINE'):
                self.rh.hset(self.dlgid, 'LINE', 'NUL')
            if not self.rh.hexists(self.dlgid, 'OUTPUTS'):
                self.rh.hset(self.dlgid, 'OUTPUTS', '-1')
            if not self.rh.hexists(self.dlgid, 'RESET'):
                self.rh.hset(self.dlgid, 'RESET', 'FALSE')
            if not self.rh.hexists(self.dlgid, 'POUT'):
                self.rh.hset(self.dlgid, 'POUT', '-1')
            if not self.rh.hexists(self.dlgid, 'PSLOT'):
                self.rh.hset(self.dlgid, 'PSLOT', '-1')
            if not self.rh.hexists(self.dlgid, 'MEMFORMAT'):
                self.rh.hset(self.dlgid, 'MEMFORMAT', 'FALSE')
            if not self.rh.hexists(self.dlgid, 'MODBUS'):
                self.rh.hset(self.dlgid, 'MODBUS', 'NUL')
            if not self.rh.hexists(self.dlgid, 'BROADCAST'):
                self.rh.hset(self.dlgid, 'BROADCAST', 'NUL')

            log(module=__name__, function='create_rcd', level='SELECT', dlgid=self.dlgid, msg='Redis init rcd. OK !!')
        else:
            log(module=__name__, function='create_rcd', dlgid=self.dlgid, msg='Redis not-connected !!')

    def insert_line(self, line):
        '''
        Inserto la ultima linea de datos en la redis
        Debo agregar un TAG de la forma 100&LINE= para que los scripts de Yosniel puedan parsearlo
        '''
        TAG = 'LINE='
        line = TAG + line
        if self.connected:
            try:
                self.rh.hset(self.dlgid, 'LINE', line)
            except Exception as err_var:
                log(module=__name__, function='insert_line', dlgid=self.dlgid, msg='ERROR: Redis insert line err !!')
                log(module=__name__, function='insert_line', dlgid=self.dlgid,
                    msg='ERROR: EXCEPTION {}'.format(err_var))
        else:
            log(module=__name__, function='insert_line', dlgid=self.dlgid, msg='ERROR: Redis not-connected !!')
        return

    def get_cmd_outputs(self, fw_version=200 ):
        # SALIDAS
        response = ''
        if self.connected:
            # DOUTS
            if self.rh.hexists(self.dlgid, 'OUTPUTS'):
                outputs = int(self.rh.hget(self.dlgid, 'OUTPUTS'))
                if outputs != -1:
                    response = 'DOUTS=%s:' % outputs
            #
            self.rh.hset(self.dlgid, 'OUTPUTS', '-1')
        else:
            log(module=__name__, function='get_cmd_outputs', dlgid=self.dlgid, msg='ERROR: Redis not-connected !!')
        #
        return (response)

    def get_cmd_modbus(self,fw_version=200 ):
        '''
        Los lineas a enviar por modbus pueden estar en 2 variables de REDIS: MODBUS y BROADCAST.
        En las versiones >= 400 se usan BROADCAST.
        En las versiones anteriores usamos MODBUS.
        '''
        response = ''
        if self.connected:
            if fw_version < 400:
                # MODBUS
                # Devuelve un bytearray por lo que decode lo transforma en string
                if self.rh.hexists(self.dlgid, 'MODBUS'):
                    mbus_line = self.rh.hget(self.dlgid, 'MODBUS').decode()
                    if mbus_line != 'NUL':
                        log(module=__name__, function='get_cmd_modbus', dlgid=self.dlgid, msg='REDIS-MODBUS:{}'.format(mbus_line))
                        response = 'MBUS=%s;' % mbus_line
                self.rh.hset(self.dlgid, 'MODBUS', 'NUL')
            else:
                # BROADCAST:
                if self.rh.hexists(self.dlgid, 'BROADCAST'):
                    mbus_line = self.rh.hget(self.dlgid, 'BROADCAST').decode()
                    if mbus_line != 'NUL':
                        log(module=__name__, function='get_cmd_modbus', dlgid=self.dlgid, msg='REDIS-MODBUS-BCAST:{}'.format(mbus_line))
                        response = 'MBUS=%s;' % mbus_line
                self.rh.hset(self.dlgid, 'BROADCAST', 'NUL')
        else:
            log(module=__name__, function='get_cmd_modbus', dlgid=self.dlgid, msg='ERROR: Redis not-connected !!')
        #
        return (response)

    def get_cmd_pilotos(self,fw_version=200):
        # PILOTO
        response = ''
        if fw_version >= 400 :
            if self.connected:
                if self.rh.hexists(self.dlgid, 'PILOTO'):
                    pout = float(self.rh.hget(self.dlgid, 'PILOTO'))
                    #log(module=__name__, function='get_cmd_pilotos', dlgid=self.dlgid, msg='Redis get_cmd_pilotos. pout={}'.format(pout))
                    if pout != -1:
                        response += 'PILOTO={}:'.format(pout)
                        self.rh.hset(self.dlgid, 'PILOTO', '-1')
            else:
                log(module=__name__, function='get_cmd_pilotos', dlgid=self.dlgid, msg='ERROR: Redis not-connected !!')
        return response

    def get_cmd_reset(self):
        # RESET
        response = ''
        if self.connected:
            if self.rh.hexists(self.dlgid, 'RESET'):
                r = self.rh.hget(self.dlgid, 'RESET')
                # r es un bytes b'RESET'
                # Para usarlo en comparaciones con strings debo convertirlos a str con decode()
                reset = r.decode()
                # Ahora reset es un str NO un booleano por lo tanto comparo contra 'True'
                if reset.upper() == 'TRUE':
                    response += 'RESET:'

                self.rh.hset(self.dlgid, 'RESET', 'FALSE')
        else:
            log(module=__name__, function='get_cmd_reset', dlgid=self.dlgid, msg='ERROR: Redis not-connected !!')

        return (response)

    def insert_bcast_line(self, dlg_rem=None, redis_brodcast_line=None, fw_version=200 ):
        '''
        Inserta en la redis de los dlg remotos, la linea de modbus en la variable BROADCAST.
        Pendiente: Verificar que la version de los dlgremotos sea >= 400.
        '''
        if fw_version < 400:
            return
        if self.connected:
            if redis_brodcast_line is not None:
                self.rh.hset(dlg_rem, 'BROADCAST', redis_brodcast_line)
            else:
                elf.rh.hset(dlg_rem, 'BROADCAST', 'NUL')

    def execute_callback(self):
        '''
        True:     si existe la variable TYPE para self.dlgid en redis.
        False:    si no existe la variable TYPE en redis o existe con los siguientes valores [ 0 0.0 ''  () [] {} None ]
        '''
        # CHEQUEO SI EXISTE LA VARIABLE TYPE.
        log(module=__name__, function='execute_callback', dlgid=self.dlgid, msg='CALL_BACKS ==> CHEQUEO TYPE')
        if self.rh.hexists(self.dlgid, 'TYPE'):
            # CHEQUEO QUE TYPE TIENE VALOR COHERENTE
            if bool(self.rh.hget(self.dlgid, 'TYPE')):
                log(module=__name__, function='execute_callback', dlgid=self.dlgid, msg='CALL_BACKS ==> EXISTE TYPE')
                return True
            else:
                log(module=__name__, function='execute_callback', dlgid=self.dlgid, msg='CALL_BACKS ==> NO EXISTE TYPE')
                return False
        else:
            return False


if __name__ == '__main__':
    print('Testing Redis module')
    rd = Redis('PRUEBA')
    rd.create_rcd()
    reset = rd.rh.hget('PRUEBA', 'RESET')
    print('Reset INIT=%s' % reset)

    rd.rh.hset('PRUEBA', 'RESET', 'False')
    reset = rd.rh.hget('PRUEBA', 'RESET')
    print('Reset Rd=%s' % reset)

    if rd.rh.exists('PRUEBA2'):
        print('Prueba 2 existe')
    else:
        print('No existe')
    response = rd.get_cmd_reset()
    print('RSP=%s' % response)

#
