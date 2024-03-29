#!/usr/bin/python3 -u

'''
Funciones de uso general.
'''

from spy_log import log

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
    #return u_parse_string( cgi_rxline, field_separator='&', key_separator='=')
    d = {k:v for (k, v) in [x.split('=') for x in cgi_rxline.split('&') if '=' in x]}
    '''
    l_fields = cgi_rxline.split('&')    # Lista con todos los pares key=value
    d = {}
    l_fields = [ x for x in l_fields if '=' in x]
    for i in l_fields:
        (k,v) = i.split('=')
        d[k]=v
    '''
    return d


def u_parse_payload( payload ):
    # return u_parse_string( payload, field_separator=';', key_separator=':')
    d = {k:v for (k, v) in [x.split(':') for x in payload.split(';') if ':' in x]}
    '''
    l_fields = payload.split(';')    # Lista con todos los pares key=value
    d = {}
    l_fields = [x for x in l_fields if ':' in x]
    for i in l_fields:
        (k,v) = i.split(':')
        d[k]=v
    '''
    return d


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


def u_send_response( fw_version=200, type='', pload=''):
    response = 'TYPE={0}&PLOAD={1}'.format(type,pload)
    # Agregamos el checksum a cada frame enviado.
    # En versiones anteriores a 4.0.4 no agrego el checksum
    if fw_version >= 404:
        cks = u_calcular_ckechsum(response)
        response += "CKS:{0};".format(cks)
    log(module=__name__, function='u_send_response', dlgid='ERROR', msg='Version={0}, rsp=[{1}]'.format(fw_version, response))

    try:
        print('Content-type: text/html\n')
        print('<html><body><h1>{0}</h1></body></html>'.format(response))
    except Exception as e:
        log(module=__name__, function='u_send_response', dlgid='ERROR', msg='EXCEPTION SEND RESPONSE [{0}]'.format(e))
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


def mbusWrite(dlgid='', register='', dataType='', value='', fdbk='', mbTag=''):
    '''
        FLOWCHART -> https://drive.google.com/file/d/191gir1No6tSEBDgU3e76ekZJqHQl5jET/view?usp=sharing

        v 1.2.3 21/04/2021

        funcion que implementa una cola en donde existe en buffer de transmisión que se puede llenar hasta cubrir el ancho de cirta ventana.
        el resto de los bytes que quedan por fuera de la ventana se insertan en una cola FIFO si no existen en la misma. En caso de que existan tanto en 
        el buffer de tx como en la cola serán actualizados.
        EX:
            mbusWrite(self.DLGID_CTRL,'2097','interger',105)
    '''
    # Dependencias
    import redis
    from spy_config import Config
    from spy_log import log

    # Definición de ventanas de buffers de transmisión
    windowsFirmNuevo = 7
    windowsFirmViejo = 3

    # parametros usados en el firmware nuevo
    MbusSlave = 2
    NumberOfReg2Read = 1 if dataType == 'interger' else 2
    dataTypeNew = 'I16' if dataType == 'interger' else 'FLOAT'
    dataCodec = 'C1032'
    MBTAG = 'MBTAG'

    # parametros usados en el firmware viejo
    dataType = 'I' if dataType == 'interger' else 'F'

    # funciones auxiliares
    def lst2str(list):
        '''
            Convierto de lista a string
              EX:
                string = lst2str(['print_log', True, 'DLGID_CTRL', 'MER001'])
                >> string = print_log,True,DLGID_CTRL,MER001
        '''
        my_str = str(list[0])
        n = 0
        for param in list:
            if n < (len(list)-1):
                n += 1
                my_str = "{my_str},{list}".format(
                    my_str=my_str, list=str(list[n]))
        return my_str

    def getRegistersInfo(redisKey):
        '''
            Obtiene la info de los registros del string almacenado en redisKey y la devuelve en un dict.
        '''
        try:
            RegistersInfo = rh.hget(dlgid, redisKey).decode()
            RegistersInfo = lst2str(RegistersInfo.split("["))
            RegistersInfo = lst2str(RegistersInfo.split("]"))
            lstRegistersInfo = RegistersInfo.split(",")

            # limpio la lista lstLastBROADCAST de elementos vacios
            for element in lstRegistersInfo:
                if element == '':
                    lstRegistersInfo.remove('')

            if redisKey == 'MODBUS' or redisKey == 'lastMODBUS':
                # extraigo la informacion que contiene el formato del firmware viejo
                n = 0
                lstRegisters = []
                lstDataType = []
                lstValues = []
                for element in lstRegistersInfo:
                    lstRegisters.append(lstRegistersInfo[n])
                    lstDataType.append(lstRegistersInfo[n+1])
                    lstValues.append(lstRegistersInfo[n+2])
                    n += 3
                    if n >= len(lstRegistersInfo):
                        break
                return dict(lstRegisters=lstRegisters, lstDataType=lstDataType, lstValues=lstValues)
            else:
                # extraigo la informacion que contiene el formato del firmware nuevo
                n = 0
                lstMbusSlave = []
                lstRegisters = []
                lstNumberOfReg2Read = []
                lstDataType = []
                lstdataCodec = []
                lstValues = []
                for element in lstRegistersInfo:
                    lstMbusSlave.append(lstRegistersInfo[n])
                    lstRegisters.append(lstRegistersInfo[n+1])
                    lstNumberOfReg2Read.append(lstRegistersInfo[n+2])
                    lstDataType.append(lstRegistersInfo[n+4])
                    lstdataCodec.append(lstRegistersInfo[n+5])
                    lstValues.append(lstRegistersInfo[n+6])
                    n += 7
                    if n >= len(lstRegistersInfo):
                        break

                return dict(lstMbusSlave=lstMbusSlave, lstRegisters=lstRegisters, lstNumberOfReg2Read=lstNumberOfReg2Read, lstDataType=lstDataType, lstdataCodec=lstdataCodec, lstValues=lstValues)
        except:
            return False

    def makeFrame2Send(RegistersInfo):
        '''
            # le entra un diccionario con los datos de los registros y devulve el frame a escribir para el envio de los registros modbus al datalogger con el firmware nuevo o viejo según la info que se le pase en el dict.
        '''
        try:
            # formato para el firmware nuevo
            n = 0
            format4FirmwNew = ''
            for register in RegistersInfo['lstRegisters']:
                if n == 0:
                    format4FirmwNew = "[{0},{1},{2},16,{3},{4},{5}]".format(
                        RegistersInfo['lstMbusSlave'][n], register, RegistersInfo['lstNumberOfReg2Read'][n], RegistersInfo['lstDataType'][n], RegistersInfo['lstdataCodec'][n], RegistersInfo['lstValues'][n])
                else:
                    format4FirmwNew = "{0}[{1},{2},{3},16,{4},{5},{6}]".format(format4FirmwNew, RegistersInfo['lstMbusSlave'][n], register, RegistersInfo[
                                                                               'lstNumberOfReg2Read'][n], RegistersInfo['lstDataType'][n], RegistersInfo['lstdataCodec'][n], RegistersInfo['lstValues'][n])
                n += 1
            return format4FirmwNew
        except:
            # formato para el firmware viejo
            n = 0
            format4FirmwOld = ''
            for register in RegistersInfo['lstRegisters']:
                if n == 0:
                    format4FirmwOld = "[{0},{1},{2}]".format(
                        register, RegistersInfo['lstDataType'][n], RegistersInfo['lstValues'][n])
                else:
                    format4FirmwOld = "{0}[{1},{2},{3}]".format(
                        format4FirmwOld, register, RegistersInfo['lstDataType'][n], RegistersInfo['lstValues'][n])
                n += 1
            return format4FirmwOld

    def scrollWindows(RegistersInfo, win):
        '''
            toma el diccionario de entrada y le pasa una ventana deslizante para obtener dos diccionarios a la salida. Uno que esté dentro de la ventana y otro que queda fueraa de la misma
        '''
        try:
            # Formato para firmwares nuevos
            reg2send = dict(lstMbusSlave=[], lstRegisters=[], lstNumberOfReg2Read=[
            ], lstDataType=[], lstdataCodec=[], lstValues=[])
            reg2save = dict(lstMbusSlave=[], lstRegisters=[], lstNumberOfReg2Read=[
            ], lstDataType=[], lstdataCodec=[], lstValues=[])
            n = 0
            for register in RegistersInfo['lstRegisters']:
                if n < win:
                    reg2send['lstMbusSlave'].append(
                        RegistersInfo['lstMbusSlave'][n])
                    reg2send['lstRegisters'].append(register)
                    reg2send['lstNumberOfReg2Read'].append(
                        RegistersInfo['lstNumberOfReg2Read'][n])
                    reg2send['lstDataType'].append(
                        RegistersInfo['lstDataType'][n])
                    reg2send['lstdataCodec'].append(
                        RegistersInfo['lstdataCodec'][n])
                    reg2send['lstValues'].append(RegistersInfo['lstValues'][n])
                else:
                    reg2save['lstMbusSlave'].append(
                        RegistersInfo['lstMbusSlave'][n])
                    reg2save['lstRegisters'].append(register)
                    reg2save['lstNumberOfReg2Read'].append(
                        RegistersInfo['lstNumberOfReg2Read'][n])
                    reg2save['lstDataType'].append(
                        RegistersInfo['lstDataType'][n])
                    reg2save['lstdataCodec'].append(
                        RegistersInfo['lstdataCodec'][n])
                    reg2save['lstValues'].append(RegistersInfo['lstValues'][n])
                n += 1
        except:
            # Formato para firmwares viejos
            reg2send = dict(lstRegisters=[], lstDataType=[], lstValues=[])
            reg2save = dict(lstRegisters=[], lstDataType=[], lstValues=[])
            n = 0
            for register in RegistersInfo['lstRegisters']:
                if n < win:
                    reg2send['lstRegisters'].append(register)
                    reg2send['lstDataType'].append(
                        RegistersInfo['lstDataType'][n])
                    reg2send['lstValues'].append(RegistersInfo['lstValues'][n])
                else:
                    reg2save['lstRegisters'].append(register)
                    reg2save['lstDataType'].append(
                        RegistersInfo['lstDataType'][n])
                    reg2save['lstValues'].append(RegistersInfo['lstValues'][n])
                n += 1
        return reg2send, reg2save

    def writeFrameIn(Frame2SendReg, redisKey):
        '''
            escribo el redisKey con el buffer o el tailFIFO el Frame2SendReg bajo ciertas condiciones.
        '''
        if redisKey == 'BROADCAST':
            if Frame2SendReg:
                rh.hset(dlgid, redisKey, Frame2SendReg)
        elif redisKey == 'lastBROADCAST':
            if Frame2SendReg:
                rh.hset(dlgid, redisKey, Frame2SendReg)
            else:
                rh.hdel(dlgid, redisKey)
        elif redisKey == 'MODBUS':
            if Frame2SendReg:
                rh.hset(dlgid, redisKey, Frame2SendReg)
        elif redisKey == 'lastMODBUS':
            if Frame2SendReg:
                rh.hset(dlgid, redisKey, Frame2SendReg)
            else:
                rh.hdel(dlgid, redisKey)

    def appEndReg(RegistersInfo, Desable):
        '''
            añado al final de la cola el registro actual si Desable is False
        '''
        if not Desable:
            try:
                # anado los valores nuevos que se quieren poner para el formato del firmware nuevo
                RegistersInfo['lstMbusSlave'].append(MbusSlave)
                RegistersInfo['lstRegisters'].append(register)
                RegistersInfo['lstNumberOfReg2Read'].append(NumberOfReg2Read)
                RegistersInfo['lstDataType'].append(dataTypeNew)
                RegistersInfo['lstdataCodec'].append(dataCodec)
                RegistersInfo['lstValues'].append(value)
            except:
                # anado los valores nuevos que se quieren poner para el formato del firmware viejo
                RegistersInfo['lstRegisters'].append(register)
                RegistersInfo['lstDataType'].append(dataType)
                RegistersInfo['lstValues'].append(value)
        return RegistersInfo

    def IsExist(redisKey):
        '''
            se detecta si existe el redisKey devolviendo true or false
        '''
        if rh.hexists(dlgid, redisKey) == 1:
            return True
        else:
            return False

    def IsRedisConnected(host='192.168.0.6', port='6379', db='0'):
        '''
            se conecta con la RedisDb y devuelve el objeto rh asi como el estado de la conexion
        '''
        try:
            rh = redis.Redis(host, port, db)
            return True, rh
        except Exception as err_var:
            log(module=__name__, function='__init__',
                dlgid=dlgid, msg='Redis init ERROR !!')
            log(module=__name__, function='__init__',
                dlgid=dlgid, msg='EXCEPTION {}'.format(err_var))
            return False, ''

    def IsNull(key):
        '''
            detecta si key tiene el valor NUL. En caso de que lo tenga ejecuta una limpieza
        '''
        try:
            if rh.hget(dlgid, key).decode() == 'NUL':
                # if key == 'BROADCAST':
                #     if rh.exists(dlgid,'MODBUS'): rh.hdel(dlgid,'MODBUS')
                #     if rh.exists(dlgid,'lastMODBUS'): rh.hdel(dlgid,'lastMODBUS')
                # elif key == 'MODBUS':
                #     if rh.exists(dlgid,'BROADCAST'): rh.hdel(dlgid,'BROADCAST')
                #     if rh.exists(dlgid,'lastBROADCAST'): rh.hdel(dlgid,'lastBROADCAST')
                return True
            else:
                return False
        except:
            return True

    def IsExisting(key):
        '''
            verifica si existe key. Restorna True en caso positivo y False en caso negativo
        '''
        try:
            if rh.hexists(dlgid, key):
                return True
            else:
                return False
        except:
            return False

    def updateReg(RegistersInfo):
        '''
            Actualiza el RegistersInfo que se le pasa como parametro en caso de que el registro actual este contenido en el mismo.
            Se devuelve el diccionario actualizado y un parametro adicional que dice si se realizo actualizacion o no
        '''
        if register in RegistersInfo['lstRegisters']:
            # obtengo la ubicacion del registro a actualizar
            registerIndex = RegistersInfo['lstRegisters'].index(register)
            try:
                # para los firmwares nuevos
                if RegistersInfo['lstMbusSlave'][registerIndex] == MbusSlave:
                    updated = False
                else:
                    RegistersInfo['lstMbusSlave'][registerIndex] = MbusSlave
                    updated = True
                
                if RegistersInfo['lstNumberOfReg2Read'][registerIndex] == NumberOfReg2Read:
                    updated = False
                else:
                    RegistersInfo['lstNumberOfReg2Read'][registerIndex] = NumberOfReg2Read
                    updated = True
                
                if RegistersInfo['lstdataCodec'][registerIndex] == dataCodec:
                    updated = False
                else:
                    RegistersInfo['lstdataCodec'][registerIndex] = dataCodec
                    updated = True
                
                if RegistersInfo['lstDataType'][registerIndex] == dataTypeNew:
                    updated = False
                else:
                    RegistersInfo['lstDataType'][registerIndex] = dataTypeNew
                    updated = True
                
                if RegistersInfo['lstValues'][registerIndex] == value:
                    updated = False
                else:
                    RegistersInfo['lstValues'][registerIndex] = value
                    updated = True

            except:
                # para los firmwares viejos
                if RegistersInfo['lstDataType'][registerIndex] == dataType:
                    updated = False
                else:
                    RegistersInfo['lstDataType'][registerIndex] = dataType
                    updated = True
                
                if RegistersInfo['lstValues'][registerIndex] == value:
                    updated = False
                else:
                    RegistersInfo['lstValues'][registerIndex] = value
                    updated = True
             
            inRegInfo = True
        else:
            inRegInfo = False
            updated = False
        return RegistersInfo, inRegInfo, updated

    def mbTagGenerator(delete):
        '''en cada llamada crea valores continuos que van desde 0-50'''
        if not delete:
            if rh.hexists(dlgid, MBTAG) == 1:
                rdMbtag = int(rh.hget(dlgid, MBTAG).decode())
                if (rdMbtag == 50):
                    rh.hset(dlgid, MBTAG, 1)
                else:
                    rh.hset(dlgid, MBTAG, rdMbtag + 1)
            else:
                rh.hset(dlgid, MBTAG, 1)
        else:
            if rh.hexists(dlgid, MBTAG) == 1:
                rh.hdel(dlgid, MBTAG)

    def IsOkRx():
        rdMbtag = rh.hget(dlgid, MBTAG).decode() if rh.hexists(dlgid, MBTAG) == 1 else '-1'

        if (fdbk == 'ACK' and rdMbtag == mbTag):
            return True 
        else:
            return False

    def setKeyNull(key):
        rh.hset(dlgid, key, 'NUL')

    # main program
    redisConnection,rh = IsRedisConnected(host=Config['REDIS']['host'], port=Config['REDIS']['port'], db=Config['REDIS']['db'])
    # redisConnection, rh = IsRedisConnected()
    if redisConnection:
        if register:
            # para firmwares nuevos
            if IsExist('BROADCAST'):

                if IsNull('BROADCAST'):

                    if IsExisting('lastBROADCAST'):

                        dictLastBROADCAST = getRegistersInfo('lastBROADCAST')

                        dictLastBROADCAST, IsInlastBROADCAST, WasUpdatedLastBROADCAST = updateReg(            
                            dictLastBROADCAST)

                        dictLastBROADCAST = appEndReg(
                            dictLastBROADCAST, IsInlastBROADCAST)

                        RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                            dictLastBROADCAST, windowsFirmNuevo)

                        Frame2SendRegFirmwNew = makeFrame2Send(
                            RegistersInfo2Send)

                        Frame2SaveRegFirmwNew = makeFrame2Send(
                            RegistersInfo2Save)

                        mbTagGenerator(False)

                        writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')

                        writeFrameIn(Frame2SaveRegFirmwNew, 'lastBROADCAST')

                    else:

                        Frame2SendRegFirmwNew = makeFrame2Send(dict(lstMbusSlave=[MbusSlave], lstRegisters=[register], lstNumberOfReg2Read=[
                                                               NumberOfReg2Read], lstDataType=[dataTypeNew], lstdataCodec=[dataCodec], lstValues=[value]))

                        mbTagGenerator(False)

                        writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')
                else:

                    if IsExisting('lastBROADCAST'):

                        dictBROADCAST = getRegistersInfo('BROADCAST')

                        dictBROADCAST, IsInBROADCAST, WasUpdatedBROADCAST = updateReg(
                            dictBROADCAST)

                        if not IsInBROADCAST:

                            dictLastBROADCAST = getRegistersInfo(
                                'lastBROADCAST')

                            dictLastBROADCAST, IsInLastBroadCast, WasUpdatedLastBroadCast = updateReg(
                                dictLastBROADCAST)

                            dictLastBROADCAST = appEndReg(
                                dictLastBROADCAST, IsInLastBroadCast)

                            Frame2SaveRegFirmwNew = makeFrame2Send(
                                dictLastBROADCAST)

                            writeFrameIn(Frame2SaveRegFirmwNew,
                                         'lastBROADCAST')

                            if IsOkRx():

                                RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                                    dictLastBROADCAST, windowsFirmNuevo)

                                Frame2SendRegFirmwNew = makeFrame2Send(
                                    RegistersInfo2Send)

                                Frame2SaveRegFirmwNew = makeFrame2Send(
                                    RegistersInfo2Save)

                                mbTagGenerator(False)

                                writeFrameIn(
                                    Frame2SendRegFirmwNew, 'BROADCAST')

                                writeFrameIn(Frame2SaveRegFirmwNew,
                                             'lastBROADCAST')

                        else:

                            if WasUpdatedBROADCAST:

                                Frame2SendRegFirmwNew = makeFrame2Send(
                                    dictBROADCAST)
                                
                                mbTagGenerator(False)

                                writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')

                    else:

                        dictBROADCAST = getRegistersInfo('BROADCAST')

                        dictBROADCAST, IsInBROADCAST, WasUpdatedInBroadCast = updateReg(
                            dictBROADCAST)

                        if not IsInBROADCAST:

                            if len(dictBROADCAST['lstRegisters']) < windowsFirmNuevo:

                                dictBROADCAST = appEndReg(
                                    dictBROADCAST, IsInBROADCAST)

                                Frame2SendRegFirmwNew = makeFrame2Send(
                                    dictBROADCAST)

                                mbTagGenerator(False)

                                writeFrameIn(
                                    Frame2SendRegFirmwNew, 'BROADCAST')

                            else:

                                Frame2SaveRegFirmwNew = makeFrame2Send(dict(lstMbusSlave=[MbusSlave], lstRegisters=[register], lstNumberOfReg2Read=[
                                                                       NumberOfReg2Read], lstDataType=[dataTypeNew], lstdataCodec=[dataCodec], lstValues=[value]))

                                writeFrameIn(
                                    Frame2SaveRegFirmwNew, 'lastBROADCAST')

                        else:

                            if WasUpdatedInBroadCast:
                            
                                Frame2SendRegFirmwNew = makeFrame2Send(
                                    dictBROADCAST)

                                mbTagGenerator(False)

                                writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')

            # para fimrwares viejos
            if IsExist('MODBUS'):

                if IsNull('MODBUS'):

                    if IsExisting('lastMODBUS'):

                        dictlastMODBUS = getRegistersInfo('lastMODBUS')

                        dictlastMODBUS, IsInlastMODBUS, IsUpdatedlastMODBUS = updateReg(dictlastMODBUS)

                        dictlastMODBUS = appEndReg(dictlastMODBUS, IsInlastMODBUS)

                        RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                            dictlastMODBUS, windowsFirmViejo)

                        Frame2SendRegFirmwOld = makeFrame2Send(
                            RegistersInfo2Send)

                        Frame2SaveRegFirmwOld = makeFrame2Send(
                            RegistersInfo2Save)

                        writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

                        writeFrameIn(Frame2SaveRegFirmwOld, 'lastMODBUS')

                    else:

                        Frame2SendRegFirmwOld = makeFrame2Send(
                            dict(lstRegisters=[register], lstDataType=[dataType], lstValues=[value]))

                        writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

                else:

                    if IsExisting('lastMODBUS'):

                        dictMODBUS = getRegistersInfo('MODBUS')

                        dictMODBUS, IsInMODBUS, WasUpdatedInMODBUS = updateReg(dictMODBUS)

                        if not IsInMODBUS:

                            dictLastMODBUS = getRegistersInfo('lastMODBUS')

                            dictLastMODBUS, IsInLastMODBUS, WasUpdatedLastMODBUS = updateReg(
                                dictLastMODBUS)

                            dictLastMODBUS = appEndReg(
                                dictLastMODBUS, IsInLastMODBUS)

                            Frame2SaveRegFirmwOld = makeFrame2Send(
                                dictLastMODBUS)

                            writeFrameIn(Frame2SaveRegFirmwOld, 'lastMODBUS')

                        else:

                            Frame2SendRegFirmwOld = makeFrame2Send(dictMODBUS)

                            writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

                    else:

                        dictMODBUS = getRegistersInfo('MODBUS')

                        dictMODBUS, IsInMODBUS, WasUpdatedMODBUS = updateReg(dictMODBUS)

                        if not IsInMODBUS:

                            if len(dictMODBUS['lstRegisters']) < windowsFirmViejo:

                                dictMODBUS = appEndReg(
                                    dictMODBUS, IsInMODBUS)

                                Frame2SendRegFirmwOld = makeFrame2Send(
                                    dictMODBUS)

                                writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

                            else:

                                Frame2SaveRegFirmwOld = makeFrame2Send(
                                    dict(lstRegisters=[register], lstDataType=[dataTypeNew], lstValues=[value]))

                                writeFrameIn(
                                    Frame2SaveRegFirmwOld, 'lastMODBUS')

                        else:

                            Frame2SendRegFirmwOld = makeFrame2Send(dictMODBUS)

                            writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

        else:
            # para firmwares nuevos
            if IsExist('BROADCAST'):

                if IsNull('BROADCAST'):

                    if IsExisting('lastBROADCAST'):

                        RegistersInfo = getRegistersInfo('lastBROADCAST')

                        RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                            RegistersInfo, windowsFirmNuevo)

                        Frame2SendRegFirmwNew = makeFrame2Send(
                            RegistersInfo2Send)

                        Frame2SaveRegFirmwNew = makeFrame2Send(
                            RegistersInfo2Save)

                        mbTagGenerator(False)

                        writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')

                        writeFrameIn(Frame2SaveRegFirmwNew, 'lastBROADCAST')
                else:

                    if IsOkRx():
                        if IsExisting('lastBROADCAST'):

                            RegistersInfo = getRegistersInfo('lastBROADCAST')

                            RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                                RegistersInfo, windowsFirmNuevo)

                            Frame2SendRegFirmwNew = makeFrame2Send(
                                RegistersInfo2Send)

                            Frame2SaveRegFirmwNew = makeFrame2Send(
                                RegistersInfo2Save)

                            mbTagGenerator(False)

                            writeFrameIn(Frame2SendRegFirmwNew, 'BROADCAST')

                            writeFrameIn(Frame2SaveRegFirmwNew,
                                         'lastBROADCAST')

                        else:

                            setKeyNull('BROADCAST')

                            mbTagGenerator(True)

            # para firmwares viejos
            if IsExist('MODBUS'):

                if IsNull('MODBUS'):

                    if IsExisting('lastMODBUS'):

                        RegistersInfo = getRegistersInfo('lastMODBUS')

                        RegistersInfo2Send, RegistersInfo2Save = scrollWindows(
                            RegistersInfo, windowsFirmViejo)

                        Frame2SendRegFirmwOld = makeFrame2Send(
                            RegistersInfo2Send)

                        Frame2SaveRegFirmwOld = makeFrame2Send(
                            RegistersInfo2Save)

                        writeFrameIn(Frame2SendRegFirmwOld, 'MODBUS')

                        writeFrameIn(Frame2SaveRegFirmwOld, 'lastMODBUS')     

def u_calcular_ckechsum(line):
    '''
     Cambiamos la forma de calcular el checksum porque el xor
     si ponemos 2 veces el miso caracter no lo detecta !!!!
     '''
    log(module=__name__, function='u_calcular_ckechsum', dlgid='ERROR', msg='CKS line [{0}]'.format(line))
    cks = 0
    for c in line:
        #cks ^= ord(c)
        cks = (cks + ord(c)) % 256
    return cks

        

                