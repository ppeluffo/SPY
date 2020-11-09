#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 19:55:43 2019

@author: pablo
"""

import os
import sys
import glob
import time
import re
from spy_log import *
from spy_bd import BD
import ast
import psutil
import signal
from spy_config import Config
from spy_utils import u_parse_string, u_format_fecha_hora, u_dataline_to_dict

MAXPROCESS = 50
# -----------------------------------------------------------------------------
#Config = configparser.ConfigParser()
#Config.read('spy.conf')
#
console = ast.literal_eval( Config['MODO']['consola'] )
#-----------------------------------------------------------------------------

def move_file_to_error_dir(file):
    # Muevo el archivo al error.
    log(module=__name__, server='processR1', function='move_file_to_error_dir', dlgid='SPYPROC01', msg='ERROR: FILE {}'.format(file))
    dirname, filename = os.path.split(file)
    try:
        errdirname = Config['PROCESS']['process_err_path']
        errfile = os.path.join(errdirname, filename)
        log(module=__name__, server='processR1', function='move_file_to_error_dir', level='SELECT', dlgid='SPYPROC01', console=console, msg='errfile={}'.format(errfile))
        os.rename(file, errfile)
    except Exception as err_var:
        log(module=__name__, server='processR1', function='move_file_to_error_dir', console=console, dlgid='SPYPROC01', msg='ERROR: [{0}] no puedo pasar a err [{1}]'.format(file, err_var))
        log(module=__name__, server='processR1', function='move_file_to_error_dir', dlgid='SPYPROC01', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def move_file_to_bkup_dir(file):
    # Muevo el archivo al backup.
    dirname, filename = os.path.split(file)
    try:
        bkdirname = Config['PROCESS']['process_bk_path']
        bkfile = os.path.join(bkdirname, filename)
        log(module=__name__, server='processR1', function='move_file_to_bkup_dir', level='SELECT', dlgid='SPYPROC01', console=console, msg='bkfile={}'.format(bkfile))
        os.rename(file, bkfile)
    except Exception as err_var:
        log(module=__name__, server='processR1', function='move_file_to_bkup_dir', console=console, dlgid='SPYPROC01', msg='ERROR: [{0}] no puedo pasar a bk [{1}]'.format(file, err_var))
        log(module=__name__, server='processR1', function='move_file_to_bkup_dir', dlgid='SPYPROC01', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def move_file_to_ute_dir(file):
    # Muevo el archivo al directorio 'ute' para ser procesados luego por DLGDB.
    dirname, filename = os.path.split(file)
    try:
        utedirname = Config['PROCESS']['process_ute_path']
        utefile = os.path.join(utedirname, filename)
        log(module=__name__, server='processR1', function='move_file_to_ute_dir', level='SELECT', dlgid='SPYPROC01', console=console, msg='utefile={}'.format(utefile))
        os.rename(file, utefile)
    except Exception as err_var:
        log(module=__name__, server='processR1', function='move_file_to_ute_dir', console=console, dlgid='SPYPROC01', msg='ERROR: [{0}] no puedo pasar a ute [{1}]'.format(file, err_var))
        log(module=__name__, server='processR1', function='move_file_to_ute_dir', dlgid='SPYPROC01', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def process_line( dlgid, line, bd):
    '''
    Recibo una linea, la parseo y dejo los campos en un diccionario
    Paso este diccionario a la BD para que la inserte.
    3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    '''
    log(module=__name__, server='processR1', function='process_line', level='SELECT', dlgid='SPYPROC01', console=console, msg='line={}'.format(line))
    d = u_dataline_to_dict(line)

    if not bd.insert_data_line(d):
        return False

    if not bd.insert_data_online(d):
        return False

    return True


def process_file(file):
    '''
    Recibo el nombre de un archivo el cual abro y voy leyendo c/linea
    y procesandola
    Al final lo muevo al directorio de backups
    c/archivo puede corresponder a un datalogger distinto por lo tanto el datasource puede ser
    distinto.
    Debo entonces resetear el datasource antes de procesar c/archivo
    C/archivo es del formato:
    CTL:1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;CTL:2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:1
    2.33;CTL:3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    '''
    dirname, filename = os.path.split(file)
    log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01', msg='file={}'.format(filename))
    dlgid, *res = re.split('_', filename)
    bd = BD(modo=Config['MODO']['modo'], dlgid=dlgid, server='process')
    log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01', msg='DLG={0}, DS={1}'.format(dlgid,bd.datasource))
    if bd.datasource == 'DS_ERROR':
        log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01',msg='ERROR: DS not found !!')
        move_file_to_error_dir(file)
        return

    elif bd.datasource == 'GDA':
        # Los archivos de GDA ya los procese al recibir el frame.
        # Si hubo error ya lo movi al directorio de errores.
        # Por lo tanto solo borro el archivo
        try: 
            log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01',msg='WARN: GDA ya procesado; {0} deleted  !!'.format(file))
            os.remove(file)
        except Exception as e: 
            log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01',msg='WARN: GDA el archivo {0} no se pudo borrar o no existe !!'.format(file))
        return

    else:
        #print('Im a child with pid {0} and FILE {1}'.format(os.getpid(), file))
        with open(file) as myfile:
            # El archivo trae una sola linea con varios frames enganchados.
            #     CTL:1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;CTL:2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:1
            #     2.33;CTL:3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
            #
            for bulkline in myfile:
                #log(module=__name__, server='process', function='process_file', level='SELECT', dlgid='PROC00',msg='bulkline={}'.format(bulkline))
                lines_list = bulkline.split('CTL:')
                #   1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
                #   2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
                #   3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
                for item in lines_list:
                    try:
                        (ctl_code, data_line) = item.split(';DATE')
                    except:
                        continue

                    # Renormalizo la linea
                    data_line = 'DATE' + data_line
                    log(module=__name__, server='processR1', function='process_file', level='SELECT', dlgid='SPYPROC01', msg='line={}'.format(data_line))

                    if not process_line( dlgid, data_line, bd):
                        move_file_to_error_dir(file)
                        return
        del bd

        if Config['SITE']['site'] == 'ute':
            move_file_to_ute_dir(file)
        else:
            move_file_to_bkup_dir(file)

        return


if __name__ == '__main__':

    # Lo primero es configurar el logger y desconocer las señales SIGCHILD
    # de los child que cree para poder despegarme como demonio
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    config_logger()

    dirname = Config['PROCESS']['process_rx_path']
    log(module=__name__, server='processR1', function='main', console=console, dlgid='SPYPROC01', msg='SERVER: dirname={}'.format(dirname))
    pid_list = list()
    #
    # A efectos de testing en modo consola corro como ./spy_process.py DEBUG
    if len(sys.argv) > 1 and sys.argv[1] == 'DEBUG':
        print('spy_process en modo DEBUG !!!')
        while True:
            file_list = glob.glob(dirname + '/*.dat')
            print ('File List: {}'.format(len(file_list)))
            for file in file_list:
                log(module=__name__, server='processR1', function='main', level='SELECT', dlgid='SPYPROC01', console=console,  msg='START: File {}'.format(file))
                process_file(file)

            time.sleep(60)

    # Modo normal
    while True:
        file_list = glob.glob(dirname + '/*.dat')
        for file in file_list:
            # Mientras halla lugar en la lista, proceso archivos
            if len(pid_list) < MAXPROCESS:
                # Creo un child
                pid = os.fork()
                if pid == 0:
                    try:
                        process_file(file)
                    except Exception as e: 
                        log(module=__name__, server='processR1', function='main', dlgid='SPYPROC01', msg='ERROR: process_file {} - {}'.format(file, str(e)))
                    sys.exit(0)
                else:
                    pid_list.append(pid)
                    log(module=__name__, server='processR1', function='main', dlgid='SPYPROC01', msg='SERVER: append child {}'.format(pid))
                    print('Server: append child {}'.format(pid))

            # No queda espacio: Espero que se vaya haciendo lugar
            while len(pid_list) == MAXPROCESS:
                log(module=__name__, server='processR1', function='main', dlgid='SPYPROC01', msg='SERVER: List FULL: {}'.format(pid_list))
                print('List FULL: {}'.format(pid_list))
                time.sleep(3)
                # Veo si alguno termino y lo saco de la lista para que quede espacio para otro
                for pid in pid_list:
                    if not psutil.pid_exists(pid):
                        pid_list.remove(pid)
                        log(module=__name__, server='processR1', function='main', dlgid='SPYPROC01',msg='SERVER: remove pid {}'.format(pid))
                        print('Server remove pid {}'.format(pid))

        # No hay mas archivos por ahora: espero
        log(module=__name__, server='processR1', function='main', dlgid='SPYPROC01',msg='SERVER: No hay mas archivos: espero')
        print('Server No hay mas archivos: espero')
        time.sleep(60)
