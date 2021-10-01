#!/usr/bin/python3 -u


from spy_log import log
import os
from spy import Config
from datetime import datetime
from spy_utils import u_send_response, u_dataline_to_dict, u_convert_fw_version_to_str
from spy_bd_redis import Redis
from spy_bd_gda import BDGDA
from spy_process import move_file_to_error_dir
from multiprocessing import Process
import sys
from spy_raw_frame_data_daemon import insert_GDA_process_daemon
from spy_raw_frame_callbacks_daemon import callbacks_process_daemon
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
        self.fw_version = u_convert_fw_version_to_str(self.version)
        self.payload_str = payload
        self.response_pload = ''
        self.bd = BDGDA( modo = Config['MODO']['modo'] )
        self.control_code_list = list()
        self.data_line_list = list()
        self.redis_db = None
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

    def broadcast_local_vars(self):
        '''
        Inserta en la redis de los dataloggers remotos la linea MBUS correspondiente.
        Un datalogger puede hacer un broadcast de una se sus medidas a varios datalgogers remotos.
        Aqui generamos las lineas correspondientes  en la redis de c/remoto
        Recibimos como parametro 'dataline' para extraer el valor de la magnitud a reenviar.
        '''
        log(module=__name__, function='broadcast_medidas', dlgid=self.dlgid, level='SELECT', msg='Start')
        # Leo la configuracion de los dlg remotos a los que hacer broadcast.
        d = self.bd.get_dlg_remotos(self.dlgid)
        # Si no hay remotos salimos ya.
        if d is None:
            return
        # Linea de datos de la que extraer el valor a enviar a los dlg remotos por mbus.
        line = self.data_line_list[-1]
        # Transformo la linea a un dict() para hallar facilmente el valor de una medida
        d_line = u_dataline_to_dict(line)
        # Creo un dict() donde voy a tener para c/dlgid remoto la linea redis que va a ir creciendo en la medida que
        # hallan mas variables para enviarle.
        d_redis = dict()
        #
        for key in d.keys():
            # Paso 1: Obtengo los datos de un datalogger remoto( las claves creadas son una tupla
            dlg_rem, medida = key
            mbus_slave = d[key]['MBUS_SLAVE']
            mbus_regaddr = d[key]['MBUS_REGADDR']
            tipo = d[key]['TIPO']
            codec = d[key]['CODEC']
            #log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT',msg='dlg_rem={0},medida={1},slave={2}'.format(dlg_rem,medida,mbus_slave))
            #
            # Paso 2: Leo el valor de la medida a enviar
            valor = d_line.get(medida, 0)
            # log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT',msg='valor={0}'.format(valor))
            #
            # Paso 3: Armo la linea redis [1,0,1,6,u16,c3210,1122]
            # El parametro modbus nro_regs y fcode lo debo inferir. En proximas versiones lo leo de la bd de lo remotos.
            nro_regs = 2
            if tipo.upper() == 'I16' or tipo.upper() == 'U16':
                nro_regs = 1
            # 1 reg(2bytes) lo escribimos con codigo 6 y 2 regs(4bytes) con codigo 16
            fcode = 6
            if nro_regs == 2:
                fcode = 16

            redis_part_line = "[{0},{1},{2},{3},{4},{5},{6}]".format(mbus_slave,mbus_regaddr,nro_regs,fcode,tipo.upper(),codec.upper(),valor)
            #log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='{0}: mbus_line={1}'.format(dlg_rem, redis_part_line))
            #
            # Leo las posibles entradas ( linea mbus) que ya hallan para el datalogger
            redis_line = d_redis.get( (dlg_rem,'REDIS_LINE'),'')
            # Agrego los datos de la variable local a enviar.
            redis_line += redis_part_line
            # Guardo nuevamente la linea compuesta
            d_redis[(dlg_rem,'REDIS_LINE')] = redis_line

        # Termine de procesar y crear todas las lineas: Para c/dlgid remoto tengo una linea compuesta: las inserto
        for key in d_redis.keys():
            dlg_rem,_ = key
            redis_brodcast_line = d_redis.get( (dlg_rem,'REDIS_LINE'),'')
            try:
                self.redis_db.insert_bcast_line( dlg_rem, redis_brodcast_line, self.fw_version )
            except:
                log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, msg='ERROR REDIS INSERT BCAST: line:{}'.format(redis_brodcast_line))
            #
            log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='{0}: redis_bcast_line: {1}'.format(dlg_rem, redis_brodcast_line))
        #
        log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='End')
        return

    def process(self):
        # Realizo todos los pasos necesarios en el payload paragenerar la respuesta al datalooger e insertar los datos en GDA
        log(module=__name__, function='process', dlgid=self.dlgid, msg='START')

        # Paso 1: Guardo los datos en un archivo temporal para que luego lo procese el 'process'
        ( tmp_file, dat_file ) = self.save_payload_in_file()

        # Paso 2: Determino los datos de la ultima linea para mandar la respuesta
        self.split_code_and_data_lists()

        # Paso 3: Actualizo la REDIS con la ultima linea
        self.redis_db = Redis(self.dlgid)
        # Guardo la ultima linea en la redis
        try: 
            self.redis_db.insert_line(self.data_line_list[-1])
        except: 
            log(module=__name__, function='process', dlgid=self.dlgid, msg='ERROR REDIS INSERT: len:{0}, line:{1}'.format(len(self.data_line_list), self.data_line_list))

        # Paso 4: Proceso los callbacks ( si estan definidos para este dlgid )
        log(module=__name__, function='process', dlgid=self.dlgid, msg='CALL_BACKS')
        ##if redis_db.execute_callback():		# yosniel cabrera -> elimine la condicion de que preguntara por type en redis antes de llamar al callback
        # self.process_callbacks()
        if self.bd.is_automatismo(self.dlgid) or self.redis_db.execute_callback():
            log(module=__name__, function='process', dlgid=self.dlgid, msg='Start CallBacks Daemon')
            callbacks_process_daemon(self)

        # Paso 5: Preparo la respuesta
        # Mando el line_id de la ultima linea recibida
        self.response_pload += 'RX_OK:{0};'.format(self.control_code_list[-1])
        # Agrego el clock para resincronizar
        self.response_pload += 'CLOCK:{};'.format(datetime.now().strftime('%y%m%d%H%M'))

        #------------------------------------------------------------------------------------------------
        # 2021-09-30
        # Transmision de una o mas varibles locales a equipos remotos. Este broadcast se hace de un equipo
        # central a remotos.
        # El central escribe en la redis de los remotos los datos de la variable a re-enviar.
        # Version >= 400:
        if self.fw_version >= 400:
            self.broadcast_local_vars()
        # ------------------------------------------------------------------------------------------------
        # OUTPUTS:
        # Si hay comandos en la redis los incorporo a la respuesta ( modbus )
        if self.fw_version < 400:
            self.response_pload += self.redis_db.get_cmd_outputs(self.fw_version)
        # ------------------------------------------------------------------------------------------------
        # MODBUS:
        # Si hay comandos en la redis para enviar por modbus, lo hago aqui
        self.response_pload += self.redis_db.get_cmd_modbus(self.fw_version)
        # ------------------------------------------------------------------------------------------------
        # Redis::Pilotos
        self.response_pload += self.redis_db.get_cmd_pilotos(self.fw_version)
        # Redis::RESET
        self.response_pload += self.redis_db.get_cmd_reset()
        # Si el commited conf indica reset lo agrego a la respuesta
        self.process_commited_conf()
        self.send_response()
        sys.stdout.flush()
        #
        # Paso 7: Inserto las lineas en GDA.
        # if self.bd.insert_data(self.dlgid, self.data_line_list):
        #     # Si salio bien renombro el archivo a .dat para que el process lo use
        #     os.rename(tmp_file, dat_file)
        # else:
        #     # Algo anduvo mal y no pude insertarlo en GDA
        #     move_file_to_error_dir(tmp_file)
        log(module=__name__, function='process', dlgid=self.dlgid, msg='Start Daemon')
        root_path = os.path.abspath('') # Obtengo la carpeta actual para que el demonio no se pierda.
        insert_GDA_process_daemon(self, tmp_file, dat_file, root_path)

        return

