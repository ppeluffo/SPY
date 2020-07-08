#!/usr/bin/python3 -u
"""
Modulo de trabajo con la BD GDA
"""

from sqlalchemy import create_engine
from sqlalchemy import text
from spy import Config
from collections import defaultdict
from spy_log import log
from time import sleep

# ------------------------------------------------------------------------------
class DLGDB:


    def __init__(self, modo='local', server='comms'):

        self.datasource = ''
        self.engine = ''
        self.conn = ''
        self.connected = False
        self.server = server
    
        self.url = Config['BDATOS']['url_dlgdb_ute']
        return


    def connect(self, tag='DLGDB'):
        """
        Retorna True/False si es posible generar una conexion a la bd GDA
        """

        if self.connected:
            return self.connected

        try:
            self.engine = create_engine(self.url, pool_size=5, pool_recycle=3600)
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server=self.server, function='connect', msg='ERROR_{}: engine NOT created. ABORT !!'.format(tag))
            log(module=__name__, server=self.server, function='connect', msg='ERROR: EXCEPTION_{0} {1}'.format(tag, err_var))
            exit(1)

        try:
            self.conn = self.engine.connect()
            self.connected = True
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server=self.server, function='connect', msg='ERROR_{}: NOT connected. ABORT !!'.format(tag))
            log(module=__name__, server=self.server, function='connect', msg='ERROR: EXCEPTION_{0} {1}'.format(tag, err_var))
            exit(1)

        return self.connected


    def read_all_conf(self, dlgid, tag='DLGDB' ):
        '''
        Leo la configuracion desde DLGDB
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                EL diccionario lo manejo con 2 claves para poder usar el metodo get y tener
                un valor por default en caso de que no tenga alguna clave
        '''
        log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='start_{}'.format(tag))

        if not self.connect(tag):
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{}: can\'t connect !!'.format(tag))
            return

        sql = "SELECT dlgid, magName, tbMCol, disp FROM tbDlgParserConf"
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql))
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            id, mag_name, tbm_col, disp = row
            if id not in d.keys():
                d[id] = {}
            if mag_name not in d[id].keys():
                d[id][mag_name] = {}
            d[id][mag_name]['TBMCOL'] = tbm_col
            d[id][mag_name]['DISP'] = disp
            #log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='BD_{0} conf: [{1}][{2}][{3}][{4}]'.format( tag, id, mag_name, tbm_col, disp))

        return d


    def read_dlg_conf(self, dlgid, tag='DLGDB'):
        '''
        Leo la configuracion desde DLGDB
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                EL diccionario lo manejo con 2 claves para poder usar el metodo get y tener
                un valor por default en caso de que no tenga alguna clave
        '''
        log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='start_{}'.format(tag))

        if not self.connect(tag):
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{}: can\'t connect !!'.format(tag))
            return

        sql = "SELECT magName, tbMCol, disp FROM tbDlgParserConf WHERE dlgId = '{}'".format (dlgid)
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql))
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            mag_name, tbm_col, disp = row
            d[mag_name] = ( tbm_col, disp,)
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='BD_{0} conf: [{1}][{2}][{3}]'.format( tag, mag_name, tbm_col, disp))

        return d


    def insert_data_line(self,dlgid, d, d_parsConf, bd, tag='DLGDB'):
        '''
        En este caso (dlgdb, UTE), recibo 2 diccionarios:
        uno es d que contiene para el datalogger dado las claves NOMBRE_MAG y los valores
        otro es d_parsConf que tiene todos los dataloggers de UTE con el nombre de magnitud, posicion y disponibilidad.
        Este d no debo tocarlo !!!.
        Recorro el diccionario d y a c/magnitud le agrego el TBMCOL y DISP.
        Luego hago con este una lista para poder armar el query.

        Inserto en las 2 tablas. datos, online

        '''
        if not self.connect():
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{}: can\'t connect!!'.format(tag))
            exit(0)

        data = list()
        for key in d.keys():
            # Si la clave (pA) tiene una entrada en parsConf
            if key in d_parsConf[dlgid].keys():
                # Voy creando una entrada con la clave, valor, tbcol, disp.
                mag_name = key
                val = d[mag_name]
                col = d_parsConf[dlgid][mag_name]['TBMCOL']
                disp = d_parsConf[dlgid][mag_name]['DISP']
                data.append( (mag_name,val,col,disp,))

        # Tengo c/elemento en una lista por lo que puedo acceder ordenadamente a la secuencia.
        # Armo el insert.
        sql_main = 'INSERT INTO tbMain (dlgId, fechaHoraData, fechaHoraSys, uxTsSys, rcvdFrame '
        sql_online = 'INSERT INTO tbMainOnline (dlgId, fechaHoraData, fechaHoraSys '
        # Variables:
        for ( mag_name,val,col,disp ) in data:
            sql_main += ',mag{0}, disp{0} '.format(col)
            sql_online += ',mag{0}, disp{0} '.format(col)

        # Valores
        sql_main += ") VALUES ( '{0}','{1}',now(), 0, '' ".format(dlgid, d['timestamp'])
        sql_online += ") VALUES ( '{0}','{1}',now() ".format(dlgid, d['timestamp'])

        first = True
        for ( mag_name,val,col,disp ) in data:
            sql_main += ',{} ,{} '.format(val,disp)
            sql_online += ',{} ,{} '.format(val, disp)

        # Tail
        sql_main += ')'
        sql_online += ')'

        # print("SQL_MAIN=[{}]".format(sql_main))
        # print("SQL_ONLINE=[{}]".format(sql_online))
        # return True

        errors = 0

        # main
        try:
            query = text(sql_main)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql_main))
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))
        # print(query)

        tr = 3
        while tr > 0:
            try:
                if not self.connect():
                    log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{}: can\'t connect!!'.format(tag))
                    tr = tr - 1
                    sleep(1)
                    continue
                rp = self.conn.execute(query)
                tr = 0
            except Exception as err_var:
                if 'Duplicate entry' in str(err_var):
                    # Los duplicados no hacen nada malo. Se da mucho en testing.
                    tr = 0
                    log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='WARN_{}: Duplicated Key'.format(tag))
                else:
                    sleep(1)
                    tr = tr - 1
                    if tr == 0:
                        log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
        # online
        try:
            query = text(sql_online)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql_online))
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))

        tr = 3
        while tr > 0:
            try:
                if not self.connect():
                    log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{}: can\'t connect!!'.format(tag))
                    tr = tr - 1
                    sleep(1)
                    continue
                rp = self.conn.execute(query)
                tr = 0
            except Exception as err_var:
                if 'Duplicate entry' in str(err_var):
                    # Los duplicados no hacen nada malo. Se da mucho en testing.
                    log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='WARN_{}: Duplicated Key'.format(tag))
                    tr = 0
                else:
                    sleep(1)
                    tr = tr - 1
                    if tr == 0:                    
                        log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))

        if errors > 0:
            return False
        else:
            return True

    def clear_online(self,dlgid, bd):
        '''
        Deja el registro mas nuevo en la tabla tbMainOnline para el dlgId determinado.

        '''
        tr = 3
        while tr > 0:
            try:
                if not self.connect():
                    log(module=__name__, server=self.server, function='clear_online', dlgid=dlgid, msg='ERROR_{}: can\'t connect!!'.format(tag))
                    tr = tr - 1
                    sleep(1)
                    continue         
                rp = self.conn.execute(text("""
                DELETE A FROM 
                    tbMainOnline AS A 
                    JOIN (SELECT MAX(tbMainOnline.fechaHoraData) AS max_date FROM tbMainOnline WHERE tbMainOnline.dlgid = '{0}') AS B
                WHERE 
                    A.fechaHoraData < B.max_date AND dlgid = '{0}'
                """.format(dlgid)))
                tr = 0
            except Exception as err_var:
                sleep(1)
                tr = tr - 1
                if tr == 0:                 
                    log(module=__name__, server=self.server, function='clear_online', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
                    return False

        return True



if __name__ == '__main__':
    bd = DLGDB(modo='ute', server='process')
    d = bd.read_all_conf(dlgid='DLG', tag='DLGDB')
    print(d)
    print('Ahora DEF400ś')
    print(d['DEF400'])
