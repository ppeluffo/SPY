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
        else:
            d[key] = ''
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
