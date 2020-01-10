#!/usr/bin/python3 -u
'''
Recive un frame en el query_string.
DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500
Parsea el frame y el payload.
A partir de esto dispara las clases que deben procesar c/cosa.

telnet 192.168.0.9 80
GET /cgi-bin/PTMP01/spy.py?DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500 HTTP/1.1
Host: www.spymovil.com

'''

from spy_utils import u_parse_cgi_line
from spy_log import log

# ------------------------------------------------------------------------------

class RAW_frame:

    def __init__(self, query_string):
        # Inicializo guardando el query string y lo parseo
        # DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500
        self.query_string = query_string
        return

    def process(self):
        # Parseo un CGI frame.
        # DLGID=TEST01&TYPE=CTL&VER=2.0.6&PLOAD=CLASS:SCAN;UID:304632333433180f000500
        # Guardo los datos y de acuerdo al tipo, lo proceso con subclases.
        # El raw frame es una linea CGI.
        # Al decodificarla y ver cual es su TYPE puedo ver que frame es y comienzo a especializar
        # su decodificacion pasandoselo a la clase correspondiente.
        form = u_parse_cgi_line(self.query_string)
        dlgid = form.get('DLGID', 'SPY000')
        version = form.get('VER', 'R0.0.0')
        payload_str = form.get('PLOAD', 'ERROR')

        log(module=__name__, function='process', dlgid=dlgid, msg='start')

        tipo_frame = form.get('TYPE', 'ERROR')
        if tipo_frame == 'CTL':
            from spy_raw_frame_ctl import RAW_CTL_frame
            raw_clt_frame = RAW_CTL_frame(dlgid, version, payload_str)
            raw_clt_frame.process()

        elif tipo_frame == 'INIT':
            from spy_raw_frame_init import RAW_INIT_frame
            raw_init_frame = RAW_INIT_frame(dlgid, version, payload_str)
            raw_init_frame.process()

        elif tipo_frame == 'DATA':
            from spy_raw_frame_data import RAW_DATA_frame
            raw_data_frame = RAW_DATA_frame(dlgid, version, payload_str)
            raw_data_frame.process()

        return
