#!/usr/bin/python3 -u

from spy_log import log
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

def insert_GDA(obj, tmp_file, dat_file, root_path):   
    # Paso el proceso a demonio.
    with daemon.DaemonContext(): 
        obj.bd = BDGDA( modo = Config['MODO']['modo'] )
        log(module=__name__, function='process', dlgid=obj.dlgid, msg='Start Daemon')

        # Paso 6: Inserto las lineas en GDA.
        if obj.process_and_insert_lines_into_GDA():
            # Si salio bien renombro el archivo a .dat para que el process lo use
            os.rename(tmp_file, dat_file)
        else:
            # move_file_to_error_dir(tmp_file)
            dirname, filename = os.path.split(tmp_file)
            errdirname = Config['PROCESS']['process_err_path']
            errfile = os.path.join(root_path,errdirname, filename)
            log(module=__name__, server='processR1', function='move_file_to_error_dir', level='SELECT', dlgid='SPYPROC01', msg='errfile={}'.format(errfile))
            shutil.move(tmp_file, errfile)        

        log(module=__name__, function='process', dlgid=obj.dlgid, msg='End Daemon')
        os._exit(0)

    return

def insert_GDA_process_daemon(obj, tmp_file, dat_file, root_path):
    # Inicio un fork para dejar como demonio al proceso que ingresa los datos en la base.
    pid = os.fork()
    if pid == 0:
        try: 
            insert_GDA(obj, tmp_file, dat_file, root_path)
        except Exception as err:
            log(module=__name__, function='process', dlgid=obj.dlgid, msg=str(err))

    return
