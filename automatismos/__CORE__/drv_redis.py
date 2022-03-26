#!/usr/aut_env/bin/python3.8
'''
DRIVER PARA EL TRABAJO CON REDIS

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.2 06-07-2020
''' 

import redis
from drv_config import rddbhost

class Redis(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.connected = 'NULL'
        self.rh = 'NULL'
        try:
            #self.rh = redis.Redis('localhost')
            self.rh = redis.Redis(rddbhost)
            self.connected = True
        except Exception as err_var:
            #print(module=__name__, function='__init__', dlgid=self.dlgid, msg='Redis init ERROR !!')
            #print(module=__name__, function='__init__', dlgid=self.dlgid, msg='EXCEPTION {}'.format(err_var))
            print(err_var)
            self.connected = False

    def hset (self,key,param,value):
        if self.connected:
            self.rh.hset( key, param, value)
            
    def hget (self,key,param):
        if self.connected:
            if self.rh.hexists(key, param): 
                value = self.rh.hget(key, param)
                return value.decode()
            else: return None
            
    def hexist(self,key, param): 
        if self.connected: return self.rh.hexists(key, param) 
        
    def hdel (self,key,param):
        if self.connected:
            if self.rh.hexists(key, param): self.rh.hdel( key, param)
    
    def no_execution(self,key):
        if self.connected:  
            if not(self.rh.hexists(key, 'no_execution')):
                self.rh.hset( key, 'no_execution', 0)
            else:
                no_execution = int(self.rh.hget(key, 'no_execution'))
                no_execution += 1
                self.rh.hset(key, 'no_execution', no_execution)
                
    def del_key(self,key):
        if self.connected:
            self.rh.delete(key)
            
    
            