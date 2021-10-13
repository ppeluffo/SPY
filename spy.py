#!/home/pablo/Spymovil/python/pyenv/ml/bin/python3
##!/usr/bin/python3 -u
##!/home/pablo/Spymovil/python/pyenv/ml/bin/python3


"""
Version 2.1c @ 2021-10-05
- Agrego modificaciones para configurar parametros del PLC remoto al que mandar datos
  de control y status.

Version 2.1b @ 2021-10-04
- Corrijo un bug que hacia que las versiones viejas quieran configurar siempre el modbus

Version 2.1a @ 2021-10-01
- Uniformizo envio de broadcast de y a todas las versiones.

Version 2.1 @ 2021-10-01
- Broadcast de medidas locales a dataloggers remotos por modbus.

Version 2.0 @ 2021-09-28
- Modbus + redis
- Pilotos

Version 2.0 @ 2021-09-24
- Corrijo bug de fork al procesar datos.
- Modifico el sistema de configuracion de pilotos para soportar 12 consignas
- Permito que en las respuestas a datos se mande una nueva presion a fijar momentaneamente por el piloto

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
import sys
from spy_raw_frame import *
from spy_log import *
from spy_config import Config

# -----------------------------------------------------------------------------
# cgitb.enable()
#
#Config = configparser.ConfigParser()
#Config.read('spy.conf')
#
# ------------------------------------------------------------------------------

def print_error():
    print('Argumentos invalidos')
    print('USO: ./spy.py ')
    print('''
     DEBUG_CONF_AUTH
     DEBUG_CONF_UPDATE
     DEBUG_CONF_GLOBAL     
     DEBUG_CONF_BASE
     DEBUG_CONF_ANALOG
     DEBUG_CONF_DIGITAL
     DEBUG_CONF_COUNTER
     DEBUG_CONF_PSENSOR
     DEBUG_CONF_RANGE 
     DEBUG_CONF_APP 
     DEBUG_CONF_CONSIGNA
     DEBUG_CONF_PPOT_SMS
     DEBUG_CONF_PPOT_LEVELS
     DEBUG_CONF_MODBUS
     DEBUG_CONF_MBUS_LOW
     DEBUG_CONF_MBUS_MED
     DEBUG_CONF_MBUS_HIGH
     DEBUG_CONF_PILOTO
     
     DEBUG_CTL_SCAN
     DEBUG_DATA
     DEBUG_TEST
       
     ''')
    exit(1)


if __name__ == '__main__':

    # Lo primero es configurar el logger
    config_logger()

    query_string = ''
    # Atajo para debugear x consola ( no cgi )!!!
    if len(sys.argv) == 2:

        if sys.argv[1] == 'DEBUG_CTL_SCAN':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_ctl_scan']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_DATA':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_data']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_AUTH':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_auth']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string [{0}]'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_UPDATE':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_update']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string [{0}]'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_GLOBAL':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_global']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string [{0}]'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_BASE':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_base']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_ANALOG':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_analog']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_DIGITAL':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_digital']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_COUNTER':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_counter']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_PSENSOR':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_psensor']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_RANGE':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_range']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_APP':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_app']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_PPOT_SMS':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_ppot_sms']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_PPOT_LEVELS':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_ppot_levels']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_CONSIGNA':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_app_consigna']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_MODBUS':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_app_modbus']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_MBUS_LOW':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_mbus_low']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_MBUS_MED':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_mbus_med']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_MBUS_HIGH':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_mbus_high']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_CONF_PILOTO':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_conf_app_piloto']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        elif sys.argv[1] == 'DEBUG_TEST':
            # Uso un query string fijo de test del archivo .conf
            query_string = Config['DEBUG']['debug_test']
            os.environ['QUERY_STRING'] = query_string
            print('TEST: query_string: {0}'.format(query_string))

        else:
            print_error()

    else:
        # Leo del cgi
        query_string = os.environ.get('QUERY_STRING')
        if query_string is None:
            print_error()

    # Proceso.
    log(module=__name__, function='__init__', level='INFO', msg='RX:[{}]'.format(query_string))

    '''
    Siempre recibo un frame que aun no se que es por lo tanto lo veo como un raw frame que debo empezar a 
    decodificar.
    '''
    raw_frame = RAW_frame(query_string)
    raw_frame.process()





