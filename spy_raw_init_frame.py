#!/usr/bin/python3 -u

from spy_utils import u_parse_payload,u_send_response
from spy_bd import BD
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

        # Leo toda la configuracion desde la BD en un dict. La leo aqui porque la necesito
        # en todos los frames de INITS.
        # Si no tengo un datasource valido salgo.
        bd = BD( modo = Config['MODO']['modo'], dlgid = self.dlgid )
        if bd.datasource == 'DS_ERROR':
            u_send_response(type='INIT',pload='STATUS:ERROR_DS')
            return

        dlgbdconf_dict = bd.read_dlg_conf()
        if dlgbdconf_dict == {}:
            log(module=__name__, function='process', dlgid=self.dlgid, msg='ERROR: No hay datos en la BD')
            u_send_response(type='INIT',pload='STATUS:ERROR_DICT')
            return

        # Selector de las diferentes clases de payload
        payload_class = payload_dict.get('CLASS', 'ERROR')
        if payload_class == 'GLOBAL':
            from spy_raw_init_global_frame import RAW_INIT_GLOBAL_frame
            raw_init_global_frame = RAW_INIT_GLOBAL_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_global_frame.process()

        if payload_class == 'BASE':
            from spy_raw_init_base_frame import RAW_INIT_BASE_frame
            raw_init_base_frame = RAW_INIT_BASE_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_base_frame.process()

        if payload_class == 'ANALOG':
            from spy_raw_init_analog_frame import RAW_INIT_ANALOG_frame
            raw_init_analog_frame = RAW_INIT_ANALOG_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_analog_frame.process()

        if payload_class == 'DIGITAL':
            from spy_raw_init_digital_frame import RAW_INIT_DIGITAL_frame
            raw_init_digital_frame = RAW_INIT_DIGITAL_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_digital_frame.process()

        if payload_class == 'COUNTER':
            from spy_raw_init_counter_frame import RAW_INIT_COUNTER_frame
            raw_init_counter_frame = RAW_INIT_COUNTER_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_counter_frame.process()

        if payload_class == 'RANGE':
            from spy_raw_init_range_frame import RAW_INIT_RANGE_frame
            raw_init_range_frame = RAW_INIT_RANGE_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_range_frame.process()

        if payload_class == 'PSENSOR':
            from spy_raw_init_psensor_frame import RAW_INIT_PSENSOR_frame
            raw_init_psensor_frame = RAW_INIT_PSENSOR_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_psensor_frame.process()

        if payload_class == 'OUTPUTS':
            from spy_raw_init_outputs_frame import RAW_INIT_OUTPUTS_frame
            raw_init_outputs_frame = RAW_INIT_OUTPUTS_frame(self.dlgid, self.version, payload_dict, dlgbdconf_dict )
            raw_init_outputs_frame.process()

        return
