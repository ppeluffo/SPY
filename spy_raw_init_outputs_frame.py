#!/usr/bin/python3 -u


from spy_log import log
from spy_utils import u_send_response
from spy_conf_outputs import Confoutputs

# ------------------------------------------------------------------------------

class RAW_INIT_OUTPUTS_frame:
    '''
    PLOAD=CLASS:OUTPUTS;MODO:OFF
        CLASS:OUTPUTS
        MODO:OFF
    PLOAD=CLASS:OUTPUTS;MODO:CONSIGNA,06,30,23,45
        CLASS:OUTPUTS
        MODO:CONSIGNA
        CHH1:06
        CMM1:30
        CHH2:23
        CMM2:45
    PLOAD=CLASS:OUTPUTS;MODO:PERF
        CLASS:OUTPUTS
        MODO:PERF
    PLOAD=CLASS:CLASS:OUTPUTS;MODO:PILOTO;STEPS:6;BAND:0.02;SLOT0:06,30,3.45;SLOT1:07,30,2.45;SLOT2:10,30,1.45;SLOT3:12,30,2.45;SLOT4:14,30,3.45;
        CLASS:OUTPUTS
        MODO:PILOTO
        STEPS:6
        BAND:0.02
        SLOT0:06,30,3.45
        SLOT1:07,30,2.45
        SLOT2:10,30,1.45
        SLOT3:12,30,2.45
        SLOT4:14,30,3.45;

    '''

    def __init__(self, dlgid, version, payload_dict, dlgbdconf_dict):
        self.dlgid = dlgid
        self.version = version
        self.payload_dict = payload_dict
        self.dlgbdconf_dict = dlgbdconf_dict
        self.response_pload = ''
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return


    def send_response(self):
        pload = 'CLASS:OUTPUTS;{}'.format(self.response_pload)
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return


    def process(self):

        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='start')

        # Creo una configuracion tipo 'analog' vacia
        # y la cargo con los datos del datalogger.
        conf_from_dlg = Confoutputs(self.dlgid)
        conf_from_dlg.init_from_payload(self.payload_dict)
        conf_from_dlg.log(tag='dlgconf')

        # Idem pero la cargo con la configuracion de la base de datos
        conf_from_bd = Confoutputs(self.dlgid)
        conf_from_bd.init_from_bd(self.dlgbdconf_dict)
        conf_from_bd.log(tag='bdconf')

        if conf_from_dlg == conf_from_bd:
            log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='Conf BASE: BD eq DLG')
        else:
            log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='Conf BASE: BD ne DLG')
            self.response_pload = conf_from_bd.get_response_string( conf_from_dlg )
            log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='RSP=[{}]'.format(self.response_pload))

        self.send_response()

