#!/usr/aut_env/bin/python3.8
'''
DRIVER VISUALIZACION DE CTRL_FREC

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 3.1.0 27-04-2020 14:53
''' 



#                keys                     #name              #True_value       #False_value    #value_1     #value_2

visual_dic = {  
                'WEB_MODE':             [ 'SW1',                'AUTO',         'REMOTO',       'BOYA',     'TIMER'   ],
                'PUMP_1_WEB_MODE':      [ 'SW2',                'ON',           'OFF',                                ],
                'MAG_REF':              [ 'MAG_REF',            1                                                     ],
                'PUMP_FREC':            [ 'PUMP_FREC',          100                                                   ],
                
                'TX_ERROR':             [ 'TX_ERROR',           'SI',           'NO',                                 ],
                'MODO_LOCAL':           [ 'LOCAL_MODE',         'SI',           'NO',                                 ],
                'WORKING_FREC':         [ 'D_EXEC_REC_PUMP1',   '50 Hz',                                              ],
                'GABINETE_ABIERTO':     [ 'GABINETE_ABIERTO',   'SI',           'NO',                                 ],
                'FALLA_ELECTRICA':      [ 'FALLA_ELECTRICA',    'SI',           'NO',                                 ],
                'FALLA_TERMICA_1':      [ 'FALLA_TERMICA_1',    'SI',           'NO',                                 ],
                'DATA_DATE_TIME':       [ 'LAST_FECHA_DATA',    '20200424_151649'                                     ],
                'PUMP1_STATE':          [ 'PUMP1_REC_STATE',    'ON',           'OFF',                                ],
                'PUMP1_DAILY_TIME':     [ 'D_EXEC_REC_PUMP1',   '0h 0m'                                               ],
                'PUMP1_MONTHLY_TIME':   [ 'M_EXEC_REC_PUMP1',   '0 horas'                                             ],
                'PUMP1_TOTAL_TIME':     [ 'T_EXEC_REC_PUMP1',   '0 horas'                                             ],
                
                
    }

#
class manage_dic():
    def __init__(self,dic_in):
        '''
        #Constructor
        '''
        self.my_dic = dic_in 
    
    
    def get_dic(self,keys,atributo):
        '''
        atributos validos:  name
                            True_value
                            False_value
                            value_1
                            value_2
        '''
        
        try:
            # CHEQUEO QUE ATRIBUTO SE ESTA PASANDO
            if atributo == 'name':
                lst = self.my_dic.get(keys)
                list_sel = lst[0]
            elif atributo == 'True_value':
                lst = self.my_dic.get(keys)
                list_sel = lst[1]
            elif atributo == 'False_value':
                lst = self.my_dic.get(keys)
                list_sel = lst[2]
            elif atributo == 'value_1':
                lst = self.my_dic.get(keys)
                list_sel = lst[3]
            elif atributo == 'value_2':
                lst = self.my_dic.get(keys)
                list_sel = lst[4]
            else:
                return None
        
            return list_sel
        
        except:
            return None
        
dic = manage_dic(visual_dic)


            
#            
    