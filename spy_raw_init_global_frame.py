#!/usr/bin/python3 -u

'''
DLGID=TEST02&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GLOBAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2

telnet localhost 80
GET /cgi-bin/PTMP01/spy.py?DLGID=TEST02&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GLOBAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2 HTTP/1.1
Host: www.spymovil.com
'''


from spy_log import log
from spy_utils import u_send_response
from datetime import datetime
import os
import cgi
from spy_bd import BD
from spy_bd_redis import Redis
from spy import Config

# ------------------------------------------------------------------------------

class RAW_INIT_GLOBAL_frame:
    '''
    PLOAD=CLASS:GLOBAL;NACH:5;NDCH:3;NCNT:3;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2
    '''

    def __init__(self, dlgid, version, payload_dict, dlgbdconf_dict):
        self.dlgid = dlgid
        self.version = version
        self.payload_dict = payload_dict
        self.dlgbdconf_dict = dlgbdconf_dict
        self.response_pload = 'CLOCK:{}'.format(datetime.now().strftime('%y%m%d%H%M'))
        log(module=__name__, function='__init__', dlgid=self.dlgid, msg='start')
        return


    def send_response(self):
        pload = 'CLASS:GLOBAL;{}'.format(self.response_pload)
        u_send_response('INIT', pload)
        log(module=__name__, function='send_response', dlgid=self.dlgid, msg='PLOAD={0}'.format(pload))
        return


    def process(self):
        '''
        Define la logica de procesar los frames de INIT:GENERAL
        PLOAD=CLASS:GLOBAL;NACH:5;NDCH:3;NCNT:3;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2
        Leo toda la configuracion en un dict y luego lo paso a los diferentes modulos que calculan los ckecksum
        de c/seccion.
        Si algun checksum no coincide voy agregandolo a la respuesta al server.
        '''
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='start')

        '''
        La configuracion del dlg de la base de datos ya fue leida en la clase superior RAW_INIT y se encuentra
        en self.dlgbdconf_dict
        '''
        # Parametros administrativos:
        simpwd = self.payload_dict.get('SIMPWD', 'ERROR')
        wrst = self.payload_dict.get('WRST', 'ERROR')
        d = dict()
        try:
            d['IPADDRESS'] = cgi.escape(os.environ["REMOTE_ADDR"])
        except:
            d['IPADDRESS'] = '0.0.0.0'

        d['RCVDLINE'] = os.environ['QUERY_STRING']
        d['FIRMWARE'] = self.version
        d['IMEI'] = self.payload_dict.get('IMEI', 'ERROR')
        d['CSQ'] = self.payload_dict.get('CSQ', 'ERROR')
        d['SIMID'] = self.payload_dict.get('SIMID', 'ERROR')
        d['COMMITED_CONF'] = 0

        # Actualizo la BD con estos datos.
        bd = BD( modo = Config['MODO']['modo'], dlgid = self.dlgid )
        bd.bdr.update(self.dlgid,d)
        # Creo un registo inicialiado en la redis.
        redis_db = Redis(self.dlgid).create_rcd()

        # Analizo los checksums individuales
        # Checksum parametros base
        #log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT',msg='DEBUG_base')
        a = int(self.payload_dict.get('BASE', '0'), 16)
        b = self.PV_checksum_base(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_BASE: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';BASE'

        # checksum parametros analog
        #log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='DEBUG_analog')
        a = int(self.payload_dict.get('AN', '0'), 16)
        b = self.PV_checksum_analog(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_AN: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';ANALOG'

        # chechsum parametros digital
        a = int(self.payload_dict.get('DG', '0'), 16)
        b = self.PV_checksum_digital(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_DG: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';DIGITAL'

        # chechsum parametros contadores
        a = int(self.payload_dict.get('CNT', '0'), 16)
        b = self.PV_checksum_counters(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_CNT: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';COUNTERS'

        # chechsum parametros range
        a = int(self.payload_dict.get('RG', '0'),16)
        b = self.PV_checksum_range(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_RANGE: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';RANGE'

        # chechsum parametros psensor
        a = int(self.payload_dict.get('PSE', '0'),16)
        b = self.PV_checksum_psensor(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_PSENS: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';PSENSOR'


        # chechsum parametros aplicacion
        a = int(self.payload_dict.get('APP', '0'),16)
        b = self.PV_checksum_aplicacion(self.dlgbdconf_dict)
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='CKS_APP: dlg={0}, bd={1}'.format(hex(a),hex(b)))
        if a != b:
            self.response_pload += ';APLICACION'

        self.send_response()
        return


    def PV_calcular_ckechsum(self, line):
        '''
        Cambiamos la forma de calcular el checksum porque el xor
        si ponemos 2 veces el miso caracter no lo detecta !!!!
        '''
        cks = 0
        for c in line:
            #cks ^= ord(c)
            cks = (cks + ord(c)) % 256
        return cks


    def PV_checksum_base(self, d):

        timerdial = d.get(('BASE','TDIAL'),'0')
        timerpoll = d.get(('BASE', 'TPOLL'),'0')
        aplicacion = d.get(('BASE', 'APP'), 'OFF')
        pwrs_modo = d.get(('BASE', 'PWRS_MODO'),'0')
        if pwrs_modo == '0':
            pwrs_modo = 'OFF'
        elif pwrs_modo == '1':
            pwrs_modo = 'ON'

        pwrs_start = d.get(('BASE', 'PWRS_HHMM1'),'0000')
        if int(pwrs_start) < 1000:
            pwrs_start = '0' + pwrs_start
        pwrs_end = d.get(('BASE', 'PWRS_HHMM2'),'0000')
        if int(pwrs_end) < 1000:
            pwrs_end = '0' + pwrs_end

        # Calculo el checksum.
        # Debo hacerlo igual a como lo hago en el datalogger.
        cks_str = '{},{},{},{},{},{}'.format( aplicacion, timerdial,timerpoll,pwrs_modo, pwrs_start,pwrs_end )
        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_base', dlgid=self.dlgid, level='SELECT', msg='CKS_BASE: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_analog(self, d):
        # Los canales analogicos van del 0 hasta el 7 ( maximo )
        # Pueden faltar algunos que no usemos por lo que no esten definidos.
        # A0:A0,0,20,0.000,6.000;A1:A1,0,20,0.000,6.000;A2:A2,0,20,0.000,6.000;A3:A3,0,20,0.000,6.000;A4:A4,0,20,0.000,6.000;
        cks_str = ''
        nro_analog_channels = int(self.payload_dict.get('NACH', '0'))
        for ch in range(nro_analog_channels):
            ch_id = 'A{}'.format(ch)            # ch_id = A1
            if (ch_id,'NAME') in d.keys():      # ( 'A1', 'NAME' ) in  d.keys()
                cks_str += '%s:%s,%d,%d,%.03f,%.03f;' % (ch_id, d.get((ch_id, 'NAME'),'AX'), int(d.get((ch_id, 'IMIN'),'0')), int(d.get((ch_id, 'IMAX'),'0')), float(d.get((ch_id, 'MMIN'),'0')), float(d.get((ch_id, 'MMAX'),'0')) )
            else:
                cks_str += '{}:X,4,20,0.000,10.000;'.format(ch_id)

        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_analog', dlgid=self.dlgid, level='SELECT', msg='CKS_AN ({0}ch): [{1}][{2}]'.format(nro_analog_channels, cks_str,hex(cks)))
        return cks


    def PV_checksum_digital(self, d):
        # Los canales digitales van del 0 hasta el 7 ( maximo )
        # Pueden faltar algunos que no usemos por lo que no esten definidos.
        # D0:D0,1;D1:D1,1;
        cks_str = ''
        nro_digital_channels = int(self.payload_dict.get('NDCH', '0'))
        for ch in range(nro_digital_channels):
            ch_id = 'D{}'.format(ch)            # ch_id = D1
            if (ch_id,'NAME') in d.keys():      # ( 'D1', 'NAME' ) in  d.keys()
                if int(d.get((ch_id, 'MODO'),'0')) == 0:
                    # Modo NORMAL
                    cks_str += '%s:%s,NORMAL;' % (ch_id, d.get((ch_id, 'NAME'),'DX'))
                else:
                    # Modo TIMER
                    cks_str += '%s:%s,TIMER;' % (ch_id, d.get((ch_id, 'NAME'),'DX'))
            else:
                cks_str += '{}:X,0,NORMAL;'.format(ch_id)


        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_digital', dlgid=self.dlgid, level='SELECT', msg='CKS_DG ({0}ch): [{1}][{2}]'.format(nro_digital_channels, cks_str,hex(cks)))
        return cks


    def PV_checksum_counters(self, d):
        # Los canales contadores son maximo 2
        # Pueden faltar algunos que no usemos por lo que no esten definidos.
        # C0:C0,1.000,100,10,0;C1:C1,1.000,100,10,0;
        cks_str = ''
        nro_counter_channels = int(self.payload_dict.get('NCNT', '0'))
        for ch in range(nro_counter_channels):
            ch_id = 'C{}'.format(ch)            # ch_id = C1
            if (ch_id,'NAME') in d.keys():      # ( 'C1', 'NAME' ) in  d.keys()
                # La velocidad en la BD es LS o HS
                cks_str += '%s:%s,%.03f,%d,%d,%s;' % (ch_id, d.get((ch_id, 'NAME'),'CX'), float(d.get((ch_id, 'MAGPP'),'0')), int(d.get((ch_id, 'PERIOD'),'0')),int(d.get((ch_id, 'PWIDTH'),'0')), d.get((ch_id,'SPEED'),'LS') )
            else:
                cks_str += '{}:X,0.000,0,0,LS;'.format(ch_id)

        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_counters', dlgid=self.dlgid, level='SELECT', msg='CKS_CNT ({0}ch): [{1}][{2}]'.format(nro_counter_channels, cks_str,hex(cks)))
        return cks


    def PV_checksum_range(self, d):
        name = d.get(('RANGE','NAME'),'X')
        cks_str = '{}'.format(name)
        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_range', dlgid=self.dlgid, level='SELECT', msg='CKS_RANGE: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_psensor(self, d):
        name = d.get(('PSENS','NAME'),'X')
        pmin = float(d.get(('PSENS', 'PMIN'),'0'))
        pmax = float(d.get(('PSENS', 'PMAX'),'0'))
        poffset = float(d.get(('PSENS', 'POFFSET'),'0'))
        cks_str = '%s,%.03f,%.03f,%.03f' % (name,pmin,pmax,poffset)
        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_psensor', dlgid=self.dlgid, level='SELECT', msg='CKS_PSENSOR: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_aplicacion(self, d):
        output_modo = d.get(('BASE','APLICACION'),'OFF')
        cks_str = ''
        if output_modo == 'OFF':
            cks_str = 'OFF'
        elif output_modo == 'TANQUE':
            cks_str = 'TANQUE'
        elif output_modo == 'PERFORACION':
            cks_str = 'PERFORACION'
        elif output_modo == 'CONSIGNA':
            consigna_hhmm1 = int(d.get(('CONS','HHMM1'),'0000'))
            consigna_hhmm2 = int(d.get(('CONS', 'HHMM2'), '0000'))
            cks_str = 'CONSIGNA,%04d;%04d' % (consigna_hhmm1, consigna_hhmm2)

        cks = self.PV_calcular_ckechsum(cks_str)
        log(module=__name__, function='PV_checksum_aplicacion', dlgid=self.dlgid, level='SELECT', msg='CKS_APLICACION: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks

