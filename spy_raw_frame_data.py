#!/usr/bin/python3 -u


from spy_log import log
import os
from spy import Config
from datetime import datetime
from spy_utils import u_send_response
from spy_bd_redis import Redis
from spy_bd import BD


# ------------------------------------------------------------------------------
class RAW_DATA_frame:
    # Esta clase esta especializada en los frames de datos.
    # DLGID=TEST01&TYPE=DATA&VER=2.0.6&PLOAD=
    # CTL:1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    # CTL:2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
    # CTL:3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;

    def __init__(self,dlgid,version, payload):
        self.dlgid = dlgid
        self.version = version
        self.payload_str = payload
        self.response_pload = ''
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return


    def send_response(self):
        pload = '{}'.format(self.response_pload)
        u_send_response('DATA', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return

    def process_commited_conf(self):
        '''
        Leo de la BD el commited_conf. Si esta en 1 lo pongo en 0
        Si en la respuesta no hay un reset ( puesto por la REDIS ) y el
        commited_conf fue 1, pongo un RESET.
        '''
        log(module=__name__, function='process_commited_conf', dlgid=self.dlgid, level='SELECT', msg='start')
        bd = BD( modo = Config['MODO']['modo'], dlgid=self.dlgid )
        commited_conf = bd.process_commited_conf()
        if (commited_conf == 1) and ('RESET' not in self.response_pload):
            self.response_pload += 'RESET;'
            bd.clear_commited_conf()


    def process_callbacks(self):
        #log(module=__name__, function='process_callbacks', dlgid=self.dlgid, level='SELECT',msg='CALLBACK start')
        # Aqui debo invocar al perl con el parametro self.dlgid

        # Leo los callbacks.
        dict_cb = dict()
        for key, callback_file in Config['CALLBACKS'].items():
            cb_dlgid = key.upper()
            #log(module=__name__, function='process_callbacks', dlgid=self.dlgid, level='SELECT', msg='CBK: dlgid {0}:script {1}'.format(cb_dlgid, callback_file))
            dict_cb[cb_dlgid] = callback_file

        if self.dlgid in dict_cb:
            log(module=__name__, function='process_callbacks', dlgid=self.dlgid, level='SELECT', msg='CALLBACK start')
            newpid = os.fork()
            if newpid == 0:
                # Child
                PATH = Config['CALLBACKS_PATH']['cbk_path']
                PROGRAM = dict_cb[self.dlgid]
                CBK = os.path.join(PATH,PROGRAM)
                os.execl(CBK, PROGRAM, self.dlgid)

        exit(0)


    def process(self):
        # Decodifico el payload y veo a que clase pertenece. A partir de la clase es que
        # puedo invocar a una clase mas especializada.

        log(module=__name__, function='process', dlgid=self.dlgid, msg='start')

        lines_list = self.payload_str.split('CTL:')
         #   1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
         #   2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
         #   3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
        control_code_list = list()
        data_line_list = list()
        for item in lines_list:
            #log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT',  msg='DEBUG ITEM={0}'.format(item))
            try:
                ( ctl_code, data_line) = item.split(';DATE')
            except:
                continue
            control_code_list.append(ctl_code)
            data_line = 'DATE' + data_line
            data_line_list.append(data_line)
            log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='clt={0}, datline={1}'.format(ctl_code, data_line))

        now = datetime.now()
        rxpath = Config['PATH']['rx_path']
        tmp_fname = '%s_%s.tmp' % ( self.dlgid, now.strftime('%Y%m%d%H%M%S') )
        tmp_file = os.path.join( os.path.abspath(''), rxpath, tmp_fname )
        dat_fname = '%s_%s.dat' % ( self.dlgid, now.strftime('%Y%m%d%H%M%S') )
        dat_file = os.path.join( os.path.abspath(''), rxpath, dat_fname )
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='FILE: {}'.format(dat_file))

        # Abro un archivo temporal donde guardo los datos
        with open(tmp_file, 'w') as fh:
            fh.write(self.payload_str)
        # Al final lo renombro.
        os.rename(tmp_file, dat_file)

        # Genero la respuesta
        self.response_pload += 'RX_OK:{0};'.format(control_code_list[-1])

        # Actualizo la redis y leo si hay algo para mandar al datalogger
        redis_db = Redis(self.dlgid)
        # Guardo la ultima linea en la redis
        redis_db.insert_line(data_line_list[-1])
        # Si hay comandos en la redis los incorporo a la respuesta
        self.response_pload += redis_db.get_cmd_outputs()
        #self.response_pload += redis_db.get_cmd_pilotos()
        self.response_pload += redis_db.get_cmd_reset()

        self.process_commited_conf()
        self.send_response()
        self.process_callbacks()

        return

