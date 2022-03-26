#!/usr/aut_env/bin/python3.8
'''
LLAMADO CON PARAMETROS A APLICACION DE CONTROL CTRL_PpotPaysandu

Created on 15 apr. 2021

@author: Yosniel Cabrera

Version 1.0.0 15-04-2021 11:19
''' 

## LIBRERIAS
import os                                                   

## CONEXIONES
from mypython import lst2str, project_path
from time import time 

  
gen_start_time = time()  
                                             

LIST_CONFIG = [
                #VARIABLES DE EJECUCION
                'print_log',        True,                           # VER LOS LOGS EN CONSOLA [ True | False ]
                'DLGID_CTRL',       'CTRLPAY01',                    # ID DATALOGGER QUE EJECUTA LAS ACCIONES DE CONTROL
                              
                #VARIABLES DE CONFIGURACION
                'TYPE',             'CTRL_PpotPaysandu',            # [ CTRL_FREC | CTRL_PpotPaysandu ]
                'LOG_LEVEL',        'FULL',                         # [ BASIC | FULL ]: BASIC-> SOLO TIRA UN LOG QUE INDICA CORRIDA DEL AUTOMATISMO; FULL-> TIRA TODOS LOS LOGS
                'ENABLE_OUTPUTS',   True,                           # ACTIVA Y DESACTIVA LA ACCION DE LAS SALIDAS PARA ESTE DLGID_CTRL [ True | False]
                
            ]


# CONVIERTO A STRIG
STR_CONFIG = lst2str(LIST_CONFIG)
#    
# LLAMADO DEL PROGRAMA 
os.system('{0}/serv_APP_selection1.py {1}'.format(project_path,STR_CONFIG)) 

#
# CALCULO TIEMPO DE DEMORA
#print(f'control_process_frec_{LIST_CONFIG[3]} TERMINADO A {time()-gen_start_time} s')

