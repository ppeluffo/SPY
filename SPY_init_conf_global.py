#!/usr/bin/python3 -u

'''
DLGID=TEST02&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GLOBAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2

telnet localhost 80
GET /cgi-bin/PTMP01/spy.py?DLGID=TEST02&TYPE=INIT&VER=2.0.6&PLOAD=CLASS:GLOBAL;SIMPWD:DEFAULT;IMEI:860585004367917;SIMID:895980161423091055;CSQ:87;WRST:0x00;BASE:0x32;AN:0xCB;DG:0x1A;CNT:0x47;RG:0xF7;PSE:0x73;OUT:0xB2 HTTP/1.1
Host: www.spymovil.com
'''


from spy_log import log
from spy_utils import u_send_response,  u_get_fw_version
from datetime import datetime
import os
import cgi
from spy_bd_gda import BDGDA
from spy_bd_bdspy import BDSPY
from spy_bd_redis import Redis
from spy import Config

hash_table = [ 93,  153, 124,  98, 233, 146, 184, 207, 215,  54, 208, 223, 254, 216, 162, 141,
		 10,  148, 232, 115,   7, 202,  66,  31,   1,  33,  51, 145, 198, 181,  13,  95,
		 242, 110, 107, 231, 140, 170,  44, 176, 166,   8,   9, 163, 150, 105, 113, 149,
		 171, 152,  58, 133, 186,  27,  53, 111, 210,  96,  35, 240,  36, 168,  67, 213,
		 12,  123, 101, 227, 182, 156, 190, 205, 218, 139,  68, 217,  79,  16, 196, 246,
		 154, 116,  29, 131, 197, 117, 127,  76,  92,  14,  38,  99,   2, 219, 192, 102,
		 252,  74,  91, 179,  71, 155,  84, 250, 200, 121, 159,  78,  69,  11,  63,   5,
		 126, 157, 120, 136, 185,  88, 187, 114, 100, 214, 104, 226,  40, 191, 194,  50,
		 221, 224, 128, 172, 135, 238,  25, 212,   0, 220, 251, 142, 211, 244, 229, 230,
		 46,   89, 158, 253, 249,  81, 164, 234, 103,  59,  86, 134,  60, 193, 109,  77,
		 180, 161, 119, 118, 195,  82,  49,  20, 255,  90,  26, 222,  39,  75, 243, 237,
		 17,   72,  48, 239,  70,  19,   3,  65, 206,  32, 129,  57,  62,  21,  34, 112,
		 4,    56, 189,  83, 228, 106,  61,   6,  24, 165, 201, 167, 132,  45, 241, 247,
		 97,   30, 188, 177, 125,  42,  18, 178,  85, 137,  41, 173,  43, 174,  73, 130,
		 203, 236, 209, 235,  15,  52,  47,  37,  22, 199, 245,  23, 144, 147, 138,  28,
		 183,  87, 248, 160,  55,  64, 204,  94, 225, 143, 175, 169,  80, 151, 108, 122 ]

# ------------------------------------------------------------------------------

class INIT_CONF_GLOBAL:
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

        # Veo si esta autorizado y actualizo el uid
        '''
        uid = self.payload_dict.get('UID', '0000')
        log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='DEBUG dlgid={0},uid={1}'.format(self.dlgid, uid))

        if uid != '000':
            log(module=__name__, function='process', dlgid=self.dlgid, level='SELECT', msg='DEBUG UID Not default'.format(self.dlgid, uid))
            bd = BDSPY(modo=Config['MODO']['modo'] )
            if not bd.check_auth(self.dlgid, uid):
                self.response_pload += ':NOT_ALLOWED'
                self.send_response()
                return
        # La configuracion del dlg de la base de datos ya fue leida en la clase superior RAW_INIT y se encuentra
        # en self.dlgbdconf_dict
        '''
        # Parametros administrativos:
        #simpwd = self.payload_dict.get('SIMPWD', 'ERROR')
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
        d['UID'] = 'ver_bdspy'
        # Actualizo la GDA con estos datos.
        bd = BDGDA( modo = Config['MODO']['modo'])
        bd.update(self.dlgid,d)
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


    def PV_calcular_hash_checksum(self, line):
        checksum = 0
        for ch in line:
            checksum = hash_table[ (checksum ^ ord(ch))]

        return checksum


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
        timepwrsensor = d.get(('BASE', 'TIMEPWRSENSOR'), 1)
        pwrs_modo = d.get(('BASE', 'PWRS_MODO'), '0')
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

        counters_hw = d.get(('BASE', 'HW_CONTADORES'), 'OPTO')

        fw_ver = self.dlgbdconf_dict.get(('BASE', 'FIRMWARE'), '2.0.0a')
        log(module=__name__, function='PV_checksum_base', dlgid=self.dlgid, level='SELECT', msg='DEBUG1:fw_ver={}'.format(fw_ver))
        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        log(module=__name__, function='PV_checksum_base', dlgid=self.dlgid, level='SELECT', msg='DEBUG2:fw_ver={}'.format(fw_version))
        # Calculo el checksum.
        # Debo hacerlo igual a como lo hago en el datalogger.
        cks_str = ''
        if fw_version >= 300:
            cks_str = '{0},{1},{2},{3},{4},{5},{6},'.format(timerdial, timerpoll, timepwrsensor, pwrs_modo, pwrs_start,  pwrs_end, counters_hw)
            cks = self.PV_calcular_hash_checksum(cks_str)
        elif fw_version >= 299:
            # Las versiones nuevas llevan el control de counters_hw
            cks_str = '{0},{1},{2},{3},{4},{5},{6},'.format( timerdial,timerpoll,timepwrsensor,pwrs_modo, pwrs_start,pwrs_end, counters_hw )
            cks = self.PV_calcular_ckechsum(cks_str)
        else:
            cks_str = '{0},{1},{2},{3},{4},{5},'.format(timerdial, timerpoll, timepwrsensor, pwrs_modo, pwrs_start, pwrs_end)
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_base', dlgid=self.dlgid, level='SELECT', msg='CKS_BASE: (fw={0}) [{1}][{2}]'.format( fw_version, cks_str,hex(cks)))
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
                cks_str += '%s:%s,%d,%d,%.02f,%.02f,%.02f;' % (ch_id, d.get((ch_id, 'NAME'),'AX'), int(d.get((ch_id, 'IMIN'),'0')), int(d.get((ch_id, 'IMAX'),'0')), float(d.get((ch_id, 'MMIN'),'0')), float(d.get((ch_id, 'MMAX'),'0')), float(d.get((ch_id, 'OFFSET'),'0')) )
            else:
                cks_str += '{}:X,4,20,0.00,10.00,0.00;'.format(ch_id)

        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        if fw_version >= 300:
            cks = self.PV_calcular_hash_checksum(cks_str)
        else:
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_analog', dlgid=self.dlgid, level='SELECT', msg='CKS_AN ({0}ch): [{1}][{2}]'.format(nro_analog_channels, cks_str,hex(cks)))
        return cks


    def PV_checksum_digital(self, d):
        # Los canales digitales van del 0 hasta el 7 ( maximo )
        # Pueden faltar algunos que no usemos por lo que no esten definidos.
        # D0:D0,TIMER;D1:D1,NORMAL;
        cks_str = ''
        nro_digital_channels = int(self.payload_dict.get('NDCH', '0'))
        for ch in range(nro_digital_channels):
            ch_id = 'D{}'.format(ch)            # ch_id = D1
            if (ch_id,'NAME') in d.keys():      # ( 'D1', 'NAME' ) in  d.keys()
                if d.get((ch_id, 'MODO'),'NORMAL') == 'NORMAL':
                    # Modo NORMAL
                    cks_str += '%s:%s,NORMAL;' % (ch_id, d.get((ch_id, 'NAME'),'DX'))
                else:
                    # Modo TIMER
                    cks_str += '%s:%s,TIMER;' % (ch_id, d.get((ch_id, 'NAME'),'DX'))
            else:
                cks_str += '{}:X,NORMAL;'.format(ch_id)

        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        if fw_version >= 300:
            cks = self.PV_calcular_hash_checksum(cks_str)
        else:
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_digital', dlgid=self.dlgid, level='SELECT', msg='CKS_DG ({0}ch): [{1}][{2}]'.format(nro_digital_channels,cks_str,hex(cks)))
        return cks


    def PV_checksum_counters(self, d):
        # Los canales contadores son maximo 2
        # Pueden faltar algunos que no usemos por lo que no esten definidos.
        # C0:C0,1.000,100,10,0;C1:C1,1.000,100,10,0;

        cks_str = ''
        nro_counter_channels = int(self.payload_dict.get('NCNT', '0'))
        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        #log(module=__name__, function='PV_checksum_counters', dlgid=self.dlgid, level='SELECT', msg='fw_version={0}]'.format(fw_version))
        for ch in range(nro_counter_channels):
            ch_id = 'C{}'.format(ch)            # ch_id = C1
            modo = ''

            if fw_version >= 301:
                if (ch_id, 'NAME') in d.keys():
                    cks_str += '%s:%s,%.03f,%d,%d,%s,%s;' % (ch_id, d.get((ch_id, 'NAME'), 'CX'), float(d.get((ch_id, 'MAGPP'), '0')), int(d.get((ch_id, 'PERIOD'), '0')), int(d.get((ch_id, 'PWIDTH'), '0')),d.get((ch_id, 'SPEED'), 'LS'),d.get((ch_id, 'EDGE'), 'RISE'))
                    modo = '301/BD'
                else:
                    cks_str += '{}:X,0.100,100,10,LS,RISE;'.format(ch_id)
                    modo = '301/DEFAULT'

                cks = self.PV_calcular_hash_checksum(cks_str)

            elif fw_version >= 300:
                if (ch_id, 'NAME') in d.keys():
                    cks_str += '%s:%s,%.03f,%d,%d,%s;' % (ch_id, d.get((ch_id, 'NAME'), 'CX'), float(d.get((ch_id, 'MAGPP'), '0')),int(d.get((ch_id, 'PERIOD'), '0')), int(d.get((ch_id, 'PWIDTH'), '0')),d.get((ch_id, 'SPEED'), 'LS'))
                    modo = '300/BD'
                else:
                    cks_str += '{}:X,0.100,100,10,LS;'.format(ch_id)
                    modo = '300/DEFAULT'

                cks = self.PV_calcular_hash_checksum(cks_str)

            else:
                if (ch_id, 'NAME') in d.keys():
                    cks_str += '%s:%s,%.03f,%d,%d,%s;' % (ch_id, d.get((ch_id, 'NAME'), 'CX'), float(d.get((ch_id, 'MAGPP'), '0')),int(d.get((ch_id, 'PERIOD'), '0')), int(d.get((ch_id, 'PWIDTH'), '0')),d.get((ch_id, 'SPEED'), 'LS'))
                    modo = '2xx/BD'
                else:
                    cks_str += '{}:X,0.100,100,10,LS;'.format(ch_id)
                    modo = '2xx/DEFAULT'

                cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_counters', dlgid=self.dlgid, level='SELECT', msg='CKS_CNT ({0}ch): [{1}][{2} modo={3}]'.format(nro_counter_channels, cks_str,hex(cks), modo))
        return cks


    def PV_checksum_range(self, d):
        name = d.get(('RANGE','NAME'),'X')
        cks_str = '{}'.format(name)
        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        if fw_version >= 300:
            cks = self.PV_calcular_hash_checksum(cks_str)
        else:
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_range', dlgid=self.dlgid, level='SELECT', msg='CKS_RANGE: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_psensor(self, d):
        name = d.get(('PSENSOR', 'NAME'), 'X')
        count_min = int(d.get(('PSENSOR', 'COUNT_MIN'), 0))
        count_max = int(d.get(('PSENSOR', 'COUNT_MAX'), 0))
        p_max = float(d.get(('PSENSOR', 'PRESION_MAX'), 0))
        p_min = float(d.get(('PSENSOR', 'PRESION_MIN'), 0))
        offset = float(d.get(('PSENSOR', 'OFFSET'), 0))
        cks_str = '%s,%d,%d,%.01f,%.01f,%.01f' % (name,count_min,count_max, p_min,p_max,offset)

        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        if fw_version >= 300:
            cks = self.PV_calcular_hash_checksum(cks_str)
        else:
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_psensor', dlgid=self.dlgid, level='SELECT', msg='CKS_PSENSOR: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_aplicacion(self, d):
        output_modo = d.get(('BASE','APLICACION'),'OFF')
        cks_str = ''
        if output_modo == 'OFF':
            cks_str = self.PV_checksum_str_app_off(d)
        elif output_modo == 'TANQUE':
            cks_str = self.PV_checksum_str_app_tanque(d)
        elif output_modo == 'PERFORACION':
            cks_str = self.PV_checksum_str_app_perforacion(d)
        elif output_modo == 'CONSIGNA':
            cks_str = self.PV_checksum_str_app_consigna(d)
        elif output_modo == 'PLANTAPOT':
            cks_str = self.PV_checksum_str_app_plantapot(d)

        fw_version = u_get_fw_version(self.dlgbdconf_dict)
        if fw_version >= 300:
            cks = self.PV_calcular_hash_checksum(cks_str)
        else:
            cks = self.PV_calcular_ckechsum(cks_str)

        log(module=__name__, function='PV_checksum_aplicacion', dlgid=self.dlgid, level='SELECT', msg='CKS_APLICACION: [{0}][{1}]'.format(cks_str,hex(cks)))
        return cks


    def PV_checksum_str_app_off(self,d):
        cks_str = 'OFF'
        return(cks_str)


    def PV_checksum_str_app_tanque(self,d):
        cks_str = 'TANQUE'
        return(cks_str)


    def PV_checksum_str_app_perforacion(self,d):
        cks_str = 'PERFORACION'
        return(cks_str)


    def PV_checksum_str_app_consigna(self,d):
        cons_hhmm1 = int(d.get(('CONS', 'HHMM1'), '0000'))
        cons_hhmm2 = int(d.get(('CONS', 'HHMM2'), '0000'))
        cks_str = 'CONSIGNA,%04d,%04d' % ( cons_hhmm1, cons_hhmm2 )
        return(cks_str)


    def PV_checksum_str_app_plantapot(self,d):
        # header
        cks_str = 'PPOT;'

        # sms's
        level_default = 1
        for i in range(9):
            name = 'SMS{}'.format(i)
            nivel = 'NV_SMS{}'.format(i)
            nro_default = '099' + str(i) * 6

            SMS_nro = d.get(('PPOT', name), nro_default)
            if SMS_nro == '':
                SMS_nro = nro_default
            SMS_nivel = d.get(('PPOT', nivel), level_default)
            if SMS_nivel == '':
                SMS_nivel = level_default

            level_default += 1
            if level_default > 3:
                level_default = 1

            cks_str += "SMS0{0}:{1},{2};".format(i, SMS_nro, SMS_nivel)

        # levels
        from spy_utils import d_defaults
        for ch in range(6):
            CH = 'CH{}'.format(ch)
            cks_str += 'LCH{}:'.format(ch)
            for level in range(1, 4):
                LVL_INF = 'A{}_INF'.format(level)
                LVL_SUP = 'A{}_SUP'.format(level)
                def_val_inf = d_defaults[CH][LVL_INF]
                def_val_sup = d_defaults[CH][LVL_SUP]

                val_inf = d.get((CH, LVL_INF), def_val_inf)
                if val_inf == '':
                    val_inf = def_val_inf

                val_sup = d.get((CH, LVL_SUP), def_val_sup)
                if val_sup == '':
                    val_sup = def_val_sup

                cks_str += '%.02f,%.02f' % (float(val_inf), float(val_sup))
                if level < 3:
                    cks_str += ','
                else:
                    cks_str += ';'

        # print(cks_str)
        return cks_str


if __name__ == '__main__':
    str = "C0:PCAU,1.000,1000,100,LS;C1:X,0.100,100,10,LS;"
    #str = "C0:PCAU,1.000,1000,100,LS;"
    #str = "C1:X,0.100,100,10,LS;"
    cglobal = INIT_CONF_GLOBAL("MER007", "3.0.0a", None, None)
    cks = cglobal.PV_calcular_hash_checksum(str)
    print("STR={0}".format(str))
    print("CKS={0}, hex={1}".format(cks, hex(cks)))