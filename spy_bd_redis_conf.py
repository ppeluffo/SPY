#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 14:37:29 2019

@author: pablo

Importar el modulo redis a python
pip3 install redis

En este modulo manejamos la bd:1 de redis donde guardamos la configuracion de c/datalogger.
Cuando tenemos un init AUTH leemos la BD_GDA y la volcamos a la redis.
Luego, las otras veces que tenemos que leer la BD, la leemos de Redis.
De este modo no generamos tantas transacciones al disco.
Las operaciones de IN/OUT son a traves de pickle para serializar los datos.

"""

import redis
from spy_log import log
from spy_config import Config
import pickle


class RedisBdConf:

    def __init__(self, dlgid):
        '''
        Me conecto a la redis local y dejo el conector en un objeto local
        '''
        self.dlgid = dlgid
        self.connected = ''
        self.rhandle = ''
        try:
            self.rhandle = redis.Redis(host=Config['REDIS']['host'], port=Config['REDIS']['port'], db=Config['REDIS']['db_conf'], socket_connect_timeout=2 )
        except Exception as err_var:
            log(module=__name__, function='__init__', dlgid=self.dlgid, msg='RedisBdConf init ERROR !!')
            log(module=__name__, function='__init__', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))

        # Para confirmar si redis esta conectado debo hacer un ping()
        self.connected = True
        try:
            self.rhandle.ping()
        except:
            self.connected = False

    def save_conf_to_redis(self, dlg_conf ):
        '''
        Serializa el diccionario de la configuracion y lo salva en la redis con la clave el dlgid.
        Pongo un timestamp de modo que si los datos tienen mas de 1h de antiguedad, los descarto.
        '''
        pdict = pickle.dumps(dlg_conf)
        self.rhandle.set( self.dlgid, pdict)


    def get_conf_from_redis(self):
        '''
        Recupera la clave dlgid, des-serializa y obtiene el diccionario con la configuracion
        '''
        pdict = self.rhandle.get(self.dlgid)
        if pdict is not None:
            dconf = pickle.loads(pdict)
        else:
            dconf = None
        return dconf
