#!/usr/bin/python3 -u
"""
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

"""

from spy_utils import u_parse_payload
from spy_log import log

# ------------------------------------------------------------------------------
class RAW_CTL_frame:
    # Esta clase esta especializada en los frames de control.
    # DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500
    # En el init le pase el raw_frame que es la instancia superior de modo que esta clase pueda
    # acceder a los datos del payload
    def __init__(self,dlgid, version, payload):
        # payload = "CLASS:AUTH;UID:3759303135321102000600"
        self.dlgid = dlgid
        self.version = version
        self.payload_str = payload
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return

    def process(self):
        # Decodifico el payload y veo a que clase pertenece. A partir de la clase es que
        # puedo invocar a una clase mas especializada.
        # payload = "CLASS:AUTH;UID:3759303135321102000600"
        log(module=__name__, function='process', dlgid=self.dlgid, msg='start')
        d_payload = u_parse_payload(self.payload_str)
        payload_class = d_payload.get('CLASS','ERROR')

        if payload_class == 'SCAN':
            '''
            Invoco a la clase mas especializada y le paso una instancia de mi misma de modo que 
            la clase especializada que en realidad hace el trabajo pueda acceder a todos los datos
            de las clases superiores.
            '''
            from SPY_ctl_scan import RAW_CTL_SCAN_frame
            raw_ctl_scan_frame = RAW_CTL_SCAN_frame(self.dlgid,self.version, self.payload_dict )
            raw_ctl_scan_frame.process()

        return

