#!/usr/bin/python3 -u
"""
Modulo de conexion a la BD BDSPY.
Implemento la BD como una clase
En el init me conecto y me quedo con el conector.
Luego, c/metodo me da los parametros que quiera
"""

from sqlalchemy import create_engine
from sqlalchemy import text
from spy import Config
from spy_log import log

# ------------------------------------------------------------------------------


class BDSPY:

    def __init__(self, modo='local', server='comms'):

        self.datasource = ''
        self.engine = ''
        self.conn = ''
        self.connected = False
        self.server = server
        self.dlgid = ''

        if modo == 'spymovil':
            self.url = Config['BDATOS']['url_bdspy_spymovil']
        elif modo == 'local':
            self.url = Config['BDATOS']['url_bdspy_local']
        elif modo == 'ute':
            self.url = Config['BDATOS']['url_bdspy_ute']

        log(module=__name__, function='BDSPY__init__', dlgid=self.dlgid, msg='start')
        return

    def connect(self, tag='BDSPY'):
        """
        Si no estoy conectado a la BD intento conectarme.
        Retorna True/False si es posible generar una conexion a la bd BDSPY
        """
        if self.connected:
            return True

        try:
            self.engine = create_engine(self.url)
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server=self.server, function='BDSPY_connect', msg='ERROR_{}: engine NOT created. ABORT !!'.format(tag))
            log(module=__name__, server=self.server, function='BDSPY_connect',  msg='ERROR: EXCEPTION_{0} {1}'.format(tag, err_var))
            exit(1)

        try:
            self.conn = self.engine.connect()
            self.connected = True
            return True
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_{}: BDSPY NOT connected. ABORT !!'.format(tag))
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR: EXCEPTION {}'.format(err_var))
            exit(1)

        return False

    def dlg_is_defined(self, dlgid):
        """
        Retorna True/False dependiendo si se encontrol el dlgid definido en BDSPY
        BDSPY es la madre de todas las BD ya que es la que indica en que BD tiene
        la unidad definida su configuracion y cual es su datasource
        """
        retVar = False
        log(module=__name__, function='BDSPY_dlg_is_defined', dlgid=self.dlgid, msg='ENTRY')

        if not self.connect():
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: can\'t connect bdspy !!')
            return False

        # Vemos si el dlg esta definido en la BDSPY
        query = text("SELECT id FROM spy_equipo WHERE dlgid = '{}'".format(dlgid))
        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: can\'t exec bdspy !!')
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: EXCEPTION {}'.format(err_var))
            return False

        row = rp.first()
        log(module=__name__, function='BDSPY_dlg_is_defined', dlgid=self.dlgid, msg='query={}'.format(query))
        log(module=__name__, function='BDSPY_dlg_is_defined', dlgid=self.dlgid, msg='row={}'.format(row))
        if row is None:  # Veo no tener resultado vacio !!!
            retVar = False
        else:
            retVar = True

        log(module=__name__, function='BDSPY_dlg_is_defined', dlgid=self.dlgid, msg='EXIT. [{0}]'.format(retVar))
        return retVar

    def uid_is_defined(self, uid):
        """
        Retorna True/False si el uid esta definido en la BDSPY.
        Cuando no encontramos una entrada por dlgid, buscamos por uid y esta es
        la que nos permite reconfigurar el dlgid.
        En este caso guardamos el dlgid en el self para luego ser consultado.
        """
        if not self.connect():
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: can\'t connect bdspy !!')
            return False

        query = text("SELECT dlgid FROM spy_equipo WHERE uid = '{}'".format (uid))
        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: can\'t exec bdspy !!')
            log(module=__name__, server = self.server, function='BDSPY_connect', msg='ERROR_BDSPY: EXCEPTION {}'.format(err_var))
            return False

        row = rp.first()
        log(module=__name__, function='BDSPY_uid_is_defined', dlgid=self.dlgid, msg='query={}'.format(query))
        log(module=__name__, function='BDSPY_uid_is_defined', dlgid=self.dlgid, msg='row={}'.format(row))
        if row is None:
            return False
        else:
            return True

    def get_dlgid_from_uid(self, uid):

        if not self.connect():
            log(module=__name__, function='BDSPY_get_dlgid_from_uid', msg='ERROR: can\'t connect bdspy !!')
            return False

        query = text("SELECT dlgid FROM spy_equipo WHERE uid = '{}'".format(uid))
        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, function='BDSPY_get_dlgid_from_uid', msg='ERROR: can\'t exec bdspy !!')
            log(module=__name__, function='BDSPY_get_dlgid_from_uid', msg='ERROR: EXCEPTION {}'.format(err_var))
            return ''

        row = rp.first()
        self.dlgid = row[0]
        return self.dlgid

    def find_data_source(self, dlgid):
        """
        Determina en que base de datos (GDA/TAHONA/bd_ose) esta definido el dlg
        Retorna True/False
        En la bd_ose tenemos 3 grupos de tablas: PZ(pozos), TQ(tanques), PQ(presiones y caudales)
        En esta instancia si el datasource es bd_ose, determinamos a que grupo pertenece de modo
        de ahorrarle trabajo luego a las funciones de lectura/escritura de la BD.
        Retorna: datasource o None
        """

        # Si ya tengo el datasource no tengo que consultar a la BD.
        if self.datasource == 'GDA' or self.datasource == 'bd_ose':
            return self.datasource

        if not self.connect():
            log(module=__name__, server = self.server, function='BDSPY_find_data_source', dlgid=dlgid, msg='ERROR: can\'t connect bdspy !!')
            return

        query = text("SELECT datasource FROM spy_equipo WHERE dlgid = '{}'".format(dlgid))
        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server = self.server, function='BDSPY_find_data_source', dlgid=dlgid, msg='ERROR: can\'t exec bdspy !!')
            log(module=__name__, server = self.server, function='BDSPY_find_data_source', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return

        results = rp.fetchone()
        if results is None:
            log(module=__name__, server = self.server, function='BDSPY_find_data_source', dlgid=dlgid, msg='ERROR: DS=None')
            return

        self.datasource = results[0]
        log(module=__name__, server = self.server, function='BDSPY_find_data_source', dlgid=dlgid, msg='DS={}'.format(self.datasource))

        return self.datasource

    def reset_datasource(self, dlgid):
        self.datasource = ''
        log(module=__name__, function='BDSPY_reset_datasource', level='SELECT', dlgid=dlgid, msg='start')

    def check_auth(self, dlgid, uid):
        log(module=__name__, function='BDSPY___init__', dlgid=dlgid, msg='start')
        if not self.dlg_is_defined(dlgid):
           return False
        #El dlgid esta en la BD. Actualizo su UID
        log(module=__name__, function='check_auth', dlgid='DEBUG', msg='AUTH: DLGID={0}, UID={1}'.format(dlgid, uid))
        return self.update_uid(dlgid, uid)

    def update_uid2(self, dlgid, uid):
        # return True

        if not self.connect():
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='UID={}'.format(uid))

        # Controlo integridad: UID <> 00000
        if uid == '00000':
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid='DEBUG', msg='ERROR: dlgid={0}, uid={1}!!'.format(dlgid,uid))
            return False

        # PASS1: Borro todos los registros que tienen el uid dado
        datasource = self.find_data_source(dlgid)
        log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='DATASOURCE={}'.format(datasource))

        sql = "DELETE FROM spy_equipo WHERE uid='{0}' OR dlgid='{1}'".format(uid, dlgid)
        log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid='DEFAULT', msg='DELETE SQLQUERY: {}'.format(sql))
        query = ''
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,  msg='ERROR: SQLQUERY: {}'.format( sql))
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,msg='ERROR: exec EXCEPTION {}'.format(err_var))
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid='DEFAULT', msg='{0}: Borro todas UID OK!'.format(dlgid))

        # PASS2: Creo un registro con el UID/DLGID
        sql = "INSERT INTO spy_equipo (dlgid, uid, datasource) VALUES ('{0}','{1}','{2}')".format(dlgid,uid,datasource)
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,msg='ERROR: SQLQUERY: {}'.format(sql))
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Update UID query={}'.format(query))

        try:
            rp = self.conn.execute(query)
            log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Updated UID OK!')
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: exec EXCEPTION {}'.format(err_var))
            return False

        log(module=__name__, server=self.server, function='BDSPY_update_uid', level='SELECT', dlgid=dlgid, msg='DEBUG update_uid OK')
        return True

    def update_uid(self, dlgid, uid):

        if not self.connect():
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: can\'t connect !!')
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid='DEBUG', msg='DLGID={0}, UID={1}'.format(dlgid, uid))

        # Controlo integridad: UID <> 00000
        if uid == '00000':
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid='DEBUG', msg='ERROR: dlgid={0}, uid={1}!!'.format(dlgid,uid))
            return False

        # SPActualizo el UID.
        sql = "UPDATE spy_equipo SET uid='{0}' WHERE dlgid='{1}'".format(uid,dlgid)
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,  msg='ERROR: SQLQUERY: {}'.format( sql))
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Update UID query={}'.format(query))

        try:
            rp = self.conn.execute(query)
            log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Updated UID OK!')
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,msg='ERROR: exec EXCEPTION {}'.format(err_var))
            return False

        # Dejo vacio las otras entradas que tengan el mismo uid
        sql = "UPDATE spy_equipo SET uid = '' WHERE uid = '{0}' AND dlgid != '{1}'".format(uid,dlgid)
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,  msg='ERROR: SQLQUERY: {}'.format( sql))
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid, msg='ERROR: EXCEPTION {}'.format(err_var))
            return False

        log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Delete UIDs query={}'.format(query))

        try:
            rp = self.conn.execute(query)
            log(module=__name__, function='BDSPY_update_uid', dlgid=self.dlgid, msg='Deltete others UID lines OK!')
        except Exception as err_var:
            log(module=__name__, server=self.server, function='BDSPY_update_uid', dlgid=dlgid,msg='ERROR: exec EXCEPTION {}'.format(err_var))
            return False

        # log(module=__name__, server=self.server, function='BDSPY_update_uid', level='SELECT', dlgid=dlgid, msg='DEBUG update_uid OK')
        return True
