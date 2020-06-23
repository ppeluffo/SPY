#!/usr/bin/python3 -u
'''
Protocolo:
Se introduce el fram de SCAN a partir de R 1.0.4 @ 2019-05-10

Sent:
GET /cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500 HTTP/1.1
Host: www.spymovil.com

Receive:
   SCAN_ERR
   SCAN_OK
   DLGID=$dlgid
   NOTDEFINED

Procedimiento:
        Vemos que el DLGID este definido en la BD en la tabla 'spy_equipo'
        Si esta definido actualizo el UID en la BD.spy_equipo
        Retorno: SCAN_OK

        Si el DLGID no esta definido pero si el UID, leo el dlgid que corresponde
        y se lo mando.
        Retorno: DLGID=$dlgid

        Si no tengo definido ni el UID ni el DLGID retorno error
        Retorno: NOTDEFINED

        En caso de problemas, retorno SCAN_ERR

Testing:
- Con telnet:
telnet localhost 80
GET /cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500 HTTP/1.1
Host: www.spymovil.com

telnet www.spymovil.com 90
GET /cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500 HTTP/1.1
Host: www.spymovil.com

- Con browser:
> usamos el url: http://localhost/cgi-bin/PY/spy.py?DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500

'''
from spy_bd_bdspy import BDSPY
from spy import Config
from spy_log import log
from spy_utils import u_send_response

# ------------------------------------------------------------------------------

class RAW_CTL_SCAN_frame:

    def __init__(self, dlgid, version, payload_dict):
        # payload_dict={TYPE:SCAN;UID:304632333433180f000500}
        self.dlgid = dlgid
        self.version = version
        self.payload_dict = payload_dict
        self.response_pload = ''
        log(module=__name__, function='scan__init__', dlgid=self.dlgid, msg='start')
        return

    def send_response(self):
        pload = 'CLASS:SCAN;{}'.format(self.response_pload)
        u_send_response('CTL', pload)
        log(module=__name__, function='scan_send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def process(self):
        '''
        Define la logica de procesar los frames de SCAN
        Primero hago una conexion a la BDSPY.
        - Si el dlgid esta definido, OK
        - Si no esta pero si el uid, le mando al datalogger que se reconfigure
           con el dlg asociado al uid.
        - Si no esta el dlgid ni el uid, ERROR
        '''
        log(module=__name__, function='scan_process', dlgid=self.dlgid, msg='start')

        bd = BDSPY(Config['MODO']['modo'])
        uid = self.payload_dict.get('UID', 'ERROR')
        log(module=__name__, function='scan_process', dlgid='DEBUG', msg='start: dlgid={0},uid={1}'.format(self.dlgid, uid))

        # Primero vemos que el dlgid este definido sin importar su uid
        if bd.dlg_is_defined(self.dlgid):
            log(module=__name__, function='scan_process', dlgid=self.dlgid, msg='SCAN OK')
            # Actualizo el uid c/vez que me conecto si el dlgid coincide
            bd.update_uid(self.dlgid, uid)
            self.response_pload = 'STATUS:OK'
            self.send_response()
            return

        # Si no esta definido, busco si hay algun uid y a que dlgid corresponde
        if bd.uid_is_defined(uid):
            new_dlgid = bd.get_dlgid_from_uid(uid)
            self.response_pload = 'STATUS:RECONF;DLGID:{}'.format(new_dlgid)
            log(module=__name__, function='scan_process', dlgid=self.dlgid, msg='bdconf NEW_DLGID={}'.format(new_dlgid))
            self.send_response()
            return

        # DEFAULT
        self.response_pload = 'STATUS:UNDEF'
        self.send_response()
        log(module=__name__, function='scan_process', dlgid=self.dlgid, msg='DLGID/UID not Defined !!')
        return
