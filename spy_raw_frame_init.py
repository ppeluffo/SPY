#!/usr/bin/python3 -u

from spy_utils import u_parse_payload,u_send_response, u_convert_fw_version_to_str
from spy_bd_gda import BDGDA
from spy import Config
from spy_log import log
from spy_bd_redis_conf import RedisBdConf

# ------------------------------------------------------------------------------
class RAW_INIT_frame:

    def __init__(self, dlgid,version, payload):
        self.dlgid = dlgid
        self.version = version
        self.fw_version = u_convert_fw_version_to_str(version)
        self.payload_str = payload
        self.redis_db = None
        self.d_dlgbdconf = None
        self.d_payload = None
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return

    def process(self):
        log(module=__name__, function='process', dlgid=self.dlgid, msg='start')

        self.d_payload = u_parse_payload(self.payload_str)
        payload_class = self.d_payload.get('CLASS', 'ERROR')

        if payload_class == 'AUTH':
            '''
            Es un frame de INIT al cual debo verificarle la integridad.
            Lo debo procesar distinto ya que si hay algún problema en el DS debo
            intentar corregirlo en vez de dar error de primera.
            payload_str = CLASS:AUTH;UID:3759303135321102000600;
            '''
            uid = self.d_payload.get('UID','00000')
            from SPY_init_conf_auth import INIT_CONF_AUTH
            init_conf_auth = INIT_CONF_AUTH(self.dlgid, self.version, uid )
            init_conf_auth.process()
            return

        ''' 
        NUEVO PROTOCOLO DE INITS DEL DATALOGGER 2019-12-21.
        Todos los dataloggers en los inits mandan primero un AUTH y luego un GLOBAL.
        Recien despues pueden llegar a mandar los otros tipos de inits si son necesarios
        En el procesamiento del GLOBAL es que leo la configuracion de la BD y la dejo en la redis para el resto.
        '''
        if payload_class == 'GLOBAL':
            # Leo la BD GDA con la configuracion y la almaceno en la redis
            # payload_str = CLASS:GLOBAL;NACH:5;NDCH:2;NCNT:2;IMEI:860585007274342;SIMID:8959801619642629015F;CSQ:25;WRST:20;BASE:0x56;AN:0x18;DG:0xC6;CNT:0xEF;MB:0x9D;APP:0x4C;SMS:0xE3;
            bd = BDGDA(modo=Config['MODO']['modo'])
            self.d_dlgbdconf = bd.read_dlg_conf(self.dlgid)

            # Si no tengo configuracion salgo.
            if self.d_dlgbdconf is None:
                log(module=__name__, function='process', dlgid=self.dlgid, msg='ERROR: No hay datos en la BD')
                u_send_response(self.fw_version, type='INIT', pload='STATUS:ERROR_DICT;')
                return

            # Si la lei, guardo la conf. en redis y proceso el la clase GLOBAL
            self.redis_db = RedisBdConf(self.dlgid)
            if self.redis_db.connected:
                self.redis_db.save_conf_to_redis(self.d_dlgbdconf)
                from SPY_init_conf_global import INIT_CONF_GLOBAL   # Proceso el frame GLOBAL
                init_conf_global_frame = INIT_CONF_GLOBAL( self.dlgid, self.version, self.d_payload, self.d_dlgbdconf )
                init_conf_global_frame.process()

            return

        # En modo testing, no paso por el GLOBAL por lo que la base esta vacia y entonces debo leerla de la BD o redis.

        # En el resto de los INIT, la configuracion deberia estar en la redis.
        self.redis_db = RedisBdConf(self.dlgid)
        if self.redis_db.connected:
            self.d_dlgbdconf = self.redis_db.get_conf_from_redis()
        else:
            log(module=__name__, function='process', dlgid=self.dlgid, msg='ERROR: Redis not connected')
            u_send_response(self.fw_version, type='INIT', pload='STATUS:ERROR_BD_REDIS;')
            return

        # Si por alguna causa la configuracion no estaba en redis la leo de la BD.
        if self.d_dlgbdconf is None:
            bd = BDGDA(modo=Config['MODO']['modo'])
            self.d_dlgbdconf = bd.read_dlg_conf(self.dlgid)
            log(module=__name__, function='process', dlgid=self.dlgid, msg='WARNING: Reading bdconf.')

        if payload_class == 'UPDATE':
            from SPY_init_conf_update import INIT_CONF_UPDATE
            init_conf_global_update = INIT_CONF_UPDATE( self.dlgid, self.version, self.d_payload, self.d_dlgbdconf )
            init_conf_global_update.process()
            return

        if payload_class == 'CONF_BASE':
            from SPY_init_conf_base import INIT_CONF_BASE
            init_conf_base_frame = INIT_CONF_BASE( self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_base_frame.process()
            return

        if payload_class == 'CONF_ANALOG':
            from SPY_init_conf_analog import INIT_CONF_ANALOG
            init_conf_analog_frame = INIT_CONF_ANALOG(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_analog_frame.process()
            return

        if payload_class == 'CONF_DIGITAL':
            from SPY_init_conf_digital import INIT_CONF_DIGITAL
            init_conf_digital_frame = INIT_CONF_DIGITAL(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_digital_frame.process()
            return

        if payload_class == 'CONF_COUNTER':
            from SPY_init_conf_counter import INIT_CONF_COUNTER
            init_conf_counter_frame = INIT_CONF_COUNTER(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_counter_frame.process()
            return

        if payload_class == 'CONF_PSENSOR':
            from SPY_init_conf_psensor import INIT_CONF_PSENSOR
            init_conf_psensor_frame = INIT_CONF_PSENSOR(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_psensor_frame.process()
            return

        if payload_class == 'CONF_RANGE':
            from SPY_init_conf_range import INIT_CONF_RANGE
            init_conf_range_frame = INIT_CONF_RANGE(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_range_frame.process()
            return

        if payload_class == 'CONF_APP':
            from SPY_init_conf_app import INIT_CONF_APP
            init_conf_app = INIT_CONF_APP(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_app.process()
            return

        if payload_class == 'CONF_PPOT_SMS':
            from SPY_init_conf_ppot_sms import INIT_CONF_PPOT_SMS
            init_conf_ppot_sms = INIT_CONF_PPOT_SMS(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_ppot_sms.process()
            return

        if payload_class == 'CONF_PPOT_LEVELS':
            from SPY_init_conf_ppot_levels import INIT_CONF_PPOT_LEVELS
            init_conf_ppot_levels = INIT_CONF_PPOT_LEVELS(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_ppot_levels.process()
            return

        if payload_class == 'CONF_CONSIGNA':
            from SPY_init_conf_consigna import INIT_CONF_CONSIGNA
            init_conf_consigna = INIT_CONF_CONSIGNA(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_consigna.process()
            return

        if payload_class == 'CONF_MODBUS':
            from SPY_init_conf_modbus import INIT_CONF_MODBUS
            init_conf_modbus = INIT_CONF_MODBUS(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_LOW':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_LOW
            init_conf_modbus = INIT_CONF_MBUS_LOW(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_MED':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_MED
            init_conf_modbus = INIT_CONF_MBUS_MED(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_HIGH':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_HIGH
            init_conf_modbus = INIT_CONF_MBUS_HIGH(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_modbus.process()
            return

        # A partir de firmware 4.0.4b
        if payload_class == 'CONF_MBUS':
            from SPY_init_conf_modbus import INIT_CONF_MBUS
            init_conf_modbus = INIT_CONF_MBUS(self.dlgid, self.version, self.d_dlgbdconf, self.d_payload )
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_PILOTO_SLOTS':
            from SPY_init_conf_piloto_slots import INIT_CONF_PILOTO_SLOTS
            init_conf_piloto_slots = INIT_CONF_PILOTO_SLOTS(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_piloto_slots.process()
            return

        if payload_class == 'CONF_SMS':
            from SPY_init_conf_sms import INIT_CONF_SMS
            init_conf_sms = INIT_CONF_SMS(self.dlgid, self.version, self.d_dlgbdconf )
            init_conf_sms.process()
            return

        return
