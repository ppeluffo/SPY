#!/usr/aut_env/bin/python3.8
'''
CONTROL DE ERRORES EN CTRL_PpotPaysandu

Version 2.1.6 07-06-2020 12:58
''' 

## LIBRERIAS
import os


## CONEXIONES
from __CORE__.mypython import config_var, str2bool
from __CORE__.drv_logs import ctrl_logs
from __CORE__.drv_redis import Redis
from __CORE__.drv_dlg import dlg_detection
from CTRL_PpotPaysandu.PROCESS.ctrl_library import errorProcess





def error_process(LIST_CONFIG):
    
    name_function = 'ERROR_PROCESS'
    
    conf = config_var(LIST_CONFIG)
       
    #VARIABLES DE EJECUCION
    print_log = str2bool(conf.lst_get('print_log'))
    DLGID = conf.lst_get('DLGID') 
    TYPE = conf.lst_get('TYPE')         
    LOG_LEVEL =  conf.lst_get('LOG_LEVEL')        

    
    
    #VARIABLES DE CONFIGURACION
    SWITCH_OUTPUTS = str2bool(conf.lst_get('SWITCH_OUTPUTS'))
    TEST_OUTPUTS = str2bool(conf.lst_get('TEST_OUTPUTS'))
    RESET_ENABLE = str2bool(conf.lst_get('RESET_ENABLE'))
    EVENT_DETECTION = str2bool(conf.lst_get('EVENT_DETECTION'))
    TIMER_POLL = str2bool(conf.lst_get('TIMER_POLL'))
    
    ## INSTANCIAS
    #logs = ctrl_logs(TYPE,DLGID,print_log)
    logs = ctrl_logs(TYPE,'CTRL_FREC_error',DLGID,print_log,LOG_LEVEL)
    redis = Redis()
    e = errorProcess(LIST_CONFIG)

    #---------------------------------------------------------
    ##ERROR PROCESS
    logs.basicLog(__doc__)
    #logs.print_log(__doc__)
    
    # ESCRIBO LA EJECUCION DEL SCRIPT
    logs.print_inf(name_function,'')
    
    
    # MUESTRO VARIABLES DE ENTRADA
    logs.print_in(name_function, 'print_log', print_log)
    logs.print_in(name_function, 'DLGID', DLGID)
    logs.print_in(name_function, 'TYPE', TYPE)
    #
    if SWITCH_OUTPUTS: logs.print_in(name_function, 'SWITCH_OUTPUTS', SWITCH_OUTPUTS)
    if SWITCH_OUTPUTS: logs.print_in(name_function, 'TEST_OUTPUTS', TEST_OUTPUTS)
    if SWITCH_OUTPUTS: logs.print_in(name_function, 'RESET_ENABLE', RESET_ENABLE)
    if EVENT_DETECTION: logs.print_in(name_function, 'EVENT_DETECTION', EVENT_DETECTION)
    if EVENT_DETECTION: logs.print_in(name_function, 'TIMER_POLL', TIMER_POLL)
    #
    
    # ESCRIBO NUMERO DE EJECUCION
    redis.no_execution(f'{DLGID}_ERROR')
    
    # CHEQUEO ERROR TX
    logs.print_inf(name_function, 'TEST_TX_ERRORS')

    
    testTxResult = e.test_tx()          # chequeo estado de transmision del equipo

    if testTxResult != 'noLine':
        if testTxResult:
            # Condicion que se cumple cuando el equipo no presenta errores TX
            pass
                
        else:
            pass

    else:
        logs.print_inf(name_function, f'NO EXISTE VARIABLE LINE EN {DLGID}')
        logs.print_inf(name_function, f'NO SE EJECUTA {name_function}')
    
    
    
    
    
    
    
    
