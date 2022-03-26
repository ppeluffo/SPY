#!/usr/aut_env/bin/python3.8
'''
CTRL_FREC

Version 1.0.0 15-04-2021 11:19
''' 


## LIBRERIAS
import sys
import os
import configparser

## CONEXIONES
from CTRL_FREC.PROCESS.drv_visual import dic
from __CORE__.drv_redis import Redis
from __CORE__.drv_logs import ctrl_logs
from __CORE__.mypython import str2bool, config_var
from __CORE__.drv_dlg import emerg_system, read_param
from time import time  
from __CORE__.drv_config import serv_APP_config
from CTRL_FREC.PROCESS.ctrl_library import ctrlProcess

ctrl_start_time = time() 



def control_process(LIST_CONFIG):
    ''''''
    
    name_function = 'CONTROL_PROCESS'
    
    conf = config_var(LIST_CONFIG)
    
    # VARIABLES DE EJECUCION
    DLGID_CTRL = conf.lst_get('DLGID_CTRL') 
    TYPE = conf.lst_get('TYPE')                  
    print_log = str2bool(conf.lst_get('print_log'))
    LOG_LEVEL = conf.lst_get('LOG_LEVEL')
    
    #VARIABLES DE CONFIGURACION
    ENABLE_OUTPUTS = str2bool(conf.lst_get('ENABLE_OUTPUTS'))
    TYPE_IN_FREC = conf.lst_get('TYPE_IN_FREC')
    DLGID_REF = conf.lst_get('DLGID_REF')   
    CHANNEL_REF = conf.lst_get('CHANNEL_REF') 
    DLGID_REF_1 = conf.lst_get('DLGID_REF_1')   
    CHANNEL_REF_1 = conf.lst_get('CHANNEL_REF_1') 

    
    ## INSTANCIAS
    logs = ctrl_logs(TYPE,'CTRL_FREC_process',DLGID_CTRL,print_log,LOG_LEVEL)
    config = configparser.ConfigParser()
    redis = Redis()
    #gda = GDA(serv_APP_config['CONFIG']['working_mode'])
    
    redis.no_execution('MER004')
    
    '''
    # INSTANCIA DE error_process
    import importlib.util
    #spec = importlib.util.spec_from_file_location("archivo", f"../{TYPE}/PROCESS/ctrl_library.py")
    spec = importlib.util.spec_from_file_location("archivo", f"/datos/cgi-bin/spx/AUTOMATISMOS/{TYPE}/PROCESS/ctrl_library.py")
    archivo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archivo)
    p = archivo.ctrl_process(LIST_CONFIG)'''

    p = ctrlProcess(LIST_CONFIG)

    
    # OBTENFO LA CARPETA EN DONDE SE ENCUENTRA EL ARCHIVO ACTUAL
    current_path = os.path.dirname(os.path.abspath(__file__))
    # LEO EL ARCHIVO DE CONFIGURACION
    config.read(f"{current_path}/ctrl_config.ini")
    
    #---------------------------------------------------------
    ##PROCESS
    
    logs.basicLog(__doc__)
    
    # ESCRIBO LA EJECUCION DEL SCRIPT
    logs.print_log(f"{name_function}")
   
    #logs.script_performance(f"{name_function}")
    
    
    
    
    # MUESTRO VARIABLES DE ENTRADA
    logs.print_in(name_function, 'print_log', print_log)
    logs.print_in(name_function, 'DLGID_CTRL', DLGID_CTRL)
    logs.print_in(name_function, 'TYPE', TYPE)
    logs.print_in(name_function, 'ENABLE_OUTPUTS', ENABLE_OUTPUTS)
    logs.print_in(name_function, 'TYPE_IN_FREC', TYPE_IN_FREC)
    logs.print_in(name_function, 'DLGID_REF', DLGID_REF)
    logs.print_in(name_function, 'CHANNEL_REF', CHANNEL_REF)
    logs.print_in(name_function, 'DLGID_REF_1', DLGID_REF_1)
    logs.print_in(name_function, 'CHANNEL_REF_1', CHANNEL_REF_1)
    
    
    # ESCRIBO NUMERO DE EJECUCION
    #redis.no_execution(DLGID_CTRL)
    
    
    # CHEQUEO QUE EXISTAN LOS LINES DEL DATALOGGER DE CONTROL Y EL DE REFERENCIA.
    if not(redis.hexist(DLGID_CTRL,'LINE')): 
        #logs.script_performance(f'{name_function} ==> NO EXISTE LINE {DLGID_CTRL}')
        logs.print_inf(name_function,f'NO EXISTE LINE {DLGID_CTRL}')
        logs.print_inf(name_function,'EJECUCION INTERRUMPIDA')
        quit()
    
    if not(redis.hexist(DLGID_REF,'LINE')): 
        #logs.script_performance(f'NO EXISTE LINE {DLGID_REF}')
        logs.print_inf(name_function,f'NO EXISTE LINE {DLGID_REF}')
        logs.print_inf(name_function,'EJECUCION INTERRUMPIDA')
        quit()
    
    #
    logs.print_inf(name_function, 'CHEQUEO_ALARMAS')
    p.chequeo_alarmas()
    #
    #logs.print_inf(name_function, 'CHEQUEO_SENSOR')   
    #p.chequeo_sensor()
    #
    logs.print_inf(name_function, 'MAIN')   
    
    # FUNCION MAIN
    name_function = 'MAIN'
    
    # CONDICIONES INICIALES
    #
    ## ACTIVO BANDERA PARA QUE control_error NOTIFIQUE QUE SE ESTA TRABAJANDO CON REFERENCIA_1
    redis.hset(DLGID_CTRL, 'flag_work_syst_ref_1','NO')
    
    
    # REVISO SI ESTA TRABAJANDO EN MODO LOCAL EN EL TABLERO
    if read_param(DLGID_CTRL,'LM') == '1': 
        logs.print_inf(name_function, 'TRABAJO EN MODO LOCAL')
        redis.hset(DLGID_CTRL, 'LOCAL_MODE', 'SI')    
    elif read_param(DLGID_CTRL,'LM') == '0':
        redis.hset(DLGID_CTRL, 'LOCAL_MODE', 'NO')    #VISUALIZACION
        #
        # SI NO EXISTE LA VARIABLE DE SELECCION SW1 LA CREO CON VALOR AUTO
        if not(redis.hexist(DLGID_CTRL, dic.get_dic('WEB_MODE', 'name'))): 
            redis.hset(DLGID_CTRL, dic.get_dic('WEB_MODE', 'name'), dic.get_dic('WEB_MODE', 'True_value'))
            # MUESTRO LOGS DE ADVERTENCIA
            logs.print_inf(name_function, 'NO EXISTE LA VARIABLE SW1 EN REDIS')
            logs.print_inf(name_function, 'SE CREA LA VARIABLE CON VALOR [0]'.format(dic.get_dic('WEB_MODE', 'True_value')))
            #logs.script_performance('error in [0] [1] = ,'.format(name_function,dic.get_dic('WEB_MODE', 'name')))
            #logs.script_performance('error in [0], SE CREA [1] = [2]'.format(name_function,dic.get_dic('WEB_MODE', 'name'),dic.get_dic('WEB_MODE', 'True_value')))
        #
        # LEO VAERIABLE WEB_MODE
        WEB_MODE = redis.hget(DLGID_CTRL, dic.get_dic('WEB_MODE', 'name'))
        
        
        # REVISO EL MODO DE TRABAJO WEB
        if WEB_MODE == 'REMOTO':
            logs.print_inf(name_function, 'TRABAJO EN MODO REMOTO')
            p.modo_remoto()
            
        elif WEB_MODE in [dic.get_dic('WEB_MODE', 'value_1'), dic.get_dic('WEB_MODE', 'value_1'), ]:
            logs.print_inf(name_function, 'TRABAJO EN MODO SISTEMA DE EMERGENCIA')
            # REVISO EL ESTADO DE ENABLE_OUTPUTS
            if ENABLE_OUTPUTS:
                emerg_system(DLGID_CTRL)
            else:
                logs.print_inf(name_function, f"SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {ENABLE_OUTPUTS}]")    
                #logs.script_performance(f"{name_function} ==> SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {ENABLE_OUTPUTS}]")
            
        elif WEB_MODE == 'AUTO':
            logs.print_inf(name_function, 'TRABAJO EN MODO AUTOMATICO')
            #
            # SI NO EXISTE LA VARIABLE TX_ERROR EN DLGID_REF LA CREO CON VALOR NO
            if not(redis.hexist(DLGID_REF, dic.get_dic('TX_ERROR', 'name'))): 
                redis.hset(DLGID_REF, dic.get_dic('TX_ERROR', 'name'), dic.get_dic('TX_ERROR', 'False_value'))
            #
            # LEO MAG_REF SELECCIONADA POR EL CLIENTE. SI NO EXISTE LMIN LO CREO CON VALOR 1
            if not(redis.hexist(DLGID_CTRL, dic.get_dic('MAG_REF', 'name'))): 
                redis.hset(DLGID_CTRL, dic.get_dic('MAG_REF', 'name'), dic.get_dic('MAG_REF', 'True_value'))
            else:
                MAG_REF = float(redis.hget(DLGID_CTRL, dic.get_dic('MAG_REF', 'name')))
                
            
            # LEO TX_ERROR Y # error_1min
            TX_ERROR = redis.hget(DLGID_REF, dic.get_dic('TX_ERROR', 'name'))
            error_1min = redis.hget(DLGID_REF,'error_1min')
                                         
            # CHEQUEO ERROR TX EN EL DLG DE REFERENCIA (SE DECLARA ERROR_TX CUANDO PASAN 10 MIN SIN TRANSMITIR)
            if TX_ERROR == 'SI':
                logs.print_inf(name_function, f'ERROR TX EN SISTEMA DE REFERENCIA [ {DLGID_REF} ]')
                #logs.print_inf(name_function, 'AUTOMATISMO TRABAJADO CON SISTEMA DE EMERGENCIA')
                #
                # CHEQUEO QUE SE HAYA ESCRITO LA DIFERENCIA EN MAGNITUD ENTRE LOS SENSORES
                if redis.hexist(DLGID_CTRL,'delta_ref1_ref'):
                    #
                    # LEO LA DIFERENCIA ENTRE LAS MAGNITUDES DE REFERENCIA
                    delta_ref1_ref = float(redis.hget(DLGID_CTRL,'delta_ref1_ref'))
                    #
                    # CHEQUEO EL ESTADO DEL SENSOR DE REFERENCIA 1
                    if not(p.chequeo_sensor(DLGID_REF_1,CHANNEL_REF_1)):
                        logs.print_inf(name_function, 'ERROR DE SENSOR EN SISTEMA DE REFERENCIA 1')
                        logs.print_inf(name_function, 'AUTOMATISMO TRABAJADO CON SISTEMA DE EMERGENCIA')
                        emerg_system(DLGID_CTRL)
                    else:
                        logs.print_inf(name_function, 'AUTOMATISMO TRABAJADO CON SISTEMA DE REFERENCIA 1')
                        #
                        # ACTIVO BANDERA PARA QUE control_error NOTIFIQUE QUE SE ESTA TRABAJANDO CON REFERENCIA_1
                        redis.hset(DLGID_CTRL, 'flag_work_syst_ref_1','SI')
                        #
                        # LLAMO AL CONTROL DEL SISTEMA
                        p.control_sistema(DLGID_REF_1,CHANNEL_REF_1,MAG_REF + delta_ref1_ref)
                #
                else:
                    logs.print_inf(name_function, 'AUTOMATISMO TRABAJADO CON SISTEMA DE EMERGENCIA')
                    emerg_system(DLGID_CTRL)
                    
            elif TX_ERROR == 'NO':
                # ME ASEGURO QUE LA REFENCIA ME HAYA MANDADO UN DATO NUEVO 
                if error_1min == 'NO':
                    # CHEQUEO ERROR EN EL SENSOR
                    if not(p.chequeo_sensor(DLGID_REF,CHANNEL_REF)):
                        logs.print_inf(name_function, 'ERROR DE SENSOR EN SISTEMA DE REFERENCIA')
                        logs.print_inf(name_function, 'AUTOMATISMO TRABAJADO CON SISTEMA DE EMERGENCIA')
                        #
                        emerg_system(DLGID_CTRL)
                    else:
                        logs.print_inf(name_function, 'CONTROL_SISTEMA')
                        p.control_sistema(DLGID_REF,CHANNEL_REF,MAG_REF)
                        #
                        logs.print_inf(name_function, 'DELTA_MAG')
                        p.delta_mag()
                else:
                    logs.print_inf(name_function, 'EN ESPERA DE DATOS DE LA REFERENCIA')
                        
            else:
                logs.print_inf(name_function, "error in [0], [1] = [2]".format(name_function,dic.get_dic('TX_ERROR', 'name'),TX_ERROR))
                # DEJAR REGISTRO DEL ERROR
                #logs.script_performance("error in [0], [1] = [2]".format(name_function,dic.get_dic('TX_ERROR', 'name'),TX_ERROR))
            #
        else:
            logs.print_inf(name_function, 'error in [0], [1] = [2]'.format(name_function,dic.get_dic('WEB_MODE', 'name'),WEB_MODE))
            # DEJAR REGISTRO DEL ERROR
            #logs.script_performance('error in [0], [1] = [2]'.format(name_function,dic.get_dic('WEB_MODE', 'name'),WEB_MODE))
            
    else:
        logs.print_inf(name_function, f"error in {name_function}, LM = {read_param(DLGID_CTRL,'LM')}")
        logs.print_inf(name_function,'EJECUCION INTERRUMPIDA')
        # DEJAR REGISTRO DEL ERROR
        #logs.script_performance(f"error in {name_function}, LM = {read_param(DLGID_CTRL,'LM')}")
            
    # LATCHEO LAS SALIDAS
    p.latch__outpust(DLGID_CTRL)
    
    # PREPARO DATA_DATE_TIME PARA MOSTRAR EN LA VISUALIZACION EN EL DATALOGGER DE CONTROL
    logs.print_inf(name_function, 'SHOW_DATA_DATE_TIME')
    p.show_DATA_DATE_TIME(DLGID_CTRL)
    
    # PREPARO DATA_DATE_TIME PARA MOSTRAR EN LA VISUALIZACION EN EL DATALOGGER DE REFERENCIA
    p.show_DATA_DATE_TIME(DLGID_REF)
    
    # PREPARO PUMP1_STATE PARA MOSTRAR EL ESTADO DE LA BOMBA
    logs.print_inf(name_function, 'SHOW_PUMP1_STATE')
    p.show_pump1_state('BR1')
    
    # MUESTRA LA FRECUENCIA ACTUAL A LA QUE SE ESTA TRABAJANDO 
    logs.print_inf(name_function, 'SHOW_WORK_FREQUENCY')
    p.show_work_frequency()
    
    #
    # CALCULO TIEMPO DE DEMORA
    #print('')
    #print('TIME_ALALYSIS')
    #print(f'ctrl_process_frec TERMINADO A {time()-ctrl_start_time} s') 
    
    
        
        
        
## VARIABLES DEL SCRIPT PARA EJECUCION LOCAL       
if __name__ == '__main__':
    # PREPARO EL SCRIPT PARA LLAMADA LOCAL. SE TOMA LA CONFIGURACION ESCRITA AL INICIO
    LIST_CONFIG = [
                #VARIABLES DE EJECUCION
                'print_log',        True,                          # VER LOS LOGS EN CONSOLA [ True | False ]
                'DLGID_CTRL',       'MER007',                      # ID DATALOGGER QUE EJECUTA LAS ACCIONES DE CONTROL
                'TYPE',             'FREC',                        # CUANDO TIENE LE VALOR CHARGE SE CARGA LA CONFIGURACION DE LA db
                
                
                #VARIABLES DE CONFIGURACION
                'TYPE_IN_FREC',     'NPN',                         # FORMA EN QUE EL VARIADOR DE VELOCIDAD DETECTA LAS ENTRADAS [ NPN (not_in)| PNP] 
                'DLGID_REF',        'MER005',                      # DATALOGGER QUE SE USA DE REFERENCIA PARA EL AUTOMATIMO
                'CHANNEL_REF',      'PMP',                         # NOMBRE DEL CANAL CON LA MEDIDA DE REFERENCIA PARA EL AUTOMATISMO
                'DLGID_REF_1',      '',                            # DATALOGGER AUXILIAR QUE SE VA A USAR DE REFERENCIA EN CASO DE FALLAS DE COMUNICACION DEL PRINCIPAL
                'CHANNEL_REF_1',    '',                            # NOMBRE DEL CANAL AUXILIAR CON LA MEDIDA DE REFERENCIA PARA EL AUTOMATISMO
            
            ]        

    
    control_process(LIST_CONFIG)
        
    
   
        
