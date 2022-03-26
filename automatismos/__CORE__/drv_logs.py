#!/usr/aut_env/bin/python3.8
'''
DRIVER PARA EL TRABAJO CON LOGS

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.1 07-06-2020 
''' 

## LIBRERIAS
import os
import json
import logging
import logging.handlers


#CONEXIONES
from __CORE__.drv_dlg import read_param
from __CORE__.drv_config import project_path,easy_log
from io import open
from __CORE__.mypython import system_date,system_date_raw,system_hour


class saved_logs(object):
    '''
        Clase que genera los logs que se guardan en la PC
        
        header => 07/06/2020 20:01:22 [MER001] TEXTO
    '''
    def __init__(self,name_log, dlgid = 'null', path_log = ''):
        '''
            name_log = nombre del archivo que va a servir de log
            dlgid    = datalogger que genera el log.
            path_log = ruta en donde se va a crear el log
        '''
        self.name_log = name_log
        self.path_log = path_log
        self.dlgid = dlgid
        
        # CREO LA CARPETA DONDE VA A ESTAR EL LOG
        if not(os.path.exists(path_log)): 
            os.makedirs(f"{path_log}",0o777)
            
        # CREO EL ARCHIVO EN DONDE SE VAN A REGISTRAR LOS LOGS
        log = open(f"{path_log}{name_log}.log",'a')
        #
        # CERRAMOS EL LOG
        log.close()
        #
        # DOY PERMISOS 777 AL ARCHIVO CREADO
        try:
            os.chmod(f"{path_log}{name_log}.log", 0o777)
        except Exception as err_var:
            #log.write(f"{system_date} {system_hour} [{self.dlgid}] {err_var}\n") 
            pass
        
    def write(self, message): 
        # ABRO EL ARCHIVO LOG
        log = open(f"{self.path_log}{self.name_log}.log",'a')
               
        # EXCRIBIMOS EL LOG
        log.write(f"{system_date} {system_hour} [{self.dlgid}] {message}\n") 
        
        # CERRAMOS EL LOG
        log.close()
        
class sysLogs(object):
    '''
        Clase que envia los logs al syslog
    '''
    
    def __init__(self, processName = 'processNameEmpty', dlgid = 'dlgidEmpty', logLevel = 'BASIC'):
        '''
            
        '''
        self.processName = processName
        self.dlgid = dlgid
        self.LOG_LEVEL = logLevel

        logging.basicConfig(level=logging.DEBUG)

        formatter = logging.Formatter('AUTO_CTRL: [%(levelname)s] %(message)s')
        handler = logging.handlers.SysLogHandler('/dev/log')
        handler.setFormatter(formatter)
            
        logger1 = logging.getLogger()       # Creo un logger derivado del root para usarlo en los modulos
        lhStdout = logger1.handlers[0]      # Le leo el handler de consola para deshabilitarlo
        logger1.removeHandler(lhStdout)
        logger1.addHandler(handler)         # y le agrego el handler del syslog.
            
        # Creo ahora un logger child local.
        LOG = logging.getLogger('auto')
        LOG.addHandler(handler)
    
    def write(self, message): 
        if self.LOG_LEVEL == 'FULL':
            logging.info('[{0}][{1}][{2}]'.format(self.processName, self.dlgid, message))

    def warning(self, message):
        logging.warning('[{0}][{1}][{2}]'.format(self.processName, self.dlgid, message))

    def lowLevelLog (self, message):
        logging.info('[{0}][{1}][{2}]'.format(self.processName, self.dlgid, message))



class ctrl_logs(object):
    '''
        Clase que maneja el tema de los logs tanto de pantalla como de archivo
        que se mandan desde los scripts
    '''
    def __init__(self,project_folder_name = '/',process_name = 'empty',DLGID_CTRL = 'empty',show_log = True,logLevel = 'BASIC'):
        '''
        Constructor
        '''
        self.project_folder_name = project_folder_name
        self.process_name = process_name
        self.DLGID_CTRL = DLGID_CTRL
        self.LOG_LEVEL = logLevel
        self.script_performance = sysLogs(self.process_name, self.DLGID_CTRL, self.LOG_LEVEL)
        if easy_log and self.project_folder_name:
            self.easy_dlg_performance_check = saved_logs(f'{self.DLGID_CTRL}_{system_date_raw}', self.DLGID_CTRL, f'{project_path}/{self.project_folder_name}/DLG_PERFORMANCE/')
        

        # GARANTIZO QUE SIEMPRE ME ENTRE UN BOOL
        try: self.show_log = json.loads(show_log.lower()) 
        except: self.show_log = show_log
                   
    def print_log(self,message):
        if self.show_log: print(message)
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(message)
            
    def print_in(self,name_function,name_var,value_var):
        if self.show_log: print(f"{name_function} <= [{name_var} = {value_var}]")
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(f"{name_function} <= [{name_var} = {value_var}]")
    
    def print_out(self,name_function,name_var,value_var):
        if self.show_log: print(f"{name_function} => [{name_var} = {value_var}]")
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(f"{name_function} => [{name_var} = {value_var}]")
    
    def print_inf(self,name_function,message):
        if self.show_log: print(f"{name_function} ==> {message}")
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(f"{name_function} ==> {message}")
    
    def print_error(self,name_function,message):
        if self.show_log: print(f"{name_function} ==> ERROR: {message}")
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(f"{name_function} ==> ERROR: {message}")
        
    def dlg_performance(self,message):
        
        # CREO EL OBJETO dlg_performance 
        #dlg_performance = saved_logs('auto_dlg_performance', self.DLGID_CTRL)
        
        
        # OBTENGO LA FECHA DEL DLGID
        dlgid_date = read_param(self.DLGID_CTRL, 'DATE')
        
        # OBTENGO LA HORA DEL DLGID 
        dlgid_time = read_param(self.DLGID_CTRL, 'TIME')
       
        # ESCRIBO EL LOGS
        self.script_performance.warning(f'[{dlgid_date}-{dlgid_time}] {message}')
        
        
        # ESCRIBO EL LOG FACIL EN CASO DE QUE ESTE HABILITADO
        if easy_log:
            # CREO EL OBJETO easy_dlg_performance_check   MER004_20200501.log
            #easy_dlg_performance_check = saved_logs(f'{self.DLGID_CTRL}_{system_date_raw}', self.DLGID_CTRL, f'{project_path}/{self.project_folder_name}/DLG_PERFORMANCE/')
            #
            # ESCRIBO EL LOGS
            self.easy_dlg_performance_check.write(f'[{dlgid_date}-{dlgid_time}] {message}')

    def basicLog(self,processName):
        if self.show_log: print(processName)
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.lowLevelLog(processName)



     
        