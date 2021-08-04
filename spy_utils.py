#!/usr/bin/python3 -u

'''
Funciones de uso general.
'''

d_defaults = {
    'CH0': {'A1_INF': '6.7', 'A1_SUP': '8.3', 'A2_INF': '6.0', 'A2_SUP': '9.0', 'A3_INF': '5.5', 'A3_SUP': '9.5'},
    'CH1': {'A1_INF': '-1.0', 'A1_SUP': '0.9', 'A2_INF': '-1.0', 'A2_SUP': '4.0', 'A3_INF': '-1.0', 'A3_SUP': '9.0'},
    'CH2': {'A1_INF': '0.7', 'A1_SUP': '2.3', 'A2_INF': '0.5', 'A2_SUP': '3.5', 'A3_INF': '-1.0', 'A3_SUP': '5.0'},
    'CH3': {'A1_INF': '4', 'A1_SUP': '6', 'A2_INF': '3', 'A2_SUP': '7', 'A3_INF': '2', 'A3_SUP': '8'},
    'CH4': {'A1_INF': '4', 'A1_SUP': '6', 'A2_INF': '3', 'A2_SUP': '7', 'A3_INF': '2', 'A3_SUP': '8'},
    'CH5': {'A1_INF': '4', 'A1_SUP': '6', 'A2_INF': '3', 'A2_SUP': '7', 'A3_INF': '2', 'A3_SUP': '8'}
    }


def u_parse_string( string_to_parse, field_separator=';', key_separator=':'):
    '''
    Como pueden haber campos con solo la key, para el parseo utilizo *value.
    Pero esto me devuelve una lista y no un string como requiero.
    Para esto debo ver el largo de la lista.
    '''
    d = dict()
    list_of_fields = string_to_parse.split(field_separator)
    for pair in list_of_fields:
        (key ,*value) = pair.split(key_separator)
        # Si la lista tiene al menos 1 elemento, devulevo el primero como str.
        if len(value) > 0:
            d[key] = value[0]
        #else:
        #    d[key] = ''

    #for key in d:
    #    print('DEBUG: {0}=>{1}'.format(key,d[key]))

    return d


def u_parse_cgi_line( cgi_rxline ):
    return u_parse_string( cgi_rxline, field_separator='&', key_separator='=')


def u_parse_payload( payload ):
    return u_parse_string( payload, field_separator=';', key_separator=':')


def u_print_form(form):
    # form es un diccionario
    print('Query string Form:')
    for key in form:
        print('\t{0}={1}'.format(key, form[key]))


def u_print_payload(pload):
    # pload es un diccionario
    print ('Payload:')
    for key in pload:
        print('\t{0}={1}'.format(key,pload[key]))


def u_send_response(type='', pload=''):
    #LOG.info('[%s] RSP=[%s]' % (self, self.response))
    response = 'TYPE={0}&PLOAD={1}'.format(type,pload)
    print('Content-type: text/html\n')
    print('<html><body><h1>{0}</h1></body></html>'.format(response))
    return


def u_format_fecha_hora(fecha, hora):
    '''
    Funcion auxiliar que toma la fecha y hora de los argumentos y
	las retorna en formato DATE de la BD.
    121122,180054 ==> 2012-11-22 18:00:54
    '''
    lfecha = [(fecha[i:i + 2]) for i in range(0, len(fecha), 2)]
    lhora = [(hora[i:i + 2]) for i in range(0, len(hora), 2)]
    timestamp = '20%s-%s-%s %s:%s:%s' % ( lfecha[0], lfecha[1], lfecha[2], lhora[0], lhora[1], lhora[2] )
    return timestamp


def u_dataline_to_dict(line):
    '''
    Parseo y dejo los campos en un diccionario
    Paso este diccionario a la BD para que la inserte.
    line = DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    '''
    line = line.rstrip('\n|\r|\t')
    d = u_parse_string(line, field_separator=';', key_separator=':')
    # Agrego los campos que faltan
    d['timestamp'] = u_format_fecha_hora(d['DATE'], d['TIME'])
    d['RCVDLINE'] = line
    # Elimino las claves que se que no van en la bd(DATE,TIME,CTL)
    del d['DATE']
    del d['TIME']
    return d


def u_get_fw_version(d):
    '''
    Dado el campo d{'BASE','FIRMWARE'} que es del tipo 2.0.3a, lo convierte a 203
    de modo que pueda determinar numericamente la version en comparaciones
    '''
    fw_ver = d.get(('BASE', 'FIRMWARE'), '2.0.0a')
    l=fw_ver.split('.')
    if len(l) < 3:
        l = [ '2','0','0']
    rev_mayor = int(l[0])
    rev_media = int(l[1])
    rev_menor = int(l[2][0])
    version = int(rev_mayor)*100 + int(rev_media)*10 + int(rev_menor)
    return version

def u_convert_fw_version_to_str( str_version ):
    '''
    Dado el campo d{'BASE','FIRMWARE'} que es del tipo 2.0.3a, lo convierte a 203
    de modo que pueda determinar numericamente la version en comparaciones
    '''
    l= str_version.split('.')
    if len(l) < 3:
        l = [ '2','0','0']
    rev_mayor = int(l[0])
    rev_media = int(l[1])
    rev_menor = int(l[2][0])
    version = int(rev_mayor)*100 + int(rev_media)*10 + int(rev_menor)
    return version
