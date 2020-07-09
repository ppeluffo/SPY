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


def process_and_insert_lines_into_GDA(dlgid, data_line_list):
    # self.data_line_list = [ DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
    #                         DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
    #                         DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    #                       ]
    bd = BDGDA( modo = Config['MODO']['modo'] )

    for line in data_line_list:
        log(module=__name__, function='process_and_insert_lines_into_GDA', dlgid=dlgid, level='SELECT', msg='line={0}'.format(line))
        d = u_dataline_to_dict(line)
        #for key in d:
        #    log(module=__name__, server='process', function='pprocess_and_insert_lines_into_GDA', level='SELECT', dlgid='PROC00',msg='key={0}, val={1}'.format(key, d[key]))

        if not bd.insert_data_line(dlgid, d):
            return False

        if not bd.insert_data_online(dlgid,d):
            return False

    return True

def insert_GDA(dlgid, data_line_list, tmp_file, dat_file, root_path):   
    # Paso el proceso a demonio.

    with daemon.DaemonContext(): 
        log(module=__name__, function='process', dlgid=dlgid, msg='Start Daemon')

        # Paso 6: Inserto las lineas en GDA.
        if process_and_insert_lines_into_GDA(dlgid, data_line_list):
            # Si salio bien renombro el archivo a .dat para que el process lo use
            shutil.move(tmp_file, dat_file)
        else:
            # move_file_to_error_dir(tmp_file)
            dirname, filename = os.path.split(tmp_file)
            errdirname = Config['PROCESS']['process_err_path']
            errfile = os.path.join(root_path,errdirname, filename)
            log(module=__name__, server='processR1', function='move_file_to_error_dir', level='SELECT', dlgid=dlgid, msg='errfile={}'.format(errfile))
            shutil.move(tmp_file, errfile)        

        log(module=__name__, function='process', dlgid=dlgid, msg='End Daemon')
        os._exit(0)

    return

def insert_GDA_process_daemon(obj, tmp_file, dat_file, root_path):
    # Inicio un fork para dejar como demonio al proceso que ingresa los datos en la base.
    pid = os.fork()
    if pid == 0:
        try: 
            insert_GDA(obj.dlgid, obj.data_line_list, tmp_file, dat_file, root_path)
        except Exception as err:
            log(module=__name__, function='process', dlgid=obj.dlgid, msg=str(err))

    return
