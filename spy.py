#!/usr/bin/python3 -u
"""
Version 1.0 @ 2019-07-19

Ref:
    Consulta sql sin resultados
    https://stackoverflow.com/questions/19448559/sqlalchemy-query-result-is-none

    Evaluacion de resultados como instancias
    https://www.programiz.com/python-programming/methods/built-in/isinstance

    Errores en Apache
    https://blog.tigertech.net/posts/apache-cve-2016-8743/
    https://serverfault.com/questions/853103/500-internal-server-ah02429-response-header-name

    Redis:
    https://realpython.com/python-redis/#using-redis-py-redis-in-python
    https://redis-py.readthedocs.io/en/latest/genindex.html

Advertencias:
    1) init_from_qs: Al leer un cgi si clave ( form.getvalue ) retorna None
    Conviene leer con gerfirst por si retornara una lista, no genera error: more safe.
    Devuelve None como default.
    2) init_from_qs: Al hacer un split, usar un try por si el unpack devuelve diferente cantidad
       de variables de las que se esperan
    3) init_from_bd: Los diccionarios al acceder a claves que no existen retornan error por
       lo que usamos el metodo get o try.
    4) La redis devuelve bytes por lo que debemos convertirlos a int para compararlos
       Los strings que maneja la redis los devuleve como bytes por lo tanto para usarlos como
       str debo convertirlos con decode().

Testing:
- Con telnet:
telnet localhost 80
GET /cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GENERAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2
 HTTP/1.1
Host: www.spymovil.com

telnet www.spymovil.com 90
GET /cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GENERAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2
 HTTP/1.1
Host: www.spymovil.com

- Con browser:
> usamos el url: http://localhost/cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GENERAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2



"""

import os
# import cgitb
import configparser
import sys
from spy_raw_frame import *
from spy_log import *

# -----------------------------------------------------------------------------
# cgitb.enable()
#
Config = configparser.ConfigParser()
Config.read('spy.conf')
#
# ------------------------------------------------------------------------------

if __name__ == '__main__':

    # Lo primero es configurar el logger
    config_logger()

    query_string = ''
    # Atajo para debugear x consola ( no cgi )!!!
    if len(sys.argv) > 1:
        if sys.argv[1] == 'DEBUG_INIT_GLOBAL':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_global']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string [{0}]'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_BASE':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_base']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_ANALOG':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_analog']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_DIGITAL':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_digital']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_COUNTER':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_counter']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_RANGE':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_range']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_PSENSOR':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_psensor']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_OUTPUTS_OFF':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_outputs_off']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_OUTPUTS_CONSIGNA':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_outputs_consigna']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_INIT_OUTPUTS_PERF':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_init_outputs_perf']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CTL_SCAN':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_ctl_scan']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_DATA':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_data']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        else:
            print('Argumentos invalidos')
            exit(1)

    else:
        # Leo del cgi
        query_string = os.environ.get('QUERY_STRING')

    log(module=__name__, function='__init__', level='INFO', msg='RX:[{}]'.format(query_string))

    '''
    Siempre recibo un frame que aun no se que es por lo tanto lo veo como un raw frame que debo empezar a 
    decodificar.
    '''
    raw_frame = RAW_frame(query_string)
    raw_frame.process()





