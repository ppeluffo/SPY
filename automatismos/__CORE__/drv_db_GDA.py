#!/usr/aut_env/bin/python3.8
'''
DRIVER PARA EL TRABAJO CON LA BASE DE DATOS GDA DE MySQL

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.1 07-06-2020
''' 

# CANEXIONES
from sqlalchemy import Table, select, create_engine, MetaData, update, delete
from sqlalchemy.orm import sessionmaker
from collections import defaultdict
from __CORE__.drv_config import dbUrl


class GDA(object):
    '''
        clase para el trabajo con la base de datos GDA
    '''

    def __init__(self,dbUrl):
            '''
                Constructor
            '''
            self.engine = None
            self.conn = None
            self.connected = False
            self.metadata = None
            self.session = None
            #self.url = 'mysql+pymysql://pablo:spymovil@192.168.0.8/GDA'
            #self.url = 'postgresql+psycopg2://admin:pexco599@192.168.0.6/GDA'
            self.url = dbUrl

    def connect(self):
        """
            Retorna True/False si es posible generar una conexion a la bd GDA
        """
        try:
            self.engine = create_engine(self.url)
            Session = sessionmaker(bind=self.engine) 
            self.session = Session()
        except Exception as err_var:
            print('ERROR: engine NOT created. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            return False

        try:
            self.conn = self.engine.connect()
        except Exception as err_var:
            print('ERROR: NOT connected. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            return False

        self.metadata = MetaData()
        return True

    def read_all_dlg_conf(self, dlgid):
        '''
        Leo la configuracion desde GDA
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                
        '''
        
        if not self.connect():
            return

        sql = """SELECT spx_unidades_configuracion.nombre as 'canal', spx_configuracion_parametros.parametro, 
                    spx_configuracion_parametros.value, spx_configuracion_parametros.configuracion_id as 'param_id' FROM spx_unidades,
                    spx_unidades_configuracion, spx_tipo_configuracion, spx_configuracion_parametros 
                    WHERE spx_unidades.id = spx_unidades_configuracion.dlgid_id 
                    AND spx_unidades_configuracion.tipo_configuracion_id = spx_tipo_configuracion.id 
                    AND spx_configuracion_parametros.configuracion_id = spx_unidades_configuracion.id 
                    AND spx_unidades.dlgid = '{}'""".format (dlgid)            
                    
        try:
            query = text(sql)
        except Exception as err_var:
            print(err_var)
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            print(err_var)
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            #print(row)
            canal, pname, value, pid = row
            d[(canal, pname)] = value
        return d

    def read_dlg_conf(self,dlgid,canal,param):
        self.connect()
        dlg_config = self.read_all_dlg_conf(dlgid)
        key = (canal, param)
        return dlg_config.get(key)
        
    def readAutConf(self,dlgId,param):
        '''
            lee el valor del parametro param para el dlgId de GDA
        '''

        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True
            
        # si la conexion fue exitosa
        if self.connected:
            
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)
            
            # obtengo el valor del id del automatismo   
            sel = select([tb_automatismo.c.id])
            sel = sel.where(tb_automatismo.c.dlgid == dlgId)
            autoId = self.conn.execute(sel)
            autoId = autoId.fetchall()

            if autoId:
                # obtengo el valor del parametro  
                autoId = autoId[0][0]
                sel = select([tb_automatismoParametro.c.valor])
                sel = sel.where(tb_automatismoParametro.c.auto_id == autoId)
                sel = sel.where(tb_automatismoParametro.c.nombre == param)
                value = self.conn.execute(sel)
                
                value = value.fetchall()
                if value: return value[0][0]

    def WriteAutConf(self,dlgId,param,value):
        """
            actualiza el valor de parametro para el automatismo autoId de la tabla automatismo_parametro de GDA
        """
        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True

        # si la conexion fue exitosa
        if self.connected:
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)

            # obtengo el valor del id del automatismo   
            sel = select([tb_automatismo.c.id])
            sel = sel.where(tb_automatismo.c.dlgid == dlgId)
            rps = self.conn.execute(sel)
            rps = rps.fetchall()[0][0]

            # actualizo el valor del parametro
            update_statement = tb_automatismoParametro.update()\
                .where(tb_automatismoParametro.c.auto_id == rps)\
                .where(tb_automatismoParametro.c.nombre == param)\
                .values(valor = value)

            self.engine.execute(update_statement)

    def InsertAutConf(self,dlgId,param,value):
        '''
            Inserto o actualizo un nuevo dato
        '''
        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True
        
        # si la conexion fue exitosa
        if self.connected:
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)
            
            # reviso si el dlg ya existe
            dlgExist = True
            try:
                # obtengo el valor del id del automatismo   
                sel = select([tb_automatismo.c.id])
                sel = sel.where(tb_automatismo.c.dlgid == dlgId)
                autoId = self.conn.execute(sel)
                autoId = autoId.fetchall()[0][0]
            except:
                dlgExist = False
            
            # si el dlg no existe lo inserto en la tabla automatismos
            if not dlgExist:
                insert_statement = tb_automatismo.insert()\
                .values(dlgid = dlgId)
                self.engine.execute(insert_statement)

                # obtengo el valor del nuevo id del automatismo creado
                sel = select([tb_automatismo.c.id])
                sel = sel.where(tb_automatismo.c.dlgid == dlgId)
                autoId = self.conn.execute(sel)
                autoId = autoId.fetchall()[0][0]
            
            # chequeo si existe el parametro para el datalogger
            paramExist = True
            try:
                # obtengo el valor del id del automatismo   
                sel = select([tb_automatismoParametro.c.id])
                sel = sel.where(tb_automatismoParametro.c.auto_id == autoId)
                sel = sel.where(tb_automatismoParametro.c.nombre == param)
                rps = self.conn.execute(sel)
                rps = rps.fetchall()[0][0]
            except:
                paramExist = False

            # si el parametro no existe lo inserto en la tabla automatismos con su correspondiente valor
            if not paramExist:
                insert_statement = tb_automatismoParametro.insert()\
                .values(auto_id = autoId)\
                .values(nombre = param)\
                .values(valor = value)
                self.engine.execute(insert_statement)

            # si el parametro existe le hacemos un update
            else:
                # actualizo el valor del parametro
                update_statement = tb_automatismoParametro.update()\
                    .where(tb_automatismoParametro.c.auto_id == autoId)\
                    .where(tb_automatismoParametro.c.nombre == param)\
                    .values(valor = value)

                self.engine.execute(update_statement)

    def DeleteAutConf(self,dlgId,param):
        
        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True
        
        # si la conexion fue exitosa
        if self.connected:
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)
            
            # obtengo el valor del id del automatismo   
            sel = select([tb_automatismo.c.id])
            sel = sel.where(tb_automatismo.c.dlgid == dlgId)
            autoId = self.conn.execute(sel)
            autoId = autoId.fetchall()[0][0]
            
            # obtengo el valor del id del automatismo   
            sel = select([tb_automatismoParametro.c.id])
            sel = sel.where(tb_automatismoParametro.c.auto_id == autoId)
            sel = sel.where(tb_automatismoParametro.c.nombre == param)
            paramId = self.conn.execute(sel)
            paramId = paramId.fetchall()[0][0]
                    
            # elimino el paramatro
            sql = (delete(tb_automatismoParametro)
                .where(tb_automatismoParametro.c.id == paramId))
            self.conn.execute(sql)       

    def getAllAutConf(self,dlgId):
        '''
            se trae toda la configuracion de los dataloggers que estan en la tabla automatismo y la devuelve en una lista
        '''

        ''' SELECT gda.automatismo_parametro.nombre, gda.automatismo_parametro.valor  FROM gda.automatismo_parametro
                INNER JOIN gda.automatismo ON gda.automatismo.id= gda.automatismo_parametro.auto_id
                WHERE gda.automatismo.dlgid = 'CTRLPAY01'''

        outPut = []

        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True
        
        # si la conexion fue exitosa
        if self.connected:
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)
            
            j1 = tb_automatismo.join(tb_automatismoParametro,tb_automatismo.c.id == tb_automatismoParametro.c.auto_id)
            sel = select([tb_automatismoParametro.c.nombre, tb_automatismoParametro.c.valor])
            sel = sel.select_from(j1)
            sel = sel.where(tb_automatismo.c.dlgid == dlgId)
            autoId = self.conn.execute(sel)
            autoId = autoId.fetchall()
            #print(autoId)

            # armo lista
            for param in autoId:
                for subParam in param:
                    outPut.append(subParam)
            
            return outPut

    def DeleteAllAutConf(self,dlgId):
        
        # establecemos conexion a la bd en caso de que no exista
        if not self.connected:
            if self.connect():
                self.connected = True
        
        # si la conexion fue exitosa
        if self.connected:
            tb_automatismo = Table('automatismo', self.metadata, autoload=True, autoload_with=self.engine)
            tb_automatismoParametro = Table('automatismo_parametro', self.metadata, autoload=True, autoload_with=self.engine)
            
            # obtengo el valor del id del automatismo   
            sel = select([tb_automatismo.c.id])
            sel = sel.where(tb_automatismo.c.dlgid == dlgId)
            autoId = self.conn.execute(sel)
            autoId = autoId.fetchall()[0][0]
            
            # elimino toda la configuracion para ese automatismo
            sql = (delete(tb_automatismoParametro)
                .where(tb_automatismoParametro.c.auto_id == autoId))
            self.conn.execute(sql)          












'''


# ONLY FOR TEST
dbUrl = 'postgresql+psycopg2://admin:pexco599@10.1.1.153/GDA'
gda = GDA(dbUrl)
        
print(gda.getAllAutConf('CTRLPAY01'))
#print(gda.getAllAutConf('MER004'))
#gda.DeleteAllAutConf('CTRLPAY01')
#gda.DeleteAutConf('CTRLPAY01','LOG_LEVEL')
print(gda.getAllAutConf('CTRLPAY01'))



'''