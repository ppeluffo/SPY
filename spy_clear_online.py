#!/usr/bin/python3 -u
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
import datetime as dt
engine = create_engine('mysql://ulises:pexco599@192.168.0.8/GDA', pool_recycle=3600, pool_size = 5)
conn = engine.connect()


sql = "SELECT * FROM spx_online"
df = pd.read_sql_query(sql, conn)
df.set_index('id', inplace=True)
df


# data_error = df[df['fechadata'] > dt.datetime.now()]['id'].to_list()
df_error = df[(df['fechadata'] > dt.datetime.now()) | (df['fechadata'].isnull())]
df.drop(df_error.index, inplace=True, axis=0)
df_error           


for i, row in df_error.iterrows():
    print(str(i))
    sql = "DELETE FROM spx_online WHERE id={}".format(i)
        
    query = text(sql)
    conn.execute(query)


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

