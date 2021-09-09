#!/usr/bin/python3 -u

from spy_utils import u_parse_payload,u_send_response
from spy_bd_gda import BDGDA
from spy import Config
from spy_log import log

# ------------------------------------------------------------------------------
class RAW_INIT_frame:

    def __init__(self, dlgid,version, payload):
        self.dlgid = dlgid
        self.version = version
        self.payload_str = payload
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return

    def process(self):
        log(module=__name__, function='process', dlgid=self.dlgid, msg='start')

        payload_dict = u_parse_payload(self.payload_str)

        # Selector de las diferentes clases de payload
        payload_class = payload_dict.get('CLASS', 'ERROR')

        if payload_class == 'AUTH':
            '''
            Es un frame de INIT al cual debo verificarle la integridad.
            Lo debo procesar distinto ya que si hay algún problema en el DS debo
            intentar corregirlo en vez de dar error de primera.
            '''
            uid = payload_dict.get('UID','00000')
            from SPY_init_conf_auth import INIT_CONF_AUTH
            init_conf_auth = INIT_CONF_AUTH(self.dlgid, self.version, uid )
            init_conf_auth.process()
            return

        # Leo toda la configuracion desde la BD en un dict. La leo aqui porque la necesito
        # en todos los frames de INITS.
        # Si no tengo un datasource valido salgo.

        bd = BDGDA( modo = Config['MODO']['modo'] )
        dlgbdconf_dict = bd.read_dlg_conf(self.dlgid)

        if dlgbdconf_dict == {}:
            log(module=__name__, function='process', dlgid=self.dlgid, msg='ERROR: No hay datos en la BD')
            u_send_response(type='INIT',pload='STATUS:ERROR_DICT')
            return

        # NUEVO PROTOCOLO DE INITS DEL DATALOGGER 2019-12-21.

        if payload_class == 'GLOBAL':
            from SPY_init_conf_global import INIT_CONF_GLOBAL
            init_conf_global_frame = INIT_CONF_GLOBAL( self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            init_conf_global_frame.process()
            return

        if payload_class == 'UPDATE':
            from SPY_init_conf_update import INIT_CONF_UPDATE
            init_conf_global_update = INIT_CONF_UPDATE( self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            init_conf_global_update.process()
            return

        if payload_class == 'CONF_BASE':
            from SPY_init_conf_base import INIT_CONF_BASE
            init_conf_base_frame = INIT_CONF_BASE( self.dlgid, self.version, dlgbdconf_dict )
            init_conf_base_frame.process()
            return

        if payload_class == 'CONF_ANALOG':
            from SPY_init_conf_analog import INIT_CONF_ANALOG
            init_conf_analog_frame = INIT_CONF_ANALOG(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_analog_frame.process()
            return

        if payload_class == 'CONF_DIGITAL':
            from SPY_init_conf_digital import INIT_CONF_DIGITAL
            init_conf_digital_frame = INIT_CONF_DIGITAL(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_digital_frame.process()
            return

        if payload_class == 'CONF_COUNTER':
            from SPY_init_conf_counter import INIT_CONF_COUNTER
            init_conf_counter_frame = INIT_CONF_COUNTER(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_counter_frame.process()
            return

        if payload_class == 'CONF_PSENSOR':
            from SPY_init_conf_psensor import INIT_CONF_PSENSOR
            init_conf_psensor_frame = INIT_CONF_PSENSOR(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_psensor_frame.process()
            return

        if payload_class == 'CONF_RANGE':
            from SPY_init_conf_range import INIT_CONF_RANGE
            init_conf_range_frame = INIT_CONF_RANGE(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_range_frame.process()
            return

        if payload_class == 'CONF_APP':
            from SPY_init_conf_app import INIT_CONF_APP
            init_conf_app = INIT_CONF_APP(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_app.process()
            return

        if payload_class == 'CONF_PPOT_SMS':
            from SPY_init_conf_ppot_sms import INIT_CONF_PPOT_SMS
            init_conf_ppot_sms = INIT_CONF_PPOT_SMS(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_ppot_sms.process()
            return

        if payload_class == 'CONF_PPOT_LEVELS':
            from SPY_init_conf_ppot_levels import INIT_CONF_PPOT_LEVELS
            init_conf_ppot_levels = INIT_CONF_PPOT_LEVELS(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_ppot_levels.process()
            return

        if payload_class == 'CONF_CONSIGNA':
            from SPY_init_conf_consigna import INIT_CONF_CONSIGNA
            init_conf_consigna = INIT_CONF_CONSIGNA(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_consigna.process()
            return

        if payload_class == 'CONF_MODBUS':
            from SPY_init_conf_modbus import INIT_CONF_MODBUS
            init_conf_modbus = INIT_CONF_MODBUS(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_LOW':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_LOW
            init_conf_modbus = INIT_CONF_MBUS_LOW(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_MED':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_MED
            init_conf_modbus = INIT_CONF_MBUS_MED(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_MBUS_HIGH':
            from SPY_init_conf_modbus import INIT_CONF_MBUS_HIGH
            init_conf_modbus = INIT_CONF_MBUS_HIGH(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_modbus.process()
            return

        if payload_class == 'CONF_PILOTO_SLOTS':
            from SPY_init_conf_piloto_slots import INIT_CONF_PILOTO_SLOTS
            init_conf_piloto_slots = INIT_CONF_PILOTO_SLOTS(self.dlgid, self.version, dlgbdconf_dict)
            init_conf_piloto_slots.process()
            return

        return
