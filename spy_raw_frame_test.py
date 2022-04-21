#!/usr/bin/python3 -u

from spy_utils import u_send_response


class RAW_TEST_frame:
    # Esta clase esta especializada en los frames de testing. Solo responde
    def __init__(self):
        self.fw_version = 200
        return

    def process(self):
        u_send_response(self.fw_version, type='TEST', pload='SPYMOVIL_TESTING')
        return
