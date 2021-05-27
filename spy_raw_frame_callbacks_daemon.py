#!/usr/bin/python3 -u

from spy_log import *
import os
import sys
from spy import Config
from datetime import datetime
from spy_utils import u_send_response, u_dataline_to_dict
from spy_bd_redis import Redis
from spy_bd_gda import BDGDA
from spy_process import move_file_to_error_dir
import daemon
import shutil


def process_callbacks(obj):   
    # Paso el proceso a demonio.
    with daemon.DaemonContext(): 
        config_logger()
        log(module=__name__, function='process_callbacks', dlgid=obj.dlgid, msg='CALLBACK ==> START')
        
        def run_program():
            os.system('{0} {1}'.format(CBK,obj.dlgid))
            #os.execl(CBK, PROGRAM, obj.dlgid)
                
        # PREPARO ARGUMENTOS
        try:
            PATH = Config['CALLBACKS_PATH']['cbk_path']
            PROGRAM = Config['CALLBACKS_PROGRAM']['cbk_program']
            CBK = os.path.join(PATH, PROGRAM)
            #
            log(module=__name__, function='process_callbacks', dlgid=obj.dlgid, msg='CALL_BACKS ==> {0} {1}]'.format(CBK,obj.dlgid))
            # EJECUTO CALLBACKS SI LAS VARIABLES PATH y PROGRAM TIENEN VALORES COHERENTES
            if bool(PROGRAM) & bool(PATH):
                # EJECUTO EL CALLBACKS CON TIEMPO MAXIMO DE EJECUCION DE 1 s
                run_program()
            else: 
                log(module=__name__, function='process_callbacks', dlgid=obj.dlgid, msg='CALLBACKS ==> [PATH = {0}],[PROGRAM = {1}'.format(PATH,PROGRAM))
                log(module=__name__, function='process_callbacks', dlgid=obj.dlgid, msg='CALLBACKS ==> INTERRUMPIDO')
        
        except:
            log(module=__name__, function='process_callbacks', dlgid=obj.dlgid, msg='CALLBACKS ==> ERROR A LEER cbk vars de spy.conf')
    
        log(module=__name__, function='process', dlgid=obj.dlgid, msg='CALLBACK ==> END')
        os._exit(0)

def callbacks_process_daemon(obj):
    # Inicio un fork para dejar como demonio al proceso que ingresa los datos en la base.
    pid = os.fork()
    if pid == 0:
        try: 
            process_callbacks(obj)
        except Exception as err:
            log(module=__name__, function='process', dlgid=obj.dlgid, msg=str(err))

    return



