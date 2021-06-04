#!/usr/bin/python3 -u
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import datetime as dt
from spy_config import Config

engine = create_engine(Config['BDATOS']['url_gda_spymovil'], pool_recycle=3600, pool_size = 5)
conn = engine.connect()


# Elimino todos los NaN. 
sql = "DELETE FROM spx_online WHERE valor = 'NaN'"
query = text(sql)
conn.execute(query)

# Cargo todo en spx_online
sql = "SELECT * FROM spx_online"
df = pd.read_sql_query(sql, conn)
df.set_index('id', inplace=True)
df

# Eliminar los datos invalidos en online.
df_error = df[(df['fechadata'] > dt.datetime.now()) | (df['fechadata'].isnull())]
df.drop(df_error.index, inplace=True, axis=0)
df_error           


for i, row in df_error.iterrows():
    print(str(i))
    sql = "DELETE FROM spx_online WHERE id={}".format(i)
        
    query = text(sql)
    conn.execute(query)

# Eliminar los datos viejos en online.

df.sort_values(['medida_id','ubicacion_id', 'fechadata'], inplace=True)
df.drop_duplicates(('medida_id','ubicacion_id'), keep="last", inplace=True)  
df


df.dropna(inplace=True)
dic_list = df.to_dict('records')
dic_list


for d in dic_list: 
    print(d['fechadata'])
    print(d['ubicacion_id'])
    print(d['medida_id'])
    sql = "DELETE FROM spx_online WHERE ubicacion_id = {} AND medida_id = {} AND fechadata < '{}'".format(d['ubicacion_id'], d['medida_id'], (d['fechadata']).strftime("%Y-%m-%d %H:%M:%S"))
        
    query = text(sql)
    conn.execute(query)

# Eliminar tipos de configuracion no configurados en el DLG.
sql = """SELECT DISTINCT ubicacion_id, tipo_configuracion_id FROM 
spx_unidades_configuracion AS uc
INNER JOIN spx_instalacion AS i ON uc.dlgid_id = i.unidad_id
ORDER BY ubicacion_id, tipo_configuracion_id"""
df_tc = pd.read_sql_query(sql, conn)

for d in dic_list: 
    if d['medida_id'] not in df_tc[df_tc['ubicacion_id']==d['ubicacion_id']]['tipo_configuracion_id'].tolist():
        print("Delete invalid TC")
        print(d['ubicacion_id'])
        print(d['medida_id'])
        sql = "DELETE FROM spx_online WHERE ubicacion_id = {} AND medida_id = {} ".format(d['ubicacion_id'], d['medida_id'])

        query = text(sql)
        conn.execute(query)  