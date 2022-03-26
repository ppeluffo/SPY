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

    # parametros usados en el firmware nuevo
    MbusSlave = 2
    NumberOfReg2Read = '2'
    dataTypeNew ='FLOAT'
    if dataType == 'interger': dataTypeNew ='I16' 
    if dataType == 'interger': NumberOfReg2Read = '1'
    dataCodec = 'C1032'

    
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
                my_str = "{my_str},{list}".format(my_str=my_str, list=str(list[n]))
        return my_str
    
    # para el firmware viejo
    def getLastModbusData():
        '''
            retorno listas con los registros, el tipo de datos y el valor
        '''
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
        return lstRegisters,lstDataTypes,lstValues
    def insertOrUpdateRegister(register,dataType,value):
        '''
            actualizo el valor del registro si se encuentra en cola de envio (lastMODBUS)
            En caso de que no se encuentre lo inserto
        ''' 
        if register in lstRegisters:
            # actualizo los nuevos valores que se quieren poner
            lstDataTypes[lstRegisters.index(register)] = dataType
            lstValues[lstRegisters.index(register)] = value
        else:
            # anado los valores nuevos que se quieren poner
            lstRegisters.append(register)
            lstDataTypes.append(dataType)
            lstValues.append(value)

        # Armo el frame a escribir en los registros del datalogger para el firmware viejo
        n = 0
        currentModbusOld = ''
        for element in lstRegisters:
            if n == 0: currentModbusOld = "[{lstRegisters},{lstDataTypes},{lstValues}]".format(lstRegisters=lstRegisters[n], lstDataTypes=lstDataTypes[n], lstValues=lstValues[n])
            else: currentModbusOld = "{currentModbusOld}[{lstRegisters},{lstDataTypes},{lstValues}]".format(currentModbusOld=currentModbusOld,lstRegisters=lstRegisters[n],lstDataTypes=lstDataTypes[n],lstValues=lstValues[n])
            n += 1

        # mando la orden de actualizar la cola 
        rh.hset(dlgid,'lastMODBUS',currentModbusOld)            # para los firmwares viejos
    def sendRegToDLG(lstRegisters,lstDataTypes,lstValues,FifioWindows):
        '''
            Saca de la cola la cantidad de registros que indica la ventana y los envia al PLC
        '''
        
        lstRegToSendOldFormat = ''  # string que se va a colocar en redis para transmitir datos modbus en el firmware viejo
        currentFIFOqueue = ''       # string que iindica como queda la cola luego haber transmitido datos
        
        # Si la cola es menor o igual que la ventana entonces en esta corrida se logran enviar todos los registros
        if len(lstRegisters) <= FifioWindows:   rh.hdel(dlgid,'lastMODBUS')     

        # armo el strig a transmitir para datalogger con firware viejo
        n = 0
        for register in lstRegisters:
            if n == 0: lstRegToSendOldFormat = "[{register},{lstDataTypes},{lstValues}]".format(register=register,lstDataTypes=lstDataTypes[n],lstValues=lstValues[n])
            else: lstRegToSendOldFormat = "{lstRegToSendOldFormat}[{register},{lstDataTypes},{lstValues}]".format(lstRegToSendOldFormat=lstRegToSendOldFormat, register=register,lstDataTypes=lstDataTypes[n],lstValues=lstValues[n])
            n += 1
            if n == FifioWindows: break        

        # elimino los datos transmitidos
        n = 0
        while True:
            try:
                # elimino los datos transmitidos
                lstRegisters.pop(0)
                lstDataTypes.pop(0)
                lstValues.pop(0)
                n += 1
                if n == FifioWindows: break
            except:
                break
        
        # Armo como quedaria la cola despues del ultimo envio
        n = 0
        for register in lstRegisters:
            if n == 0: currentFIFOqueue = "[{register},{lstDataTypes},{lstValues}]".format(register=register,lstDataTypes=lstDataTypes[n],lstValues=lstValues[n])
            else: currentFIFOqueue = "{currentFIFOqueue}[{register},{lstDataTypes},{lstValues}]".format(currentFIFOqueue=currentFIFOqueue, register=register, lstDataTypes=lstDataTypes[n], lstValues=lstValues[n])
            n += 1  
  
        # mando al datalogger los registros
        rh.hset(dlgid,'MODBUS',lstRegToSendOldFormat)
        
        # mando la orden de actualizar la cola para los firmwares viejos
        if currentFIFOqueue:    rh.hset(dlgid,'lastMODBUS',currentFIFOqueue)     

    # para el firmware nuevo
    def getLastBroadcastData():
        '''
            retorno listas todos los datos
        '''
        lastBROADCAST = rh.hget(dlgid,'lastBROADCAST').decode()
        lastBROADCAST = lst2str(lastBROADCAST.split("["))
        lastBROADCAST = lst2str(lastBROADCAST.split("]"))
        lstLastBROADCAST = lastBROADCAST.split(",")
                        
        # limpio la lista lstLastBROADCAST de elementos vacios
        for element in lstLastBROADCAST:
            if element == '': lstLastBROADCAST.remove('')             
         
        # extraigo la informacion de los registros, el dataType y los valores
        n = 0
        lstMbusSlave = []
        lstRegisters = []
        lstNumberOfReg2Read = []
        lstDataType = []
        lstdataCodec = []
        lstValues = []
        for element in lstLastBROADCAST:
            lstMbusSlave.append(lstLastBROADCAST[n])
            lstRegisters.append(lstLastBROADCAST[n+1])
            lstNumberOfReg2Read.append(lstLastBROADCAST[n+2])
            lstDataType.append(lstLastBROADCAST[n+4])
            lstdataCodec.append(lstLastBROADCAST[n+5])
            lstValues.append(lstLastBROADCAST[n+6])
            n += 7
            if n >= len(lstLastBROADCAST): break
        return lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues
    def insertOrUpdateRegister2(lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues):
        '''
            actualizo el valor del registro si se encuentra en cola de envio (lastMODBUS)
            En caso de que no se encuentre lo inserto
        '''
        if register in lstRegisters:
            # actualizo los nuevos valores que se quieren poner
            lstMbusSlave[lstRegisters.index(register)] = MbusSlave
            lstNumberOfReg2Read[lstRegisters.index(register)] = NumberOfReg2Read
            lstDataType[lstRegisters.index(register)] = dataTypeNew
            lstdataCodec[lstRegisters.index(register)] = dataCodec
            lstValues[lstRegisters.index(register)] = value
        else:
            # anado los valores nuevos que se quieren poner
            lstMbusSlave.append(MbusSlave)
            lstRegisters.append(register)
            lstNumberOfReg2Read.append(NumberOfReg2Read)
            lstDataType.append(dataTypeNew)
            lstdataCodec.append(dataCodec)
            lstValues.append(value)
        
        # Armo el frame a escribir en los registros del datalogger para el firmware nuevo
        n = 0
        currentModbusNew = ''
        for registers in lstRegisters:
            if n == 0: 
                currentModbusNew = "[{lstMbusSlave},{registers},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(lstMbusSlave=lstMbusSlave[n],registers=registers,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            else: 
                currentModbusNew = "{currentModbusNew}[{lstMbusSlave},{registers},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(currentModbusNew=currentModbusNew,lstMbusSlave=lstMbusSlave[n],registers=registers,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            n += 1

        # mando la orden de actualizar la cola 
        rh.hset(dlgid,'lastBROADCAST',currentModbusNew)            # para los firmwares viejos         
    def sendRegToDLG2(lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues,FifioWindows):
        '''
            Saca de la cola la cantidad de registros que indica la ventana y los envia al PLC
        '''
        
        lstRegToSendNewFormat = ''  # string que se va a colocar en redis para transmitir datos modbus en el firmware nuevo
        currentFIFOqueue = ''       # string que iindica como queda la cola luego haber transmitido datos
        
        # Si la cola es menor o igual que la ventana entonces en esta corrida se logran enviar todos los registros
        if len(lstRegisters) <= FifioWindows:   rh.hdel(dlgid,'lastBROADCAST')     
        
        # armo el strig a transmitir para datalogger con firware nuevo
        n = 0
        for register in lstRegisters:
            if n == 0: 
                lstRegToSendNewFormat = "[{lstMbusSlave},{register},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(lstMbusSlave=lstMbusSlave[n],register=register,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            else: 
                lstRegToSendNewFormat = "{lstRegToSendNewFormat}[{lstMbusSlave},{register},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(lstRegToSendNewFormat=lstRegToSendNewFormat, lstMbusSlave=lstMbusSlave[n],register=register,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            n += 1
            if n == FifioWindows: break         

        n = 0
        while True:
            try:
                # elimino los datos transmitidos
                lstMbusSlave.pop(0)
                lstRegisters.pop(0)
                lstNumberOfReg2Read.pop(0)
                lstDataType.pop(0)
                lstdataCodec.pop(0)
                lstValues.pop(0)
                n += 1
                if n == FifioWindows: break
            except:
                break

        # Armo como quedaria la cola despues del ultimo envio
        n = 0
        for register in lstRegisters:
            if n == 0: \
                currentFIFOqueue = "[{lstMbusSlave},{register},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(lstMbusSlave=lstMbusSlave[n],register=register,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            else: 
                currentFIFOqueue = "{currentFIFOqueue}[{lstMbusSlave},{register},{lstNumberOfReg2Read},16,{lstDataType},{lstdataCodec},{lstValues}]".format(currentFIFOqueue=currentFIFOqueue, lstMbusSlave=lstMbusSlave[n],register=register,lstNumberOfReg2Read=lstNumberOfReg2Read[n],lstDataType=lstDataType[n],lstdataCodec=lstdataCodec[n],lstValues=lstValues[n])
            n += 1 
  
        # mando al datalogger los registros
        rh.hset(dlgid,'BROADCAST',lstRegToSendNewFormat)
        
        # mando la orden de actualizar la cola para los firmwares viejos
        if currentFIFOqueue:    rh.hset(dlgid,'lastBROADCAST',currentFIFOqueue)     

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

    # Solo ejecuto la logica si tengo conexion a la base de datos
    if connected:
        if   dataType == 'interger':    dataType ='I'
        elif dataType == 'float':       dataType ='F'
        
        #
        ## FIRMWARE VIEJO --------------------------
        if register:
            # llamado con registros nuevos para escribir
            if not rh.hexists(dlgid,'lastMODBUS'):
                #rh.hset(dlgid,'MODBUS','[{0},{1},{2}]'.format(register,dataType,value))
                rh.hset(dlgid,'lastMODBUS','[{0},{1},{2}]'.format(register,dataType,value))
            else:
                # leo todos los registros, datos y valores que estan en cola
                lstRegisters,lstDataTypes,lstValues = getLastModbusData()
                #
                # Anado o actualizo el nuevo registro que se quiere escribir
                insertOrUpdateRegister(register,dataType,value)
               
        if rh.hexists(dlgid,'lastMODBUS'):  
            if rh.hexists(dlgid,'MODBUS'):                                        # reviso si hay valores para enviar
                if rh.hget(dlgid,'MODBUS').decode() == 'NUL':                           # reviso si ya se enviaron los anteriores
                    lstRegisters,lstDataTypes,lstValues = getLastModbusData()
                    sendRegToDLG(lstRegisters,lstDataTypes,lstValues,3)
        
        #
        ## FIRMWARE NUEVO --------------------------
        if register:
            # llamado con registros nuevos para escribir   
            if not rh.hexists(dlgid,'lastBROADCAST'):
                #rh.hset(dlgid,'BROADCAST','[{0},{1},{2},16,{3},{4},{5}]'.format(MbusSlave,register,NumberOfReg2Read,dataTypeNew,dataCodec,value))
                rh.hset(dlgid,'lastBROADCAST','[{0},{1},{2},16,{3},{4},{5}]'.format(MbusSlave,register,NumberOfReg2Read,dataTypeNew,dataCodec,value))
            else:
                # leo todos los registros, datos y valores que estan en cola
                #getLastBroadcastData()
                lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues = getLastBroadcastData()
                #
                # Anado o actualizo el nuevo registro que se quiere escribir
                insertOrUpdateRegister2(lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues)
               
        if rh.hexists(dlgid,'lastBROADCAST'):   
            if rh.hexists(dlgid,'BROADCAST'):                                              # reviso si hay valores para enviar
                if rh.hget(dlgid,'BROADCAST').decode() == 'NUL':                           # reviso si ya se enviaron los anteriores
                    lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues = getLastBroadcastData()
                    sendRegToDLG2(lstMbusSlave,lstRegisters,lstNumberOfReg2Read,lstDataType,lstdataCodec,lstValues,8)



        

                