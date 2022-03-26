#!/usr/aut_env/bin/python3.8
'''
SERVICIO DE DETECCION DE ERRORES EN AUTOMATISMOS

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.3 15-04-2021 09:11
''' 

# LIBRERIAS
import os
import sys


# CONEXIONES
from __CORE__.drv_redis import Redis
from __CORE__.mypython import str2lst, config_var, lst2str
from __CORE__.drv_logs import ctrl_logs
from __CORE__.drv_db_GDA import GDA
from __CORE__.drv_config import dbUrl, project_path



#---------------------------------------------------------------------------------------- 
# CONFIGURO LAS ENTRADAS DE CONFIGURACION 
if __name__ == '__main__':
    # DETECTO LLAMADA CON Y SIN PARAMETROS
    try:
        # LLAMADA CON PAR[AMETROS
        STR_CONFIG = sys.argv[1]
        LIST_CONFIG = str2lst(STR_CONFIG)
        #
    except:
        # LLAMADA SIN PARAMETROS
        LIST_CONFIG = ''
        #
        
    # INSTANCIA DE config_var
    conf = config_var(LIST_CONFIG) 
    redis = Redis()
    gda = GDA(dbUrl)
    #
    # CHEQUEO QUE TIPO DE LLAMADA SE ESTA HACIENDO
    if bool(LIST_CONFIG):
        if conf.lst_get('DLGID'):
            # LLAMADA CON VARIABLES DE EJECUCION Y CONFIGURACION
            print_log = conf.lst_get('print_log')
            DLGID = conf.lst_get('DLGID')
            TYPE = conf.lst_get('TYPE')
        else:
            # LLAMADA SOLO CON EL ID DEL DATALOGGER
            print_log = True
            DLGID = sys.argv[1]
            TYPE = 'CHARGE'
    else:
        # LLAMADA SIN DATOS [LLAMADA SE VA A EJECUTAR EN EL SERVIDOR]
        print_log = True
        DLGID = ''
        TYPE = 'CHARGE'
    
        
#----------------------------------------------------------------------------------------         
def upgrade_config(DLGID,LIST_CONFIG):
    ''''''
    
    FUNCTION_NAME = 'UPGRADE_CONFIG'
    
    #
    ## INSTANCIAS
    logs = ctrl_logs(False,'servErrorAppSelection',DLGID,print_log)
    #
    # IMPRIMIR VARIABLES DE CONFIGURACION
    n = 4
    for param in LIST_CONFIG:
        if n < (len(LIST_CONFIG)): 
            logs.print_in(FUNCTION_NAME,LIST_CONFIG[n],LIST_CONFIG[n+1])
            n += 2
    #
    ## ELIMINO LAS VARIABLES DE CONFIGURACION ANTERIORES
    if redis.hexist(f'{DLGID}_ERROR','TAG_CONFIG'):
    #if gda.readAutConf(f'{DLGID}_ERROR','TAG_CONFIG'):    
        last_TAG_CONFIG = redis.hget(f'{DLGID}_ERROR','TAG_CONFIG')
        #last_TAG_CONFIG = gda.readAutConf(f'{DLGID}_ERROR','TAG_CONFIG')
        #   
        for param in last_TAG_CONFIG.split(','):
            redis.hdel(f'{DLGID}_ERROR', param)
        #    
        redis.hdel(f'{DLGID}_ERROR','TAG_CONFIG')

    # ESCRIBO EN REDIS LAS VARIABLES DE CONFIGURACION
    logs.print_inf(FUNCTION_NAME, 'ACTUALIZO CONFIG EN REDIS' )
    
    TAG_CONFIG = []
    n = 4
    for param in LIST_CONFIG:
        if n < (len(LIST_CONFIG)): 
            redis.hset(f'{DLGID}_ERROR',LIST_CONFIG[n],LIST_CONFIG[n+1])
            #gda.WriteAutConf(f'{DLGID}_ERROR',LIST_CONFIG[n],LIST_CONFIG[n+1])
            TAG_CONFIG.append(LIST_CONFIG[n])
            n += 2
    #
    # ESCRIBO EN REDIS EL NOMBRE DE LAS VARIABLES DE CONFIGURACION PARA QUE PUEDAN SER LEIDAS
    redis.hset(f'{DLGID}_ERROR','TAG_CONFIG',lst2str(TAG_CONFIG))
    #gda.WriteAutConf(f'{DLGID}_ERROR','TAG_CONFIG',lst2str(TAG_CONFIG))
    
    # LEO VARIABLES ESCRITAS
    n = 4
    check_config = []
    for param in LIST_CONFIG:
        if n < (len(LIST_CONFIG)): 
            check_config.append(LIST_CONFIG[n])
            check_config.append(redis.hget(f'{DLGID}_ERROR',LIST_CONFIG[n]))
            #check_config.append(gda.readAutConf(f'{DLGID}_ERROR',LIST_CONFIG[n]))
            n += 2
    #
    # MUESTRO VARIABLES LEIDAS
    n = 0
    for param in check_config:
        if n < (len(check_config)): 
            logs.print_out(FUNCTION_NAME,check_config[n],check_config[n+1])
            n += 2

def read_config_var(DLGID):
    ''''''
    
    FUNCTION_NAME = 'READ_CONFIG_VAR'
    
    ## INSTANCIAS
    logs = ctrl_logs(False,'servErrorAppSelection',DLGID,print_log)
    redis = Redis()
    # 
    # LEO LOS TAGS DE CONFIGURACION
    if redis.hexist(f'{DLGID}_ERROR','TAG_CONFIG'): 
    #if gda.readAutConf(f'{DLGID}_ERROR','TAG_CONFIG'): 
        TAG_CONFIG = redis.hget(f'{DLGID}_ERROR', 'TAG_CONFIG')
        #TAG_CONFIG = gda.readAutConf(f'{DLGID}_ERROR','TAG_CONFIG')
        TAG_CONFIG = TAG_CONFIG.split(',')
    else: 
        #logs.print_inf(FUNCTION_NAME,f'NO EXISTE {DLGID}_TAG_CONFIG IN serv_error_APP_selection')
        #logs.print_inf(FUNCTION_NAME,'NO SE EJECUTA EL SCRIPT')
        return ''
    #
    
    # LEO CONFIGURACION DE LA REDIS
    #logs.print_inf(FUNCTION_NAME,'LEO CONFIG EN REDIS')
    vars_config = []
    for param in TAG_CONFIG:
        vars_config.append(param)
        vars_config.append(redis.hget(f'{DLGID}_ERROR',param))
        #vars_config.append(gda.readAutConf(f'{DLGID}_ERROR',param))
    #
    '''
    # MUESTRO VARIABLES LEIDAS
    n = 0
    for param in vars_config:
        if n < (len(vars_config)): 
            logs.print_out(FUNCTION_NAME,vars_config[n],vars_config[n+1])
            n += 2'''

    #
    # CONCATENO LAS VARIABLES DE EJECUCION Y DE CONFIGURACION
    list_out = []
    LIST_CONFIG = ['print_log', print_log, 'DLGID', DLGID, 'TYPE', TYPE]
    n = 0
    for param in LIST_CONFIG:
        if n < 4:
            list_out.append(LIST_CONFIG[n])
            n +=1
    
    for param in vars_config:
        list_out.append(param)
    
    return list_out    
    
def show_var_list(lst):

    LOG_LEVEL = config_var(LIST_CONFIG).lst_get('LOG_LEVEL')
    logs = ctrl_logs(False,'servErrorAppSelection',DLGID,print_log,LOG_LEVEL)
    if bool(lst):
        n = 0
        for param in lst:
            if n < (len(lst)): 
                logs.print_out(name_function,lst[n],lst[n+1])
                n += 2
                
def run_error_process(LIST_CONFIG):
    if bool(LIST_CONFIG):
        # INSTANCIO config_var CON EL NUEVO LIST_CONFIG
        conf = config_var(LIST_CONFIG)
        #
        TYPE = conf.lst_get('TYPE')
        
        import importlib.util
        #
        '''
        spec = importlib.util.spec_from_file_location("archivo", f"/datos/cgi-bin/spx/AUTOMATISMOS/{TYPE}/PROCESS/ctrl_error.py")
        archivo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(archivo)
        call_error_process = True'''
            
        try:
            #spec = importlib.util.spec_from_file_location("archivo", f"../{TYPE}/PROCESS/ctrl_error.py")
            #spec = importlib.util.spec_from_file_location("archivo", f"/datos/cgi-bin/spx/AUTOMATISMOS/{TYPE}/PROCESS/ctrl_error.py")
            spec = importlib.util.spec_from_file_location("archivo",'{0}/{1}/PROCESS/ctrl_error.py'.format(project_path,TYPE))
            archivo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(archivo)
            call_error_process = True
                
        except:
            logs.print_inf(name_function, f'NO SE ENCUENTRA ../{TYPE}/PROCESS/ctrl_error.py O EL MISMO TIENE ERRORES')
            call_error_process = False
            #
    
        
        
        if call_error_process:  
        #    try:
        #        archivo.error_process(LIST_CONFIG)
        #    except: 
        #        logs.print_inf(name_function, f'ERROR AL CORRER ../{TYPE}/PROCESS/ctrl_error.py - error_process(LIST_CONFIG)')
            archivo.error_process(LIST_CONFIG)
                
def add_2_RUN(dlgid):
    '''
        funcion que anade a serv_error_APP_selection / RUN 
        el DLGID_CTRL y el DLGID_REF
    '''
    
    name_function = 'ADD_VAR_TO_RUN'
    
    if redis.hexist('serv_error_APP_selection','RUN'):
    #if gda.readAutConf('serv_error_APP_selection','RUN'):
        TAG_CONFIG = redis.hget('serv_error_APP_selection', 'RUN')
        #TAG_CONFIG = gda.readAutConf('serv_error_APP_selection', 'RUN')
        lst_TAG_CONFIG = str2lst(TAG_CONFIG)
        try:
            lst_TAG_CONFIG.index(dlgid)
        except:
            lst_TAG_CONFIG.append(dlgid)
            str_TAG_CONFIG = lst2str(lst_TAG_CONFIG)
            redis.hset('serv_error_APP_selection', 'RUN', str_TAG_CONFIG)
            #gda.WriteAutConf('serv_error_APP_selection', 'RUN', str_TAG_CONFIG)
            
    else:
        redis.hset('serv_error_APP_selection', 'RUN', dlgid)
        #gda.WriteAutConf(dlgId, param, value)('serv_error_APP_selection', 'RUN', dlgid)
        
def del_2_Run(dlgid):
    '''
        funcion que elimina de  serv_error_APP_selection / RUN dlgid
    '''
    
    name_function = 'DEL_VAR_TO_RUN'
    
    if redis.hexist('serv_error_APP_selection','RUN'):
    #if gda.readAutConf('serv_error_APP_selection','RUN'):
        TAG_CONFIG = redis.hget('serv_error_APP_selection', 'RUN')
        #TAG_CONFIG = gda.readAutConf('serv_error_APP_selection', 'RUN')
        lst_TAG_CONFIG = str2lst(TAG_CONFIG)
        try:
            # ELIMINO EL DATALOGGER DE LA LISTA
            lst_TAG_CONFIG.remove(dlgid)
            #
            #SI LA LISTA QUEDA VACIA ELIMINO LA VARIABLE RUN 
            if not(bool(lst_TAG_CONFIG)):
                redis.del_key('serv_error_APP_selection')
                logs.print_inf(name_function, f'ELIMINO {dlgid} PARA QUE NO SE EJECUTE')
                return False
            #
            # CONVIERO A STR LA LISTA
            str_TAG_CONFIG = lst2str(lst_TAG_CONFIG)
            #
            # ACTUALIZO EL RUN EL LA REDIS
            redis.hset('serv_error_APP_selection', 'RUN', str_TAG_CONFIG)
            #gda.WriteAutConf('serv_error_APP_selection', 'RUN', str_TAG_CONFIG)
            #
            # LIMPIO RESTOS DE CONFIGURACION DE LA REDIS
            redis.del_key(f'{dlgid}_ERROR')
            #
            # IMPRIMO LOG EN CONSOLA
            logs.print_inf(name_function, f'ELIMINO {dlgid} PARA QUE NO SE EJECUTE')
        except:
            logs.print_inf(name_function, f'{dlgid} YA FUE ELIMINADO')
            
    
         
#----------------------------------------------------------------------------------------    
name_function = 'APP_ERROR_SELECTION'

## INSTANCIAS
logs = ctrl_logs(False,'servErrorAppSelection',DLGID,print_log)
redis = Redis()

n = -1

'''
n = -1 => Estado inicial

'''
while True:
    # CHEQUEO SI ESTOY EN ESTADO UNICIAL (PRIMERA CORRIDA)
    if n == -1:
        if conf.lst_get('DLGID'):
            # LLAMADA CON VARIABLES DE CONFIGURACION 
            
            ## VARIABLES GLOBALES QUE LE ENTRAN A CORE
            #logs.print_log(f"EXECUTE: {name_function}")
            #logs.print_in(name_function,'print_log',print_log)
            #logs.print_in(name_function,'DLGID',DLGID)
            
            # IMPRIMIR VARIABLES DE CONFIGURACION
            n = 4
            for param in LIST_CONFIG:
                if n < (len(LIST_CONFIG)): 
                    logs.print_in(name_function,LIST_CONFIG[n],LIST_CONFIG[n+1])
                    n += 2     
            
            # DETENGO LA EJECUCION DEL SCRIPT SI TYPE = DELETED
            if TYPE == 'DELETED':
                del_2_Run(DLGID)
                break
            
            
            # ANADO DLGID_CTRL A 'DLGID_CTRL_TAG_CONFIG' PARA QUE SE EJECUTE EL ctrl_error_frec
            add_2_RUN(conf.lst_get('DLGID'))
            
            # ACTUALIZO LA CONFIGURACION
            logs.print_inf(name_function,'UPGRADE CONFIG')
            upgrade_config(DLGID,LIST_CONFIG)
            
            # MUESTRO LAS VARIABLES QUE SE LE VAN A PASAR AL PROCESS Y LO LLAMO
            show_var_list(LIST_CONFIG)
            
            # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
            run_error_process(LIST_CONFIG)
            
            break
        #
        else:
            # LLAMADA CON DLGID O SIN PARAMETROS
            if bool(LIST_CONFIG):
                # LLAMADA CON DLGID
                
                ## VARIABLES GLOBALES QUE LE ENTRAN A CORE
                logs.print_log(f"EXECUTE: {name_function}")
                logs.print_in(name_function,'print_log',print_log)
                logs.print_in(name_function,'DLGID',DLGID)
                
                # LEO LAS VARIABLES DE CONFIGURACION
                logs.print_inf(name_function,'READ_CONFIG_VAR')
                LIST_CONFIG=read_config_var(DLGID)
                
                # MUESTRO LAS VARIABLES QUE SE LE VAN A PASAR AL PROCESS Y LO LLAMO
                show_var_list(LIST_CONFIG)
                
                # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
                run_error_process(LIST_CONFIG)
                
                break
            else:
                # LLAMADA SIN PARAMETROS
            
                # LEO IDs PARA EJECUTAR CORRER ctrl_error_frec.py
                if redis.hexist('serv_error_APP_selection', 'RUN'):
                #if gda.readAutConf('serv_error_APP_selection', 'RUN'):
                    str_RUN = redis.hget('serv_error_APP_selection', 'RUN')
                    #str_RUN = gda.readAutConf('serv_error_APP_selection', 'RUN')
                    lst_RUN = str2lst(str_RUN)
                else:
                    logs.print_inf(name_function, 'NO EXISTE VARIABLE RUN in serv_error_APP_selection')
                    logs.print_inf(name_function, 'NO SE EJECUTA SCRIPT') 
                    lst_RUN = ''
                    #
                    
                #
                n += 1
                #
                # ACTUALIZO EL DLGID A EJECUTAR     
                if lst_RUN: DLGID = lst_RUN[n] 
                
    #
    
    
    else:
        # ENTRAMOS EN ESTA CONDICION POR UN LLAMADO SIN ARGUMENTOS
        
        if bool(lst_RUN):
            
            # INTANCIA DE ctrl_logs SOLO PARA LLAMADA SIN ARGUMENTOS
            logs = ctrl_logs(False,'servErrorAppSelection',DLGID,print_log)
            #    
            ## VARIABLES GLOBALES QUE LE ENTRAN A CORE
            #logs.print_log(' ')
            #logs.print_log(f"EXECUTE: {name_function}")
            #logs.print_in(name_function,'print_log',print_log)
            #logs.print_in(name_function,'DLGID',DLGID)
            
            # LEO LAS VARIABLES DE CONFIGURACION
            #logs.print_inf(name_function,'READ_CONFIG_VAR')
            
            
            if read_config_var(DLGID):
                LIST_CONFIG=read_config_var(DLGID)
            else:
                # SOLO EJECUTO CON VARIABLES DE EJECUCION
                LIST_CONFIG = ['print_log', print_log, 'DLGID', DLGID, 'TYPE', TYPE]
            
            
            
            # MUESTRO LAS VARIABLES QUE SE LE VAN A PASAR AL PROCESS Y LO LLAMO
            show_var_list(LIST_CONFIG)
                    
            # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
            run_error_process(LIST_CONFIG)
            
            # EVALUO CONDICION DE RUPTURA      
            if n < (len(lst_RUN) - 1):
                n += 1
                
                # ACTUALIZO EL DLGID A EJECUTAR     
                DLGID = lst_RUN[n]
                
                
            else:
                break           
        
        else:
            break
        
        
        
    
  
        