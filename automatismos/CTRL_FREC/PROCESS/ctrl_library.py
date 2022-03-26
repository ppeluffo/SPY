#!/usr/aut_env/bin/python3.8
'''
LIBRERIA DE APLICACION CTRL_FREC

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 3.3.2 07-06-2020

''' 

# LIBRERIAS
import redis
import json

#CONEXIONES
from CTRL_FREC.PROCESS.drv_visual import dic
from __CORE__.drv_logs import *
from __CORE__.drv_redis import Redis
from __CORE__.drv_dlg import douts,pump1,emerg_system,read_param,dlg_detection,set_outs,get_outs
from __CORE__.mypython import lst2str,str2lst,str2bool,not_dec,config_var
from posix import read





# CLASES DE LA LIBRERIA
class ctrlProcess(object):
    '''
    FUNCIONES USADAS POR ctrl_process_frec.py
    '''
    
    def __init__(self,LIST_CONFIG):
        '''
        Constructor
        '''
        #
        ## DEFINICION DE VARIABLES DE LA CLASE
        self.config = config_var(LIST_CONFIG)
        self.print_log = self.config.lst_get('print_log')
        self.LOG_LEVEL = self.config.lst_get('LOG_LEVEL')
        self.DLGID_CTRL = self.config.lst_get('DLGID_CTRL')
        self.TYPE = self.config.lst_get('TYPE')
        self.ENABLE_OUTPUTS = self.config.lst_get('ENABLE_OUTPUTS')
        self.ENABLE_OUTPUTS = str2bool(self.config.lst_get('ENABLE_OUTPUTS'))
        
        self.TYPE_IN_FREC = self.config.lst_get('TYPE_IN_FREC')
        self.DLGID_REF = self.config.lst_get('DLGID_REF')
        self.CHANNEL_REF = self.config.lst_get('CHANNEL_REF')
        self.TYPE_IN_FREC = self.config.lst_get('TYPE_IN_FREC')
        self.DLGID_REF_1 = self.config.lst_get('DLGID_REF_1')
        self.CHANNEL_REF_1 = self.config.lst_get('CHANNEL_REF_1')
        self.PROGRAMMED_FREC =self.config.lst_get('PROGRAMMED_FREC')
        
        ## INSTANCIAS
        self.logs = ctrl_logs(self.TYPE,'CTRL_FREC_process',self.DLGID_CTRL,self.print_log,self.LOG_LEVEL)
        self.redis = Redis()
        
    def chequeo_alarmas(self):
        
        name_function = 'CHEQUEO_ALARMAS'
        
        # PIERTA DEL GABINETE
        if read_param(self.DLGID_CTRL,'GA') == '1':
            self.logs.print_inf(name_function, 'GABINETE_ABIERTO')
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('GABINETE_ABIERTO', 'name'), dic.get_dic('TX_ERROR', 'True_value'))
        elif read_param(self.DLGID_CTRL,'GA') == '0':
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('GABINETE_ABIERTO', 'name'), dic.get_dic('TX_ERROR', 'False_value'))
        else:
            self.logs.print_inf(name_function, f"error in {name_function}, GA = {read_param(self.DLGID_CTRL,'GA')}")
            # DEJAR REGISTRO DEL ERROR
            self.logs.script_performance(f"error in {name_function}, GA = {read_param(self.DLGID_CTRL,'GA')}")
            
        # FALLA ELECTRICA
        if read_param(self.DLGID_CTRL,'FE') == '1':
            self.logs.print_inf(name_function, 'FALLA ELECTRICA')
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('FALLA_ELECTRICA', 'name'), dic.get_dic('FALLA_ELECTRICA', 'True_value'))
        elif read_param(self.DLGID_CTRL,'FE') == '0':
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('FALLA_ELECTRICA', 'name'), dic.get_dic('FALLA_ELECTRICA', 'False_value'))
        else:
            self.logs.print_inf(name_function, f"error in {name_function}, FE = {read_param(self.DLGID_CTRL,'FE')}")
            # DEJAR REGISTRO DEL ERROR
            self.logs.script_performance(f"error in {name_function}, FE = {read_param(self.DLGID_CTRL,'FE')}")
             
        # FALLA TERMICA 1
        if read_param(self.DLGID_CTRL,'FT1') == '1':
            self.logs.print_inf(name_function, 'FALLA TERMICA 1')
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('FALLA_TERMICA_1', 'name'), dic.get_dic('FALLA_ELECTRICA', 'True_value'))
        elif read_param(self.DLGID_CTRL,'FT1') == '0':
            # ESCRIBO LA ALARMA EN REDIS
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('FALLA_TERMICA_1', 'name'), dic.get_dic('FALLA_ELECTRICA', 'False_value'))
        else:
            self.logs.print_inf(name_function, f"error in {name_function}, FT1 = {read_param(self.DLGID_CTRL,'FT1')}")
            # DEJAR REGISTRO DEL ERROR
            self.logs.script_performance(f"error in {name_function}, FT1 = {read_param(self.DLGID_CTRL,'FT1')}")
        
    def chequeo_sensor(self,dlgid,channel_came):
        
        name_function = 'CHEQUEO_SENSOR'
    
        # SI NO EXISTE LA VARIABLE ERR_SENSOR EN DLGID_REF LA CREO CON VALOR NO
        if not(self.redis.hexist(self.DLGID_REF, 'ERR_SENSOR')): self.redis.hset(self.DLGID_REF, 'ERR_SENSOR', 'NO')
                 
        return True
    
    def modo_remoto(self):
        
        name_function = 'MODO_REMOTO'
        
        pump_state = False
        #
        # SI NO EXISTE PUMP_FREC LO CREO CON VALOR 100%
        if not(self.redis.hexist(self.DLGID_CTRL, dic.get_dic('PUMP_FREC', 'name'))): 
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('PUMP_FREC', 'name'), dic.get_dic('PUMP_FREC', 'True_value'))
            PUMP_FREC = 7
        else:
            PUMP_FREC = int((int(self.redis.hget(self.DLGID_CTRL, dic.get_dic('PUMP_FREC', 'name'))))/100 * 7)
            
        # SI NO EXISTE SW2 LO CREO CON VALOR OFF
        if not(self.redis.hexist(self.DLGID_CTRL, 'SW2')): 
            self.redis.hset(self.DLGID_CTRL, 'SW2', 'OFF')
        #
        # REVISO LA ACCION TOMADA EN EL SERVER RESPECTO A LA BOMBA
        if self.redis.hget(self.DLGID_CTRL, 'SW2') == 'ON':
            self.logs.print_inf(name_function, f'PRENDER BOMBA [ PUMP_FREC = {PUMP_FREC} ]')
            #
            pump_state = True
            #
        elif self.redis.hget(self.DLGID_CTRL, 'SW2') == 'OFF':    
            self.logs.print_inf(name_function, 'APAGAR BOMBA')
            #
        else:
            self.logs.print_inf(name_function, f"error in {name_function}, SW2 = {read_param(self.DLGID_CTRL,'SW2')}")
            # DEJAR REGISTRO DEL ERROR
            self.logs.script_performance(f"error in {name_function}, SW2 = {read_param(self.DLGID_CTRL,'SW2')}")
        
        # REVISO ACCION DE LAS SALIDAS    
        if self.ENABLE_OUTPUTS:
            if pump_state:
                # SETEO LA FRECUENCIA A LA QUE SE QUIERE PRENDER LA BOMBA
                if self.TYPE_IN_FREC == 'NPN':
                    douts(self.DLGID_CTRL,not_dec(PUMP_FREC,3))
                elif self.TYPE_IN_FREC == 'PNP': 
                    douts(self.DLGID_CTRL,PUMP_FREC)
                else: 
                    self.logs.print_inf(name_function, f"error in {name_function}, TYPE_IN_FREC = {self.TYPE_IN_FREC}")    
                    self.logs.script_performance(f"error in {name_function}, TYPE_IN_FREC = {self.TYPE_IN_FREC}")
                    
            # MANDOLA ACCION A LA BOMBA
            pump1(self.DLGID_CTRL, pump_state)    
                
        else:
            self.logs.print_inf(name_function, f"SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {self.ENABLE_OUTPUTS}]")    
            self.logs.script_performance(f"{name_function} ==> SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {self.ENABLE_OUTPUTS}]")
            
    def control_sistema(self,dlgid_ref,channel_ref,MAG_REF):
        
        name_function = 'CONTROL_SISTEMA'
        
        WND = 0.1       # VENTANA DE FRECUENCIA ABIERTA
        
        # SI NO EXISTE LMIN LO CREO CON VALOR 1
        if not(self.redis.hexist(self.DLGID_CTRL, dic.get_dic('MAG_REF', 'name'))): 
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('MAG_REF', 'name'), dic.get_dic('MAG_REF', 'True_value'))
        
        #
        #ESTABLEZCO LMIN Y LMAX A PARTIR DE WND
        LMIN = MAG_REF - WND
        LMAX = MAG_REF + WND
        #
        # LEO EL CANAL DE REFERENCIA
        if self.redis.hexist(dlgid_ref,'LINE'):
            REF = float(read_param(dlgid_ref,channel_ref))
        else:
            self.logs.print_inf(name_function,f"error in {name_function}, {self.CHANNEL_REF} = {read_param(self.DLGID_CTRL,self.CHANNEL_REF)}")
         
        # MUESTRO LOGS    
        self.logs.print_in(name_function, 'ENABLE_OUTPUTS', self.ENABLE_OUTPUTS)
        self.logs.print_in(name_function, 'TYPE_IN_FREC', self.TYPE_IN_FREC)
        self.logs.print_in(name_function, 'MAG_REF', MAG_REF)
        self.logs.print_in(name_function, 'WND', WND)
        self.logs.print_in(name_function, 'REF', REF)
        
        # SI NO FREC LMIN LO CREO CON VALOR 0
        if not(self.redis.hexist(self.DLGID_CTRL, 'FREC')): self.redis.hset(self.DLGID_CTRL, 'FREC', 0)
        # LEO EL VALOR DE LA FRECUENCIA ACTUAL
        FREC = int(self.redis.hget(self.DLGID_CTRL, 'FREC'))
        self.logs.print_in(name_function, 'LAST_FREC', FREC)
        
        if REF < LMIN:
            self.logs.print_inf(name_function, 'PRESION BAJA')
            if FREC < 7: 
                FREC += 1
                self.logs.print_inf(name_function, 'SE AUMENTA LA FRECUENCIA')
                #
            else: 
                self.logs.print_inf(name_function, 'SE ALCANZA FRECUENCIA MAXIMA')
                #self.logs.dlg_performance(f'< {name_function} > SE ALCANZA FRECUENCIA MAXIMA')
                        
        elif REF > LMAX:
            self.logs.print_inf(name_function, 'PRESION ALTA')
            if FREC > 0: 
                FREC -= 1
                self.logs.print_inf(name_function, 'SE DISMINUYE LA FRECUENCIA')
        else: 
            self.logs.print_inf(name_function, 'PRESION DENTRO DEL RANGO SELECCIONADO')    
        
        # MANDO A PRENDER LA BOMBA
        pump1(self.DLGID_CTRL, True)
        
        # CHEQUEO SI LAS SALIDAS TIENEN QUE ACOPLARSE A ENTRADAS NPN o PNP Y MANDO A SETEAR EN CASO DE ENABLE_OUTPUTS
        if self.ENABLE_OUTPUTS:
            if self.TYPE_IN_FREC == 'NPN':
                douts(self.DLGID_CTRL,not_dec(FREC,3))
            elif self.TYPE_IN_FREC == 'PNP': 
                douts(self.DLGID_CTRL,FREC)
            else: 
                self.logs.print_inf(name_function, f"error in {name_function}, TYPE_IN_FREC = {self.TYPE_IN_FREC}")    
                self.logs.script_performance(f"error in {name_function}, TYPE_IN_FREC = {self.TYPE_IN_FREC}")
        else:
            self.logs.print_inf(name_function, f"SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {self.ENABLE_OUTPUTS}]")    
            self.logs.script_performance(f"{name_function} ==> SALIDAS DESCACTIVADAS [ENABLE_OUTPUTS = {self.ENABLE_OUTPUTS}]")
        
        # GUARODO LA FRECUENCIA ACTUAL DE TRABAJO
        self.logs.print_out(name_function, 'CURR_FREC', FREC)    
        self.redis.hset(self.DLGID_CTRL,'FREC',FREC)

    def latch__outpust(self,dlgid):
        
        name_function = 'LATCH_OUTPUTS'
        
        if self.redis.hexist(dlgid, 'current_OUTPUTS'):
            last_OUTPUTS = self.redis.hget(dlgid, 'current_OUTPUTS')
            self.redis.hset(dlgid, 'last_OUTPUTS', last_OUTPUTS)
    
        if self.redis.hexist(dlgid, 'OUTPUTS'):
            if self.redis.hget(dlgid, 'OUTPUTS') != '-1':
                current_OUTPUTS = self.redis.hget(dlgid, 'OUTPUTS')
                self.redis.hset(dlgid, 'current_OUTPUTS', current_OUTPUTS)
        else:
            self.logs.print_inf(name_function,f'NO EXISTE OUTPUTS EN {self.DLGID_CTRL}')
            self.logs.print_inf(name_function,'EJECUCION INTERRUMPIDA')
            quit()
   
    def show_DATA_DATE_TIME(self,dlgid):  
        #
        name_function = 'SHOW_DATA_DATE_TIME'
        #  
        DATA_DATE_TIME = f"{read_param(dlgid, 'DATE')}_{read_param(dlgid, 'TIME')}"
        #
        self.redis.hset(dlgid, dic.get_dic('DATA_DATE_TIME', 'name'), DATA_DATE_TIME)
        #
        self.logs.print_out(name_function, f'[{dlgid}] - DATA_DATE_TIME', DATA_DATE_TIME)
        
    def show_pump1_state(self,channel_pump_name):
        #
        name_function = 'SHOW_PUMP1_STATE'
        #
        pump1_state = int(read_param(self.DLGID_CTRL, channel_pump_name))
        #
        if pump1_state == 1:
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('PUMP1_STATE', 'name'), dic.get_dic('PUMP1_STATE', 'True_value'))
            self.logs.print_out(name_function, dic.get_dic('PUMP1_STATE', 'name'), dic.get_dic('PUMP1_STATE', 'True_value'))
            
        elif pump1_state == 0:
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('PUMP1_STATE', 'name'), dic.get_dic('PUMP1_STATE', 'False_value'))
            self.logs.print_out(name_function, dic.get_dic('PUMP1_STATE', 'name'), dic.get_dic('PUMP1_STATE', 'False_value'))
        
    def show_work_frequency(self):
        
        name_function = 'SHOW_WORK_FREQUENCY'
        
        #str_PROGRAMMED_FREC = self.redis.hget(self.DLGID_CTRL, 'PROGRAMMED_FREC')
        #str_PROGRAMMED_FREC = self.conf.lst_get('DLGID_CTRL') 
        lst_PROGRAMMED_FREC = self.PROGRAMMED_FREC.split('/')
        
        if self.redis.hexist(self.DLGID_CTRL, 'FREC'):
            FREC = int(self.redis.hget(self.DLGID_CTRL, 'FREC'))
            WORKING_FREQUENCY = lst_PROGRAMMED_FREC[FREC]
        else:
            self.logs.print_inf(name_function, f'NO EXISTE LA VARIABLE FREC EN {self.DLGID_CTRL}')
            self.logs.print_inf(name_function, 'NO SE MUESTRA FRECUENCIA DE TRABAJO')
            return False
        
        
        if FREC == 0:
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('WORKING_FREC', 'name'), f'[MIN]  {WORKING_FREQUENCY} Hz')
            self.logs.print_out(name_function, dic.get_dic('WORKING_FREC', 'name'), f'[MIN]  {WORKING_FREQUENCY} Hz')
        elif FREC == 7:
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('WORKING_FREC', 'name'), f'[MAX]  {WORKING_FREQUENCY} Hz')
            self.logs.print_out(name_function, dic.get_dic('WORKING_FREC', 'name'), f'[MAX]  {WORKING_FREQUENCY} Hz')
        else:
            self.redis.hset(self.DLGID_CTRL, dic.get_dic('WORKING_FREC', 'name'), f'{WORKING_FREQUENCY} Hz')
            self.logs.print_out(name_function, dic.get_dic('WORKING_FREC', 'name'), f'{WORKING_FREQUENCY} Hz')
        
    def pump_time(self,channel_pump_name,no_pump):
        #
        name_function = f'PUMP{no_pump}_TIME'
        #
        from datetime import datetime, date, time, timedelta
        #
        pump_state = int(read_param(self.DLGID_CTRL, channel_pump_name))
        #
        # PREPARO VARIABLES DE TIEMPO 
        #
        ## TIEMPO TOTAL
        if not(self.redis.hexist(self.DLGID_CTRL, f'pump{no_pump}_total_time')):
            self.redis.hset(self.DLGID_CTRL, f'pump{no_pump}_total_time','2020,1,1,0,0,0,0')
            pump_total_time = datetime(2020,1,1,0,0,0,0)
            #
            # ESCRIBO LA VARIABLE DE VISUALIZACION
            self.redis.hset(self.DLGID_CTRL, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), '0 horas')
        else:
            # OBTENGO pump_total_time EN FORMATO datetime
            str_pump_total_time = self.redis.hget(self.DLGID_CTRL, f'pump{no_pump}_total_time')
            lst_pump_total_time = str_pump_total_time.split(',')
            pump_total_time = datetime(int(lst_pump_total_time[0]),int(lst_pump_total_time[1]),int(lst_pump_total_time[2]),int(lst_pump_total_time[3]),int(lst_pump_total_time[4]),int(lst_pump_total_time[5]),int(lst_pump_total_time[6]))
            #
            # INCREMENTO 1 MINUTO EN pump_total_time SI LA BOMBA ESTA PRENDIDA
            if pump_state == 1:
                # SUMO UN MINUTO AL CONTEO DE TIEMPO
                pump_total_time = pump_total_time + timedelta(minutes=1)
                #
                # VEO LA DIFERENCIA DE TIEMPO RESPECTO A LA REFERENCIA INICIAL
                delta_total_time = pump_total_time - datetime(2020,1,1,0,0,0,0)
                #
                # CONVIERTO LA DIFERENCIA A HORAS
                delta_total_time_hours = int(delta_total_time.days * 24 + delta_total_time.seconds / 3600)
                #
                # ESCRIBO LA VARIABLE DE VISUALIZACION
                self.redis.hset(self.DLGID_CTRL, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), f'{delta_total_time_hours} horas')
                #
                self.logs.print_out(name_function, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), f'{delta_total_time_hours} horas')
            #
            # GUARDO pump_total_time EN REDIS
            str_pump_total_time = f'{pump_total_time.year},{pump_total_time.month},{pump_total_time.day},{pump_total_time.hour},{pump_total_time.minute},{pump_total_time.second},{pump_total_time.microsecond}'
            self.redis.hset(self.DLGID_CTRL, f'pump{no_pump}_total_time',str_pump_total_time)

    def delta_mag(self):
        '''
        Escribe en DLGID_CTRL/delta_ref_ref1 la diferencia entre las magnitudes de la referencia y la referencia 1
        '''
        
        name_function = 'DELTA_MAG'
        
        if (self.DLGID_REF_1 != '' and self.CHANNEL_REF_1 != ''):
            #
            mag_in_ref = float(read_param(self.DLGID_REF, self.CHANNEL_REF))
            mag_in_ref_1 = float(read_param(self.DLGID_REF_1, self.CHANNEL_REF_1))
            delta_ref1_ref = round(mag_in_ref_1 - mag_in_ref,2)
            #
            # ESCRIBO EN REDIS LA DIFERENCIA
            self.redis.hset(self.DLGID_CTRL, 'delta_ref1_ref', delta_ref1_ref)
            #
            # IMPRIMO LOGS
            self.logs.print_out(name_function, 'delta_ref1_ref', delta_ref1_ref)
        else:
            self.redis.hdel(self.DLGID_CTRL, 'delta_ref1_ref')
            self.logs.print_inf(name_function, 'NO HAY SISTEMA DE REFERENCIA 1')
 
        
class error_process(object):  
    '''
    FUNCIONES USADAS POR ctrl_error_frec.py
    '''
    
    def __init__(self,LIST_CONFIG):
        '''
        Constructor
        '''
        #
        self.config = config_var(LIST_CONFIG)
        #
        #VARIABLES DE EJECUCION
        self.print_log = self.config.lst_get('print_log')
        self.LOG_LEVEL = self.config.lst_get('LOG_LEVEL')
        self.DLGID = self.config.lst_get('DLGID')
        self.TYPE = self.config.lst_get('TYPE')
        #
        #VARIABLES DE CONFIGURACION
        self.SWITCH_OUTPUTS = str2bool(self.config.lst_get('SWITCH_OUTPUTS'))
        self.TEST_OUTPUTS = str2bool(self.config.lst_get('TEST_OUTPUTS'))
        self.RESET_ENABLE = str2bool(self.config.lst_get('RESET_ENABLE'))
        self.EVENT_DETECTION = str2bool(self.config.lst_get('EVENT_DETECTION'))
        self.TIMER_POLL = str2bool(self.config.lst_get('TIMER_POLL'))
        #
        
        # INSTANCIAS
        self.logs = ctrl_logs(self.TYPE,'CTRL_FREC_error',self.DLGID,self.print_log,self.LOG_LEVEL)
        
        self.redis = Redis()   
        
    def test_tx(self):
        '''
        detecta errores tx y RTC
        return '' =>     si no existe el line del datalogger
        return False =>  si hay errores TX de cualquier tipo
        return True =>   cualquier otra opcion
        '''
        
        name_function = 'TEST_TX_ERRORS'
        
        # CHEQUEO DE ERROR TX
        #
        
        # CHEQUEO SI EXISTE EL LINE EN EL DATALOGGER
        if not(self.redis.hexist(self.DLGID, 'LINE')):
            return 'noLine'
        
        # DEVUELVO last_line CON EL LINE ANTERIOR Y current_line CON EL LINE ACTUAL
        if self.redis.hexist(f'{self.DLGID}_ERROR', 'last_line'):
            last_line = self.redis.hget(f'{self.DLGID}_ERROR', 'last_line')
            current_line = self.redis.hget(self.DLGID, 'LINE')
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_line', current_line)
        else:
            last_line = self.redis.hget(self.DLGID, 'LINE')
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_line', last_line)
            current_line = last_line
            return True
            
        # ASIGNO EL VALOR DE LA BATERIA PARA MOSTRARLO EN LOS LOGS
        if read_param(self.DLGID, 'BAT'):
            bat = read_param(self.DLGID, 'BAT')
        else:
            bat = read_param(self.DLGID, 'bt')
        
        
        
        def error_1min_TX(self):
            '''
            return True si hubo error de TX durante un minuto
            return False si no hubo error de TX durante un minuto
            '''
            
            if last_line == current_line:
                #
                return True
            else:
                #
                self.logs.print_inf(name_function, 'TX OK')
                #
                return False
        
        def RTC_error(self,error_1min):
            '''
            return False: si no se comprueba el RTC por error_1min
                          si no hay errores RTC
            return True:  si hay errores TRC 
                          
            '''
            
            # COMPRUEBO ERROR RTC SOLO SI NO HAY ERROR TX
            if error_1min: return False
                
            # DEVUELVO LOS VALORES DE last_fecha_data y last_hora_data asi como fecha_data y hora_data
            if self.redis.hexist(f'{self.DLGID}_ERROR', 'last_fecha_data') & self.redis.hexist(f'{self.DLGID}_ERROR', 'last_hora_data'):
                last_fecha_data = self.redis.hget(f'{self.DLGID}_ERROR', 'last_fecha_data')
                last_hora_data = self.redis.hget(f'{self.DLGID}_ERROR', 'last_hora_data')
                fecha_data = read_param(self.DLGID, 'DATE')
                hora_data = read_param(self.DLGID, 'TIME')
                #
                # ACTUALIZO last_fecha_data Y last_hora_data CON LOS VALORES ACTUALES
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_fecha_data', fecha_data)
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_hora_data', hora_data)
            else:
                fecha_data = read_param(self.DLGID, 'DATE')
                hora_data = read_param(self.DLGID, 'TIME')
                last_fecha_data = fecha_data
                last_hora_data = hora_data
                #
                # ACTUALIZO last_fecha_data Y last_hora_data CON LOS VALORES ACTUALES
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_fecha_data', fecha_data)
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_hora_data', hora_data)
                #
                return False
            #
            # CHEQUEO QUE NO ESTE CAMBIANDO LA FECHA Y HORA
            if fecha_data == last_fecha_data and hora_data == last_hora_data:
                self.logs.print_inf(name_function, 'RTC ERROR')
                self.logs.dlg_performance(f'< RTC ERROR >')
                return True
            else:
                self.logs.print_inf(name_function, 'RTC OK')
                return False
        
        def error_10min_TX(self,error_1min):
            '''
            return True si hubo error de TX durante mas 10 minuto
            return False si se restablece la cominicacion
            '''
            
            if error_1min:
                # INICIALIZO EL CONTADOR DE MINUTOS CON ERORR TX 
                if not(self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx')):
                    self.redis.hset(f'{self.DLGID}_ERROR', 'count_error_tx', 1)
                
                # LEO EL CONTADOS DE TIEMPO
                count_error_tx = int(self.redis.hget(f'{self.DLGID}_ERROR','count_error_tx'))
                
                # VEO EL ESTADO DEL CONTADOR    
                if count_error_tx >= 10:
                    #
                    return True
                else:
                    self.logs.print_inf(name_function, f'CONTADOR DE ERROR TX [{count_error_tx}]')
                    count_error_tx += 1
                    self.redis.hset(f'{self.DLGID}_ERROR','count_error_tx',count_error_tx)
                    #   
                    return False
            else:
                if self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx'):
                    self.redis.hdel(f'{self.DLGID}_ERROR','count_error_tx')   
                #
                return False
            
        def error_TPOLL_TX(self,timer_poll,error_1min):
            
            '''
            return True si hubo error de TX durante mas TPOLL minutos
            return False si se restablece la cominicacion
            '''
            
            if error_1min:
                # INICIALIZO EL CONTADOR DE MINUTOS CON ERORR TX 
                if not(self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx')):
                    self.redis.hset(f'{self.DLGID}_ERROR', 'count_error_tx', 1)
                
                # LEO EL CONTADOS DE TIEMPO
                count_error_tx = int(self.redis.hget(f'{self.DLGID}_ERROR','count_error_tx'))
                
                # VEO EL ESTADO DEL CONTADOR    
                if count_error_tx >= timer_poll:
                    #
                    return True
                else:
                    self.logs.print_inf(name_function, f'CONTADOR DE ERROR TX [{count_error_tx}]')
                    count_error_tx += 1
                    self.redis.hset(f'{self.DLGID}_ERROR','count_error_tx',count_error_tx)
                    #   
                    return False
            else:
                if self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx'):
                    self.redis.hdel(f'{self.DLGID}_ERROR','count_error_tx')   
                #
                return False
        
        
        # SI TENGO TIMER_POLL
        if self.config.lst_get('TIMER_POLL'):
            # LERO EL VALOR DE TPOLL PASADO
            timer_poll = int(self.config.lst_get('TIMER_POLL'))           
            #
            # CHEQUEO ERROR TX DURANTE UN MINUTO
            error_1min = error_1min_TX(self)
            #
            # CHEQUEO ERROR DE RTC
            RTC_error(self,error_1min)
            #
            # CHEQUEO ERRORES TX EN EL TPOLL DADO
            error_TPOLL = error_TPOLL_TX(self,timer_poll,error_1min)
            #
        else:
            # CHEQUEO ERROR TX DURANTE UN MINUTO
            error_1min = error_1min_TX(self)
            #
            # CHEQUEO ERROR DE RTC
            RTC_error(self,error_1min)
            #
            # CHEQUEO ERROR TX DURANTE 10 MINUTOS
            error_10min = error_10min_TX(self,error_1min)
            #
           
        # TRABAJO LOS LOGS
        if self.config.lst_get('TIMER_POLL'):
            if error_TPOLL:
                # MUESTRO LOG EN CONSOLA
                self.logs.print_inf(name_function, f'TX STOPPED FOR MORE THAN {timer_poll} MIN')
                #
                # ESCRIBO EN EL LOG
                self.logs.dlg_performance(f'< MAS DE {timer_poll} MIN CAIDO > [BAT = {bat}]')
                #
                return False
            else:
                return True
        else:    
            if error_10min:
                #
                # MUESTRO LOG EN CONSOLA
                self.logs.print_inf(name_function, 'TX STOPPED FOR MORE THAN 10 MIN')
                self.logs.print_out(name_function, dic.get_dic('TX_ERROR', 'name'), dic.get_dic('TX_ERROR', 'True_value'))
                #
                # ESCRIBO EN EL LOG
                self.logs.dlg_performance(f'< MAS DE 10 MIN CAIDO > [BAT = {bat}]')
                #
                # ESCRIBO EN REDIS LA ALARMA TX_ERROR CON VALOR DE ALARMA PRENDIDA
                self.redis.hset(self.DLGID, dic.get_dic('TX_ERROR', 'name'), dic.get_dic('TX_ERROR', 'True_value'))
                #
                return False
            else:
                #
                # ESCRIBO EN REDIS LA ALARMA TX_ERROR CON VALOR DE ALARMA APAGADA
                self.redis.hset(self.DLGID, dic.get_dic('TX_ERROR', 'name'), dic.get_dic('TX_ERROR', 'False_value'))
                #
                #MUESTRO LOGS EN CONSOLA DE QUE SE ESCRIBIO LA ALARMA DE ERROR TX EN REDIS
                self.logs.print_out(name_function, dic.get_dic('TX_ERROR', 'name'), dic.get_dic('TX_ERROR', 'False_value'))
                #
                if error_1min:
                    # MUESTRO LOG EN CONSOLA
                    self.logs.print_inf(name_function, 'TX STOPPED')
                    #
                    # ESCRIBO EN REDIS ALARMA DE 1MIN EL EQUIPO CAIDO
                    self.redis.hset(self.DLGID, 'error_1min', 'SI')
                    #
                    # ESCRIBO EN EL LOG
                    self.logs.dlg_performance(f'< ERROR TX > [BAT = {bat}]')
                    #
                    return False
                else:
                    #
                    # ESCRIBO EN REDIS ALARMA DE 1MIN QUE INDICA QUE EL DATO QUE ESTA LLEGADNO ES VALIDO
                    self.redis.hset(self.DLGID, 'error_1min', 'NO')
                    #
                    return True
                    
    def visual(self): pass
             
    def event_detection(self):
        
        name_function = 'EVENT_DETECTION'
        
        # SI EVENT_DETECTION ES False INTERRUMPO LA FUNCION
        if not(self.EVENT_DETECTION == None):
            if not(self.EVENT_DETECTION):
                self.logs.print_inf(name_function, 'EVENT_DETECTION INHABILITADO')
                return
        
            
        # PIERTA DEL GABINETE
        if read_param(self.DLGID,'GA') == '1':
            self.logs.print_inf(name_function, 'GABINETE_ABIERTO')
            #
            # ESCRIBO EN EL LOG
            self.logs.dlg_performance(f'< {name_function} > GABINETE_ABIERTO')
            
                
        # FALLA ELECTRICA
        if read_param(self.DLGID,'FE') == '1':
            self.logs.print_inf(name_function, 'FALLA_ELECTRICA')
            #
            # ESCRIBO EN EL LOG
            self.logs.dlg_performance(f'< {name_function} > FALLA_ELECTRICA')
            
            
        # FALLA TERMICA 1
        if read_param(self.DLGID,'FT1') == '1':
            self.logs.print_inf(name_function, 'FALLA_TERMICA_1')
            #
            # ESCRIBO EN EL LOG
            self.logs.dlg_performance(f'< {name_function} > FALLA_TERMICA_1')
                
        # TRABAJO EN MODO LOCAL
        if read_param(self.DLGID,'LM') == '1': 
            self.logs.print_inf(name_function, 'MODO_LOCAL')
            #
            # ESCRIBO EN EL LOG
            self.logs.dlg_performance(f'< {name_function} > MODO_LOCAL')
            
        # TRABAJO EN MODO REMOTO
        if self.redis.hget(self.DLGID, dic.get_dic('WEB_MODE', 'name')) == dic.get_dic('WEB_MODE', 'False_value'):
            #
            # CHEQUEO QUE SE ESTE MANDANDO A PRENDER LA BOMBA
            if self.redis.hget(self.DLGID, dic.get_dic('PUMP_1_WEB_MODE', 'name')) == dic.get_dic('PUMP_1_WEB_MODE', 'True_value'):
                #
                # ESCRIBO EN EL LOG
                PUMP_FREC = self.redis.hget(self.DLGID, dic.get_dic('PUMP_FREC', 'name'))
                self.logs.print_inf(name_function, f'MODO REMOTO => PRENDER BOMBA [ PUMP_FREC = {PUMP_FREC} ]')
                self.logs.dlg_performance(f'< {name_function} > MODO REMOTO => PRENDER BOMBA [ PUMP_FREC = {PUMP_FREC} ]')
                #
            elif self.redis.hget(self.DLGID, dic.get_dic('PUMP_1_WEB_MODE', 'name')) == dic.get_dic('PUMP_1_WEB_MODE', 'False_value'):
                # ESCRIBO EN EL LOG
                self.logs.print_inf(name_function, f'MODO REMOTO => APAGAR BOMBA')
                self.logs.dlg_performance(f'< {name_function} > MODO REMOTO => APAGAR BOMBA') 
                
        # TRABAJO EN MODO EMERGENCIA
        if self.redis.hget(self.DLGID, dic.get_dic('WEB_MODE', 'name')) == dic.get_dic('WEB_MODE', 'value_1') or self.redis.hget(self.DLGID, dic.get_dic('WEB_MODE', 'name')) == dic.get_dic('WEB_MODE', 'value_2'):
            #
            # ESCRIBO EN EL LOG
            self.logs.print_inf(name_function, f'MODO BOYA O TIMER')
            self.logs.dlg_performance(f'< {name_function} > MODO BOYA O TIMER')
               
        # TRABAJO CON EL SISTEMA DE REFERENCIA_1
        if self.redis.hget(self.DLGID, 'flag_work_syst_ref_1') == 'SI':
            #
            FREC = self.redis.hget(self.DLGID, 'FREC')
            #
            # ESCRIBO EN EL LOG
            self.logs.print_inf(name_function, f'TRABAJO CON LA REFERENCIA_1 [ FREC = {FREC} ]')
            self.logs.dlg_performance(f'< {name_function} > TRABAJO CON LA REFERENCIA_1 [ FREC = {FREC} ]')
            
        # TRABAJO CON FRECUENCIA MAXIMA
        if int(self.redis.hget(self.DLGID, 'FREC')) == 7:
            self.logs.dlg_performance(f'< {name_function} > SE ALCANZA FRECUENCIA MAXIMA')
                
    def switch_outputs(self):
        
        name_function = 'SWITCH_OUTPUTS'
        
        #
        # SI ESTA HABILITADO EL SWITCH_OUTPUTS
        if not(self.SWITCH_OUTPUTS): 
            self.logs.print_inf(name_function, 'SWITCH_OUTPUTS INHABILITADO')
            #
            # ELIMINO EL MONITOR DE ESTADOS DE REDIS EN CASO DE QUE EXISTA
            if self.redis.hexist(f'{self.DLGID}_ERROR', 'outputs_states'):
                self.redis.hdel(f'{self.DLGID}_ERROR', 'outputs_states')
            return 
        
        # PREPARO INDICADOR DE ESTADOS
        if not(self.redis.hexist(f'{self.DLGID}_ERROR', 'outputs_states')):
            self.redis.hset(f'{self.DLGID}_ERROR', 'outputs_states', 0)
            outputs_states = 0
        else:
            outputs_states = int(self.redis.hget(f'{self.DLGID}_ERROR', 'outputs_states'))
            
        # DETECTO QUE TIPO DE AUTOMATISMO TENGO PARA EJECUTAR EL SWITCH DE LAS SALIDAS
        if self.TYPE == 'CTRL_FREC':
            # PASO POR ESTADOS
            if outputs_states == 0:
                DO_0 = 0;            
                DO_1 = 0;
            elif outputs_states == 1:
                DO_0 = 1;            
                DO_1 = 0;
            elif outputs_states == 2:
                DO_0 = 0;            
                DO_1 = 1;
            elif outputs_states == 3:
                DO_0 = 1;            
                DO_1 = 1;
                
            if outputs_states == 3:
                outputs_states = 0
            else:
                outputs_states +=1
                
            # MUESTRO LOGS EN CONSOLA    
            self.logs.print_out(name_function, 'DO_0', DO_0)
            self.logs.print_out(name_function, 'DO_1', DO_1)
            
            # MANDO A SETEAR LAS SALIDAS
            set_outs(self.DLGID,DO_0, DO_1)
            
            # LATCHEO LAS SALIDAS
            error_process.latch__outpust(self, self.DLGID)
            
            
        else:
            self.logs.print_inf(name_function, 'AUTOMATISMO NO RECONOCIDO')
            self.logs.print_out(name_function, 'TYPE', self.TYPE)
            return
       
        # ESCRIBO EL VALO DEL ESTADO    
        self.redis.hset(f'{self.DLGID}_ERROR', 'outputs_states', outputs_states)
        
    def test_outputs(self): 
        '''
        return True =>     SI EL TESTEO FUE SATISFACTORIO
        return False =>    SI HUBO ERRORES E/S
        retur None =>      SI TEST_OUTPUTS INHABILITADO
                           SI SE TRABAJA EN MODO LOCAL O HAY FALLA ELECTRICA
                           OTROS ERRORES
        '''   
        
        name_function = 'TEST_OUTPUTS'
        
        # SI TEST_OUTPUTS ES False INTERRUMPO LA FUNCION
        # DEJO QUE SE TESTEEN LAS SALIDAS SI NO SE CARGA TEST_OUTPUTS
        if not(self.TEST_OUTPUTS == None):
            if not(self.TEST_OUTPUTS):
                self.logs.print_inf(name_function, 'TEST_OUTPUTS INHABILITADO')
                return None
        
        # LEO EL VALOR ANTERIOR DE LAS SALIDAS
        last_OUTPUTS = self.redis.hget(self.DLGID, 'last_OUTPUTS')
        #
        # CHEQUEO EL VALOR ANTERIOR DE LAS SALIDAS ES VALIDO
        if not(last_OUTPUTS):
            self.logs.print_inf(name_function, f'NO EXISTE last_OUTPUTS en {self.DLGID}')
            self.logs.print_inf(name_function, 'NO SE TESTEAN SALIDAS')
            return None
        #
        # SELECCIONO EL TEST DE ACUERDO AL TIPO DE AUTOMATISMO
        if self.TYPE == 'CTRL_FREC':
            # DEFINO SALIDAS A TESTEAR
            DO_0 = get_outs(self.DLGID,last_OUTPUTS,0)
            DO_1 = get_outs(self.DLGID,last_OUTPUTS,1)
            #
            # DEFINO ENTRADAS A VERIFICAR
            BR1 = int(read_param(self.DLGID, 'BR1'))
            TM = int(read_param(self.DLGID, 'TM'))
            FT1 = int(read_param(self.DLGID, 'FT1'))
            
            
            # PREVEO QUE NO SE TESTEEN LAS SALIDAS BAJO MODO LOCAL O FALLA ELECTRICA
            if read_param(self.DLGID, 'LM') == '1' or read_param(self.DLGID, 'FE') == '1':
                self.logs.print_in(name_function, 'LM', read_param(self.DLGID, 'LM'))
                self.logs.print_in(name_function, 'FE', read_param(self.DLGID, 'FE'))
                self.logs.print_inf(name_function, 'NO SE TESTEAN SALIDAS POR TRABAJO EN MODO LOCAL O FALLA ELECTRICA')
                return None
                
            # STATE: MODO DE EMERGENCIA
            if DO_0 == 0:
                if TM == 0:
                    if not(BR1 == 0 and FT1 == 0):
                        self.logs.dlg_performance(f'< ERROR_E/S > [ TM = {TM} ], [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]')
                        self.logs.print_inf(name_function, f'< ERROR_E/S > [ TM = {TM} ] - [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]') 
                        return False
                    else:
                        self.logs.print_inf(name_function, 'OUTPUTS OK')
                        return True
                elif TM == 1:
                    if not(BR1 == 1 or FT1 == 1):
                        self.logs.dlg_performance(f'< ERROR_E/S > [ TM = {TM} ], [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]')
                        self.logs.print_inf(name_function, f'< ERROR_E/S > [ TM = {TM} ] - [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]') 
                        return False
                    else:
                        self.logs.print_inf(name_function, 'OUTPUTS OK')
                        return True
                else:
                    self.logs.print_inf(name_function,f'VALOR NO RECONOCIDO EN TM [ TM = {TM} ]')
                    self.logs.script_performance(f'VALOR NO RECONOCIDO EN TM [ TM = {TM} ]')
                    return None
            
            elif DO_0 == 1:
                if DO_1 == 0:
                    if not(BR1 == 0 and FT1 == 0):
                        self.logs.dlg_performance(f'< ERROR_E/S > [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]')
                        self.logs.print_inf(name_function, f'< ERROR_E/S > [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]') 
                        return False
                    else:
                        self.logs.print_inf(name_function, 'OUTPUTS OK')
                        return True
                elif DO_1 == 1:
                    if not(BR1 == 1 or FT1 == 1):
                        self.logs.dlg_performance(f'< ERROR_E/S > [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]')
                        self.logs.print_inf(name_function, f'< ERROR_E/S > [ DO_1 = {DO_1}, DO_0 = {DO_0} ] <=> [ BR1 = {BR1}, FT1 = {FT1} ]') 
                        return False
                    else:
                        self.logs.print_inf(name_function, 'OUTPUTS OK')   
                        return True         
                else:
                    self.logs.print_inf(name_function,f'VALOR NO RECONOCIDO EN DO_1 [ DO_1 = {DO_1} ]')
                    self.logs.script_performance(f'VALOR NO RECONOCIDO EN DO_1 [ DO_1 = {DO_1} ]')
                    return None
            # MODO DE CONTROL
            else:
                self.logs.print_inf(name_function,f'VALOR NO RECONOCIDO EN D0_0 [ DO_0 = {DO_0} ]')
                self.logs.script_performance(f'VALOR NO RECONOCIDO EN D0_0 [ DO_0 = {DO_0} ]')
                return None       
                
    def latch__outpust(self,dlgid):
        if self.redis.hexist(dlgid, 'current_OUTPUTS'):
            last_OUTPUTS = self.redis.hget(dlgid, 'current_OUTPUTS')
            self.redis.hset(dlgid, 'last_OUTPUTS', last_OUTPUTS)
    
        if self.redis.hget(dlgid, 'OUTPUTS') != '-1':
            current_OUTPUTS = self.redis.hget(dlgid, 'OUTPUTS')
            self.redis.hset(dlgid, 'current_OUTPUTS', current_OUTPUTS)           
           
    def pump_time(self,channel_pump_name,no_pump):
        #
        name_function = f'PUMP{no_pump}_TIME'
        #
        from datetime import datetime, date, time, timedelta
        #
        pump_state = int(read_param(self.DLGID, channel_pump_name))
        #
        # PREPARO VARIABLES DE TIEMPO 
        #
        ## TIEMPO TOTAL
        if not(self.redis.hexist(f'{self.DLGID}_ERROR', f'pump{no_pump}_total_time')):
            self.redis.hset(f'{self.DLGID}_ERROR', f'pump{no_pump}_total_time','2020,1,1,0,0,0,0')
            pump_total_time = datetime(2020,1,1,0,0,0,0)
            #
            # ESCRIBO LA VARIABLE DE VISUALIZACION
            self.redis.hset(self.DLGID, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), '0 horas')
        else:
            # OBTENGO pump_total_time EN FORMATO datetime
            str_pump_total_time = self.redis.hget(f'{self.DLGID}_ERROR', f'pump{no_pump}_total_time')
            lst_pump_total_time = str_pump_total_time.split(',')
            pump_total_time = datetime(int(lst_pump_total_time[0]),int(lst_pump_total_time[1]),int(lst_pump_total_time[2]),int(lst_pump_total_time[3]),int(lst_pump_total_time[4]),int(lst_pump_total_time[5]),int(lst_pump_total_time[6]))
            #
            # INCREMENTO 1 MINUTO EN pump_total_time SI LA BOMBA ESTA PRENDIDA
            if pump_state == 1:
                # SUMO UN MINUTO AL CONTEO DE TIEMPO
                pump_total_time = pump_total_time + timedelta(minutes=1)
                #
                # VEO LA DIFERENCIA DE TIEMPO RESPECTO A LA REFERENCIA INICIAL
                delta_total_time = pump_total_time - datetime(2020,1,1,0,0,0,0)
                #
                # CONVIERTO LA DIFERENCIA A HORAS
                delta_total_time_hours = int(delta_total_time.days * 24 + delta_total_time.seconds / 3600)
                #
                # ESCRIBO LA VARIABLE DE VISUALIZACION
                self.redis.hset(self.DLGID, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), f'{delta_total_time_hours} horas')
                #
                self.logs.print_out(name_function, dic.get_dic(f'PUMP{no_pump}_TOTAL_TIME', 'name'), f'{delta_total_time_hours} horas')
            #
            # GUARDO pump_total_time EN REDIS
            str_pump_total_time = f'{pump_total_time.year},{pump_total_time.month},{pump_total_time.day},{pump_total_time.hour},{pump_total_time.minute},{pump_total_time.second},{pump_total_time.microsecond}'
            self.redis.hset(f'{self.DLGID}_ERROR', f'pump{no_pump}_total_time',str_pump_total_time)
            
                  
            
        
            
