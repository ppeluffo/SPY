#!/usr/bin/python3 -u

from spy_log import *
from spy_process_daemon import process_line as process_line_daemon
import os
import sys
from spy import Config
from spy_bd_gda import BDGDA
from spy_bd import BD
import daemon
import shutil

def insert_GDA(dlgid, data_line_list, tmp_file, dat_file, root_path):   
    # Paso el proceso a demonio.
    with daemon.DaemonContext(): 
        config_logger()
        bd = BDGDA( modo = Config['MODO']['modo'] )
        bd.connect()
        # Paso 6: Inserto las lineas en GDA.
        if bd.insert_data(dlgid, data_line_list):
            bdProcess = BD(modo=Config['MODO']['modo'], dlgid=dlgid, server='process')
            if bdProcess.datasource == 'DS_ERROR':
                log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01',msg='ERROR: DS not found !!')

            for dl in data_line_list: 
                if bdProcess.datasource != 'DS_ERROR' and bdProcess.datasource != 'GDA':
                    process_line_daemon(dlgid, dl, bdProcess)
            # Si salio bien renombro el archivo a .dat para que el process lo use
            # shutil.move(tmp_file, dat_file)
        # else:
        #     # move_file_to_error_dir(tmp_file)
        #     dirname, filename = os.path.split(tmp_file)
        #     errdirname = Config['PROCESS']['process_err_path']
        #     errfile = os.path.join(root_path,errdirname, filename)
        #     log(module=__name__, server='processR1', function='move_file_to_error_dir', level='SELECT', dlgid=dlgid, msg='errfile={}'.format(errfile))
        #     shutil.move(tmp_file, errfile)        

        log(module=__name__, function='process', dlgid=dlgid, msg='End Daemon')
        os._exit(0)

    return

def insert_GDA_process_daemon(obj, tmp_file, dat_file, root_path):
    # Inicio un fork para dejar como demonio al proceso que ingresa los datos en la base.

    # Primer fork.
    if os.fork():
        sys.exit()

    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Segundo fork para asegurarnos no tener terminal asociada
    if os.fork():
        sys.exit()

    # stdin
    '''
    with open('/dev/null', 'r') as dev_null:
        os.dup2(dev_null.fileno(), sys.stdin.fileno())

    sys.stdout.flush()
    with open(self.stdout, 'a+', 0) as stdout:
        os.dup2(stdout.fileno(), sys.stdout.fileno())
    '''

    try:
        insert_GDA(obj.dlgid, obj.data_line_list, tmp_file, dat_file, root_path)
    except Exception as err:
        log(module=__name__, function='process', dlgid=obj.dlgid, msg=str(err))

    return


