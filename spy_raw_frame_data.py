#!/usr/bin/python3 -u


from spy_log import log
import os
from spy import Config
from datetime import datetime
from spy_utils import u_send_response, u_dataline_to_dict, u_convert_fw_version_to_str
from spy_bd_redis import Redis
from spy_bd_gda import BDGDA
#from spy_process import move_file_to_error_dir
#from multiprocessing import Process
import sys
from spy_raw_frame_data_daemon import insert_GDA_process_daemon
from spy_raw_frame_callbacks_daemon import callbacks_process_daemon
#import signal
# ------------------------------------------------------------------------------
class RAW_DATA_frame:
    # Esta clase esta especializada en los frames de datos.
    # DLGID=TEST01&TYPE=DATA&VER=2.0.6&PLOAD=NACK;
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
        self.rcv_mbus_tag_id = None
        self.rcv_mbus_tag_val = None
        self.tmp_file = None
        self.dat_file = None
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        #log(module=__name__, function='__init__', dlgid=self.dlgid, msg='DEBUG PAYLOAD {0}'.format(self.payload_str))
        return

    def send_response(self):
        pload = '{}'.format(self.response_pload)
        u_send_response(self.fw_version, 'DATA', pload)
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
        # with open(tmp_file, 'w') as fh:
        #     fh.write(self.payload_str)

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
        d_redis_bcast = dict()
        list_old_format = list()
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
            tipo_old_format = 'float'
            if tipo.upper() == 'I16' or tipo.upper() == 'U16':
                nro_regs = 1
                tipo_old_format = 'integer'
            # 1 reg(2bytes) lo escribimos con codigo 6 y 2 regs(4bytes) con codigo 16
            fcode = 6
            if nro_regs == 2:
                fcode = 16
            #
            # Armo la linea redis.
            # No importa la version del firmware. Si tiene configurados equipos remotos, genero la linea en modbus y
            # en broadcast.
            # Cual usar lo va a determinar la version del equipo remoto cuando se conecte.
            # BROADCAST ( NEW)
            bcast_part_line = "[{0},{1},{2},{3},{4},{5},{6}]".format(mbus_slave,mbus_regaddr,nro_regs,fcode,tipo.upper(),codec.upper(),valor)
            #log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='{0}: bcast_line={1}'.format(dlg_rem, bcast_part_line))
            # Leo las posibles entradas que ya hallan para el datalogger
            bcast_line = d_redis_bcast.get( (dlg_rem,'REDIS_LINE'),'')
            # Agrego los datos de la variable local a enviar.
            bcast_line += bcast_part_line
            # Guardo nuevamente la linea compuesta
            d_redis_bcast[(dlg_rem,'REDIS_LINE')] = bcast_line
            # MODBUS ( OLD )
            tmbus = tuple([dlg_rem, mbus_regaddr, tipo_old_format, valor] )
            list_old_format.append(tmbus)

        # Termine de procesar y crear todas las lineas: Para c/dlgid remoto tengo una linea compuesta: las inserto
        # BROADCAST
        for key in d_redis_bcast.keys():
            dlg_rem,_ = key
            redis_brodcast_line = d_redis_bcast.get( (dlg_rem,'REDIS_LINE'),'')
            try:
                self.redis_db.insert_bcast_line_new( dlg_rem, redis_brodcast_line, self.fw_version )
            except:
                log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, msg='ERROR REDIS INSERT BCAST: line:{}'.format(redis_brodcast_line))
            #
            log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='{0}: redis_bcast_line: {1}'.format(dlg_rem, redis_brodcast_line))
        #
        # MODBUS
        self.redis_db.insert_bcast_line_old(list_old_format, self.rcv_mbus_tag_id, self.rcv_mbus_tag_val )
        #
        log(module=__name__, function='broadcast_local_vars', dlgid=self.dlgid, level='SELECT', msg='End')
        return

    def process_payload(self):
        '''
        Podemos tener 2 tipos de payload:
        El primero es el clasico.
        PLOAD=CTL:21;DATE:010101;TIME:033948;PA:3.21;H:4.56;bt:10.11;
        El segundo puede traer un tag MBUS_TAG con un ACK o NACK
        PLOAD=NACK:-1;CTL:21;DATE:010101;TIME:033948;H:1.23;AN0:0.00;AN1:0.00;bt:10.11;
        Podemos traer lineas con datos en 0 por un bug del firmware que nos generan problemas
        con los automatismos. Las debo filtrar
        '''
        log(module=__name__, function='process', dlgid=self.dlgid, msg='DEBUG_START_PAYLOAD:{0}'.format(self.payload_str))
        lines = self.payload_str.split('CTL')
        # Paso 1: Si trae tags los proceso. El ack,nack lo tiene la linea 0 si lo tiene !!!
        if 'ACK' in self.payload_str or 'NACK' in self.payload_str:
            # Extraigo el tag.
            if lines[0] != '':
                tags = lines[0].split(':')
                # Puede haber una version que solo mande ACK o NACK sin el tag_val
                self.rcv_mbus_tag_id = tags[0]  # tag_id
                if len(tags) > 1:
                    self.rcv_mbus_tag_val = tags[1].split(';')[0]
                else:
                    self.rcv_mbus_tag_val = -1
                # Elimino la linea taggeada
                log(module=__name__, function='process', dlgid=self.dlgid, msg='{0},{1}'.format(self.rcv_mbus_tag_id, self.rcv_mbus_tag_val))

        # Paso 2: Rearmo el payload con solo las lineas de datos y filtro las lineas  en blanco por BUG001 del firmware
        lines = lines[1:]
        self.payload_str = ''
        for line in lines:
            if 'DATE:000000' in line:
                continue
            self.payload_str = self.payload_str + 'CTL' + line

        log(module=__name__, function='process', dlgid=self.dlgid, msg='DEBUG_END_PAYLOAD:{0}'.format(self.payload_str))

    def update_redis(self):
        # Guardo la ultima linea en la redis porque la uso para los automatismos
        self.redis_db = Redis(self.dlgid)
        try:
            self.redis_db.insert_line(self.data_line_list[-1])
        except:
            log(module=__name__, function='update_redis', dlgid=self.dlgid, msg='ERROR REDIS INSERT: len:{0}, line:{1}'.format(len(self.data_line_list), self.data_line_list))

    def process_callbacks(self):
        # Paso 4: Proceso los callbacks ( si estan definidos para este dlgid )
        log(module=__name__, function='process', dlgid=self.dlgid, msg='CALL_BACKS')
        if self.bd.is_automatismo(self.dlgid) or self.redis_db.execute_callback():
            log(module=__name__, function='process', dlgid=self.dlgid, msg='Start CallBacks Daemon')
            callbacks_process_daemon(self)

    def prepare_response(self):
        # Mando el line_id de la ultima linea recibida
        # Agrego el clock para resincronizar
        self.response_pload += 'RX_OK:{0};'.format(self.control_code_list[-1])
        self.response_pload += 'CLOCK:{};'.format(datetime.now().strftime('%y%m%d%H%M'))

        # OUTPUTS:
        # Si hay comandos en la redis los incorporo a la respuesta ( modbus )
        # Las nuevas versiones no usan mas este formato de OUTPUTS ya que usan modbus.
        if self.fw_version < 400:
            self.response_pload += self.redis_db.get_cmd_outputs(self.fw_version)

        # MODBUS:
        # Si hay comandos en la redis para enviar por modbus, lo hago aqui
        self.response_pload += self.redis_db.get_cmd_modbus(fw_version=self.fw_version,
                                                            rcv_mbus_tag_id=self.rcv_mbus_tag_id,
                                                            rcv_mbus_tag_val=self.rcv_mbus_tag_val)

        # PILOTOS (Redis)
        self.response_pload += self.redis_db.get_cmd_pilotos(self.fw_version)

        # RESET
        # x Redis
        self.response_pload += self.redis_db.get_cmd_reset()
        # x CommitedConf
        if 'RESET' not in self.response_pload:
            self.process_commited_conf()

        return

    def insert_into_GDA(self):
        log(module=__name__, function='process', dlgid=self.dlgid, msg='Start Daemon')
        root_path = os.path.abspath('')  # Obtengo la carpeta actual para que el demonio no se pierda.
        insert_GDA_process_daemon(self, self.tmp_file, self.dat_file, root_path)

    def process(self):
        # Realizo todos los pasos necesarios en el payload para generar la respuesta al datalooger e insertar
        # los datos en GDA
        log(module=__name__, function='process', dlgid=self.dlgid, msg='START')

        # Paso 1: Guardo los datos en un archivo temporal para que luego lo procese el 'process' en modo off-line
        # Aqui tambien extraigo los tags del modbus.
        self.process_payload()
        ( self.tmp_file, self.dat_file ) = self.save_payload_in_file()

        # Paso 2: Determino los datos de la ultima linea para mandar la respuesta
        self.split_code_and_data_lists()

        # Paso 3: Actualizo la REDIS con la ultima linea
        self.update_redis()

        # Paso 4: Proceso los callbacks ( si estan definidos para este dlgid )
        self.process_callbacks()

        # Paso 5:Transmision de una o mas varibles locales a equipos remotos. Este broadcast se hace de un equipo
        # central a remotos.
        # El central escribe en la redis de los remotos los datos de la variable a re-enviar.
        self.broadcast_local_vars()

        # Paso 6: Preparo la respuesta y transmito
        self.prepare_response()
        self.send_response()
        sys.stdout.flush()

        # Paso 7: Inserto en GDA
        # DEBUG: En testing en mi laptop no lo habilito. SI HACERLO EN PRODUCCION !!!!
        # --->>>>> 
        self.insert_into_GDA()

        return


