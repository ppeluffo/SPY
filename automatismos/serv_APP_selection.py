#!/usr/aut_env/bin/python3.8
'''
SELECCION DE AUTOMATISMOS

@author: Yosniel Cabrera

Version 2.1.6 20-05-2021
''' 

# LIBRERIAS
import sys
import configparser
import os

# CONEXIONES
from __CORE__.mypython import config_var, lst2str, str2lst
from __CORE__.drv_redis import Redis
from __CORE__.drv_logs import ctrl_logs
from __CORE__.drv_config import allowedTypes, project_path
from __CORE__.drv_db_GDA import GDA
from __CORE__.drv_config import dbUrl, perforationProcessPath
from time import time   
sel_start_time = time() 


# CALL CONFIG ---------------------------------------------------------------------------------------- 
if __name__ == '__main__':
    # LEO EL STR DE CONFIGURACION   
    
    try:    
        STR_CONFIG = sys.argv[1]
        LIST_CONFIG = STR_CONFIG.split(',')
    except:
        print('HELP')
        print('    ARGUMENT = DLGID_CTRL')
        print('    EX:')
        print('    ./serv_APP_selection.py DLGID_CTRL')
        quit()
        
    #
    # INSTANCIAS
    conf = config_var(STR_CONFIG) 
    redis = Redis()
    #
    
    #
    # CHEQUEO QUE TIPO DE LLAMADA SE ESTA HACIENDO
    ## SI SE LE PASA UN str ASIGNO VALORES ENTRADOS
    if conf.str_get('DLGID_CTRL'):
        print_log = conf.str_get('print_log')
        DLGID_CTRL = conf.str_get('DLGID_CTRL')
        if conf.str_get('TYPE'): 
            TYPE = conf.str_get('TYPE')
        else:  
            TYPE = 'CHARGE'
    ## SE SE LE PASA UN SOLO ARGUMENTO SE LO ASIGNO A DLGID
    else:
        print_log = False
        DLGID_CTRL = sys.argv[1]
        TYPE = 'CHARGE'
        
    
# FUNCTIONS ----------------------------------------------------------------------------------------    
def upgrade_config(DLGID_CTRL,LIST_CONFIG):
    '''
        actualiza en gda las variables de dconfiguracion
    '''
    
    FUNCTION_NAME = 'UPGRADE_CONFIG'
    
    ## INSTANCIAS
    logs = ctrl_logs(False,'servAppSelection',DLGID_CTRL,print_log)

    # FUNCTIONS
    def printConfigVars(LIST_CONFIG):
        n = 4
        for param in LIST_CONFIG:
            if n < (len(LIST_CONFIG)): 
                logs.print_in(FUNCTION_NAME,LIST_CONFIG[n],LIST_CONFIG[n+1])
                n += 2
    
    def saveConfigVars(LIST_CONFIG):
        logs.print_inf(FUNCTION_NAME, 'ACTUALIZO CONFIG EN GDA' )
        n = 4
        for param in LIST_CONFIG:
            if n < (len(LIST_CONFIG)): 
                gda.InsertAutConf(DLGID_CTRL,LIST_CONFIG[n],LIST_CONFIG[n+1])       # escritura de valores en dbGda
                n += 2

    # MAIN
    # imprimo en pantalla las variables de configuracion
    printConfigVars(LIST_CONFIG)

    # eliminto todas las variables de configuracion anteriores
    #gda.DeleteAllAutConf(DLGID_CTRL)

    # escribo nuevamente toda la configuracion en GDA
    saveConfigVars(LIST_CONFIG)

def add_2_RUN(dlgid,type,logLevel):
    '''
        funcion que anade a serv_error_APP_selection / RUN 
        el DLGID_CTRL y el DLGID_REF
    '''
    
    name_function = 'ADD_VAR_TO_RUN'
    
    if redis.hexist('serv_error_APP_selection','RUN'):
        TAG_CONFIG = redis.hget('serv_error_APP_selection', 'RUN')
        
        lst_TAG_CONFIG = str2lst(TAG_CONFIG)
        try:
            lst_TAG_CONFIG.index(dlgid)
            
        except:
            lst_TAG_CONFIG.append(dlgid)
            str_TAG_CONFIG = lst2str(lst_TAG_CONFIG)
            redis.hset('serv_error_APP_selection', 'RUN', str_TAG_CONFIG)
                        
    else:
        redis.hset('serv_error_APP_selection', 'RUN', dlgid)


    # SETEO VARIABLES DE CONFIGURACION
    if not(redis.hexist(f'{dlgid}_ERROR', 'TAG_CONFIG')):
        redis.hset(f'{dlgid}_ERROR', 'TAG_CONFIG', 'TYPE,LOG_LEVEL')
    
    # ACTUALIZO VARIABLES DE CONFIGURACION
    redis.hset(f'{dlgid}_ERROR', 'TYPE', type)
    redis.hset(f'{dlgid}_ERROR', 'LOG_LEVEL', logLevel)
    
def show_var_list(lst):
    # instancio los logs con la informacion del LOG_LEVEL
    LOG_LEVEL = config_var(lst).lst_get('LOG_LEVEL')
    logs = ctrl_logs(False,'servAppSelection',DLGID_CTRL,print_log,LOG_LEVEL)
    n = 0
    for param in lst:
        if n < (len(lst)): 
            logs.print_out(name_function,lst[n],lst[n+1])
            n += 2
    
def run_ctrl_process(LIST_CONFIG):
    if bool(LIST_CONFIG):
        #
        # INSTANCIO config_var CON EL NUEVO LIST_CONFIG Y LEO TYPE
        conf = config_var(LIST_CONFIG)
        TYPE = conf.lst_get('TYPE')
        #
        import importlib.util
        '''
        try:
            spec = importlib.util.spec_from_file_location("archivo",'{0}/{1}/PROCESS/ctrl_process.py'.format(project_path,TYPE))
            archivo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(archivo)
            archivo.control_process(LIST_CONFIG)
        except:
            logs.print_inf(name_function, f'NO SE ENCUENTRA ../{TYPE}/PROCESS/ctrl_process.py O EL MISMO TIENE ERRORES')
            exit(0)'''

        spec = importlib.util.spec_from_file_location("archivo",'{0}/{1}/PROCESS/ctrl_process.py'.format(project_path,TYPE))
        archivo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(archivo)
        archivo.control_process(LIST_CONFIG)
        
            
def run_perforation_process(dlgid):
    
    text = '''
    
    PERFORACIONES EN PERL
    '''
    
    #logs.print_inf(name_function,text )
    
    import os;

    #path = '/datos/cgi-bin/spx/PERFORACIONES/'
    path = perforationProcessPath
    file = 'ext_call.pl'
    param = '--dlgid'
    param_value = dlgid
    
    

    try:
        os.system('{0}{1} {2} {3}'.format(path,file,param,param_value));
    except:
        logs.print_inf(name_function, 'ERROR AL CORRER LAS PERFORACIONES EN PERL')


# MAIN ----------------------------------------------------------------------------------------    
'''
    Las variables que siempren estan disponible para el MAIN son:
        print_log = False
        DLGID_CTRL = ...
        TYPE = 'CHARGE'
        LIST_CONFIG = ...
'''

name_function = 'APP_SELECTION'

## INSTANCIAS
logs = ctrl_logs(False,'servAppSelection',DLGID_CTRL,print_log)
redis = Redis()
gda = GDA(dbUrl)


# se ejecuta el process que atiende las automatismos en perl
run_perforation_process(DLGID_CTRL)                                    # mine


# condicion que se cumple cuandos se llama desde el callback
if TYPE == 'CHARGE':                                                    
    
    # armo la lista de configuracion para el process
    LIST_CONFIG = ['print_log', print_log, 'DLGID_CTRL', DLGID_CTRL] + gda.getAllAutConf(DLGID_CTRL)

    # leo el valor de TYPE
    TYPE = config_var(LIST_CONFIG).lst_get('TYPE')
           
    # chequeo que el tipo de automatismo a ejecutar este programado
    if not TYPE in allowedTypes:
        logs.print_inf(name_function,f"[TYPE = {TYPE}]")
        logs.print_inf(name_function,'VARIABLE TYPE CON VALOR NO RECONOCIDO ')
        exit(0)

    # leo el valor de LOG_LEVEL y en caso de que no haya lo creo con el valor BASIC
    # IMPORTANTE QUE ESTE DESPUES DE CHEQUEAR LA CONDICION DE SALIDA
    LOG_LEVEL = config_var(LIST_CONFIG).lst_get('LOG_LEVEL')
    if not LOG_LEVEL:
        LIST_CONFIG += ['LOG_LEVEL','BASIC']
        gda.InsertAutConf(DLGID_CTRL, 'LOG_LEVEL', 'BASIC')
        

#condicion que se cumple cuando se llama desde un script con configuracion precargada y el tipo de automatismo esta programado
elif TYPE in allowedTypes:                                              
    
    upgrade_config(DLGID_CTRL,LIST_CONFIG)                              # actualizo la configuracion pasada en gda

    # armo la lista de configuracion para el process
    LIST_CONFIG = ['print_log', print_log, 'DLGID_CTRL', DLGID_CTRL] + gda.getAllAutConf(DLGID_CTRL)
    
    
else:
    # condicion que se cumple cuando se llama desde un script con configuracion precargada y el tipo de automatismo NO esta programado
    logs.print_inf(name_function,f"[TYPE = {TYPE}]")
    logs.print_inf(name_function,'VARIABLE TYPE CON VALOR NO RECONOCIDO ')
    exit(0)



conf = config_var(LIST_CONFIG)

TYPE = conf.lst_get('TYPE')
DLGID_CTRL = conf.lst_get('DLGID_CTRL')
DLGID_REF = conf.lst_get('DLGID_REF')
LOG_LEVEL = conf.lst_get('LOG_LEVEL')


# anado el DLGID_CTRL a 'REDIS:serv_error_APP_selection/RUN' PARA QUE SE EJECUTE EL ctrl_error_frec
add_2_RUN(DLGID_CTRL,TYPE,LOG_LEVEL)

# anado el DLGID_CTRL a 'REDIS:serv_error_APP_selection/RUN' PARA QUE SE EJECUTE EL ctrl_error_frec
if DLGID_REF:
    add_2_RUN(DLGID_REF,TYPE,LOG_LEVEL)
    
# log de las vriables que se le van a pasar al process
show_var_list(LIST_CONFIG)

# llamo al automatismo y le paso la lista con las configuraciones
run_ctrl_process(LIST_CONFIG)





# CALCULO TIEMPO DE DEMORA
#print(f'serv_APP_selection TERMINADO A {time()-sel_start_time} s')



exit(0)