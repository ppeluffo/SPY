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



def mbusWrite(dlgid,register,dataType,value):
    '''
        dlgid       => datalogger por el cual se quiere mandar el valor del registro modbus
        register    => valor del registro modbus que se quiere escribir
        dataType    => tipo de dato que se quiere escribir [ interger | float ]
        value       => valor que se quiere poner en este registro

        EX: mbusWrite(self.DLGID_CTRL,'2097','interger',105)
    '''
    # Dependencias
    import redis
    from spy_config import Config
    from spy_log import log

    def lst2str(list):
        '''
            Convierto de lista a string
              EX:
                list = ['print_log', True, 'DLGID_CTRL', 'MER001']
                string = lst2str(list)
                string = print_log,True,DLGID_CTRL,MER001
        '''
        my_str = str(list[0])
        n = 0
        for param in list:
            if n < (len(list)-1): 
                n += 1
                my_str = f"{my_str},{str(list[n])}"
        return my_str
    
    # Establezco conexión con bd redis
    connected = ''
    rh = ''
    try:
        rh = redis.Redis(host=Config['REDIS']['host'], port=Config['REDIS']['port'], db=Config['REDIS']['db'])
        connected = True
    except Exception as err_var:
        log(module=__name__, function='__init__', dlgid=dlgid, msg='Redis init ERROR !!')
        log(module=__name__, function='__init__', dlgid=dlgid, msg='EXCEPTION {}'.format(err_var))
        connected = False

    if connected:
        if   dataType == 'interger':    dataType ='I'
        elif dataType == 'float':       dataType ='F'
            
        
        if not rh.hexists(dlgid,'MODBUS'):
            rh.hset(dlgid,'MODBUS','[{0},{1},{2}]'.format(register,dataType,value))
            rh.hset(dlgid,'lastMODBUS','[{0},{1},{2}]'.format(register,dataType,value))
        else:
            if rh.hget(dlgid,'MODBUS').decode() == 'NUL':
                rh.hdel(dlgid,'lastMODBUS')              # check if all register was send to dlg and del lastMODBUS
            
            if not rh.hexists(dlgid,'lastMODBUS'):
                rh.hset(dlgid,'MODBUS','[{0},{1},{2}]'.format(register,dataType,value))
                rh.hset(dlgid,'lastMODBUS','[{0},{1},{2}]'.format(register,dataType,value))
            else:
                lastMODBUS = rh.hget(dlgid,'lastMODBUS').decode()
                lastMODBUS = lst2str(lastMODBUS.split("["))
                lastMODBUS = lst2str(lastMODBUS.split("]"))
                lstlastMODBUS = lastMODBUS.split(",")
                    
                # limpio la lista lstlastMODBUS de elementos vacios
                for element in lstlastMODBUS:
                    if element == '': lstlastMODBUS.remove('')             

                # extraigo la informacion de los registros, el dataType y los valores
                n = 0
                lstRegisters = []
                lstDataTypes = []
                lstValues = []
                for element in lstlastMODBUS:
                    lstRegisters.append(lstlastMODBUS[n])
                    lstDataTypes.append(lstlastMODBUS[n+1])
                    lstValues.append(lstlastMODBUS[n+2])
                    n += 3
                    if n >= len(lstlastMODBUS): break

                if register in lstlastMODBUS:
                    # actualizo los nuevos valores que se quieren poner
                    lstDataTypes[lstRegisters.index(register)] = dataType
                    lstValues[lstRegisters.index(register)] = value
                else:
                    # anado los valores nuevos que se quieren poner
                    lstRegisters.append(register)
                    lstDataTypes.append(dataType)
                    lstValues.append(value)

                n = 0
                currentModbus = ''
                for element in lstRegisters:
                    if n == 0: currentModbus = f"[{lstRegisters[n]},{lstDataTypes[n]},{lstValues[n]}]"
                    else: currentModbus = f"{currentModbus}[{lstRegisters[n]},{lstDataTypes[n]},{lstValues[n]}]"
                    n += 1

                # mando la orden de escribir al datalogger
                rh.hset(dlgid,'MODBUS',currentModbus)
                rh.hset(dlgid,'lastMODBUS',currentModbus)