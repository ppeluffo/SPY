#!/usr/aut_env/bin/python3.8
'''
LLAMADO CON PARAMETROS A APLICACION DE CONTROL CTRL_FREC

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.3 02-05-2020 18:25
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
                'DLGID_CTRL',       'MER004',                       # ID DATALOGGER QUE EJECUTA LAS ACCIONES DE CONTROL
                'TYPE',             'CTRL_FREC',                    # [ CTRL_FREC | ]
                
                
                #VARIABLES DE CONFIGURACION
                'LOG_LEVEL',        'FULL',                         # [ BASIC | FULL ]: BASIC-> SOLO TIRA UN LOG QUE INDICA CORRIDA DEL AUTOMATISMO; FULL-> TIRA TODOS LOS LOGS
                'ENABLE_OUTPUTS',   True,                           # ACTIVA Y DESACTIVA LA ACCION DE LAS SALIDAS PARA ESTE DLGID_CTRL [ True | False]
                'TYPE_IN_FREC',     'NPN',                          # FORMA EN QUE EL VARIADOR DE VELOCIDAD DETECTA LAS ENTRADAS [ NPN (not_in)| PNP] 
                'PROGRAMMED_FREC',  '20.0/23.7/27.4/31.1/34.9/38.6/42.3/46.0',
                                                                    # FRECUENCIAS QUE SE LE PROGRAMAN AL VARIADOR DE FRECUENCIA [ frec_1/frec_2/.../frec_8 ]
                'DLGID_REF',        'MER005',                       # DATALOGGER QUE SE USA DE REFERENCIA PARA EL AUTOMATIMO
                'CHANNEL_REF',      'PMP',                          # NOMBRE DEL CANAL CON LA MEDIDA DE REFERENCIA PARA EL AUTOMATISMO
                
                # VARIABLES OPCIONALES. EN CASO DE NO USARLAS SETEAR ''
                'DLGID_REF_1',      'MER004',                       # DATALOGGER AUXILIAR QUE SE VA A USAR DE REFERENCIA EN CASO DE FALLAS DE COMUNICACION DEL PRINCIPAL
                'CHANNEL_REF_1',    'LTQA',                         # NOMBRE DEL CANAL AUXILIAR CON LA MEDIDA DE REFERENCIA PARA EL AUTOMATISMO
                                           
            ]


# CONVIERTO A STRIG
STR_CONFIG = lst2str(LIST_CONFIG)
#    
# LLAMADO DEL PROGRAMA 
os.system('{0}/serv_APP_selection.py {1}'.format(project_path,STR_CONFIG)) 

#
# CALCULO TIEMPO DE DEMORA
#print(f'control_process_frec_{LIST_CONFIG[3]} TERMINADO A {time()-gen_start_time} s')

