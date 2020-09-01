#!/usr/bin/python3 -u


from spy_log import log
import os
from spy import Config
from datetime import datetime
from spy_utils import u_send_response, u_dataline_to_dict
from spy_bd_redis import Redis
from spy_bd_gda import BDGDA
from spy_process import move_file_to_error_dir
from spy_raw_frame_data_daemon import insert_GDA_process_daemon
import signal

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
        self.bd = BDGDA( modo = Config['MODO']['modo'] )
        self.control_code_list = list()
        self.data_line_list = list()
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

        commited_conf = self.bd.process_commited_conf(dlgid=self.dlgid)
        if (commited_conf == 1) and ('RESET' not in self.response_pload):
            self.response_pload += 'RESET;'
            self.bd.clear_commited_conf(dlgid=self.dlgid)


    def process_callbacks_old(self):
        #log(module=__name__, function='process_callbacks', dlgid=self.dlgid, level='SELECT',msg='CALLBACK start')
        # Aqui debo invocar al perl con el parametro self.dlgid

        # Leo los callbacks
        try:
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
        except Exception as e:
            log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg=str(e))


    def process_callbacks(self):
        
        log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALLBACK ==> START')
        
        def run_program():
            os.system('{0} {1}'.format(CBK,self.dlgid))
            #os.execl(CBK, PROGRAM, self.dlgid)
            
        def end_time(process,time):
            from multiprocessing import Process
            p = Process(target=process,args ='')
            p.start()
            p.join(time)
            if p.is_alive():
                p.terminate()
                log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALLBACKS ==> EJECUCION INTERRUMPIDA POR TIMEOUT')
                
        # PREPARO ARGUMENTOS
        try:
            PATH = Config['CALLBACKS_PATH']['cbk_path']
            PROGRAM = Config['CALLBACKS_PROGRAM']['cbk_program']
            CBK = os.path.join(PATH, PROGRAM)
            #
            log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALL_BACKS ==> {0} {1}]'.format(CBK,self.dlgid))
            # EJECUTO CALLBACKS SI LAS VARIABLES PATH y PROGRAM TIENEN VALORES COHERENTES
            if bool(PROGRAM) & bool(PATH):
                # EJECUTO EL CALLBACKS CON TIEMPO MAXIMO DE EJECUCION DE 1 s
                end_time(run_program,1)
            else: 
                log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALLBACKS ==> [PATH = {0}],[PROGRAM = {1}'.format(PATH,PROGRAM))
                log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALLBACKS ==> INTERRUMPIDO')
        
        except:
            log(module=__name__, function='process_callbacks', dlgid=self.dlgid, msg='CALLBACKS ==> ERROR A LEER cbk vars de spy.conf')
    
        log(module=__name__, function='process', dlgid=self.dlgid, msg='CALLBACK ==> END')
        

    def save_payload_in_file(self):
        # Guarda el payload en un archivo para que luego lo procese el 'process'
        # Lo guarda con extension tmp para aun no procesarlo
        # Retorna los nombres de archivos

        now = datetime.now()
        rxpath = Config['PATH']['rx_path']
        tmp_fname = '%s_%s.tmp' % (self.dlgid, now.strftime('%Y%m%d%H%M%S'))
        tmp_file = os.path.join(os.path.abspath(''), rxpath, tmp_fname)
        dat_fname = '%s_%s.dat' % (self.dlgid, now.strftime('%Y%m%d%H%M%S'))
        dat_file = os.path.join(os.path.abspath(''), rxpath, dat_fname)
        log(module=__name__, function='save_payload_in_file', dlgid=self.dlgid, level='SELECT', msg='FILE: {}'.format(dat_file))

        # Abro un archivo temporal donde guardo los datos
        with open(tmp_file, 'w') as fh:
            fh.write(self.payload_str)

        # Al final lo renombro.
        #os.rename(tmp_file, dat_file)

        return (tmp_file, dat_file)


    def split_code_and_data_lists(self):
        # A partir del payload genera 2 listas: la de id y la de data
        # Los control_codes los necesito para ver cual fue el id de la ultima linea y mandarlo en la respuesta
        # Los data_line los necesito porque la ultima linea es la que debo insertar en la redis.
        # La data_line me sirve porque de aqui genero el parseo para luego insertar en las BD.
        lines_list = self.payload_str.split('CTL:')
        #   1;DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
        #   2;DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
        #   3;DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;

        for item in lines_list:
            try:
                (ctl_code, data_line) = item.split(';DATE')
            except:
                continue
            self.control_code_list.append(ctl_code)
            data_line = 'DATE' + data_line
            self.data_line_list.append(data_line)
            log(module=__name__, function='split_code_and_data_lists', dlgid=self.dlgid, level='SELECT',  msg='clt={0}, data={1}'.format(ctl_code, data_line))
        #
        # self.control_code_list = [ 1, 2, 3.....]
        # self.data_line_list = [ DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
        #                    DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
        #                    DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
        #                  ]
        #


    def process_and_insert_lines_into_GDA(self):
        # self.data_line_list = [ DATE:20191022;TIME:110859;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
        #                         DATE:20191022;TIME:110958;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;,
        #                         DATE:20191022;TIME:111057;PB:-2.59;DIN0:0;DIN1:0;CNT0:0.000;DIST:-1;bt:12.33;
        #                       ]
        for line in self.data_line_list:
            log(module=__name__, function='process_and_insert_lines_into_GDA', dlgid=self.dlgid, level='SELECT', msg='line={0}'.format(line))
            d = u_dataline_to_dict(line)
            #for key in d:
            #    log(module=__name__, server='process', function='pprocess_and_insert_lines_into_GDA', level='SELECT', dlgid='PROC00',msg='key={0}, val={1}'.format(key, d[key]))

            if not self.bd.insert_data_line(self.dlgid, d):
                return False

            if not self.bd.insert_data_online(self.dlgid,d):
                return False

        return True

    def process(self):
        # Realizo todos los pasos necesarios en el payload paragenerar la respuesta al datalooger e insertar los datos en GDA
        log(module=__name__, function='process', dlgid=self.dlgid, msg='START')

        # Paso 1: Guardo los datos en un archivo temporal para que luego lo procese el 'process'
        ( tmp_file, dat_file ) = self.save_payload_in_file()

        # Paso 2: Determino los datos de la ultima linea para mandar la respuesta
        self.split_code_and_data_lists()

        # Paso 3: Actualizo la REDIS con la ultima linea
        redis_db = Redis(self.dlgid)
        # Guardo la ultima linea en la redis
        redis_db.insert_line(self.data_line_list[-1])
        
        # Paso 4: Proceso los callbacks ( si estan definidos para este dlgid )
        log(module=__name__, function='process', dlgid=self.dlgid, msg='CALL_BACKS')
        if redis_db.execute_callback(): self.process_callbacks()

        # Paso 5: Preparo la respuesta y la envio al datalogger
        # Mando el line_id de la ultima linea recibida
        self.response_pload += 'RX_OK:{0};'.format(self.control_code_list[-1])
        # Agrego el clock para resincronizar
        self.response_pload += 'CLOCK:{};'.format(datetime.now().strftime('%y%m%d%H%M'))
        # Si hay comandos en la redis los incorporo a la respuesta
        self.response_pload += redis_db.get_cmd_outputs()
        #self.response_pload += redis_db.get_cmd_pilotos()
        self.response_pload += redis_db.get_cmd_reset()
        # Si el commited conf indica reset lo agrego a la respuesta
        self.process_commited_conf()
        self.send_response()
        
        # Paso 6: Inserto las lineas en GDA.
        # if self.process_and_insert_lines_into_GDA():
        #     # Si salio bien renombro el archivo a .dat para que el process lo use
        #     os.rename(tmp_file, dat_file)
        # else:
        #     # Algo anduvo mal y no pude insertarlo en GDA
        #     move_file_to_error_dir(tmp_file)

        root_path = os.path.abspath('') # Obtengo la carpeta actual para que el demonio no se pierda. 
        insert_GDA_process_daemon(self, tmp_file, dat_file, root_path)

        
        return

