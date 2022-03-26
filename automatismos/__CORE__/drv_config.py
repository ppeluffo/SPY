#!/usr/aut_env/bin/python3.8
'''
Created on 14 may. 2020

@author: Yosniel Cabrera

Version 1.1.2 07-06-2020
'''

import configparser
import os
from __CORE__.mypython import str2bool, str2lst            


'''
    Manejo de variables de configuracion usadas en el sistema
    
    variables de salida
        !GENERAL
        project_path            ruta en donde se encuentra la carpeta automatismos
        working_mode            modo en que se ejecuta el automatimso [ LOCAL | SPY | OSE ]
        perforationProcessPath  path en donde se encuentra el ext_call.pl que llama a las perforaciones que estan en perl
        path_log                ruta en donde van a estar los logs
        easy_log                habilita (True) o deshabilita (False) los logs de adentro de la carpeta AUTOMATISMOS/..
        allowedTypes            lista con valores que puede tener la variable de redis DLGID:TYPE para que se corra el automatismo
        
        !DATABASE
        dbUrl                url de la base de datos para realizar la conexion
'''

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))




## Lectura del config.ini
serv_APP_config = configparser.ConfigParser()
serv_APP_config.read(f"{project_path}/config.ini")

# GENERAL_CONFIG
perforationProcessPath = serv_APP_config['GENERAL_CONFIG']['perforationProcessPath']
easy_log = str2bool(serv_APP_config['GENERAL_CONFIG']['easy_log']) 
sql_config2use = serv_APP_config['GENERAL_CONFIG']['sql_config2use']
redis_config2use = serv_APP_config['GENERAL_CONFIG']['redis_config2use']
allowedTypes = str2lst(serv_APP_config['GENERAL_CONFIG']['allowedTypes'])        


# SQL_config2use
dbUrl = serv_APP_config[sql_config2use]['dbUrl']


# REDIS_config2use
rddbhost = serv_APP_config[redis_config2use]['host']




