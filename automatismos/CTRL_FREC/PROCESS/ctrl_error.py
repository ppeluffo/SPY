#!/usr/aut_env/bin/python3.8
'''
CONTROL DE ERRORES EN CTRL_FREC

Version 2.1.6 07-06-2020 12:58

''' 

## LIBRERIAS
import os


## CONEXIONES
from __CORE__.mypython import config_var, str2bool
from __CORE__.drv_logs import ctrl_logs
from __CORE__.drv_redis import Redis
from __CORE__.drv_dlg import dlg_detection




def error_process(LIST_CONFIG):
    
    name_function = 'ERROR_PROCESS'
    
    conf = config_var(LIST_CONFIG)
    
    #VARIABLES DE EJECUCION
    print_log = str2bool(conf.lst_get('print_log'))
    DLGID = conf.lst_get('DLGID') 
    TYPE = conf.lst_get('TYPE')      
    LOG_LEVEL = conf.lst_get('LOG_LEVEL')            
    
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
    #
    # INSTANCIA DE error_process
    import importlib.util
    #spec = importlib.util.spec_from_file_location("archivo", f"../{TYPE}/PROCESS/ctrl_library.py")
    spec = importlib.util.spec_from_file_location("archivo", f"/datos/cgi-bin/spx/AUTOMATISMOS/{TYPE}/PROCESS/ctrl_library.py")
    archivo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archivo)
    e = archivo.error_process(LIST_CONFIG)
    
    
    
    #---------------------------------------------------------
    ##ERROR PROCESS
    
    #logs.print_log(__doc__)
    logs.basicLog(__doc__)
    
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
            # LLAMAO A FUNCIONES QUE SOLO CORREN CON DATALOGGER 8CH Y SIN ERRORES TX
            if dlg_detection(DLGID) == '8CH':
                #
                # DETECCION DE EVENTOS
                logs.print_inf(name_function, 'EVENT_DETECTION')
                e.event_detection()
                #
                # ALTERNO LAS SALIDAS
                logs.print_inf(name_function, 'SWITCH_OUTPUTS')
                e.switch_outputs()
                #
                # TESTEO LAS SALIDAS
                logs.print_inf(name_function, 'TEST_OUTPUTS')
                state_test_outputs = e.test_outputs()
                #
                # PREPARO VARIABLES DE TIEMPO QUE SE MUESTRAN EN LA VISUALIZACION
                logs.print_inf(name_function, 'PUMP1_TIME')
                e.pump_time('BR1',1)
                #
            elif dlg_detection(DLGID) == '5CH':
                # DATALOGGER DE 5CH DETECTADO
                #
                logs.print_inf(name_function, 'DLG 5CH NO SE DETECTAN EVENTOS')
                logs.print_inf(name_function, 'DLG 5CH NO SE ALTERNAN SALIDAS')
                
            else:
                # NO SE DETECTA EL TIPO DE DATALOGGER
                #
                logs.print_inf(name_function, 'NO SE DETECTA EL TIPO DE DATALOGGER')
                logs.script_performance(f'{name_function} => NO SE DETECTA EL TIPO DE DATALOGGER')
        else:
            logs.print_inf(name_function, 'NO SE DETECTAN EVENTOS POR ERROR TX')
    else:
        logs.print_inf(name_function, f'NO EXISTE VARIABLE LINE EN {DLGID}')
        logs.print_inf(name_function, f'NO SE EJECUTA {name_function}')        
    #
    logs.print_inf(name_function, 'VISUAL')
    e.visual()
    #
    
    
    
    
    
    
    
    
    
