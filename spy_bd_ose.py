#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Modulo de trabajo con la BD OSE
"""

from sqlalchemy import create_engine
from sqlalchemy import text
from spy import Config
from collections import defaultdict
import re
from spy_log import log

# ------------------------------------------------------------------------------
class BDOSE_PQ:

    def __init__(self, modo='local',server='comms'):

        self.datasource = ''
        self.engine = ''
        self.conn = ''
        self.connected = False
        self.server = server

        if modo == 'spymovil':
            self.url = Config['BDATOS']['url_bdose_spymovil']
        elif modo == 'local':
            self.url = Config['BDATOS']['url_bdose_local']
        return


    def connect(self, tag='PQ'):
        """
        Retorna True/False si es posible generar una conexion a la bd OSE
        """
        if self.connected:
            return self.connected

        try:
            self.engine = create_engine(self.url)
        except Exception as err_var:
            self.connected = False
            log(module=__name__, function='connect', dlgid = 'DEBUGBD', msg='ERROR_{0}: BDOSE engine NOT created. ABORT !!'.format(tag))
            log(module=__name__, function='connect', dlgid = 'DEBUGBD', msg='ERROR: EXCEPTION {}'.format(err_var))
            exit(1)

        try:
            self.conn = self.engine.connect()
            self.connected = True
        except Exception as err_var:
            self.connected = False
            log(module=__name__, function='connect', dlgid = 'DEBUGBD', msg='ERROR_{0}: BDOSE NOT connected. ABORT !!'.format(tag))
            log(module=__name__, function='connect', dlgid = 'DEBUGBD', msg='ERROR: EXCEPTION {}'.format(err_var))
            exit(1)

        return self.connected


    def insert_data_line(self, dlgid, d, tag='PQ'):

        log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid, msg='START')

        if not self.connect():
            log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid, msg='ERROR: BDOSE can\'t connect !!')
            return False

        sql = """INSERT INTO PQ_tbDatos ( dlgId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value,c1_name,c1_value,c2_name,c2_value,c5_name,c5_value, rcvdFrame ) \
        VALUES ( '{0}', now(), '{1}',(select pkMonitoreo from PQ_tbInstalaciones where dlgId='{0}' and status='ACTIVA'),(select pkInstalacion from PQ_tbInstalaciones where \
        dlgId='{0}' and status='ACTIVA'),'pA','{2}','pB','{3}','q0','{4}','bt','{5}','{6}')""".format(dlgid, d.get('timestamp','00-00-00 00:00'),\
        d.get('pA', '0'), d.get('pB', '0'), d.get('q0', '0'),d.get('bt', '0'), d.get('RCVDLINE', 'err'))
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid, msg='ERROR: SQLQUERY: {0}'.format(sql))
            log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid,  msg='ERROR: EXCEPTION {0}'.format( err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            if 'Duplicate entry' in str(err_var):
                # Los duplicados no hacen nada malo. Se da mucho en testing.
                log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid, msg='WARN: Duplicated Key')
                return True
            else:
                log(module=__name__, server=self.server, function='insert_data_line PQ', dlgid=dlgid,msg='ERROR: exec EXCEPTION {}'.format( err_var))
                return False

        return True


    def insert_data_online(self, dlgid, d, tag='PQ'):

        if not self.connect():
            log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        sql = """INSERT INTO PQ_tbDatosOnline ( dlgId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value,c1_name,c1_value,c2_name,c2_value,c5_name,c5_value, sqe) \
        VALUES ( '{0}', now(), '{1}',\
        (select pkMonitoreo from PQ_tbInstalaciones where dlgId='{0}' and status='ACTIVA'),\
        (select pkInstalacion from PQ_tbInstalaciones where dlgId='{0}' and status='ACTIVA'),
        'pA','{2}','pB','{3}','q0','{4}','bt','{5}',( select sqe from PQ_tbInits where dlgId='{0}' order by pkInits DESC limit 1))""".\
        format(dlgid, d.get('timestamp', '00-00-00 00:00'), d.get('pA', '0'), d.get('pB', '0'),d.get('q0', '0'), d.get('bt', '0')  )
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid, msg='ERROR: SQLQUERY:')
            log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
            return False

        # sql = """DELETE FROM PQ_tbDatosOnline WHERE dlgId = '{0}' AND  pkDatos NOT IN ( SELECT * FROM ( SELECT pkDatos FROM PQ_tbDatosOnline WHERE dlgId = '{0}' \
        # ORDER BY fechaData DESC LIMIT 1) AS temp )""".format(dlgid)

        # try:
        #     query = text(sql)
        # except Exception as err_var:
        #     log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
        #     log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
        #     return False

        # try:
        #     self.conn.execute(query)
        # except Exception as err_var:
        #     log(module=__name__, server=self.server, function='insert_data_online PQ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
        #     return False

        return True


class BDOSE_PZ (BDOSE_PQ):

    def connect(self, tag='PZ'):
        return BDOSE_PQ.connect(self, tag=tag )


    def insert_data_line(self, dlgid, d, tag='PZ'):

        if not self.connect():
            log(module=__name__, function='insert_data_line PZ', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        sql = """INSERT IGNORE INTO PZ_tbDatos (pozoId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value, rcvdFrame) \
        	        VALUES ( '{0}', now(), '{1}', (select pkMonitoreo from PZ_tbInstalaciones where pozoId='{0}' and status='ACTIVA'), \
        	        (select pkInstalacion from PZ_tbInstalaciones where pozoId='{0}' and status='ACTIVA'),'H1', {2}, '{3}' \
        	        )""".format(dlgid, d.get('timestamp', '00-00-00 00:00'), d.get('DIST', '-1'), d.get('RCVDLINE', 'err'))
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, function='insert_data_line PZ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
            log(module=__name__, function='insert_data_line PZ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, function='insert_data_line PZ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
            return False

        return True


    def insert_data_online(self, dlgid, d, tag='PZ'):

        if not self.connect():
            log(module=__name__, function='insert_data_online PZ', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        sql = """INSERT IGNORE INTO PZ_tbDatosOnline (pozoId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value, sqe) \
         	        VALUES ( '{0}', now(), '{1}', (select pkMonitoreo from PZ_tbInstalaciones where pozoId='{0}' and status='ACTIVA'), \
         	        (select pkInstalacion from PZ_tbInstalaciones where pozoId='{0}' and status='ACTIVA'),'H1', {2}, \
         	        ( select sqe from PZ_tbInits where dlgId='{0}' order by pkInits DESC limit 1)
         	        )""".format(dlgid, d.get('timestamp', '00-00-00 00:00'), d.get('DIST', '-1'))

        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, function='insert_data_online PZ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
            log(module=__name__, function='insert_data_online PZ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, function='insert_data_online PZ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
            return False

        # sql = """DELETE FROM PZ_tbDatosOnline WHERE pozoId = '{0}' AND  pkDatos NOT IN ( SELECT * FROM ( SELECT pkDatos FROM PZ_tbDatosOnline WHERE pozoId = '{0}' ORDER BY fechaData DESC LIMIT 1) AS temp )""".format(dlgid)
        # try:
        #     query = text(sql)
        # except Exception as err_var:
        #     log(module=__name__, function='insert_data_online PZ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
        #     log(module=__name__, function='insert_data_online PZ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
        #     return False

        # try:
        #     self.conn.execute(query)
        # except Exception as err_var:
        #     log(module=__name__, function='insert_data_online PZ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
        #     return False

        return True


class BDOSE_TQ (BDOSE_PQ):


    def connect(self, tag='TQ'):
        return BDOSE_PQ.connect(self, tag=tag )


    def insert_data_line(self, dlgid, d, tag='TQ'):

        if not self.connect():
            log(module=__name__, function='insert_data_line TQ', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        sql = """INSERT IGNORE INTO TQ_tbDatos (tanqueId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value,c1_name,c1_value,rcvdFrame) \
            VALUES ( '{0}', now(), '{1}',(select pkMonitoreo from TQ_tbInstalaciones where tanqueId='{0}' and status='ACTIVA'),\
            (select pkInstalacion from TQ_tbInstalaciones where tanqueId='{0}' and status='ACTIVA'),'H', {2}, 'bt', {3}, '{4}'\
            )""".format( dlgid, d.get('timestamp','00-00-00 00:00'), d.get('H','0'), d.get('bt','0'), d.get('RCVDLINE','err') )
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, function='insert_data_line TQ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
            log(module=__name__, function='insert_data_line TQ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, function='insert_data_line TQ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
            return False

        return True


    def insert_data_online(self, dlgid, d, tag='TQ'):

        if not self.connect():
            log(module=__name__, function='insert_data_line', dlgid=dlgid, msg='ERROR: can\'t connect {0} !!'.format(tag))
            exit(0)

        sql = """INSERT IGNORE INTO TQ_tbDatosOnline (tanqueId,fechaSys,fechaData,pkMonitoreo,pkInstalacion,c0_name,c0_value,c1_name,c1_value,sqe) \
        VALUES ( '{0}', now(), '{1}', (select pkMonitoreo from TQ_tbInstalaciones where tanqueId='{0}' and status='ACTIVA'),\
        (select pkInstalacion from TQ_tbInstalaciones where tanqueId='{0}' and status='ACTIVA'),'H', {2}, 'bt', {3}, \
        ( select sqe from TQ_tbInits where dlgId='{0}' order by pkInits DESC limit 1)\
        )""".format( dlgid, d.get('timestamp','00-00-00 00:00'), d.get('H','0'), d.get('bt','0') )
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, function='insert_data_online TQ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
            log(module=__name__, function='insert_data_online TQ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, function='insert_data_online TQ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
            return False

        # sql = """DELETE FROM TQ_tbDatosOnline WHERE tanqueId = '{0}' AND  pkDatos NOT IN ( SELECT * FROM ( SELECT pkDatos FROM TQ_tbDatosOnline WHERE tanqueId = '{0}' \
        # ORDER BY fechaData DESC LIMIT 1) AS temp )""".format(dlgid)
        # try:
        #     query = text(sql)
        # except Exception as err_var:
        #     log(module=__name__, function='insert_data_online TQ', dlgid=dlgid, msg='ERROR: SQLQUERY: {}'.format(sql))
        #     log(module=__name__, function='insert_data_online TQ', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
        #     return False

        # try:
        #     self.conn.execute(query)
        # except Exception as err_var:
        #     log(module=__name__, function='insert_data_online TQ', dlgid=dlgid,msg='ERROR: BDOSE exec EXCEPTION {}'.format(err_var))
        #     return False

        return True

