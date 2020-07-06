#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 19:55:43 2019

@author: pablo
Es similar a spy_process.py pero este toma los datos del directorio uteFiles, los
procesa y los guarda en la base dlgDb.
Luego los guarda en bkFiles

"""

import os
import sys
import glob
import time
import re
from spy_log import *
from spy_bd import BD
from spy_bd_dlgdb import DLGDB
import ast
import psutil
import signal
from spy_config import Config
from spy_utils import u_parse_string
import configparser
import shutil

MAXPROCESS = 30
# -----------------------------------------------------------------------------
# Config = configparser.ConfigParser()
# Config.read('config/spy_processUte.conf')
#
console = ast.literal_eval( Config['MODO']['consola'] )
#-----------------------------------------------------------------------------

def format_fecha_hora(fecha, hora):
    '''
    Funcion auxiliar que toma la fecha y hora de los argumentos y
	las retorna en formato DATE de la BD.
    121122,180054 ==> 2012-11-22 18:00:54
    '''
    lfecha = [(fecha[i:i + 2]) for i in range(0, len(fecha), 2)]
    lhora = [(hora[i:i + 2]) for i in range(0, len(hora), 2)]
    timestamp = '20%s-%s-%s %s:%s:%s' % ( lfecha[0], lfecha[1], lfecha[2], lhora[0], lhora[1], lhora[2] )
    return timestamp


def move_file_to_error_dir(file):
    # Muevo el archivo al error.
    log(module=__name__, server='process', function='move_file_to_error_dir', dlgid='PROC00', msg='ERROR: FILE {}'.format(file))
    dirname, filename = os.path.split(file)
    try:
        errdirname = Config['PROCESS']['process_err_path']
        errfile = os.path.join(errdirname, filename)
        log(module=__name__, server='process', function='move_file_to_error_dir', level='SELECT', dlgid='PROC00', console=console, msg='errfile={}'.format(errfile))
        # os.rename(file, errfile)
        shutil.move(file, errfile)
    except Exception as err_var:
        log(module=__name__, server='process', function='move_file_to_error_dir', console=console, dlgid='PROC00', msg='ERROR: [{0}] no puedo pasar a err [{1}]'.format(file, err_var))
        log(module=__name__, server='process', function='move_file_to_error_dir', dlgid='PROC00', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def move_file_to_bkup_dir(file):
    # Muevo el archivo al backup.
    dirname, filename = os.path.split(file)
    try:
        bkdirname = Config['PROCESS']['process_bk_path']
        bkfile = os.path.join(bkdirname, filename)
        print(str(bkfile))
        log(module=__name__, server='process', function='move_file_to_bkup_dir', level='SELECT', dlgid='PROC00', console=console, msg='bkfile={}'.format(bkfile))
        # os.rename(file, bkfile)
        shutil.move(file, bkfile)
    except Exception as err_var:
        log(module=__name__, server='process', function='move_file_to_bkup_dir', console=console, dlgid='PROC00', msg='ERROR: [{0}] no puedo pasar a bk [{1}]'.format(file, err_var))
        log(module=__name__, server='process', function='move_file_to_bkup_dir', dlgid='PROC00', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def move_file_to_ute_dir(file):
    # Muevo el archivo al directorio 'ute' para ser procesados luego por DLGDB.
    dirname, filename = os.path.split(file)
    try:
        utedirname = Config['PROCESS']['process_ute_path']
        utefile = os.path.join(utedirname, filename)
        log(module=__name__, server='process', function='move_file_to_ute_dir', level='SELECT', dlgid='PROC00', console=console, msg='utefile={}'.format(utefile))
        os.rename(file, utefile)
    except Exception as err_var:
        log(module=__name__, server='process', function='move_file_to_ute_dir', console=console, dlgid='PROC00', msg='ERROR: [{0}] no puedo pasar a ute [{1}]'.format(file, err_var))
        log(module=__name__, server='process', function='move_file_to_ute_dir', dlgid='PROC00', msg='ERROR: EXCEPTION {}'.format(err_var))
    return


def process_line( line, dlgid, d_parsConf, bd ):
    '''
    Recibo una linea, la parseo y dejo los campos en un diccionario
    Paso este diccionario a la BD para que la inserte.
    3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    '''
    log(module=__name__, server='process', function='process_line', level='SELECT', dlgid='PROC00', console=console, msg='line={}'.format(line))
    line = 'CTL:{}'.format(line)
    line = line[:-1]
    line = line.rstrip('\n|\r|\t')

    d = u_parse_string( line, field_separator=';', key_separator=':')
    #for key in d:
    #    log(module=__name__, server='process', function='process_line', level='SELECT', dlgid='PROC00',msg='key={0}, val={1}'.format(key, d[key]))

    d['DLGID'] = dlgid
    d['timestamp'] = format_fecha_hora( d['DATE'], d['TIME'] )
    d['RCVDLINE'] = line
    #print(d)
    #for key in d:
    #     log(module=__name__, server='process', function='process_line', level='SELECT', dlgid='PROC00',msg='key={0}, val={1}'.format(key, d[key]))

    # Elimino las claves que se que no van en la bd(DATE,TIME,CTL)
    del d['DATE']
    del d['TIME']
    del d['CTL']

    if not bd.insert_data_line(dlgid, d, d_parsConf, bd):
        print('bd.insert_data_line: False')
        return False
    print('bd.insert_data_line: True')
    return True


def process_file(file, d_parsConf, bd ):
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
    log(module=__name__, server='process', function='process_file', level='SELECT', dlgid='UPROC00', msg='file={}'.format(filename))
    dlgid, *res = re.split('_', filename)
    log(module=__name__, server='process', function='process_file', level='SELECT', dlgid='UPROC00', msg='DLG={}'.format(dlgid))
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
            for line in lines_list:
                # Elimino las lineas vacias generadas por el parseo
                if 'DATE' in line:
                    log(module=__name__, server='process', function='process_file', level='SELECT', dlgid='UPROC00', msg='line={}'.format(line))
                    if not process_line( line, dlgid, d_parsConf, bd ):
                        move_file_to_error_dir(file)
                        return

    move_file_to_bkup_dir(file)

    return


if __name__ == '__main__':

    # Lo primero es configurar el logger y desconocer las señales SIGCHILD
    # de los child que cree para poder despegarme como demonio
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    config_logger()

    # Leo los datos del directorio uteFiles.
    dirname = Config['PROCESS']['process_ute_path']
    log(module=__name__, server='process', function='main', console=console, dlgid='UPROC00', msg='SERVER: dirname={}'.format(dirname))
    pid_list = list()
    #
    bd = DLGDB(modo='ute', server='process')

    # A efectos de testing en modo consola corro como ./spy_process.py DEBUG
    if len(sys.argv) > 1 and sys.argv[1] == 'DEBUG':
        print('spy_processUte en modo DEBUG !!!')
        while True:
            # Leo la configuracion por si algo cambio
            d_parsConf = bd.read_all_conf(dlgid='UPROC00', tag='DLGDB')
            # Leo la lista de archivos pendientes de ser procesados
            file_list = glob.glob(dirname + '/*.dat')
            print ('File List: {}'.format(len(file_list)))
            for file in file_list:
                log(module=__name__, server='process', function='main', level='SELECT', dlgid='UPROC00', console=console,  msg='File {}'.format(file))
                process_file(file, d_parsConf, bd )

            time.sleep(60)

    # Modo normal
    while True:
        # Leo la configuracion por si algo cambio
        d_parsConf = bd.read_all_conf(dlgid='UPROC00', tag='DLGDB')
        # Leo la lista de archivos pendientes de ser procesados
        file_list = glob.glob(dirname + '/*.dat')
        print('files: '+str(len(file_list)) )
        for file in file_list:
            # Mientras halla lugar en la lista, proceso archivos
            if len(pid_list) < MAXPROCESS:
                # Creo un child
                pid = os.fork()
                if pid == 0:
                    process_file(file, d_parsConf, bd )
                    sys.exit(0)
                else:
                    pid_list.append(pid)
                    log(module=__name__, server='process', function='main', dlgid='UPROC00', msg='SERVER: append child {}'.format(pid))
                    print('Server: append child {}'.format(pid))

            # No queda espacio: Espero que se vaya haciendo lugar
            while len(pid_list) == MAXPROCESS:
                log(module=__name__, server='process', function='main', dlgid='UPROC00', msg='SERVER: List FULL: {}'.format(pid_list))
                print('List FULL: {}'.format(pid_list))
                time.sleep(3)
                # Veo si alguno termino y lo saco de la lista para que quede espacio para otro
                for pid in pid_list:
                    if not psutil.pid_exists(pid):
                        pid_list.remove(pid)
                        log(module=__name__, server='process', function='main', dlgid='UPROC00',msg='SERVER: remove pid {}'.format(pid))
                        print('Server remove pid {}'.format(pid))

        # No hay mas archivos por ahora: espero
        log(module=__name__, server='process', function='main', dlgid='UPROC00',msg='SERVER: No hay mas archivos: espero')
        print('Server No hay mas archivos: espero')
        time.sleep(60)
