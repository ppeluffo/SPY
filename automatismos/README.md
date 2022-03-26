ROYECTO DE SISTEMAS CON AUTOMATISMOS

FLOWCHART: project 				-> 	https://drive.google.com/file/d/1YFjm_3HncAyEX1VBOtet1D0vdXyxPA-W/view?usp=sharing
		   serv_APP_selection 	-> 	https://drive.google.com/file/d/1ImChibsiLTjf7Fgl6tJeAeD8pxPpUmb0/view?usp=sharing
		   CTRL_FREC			->	
		   CTRL_PpotPaysandu	->  https://drive.google.com/file/d/1VDwYcD7yKF_tMaDpcf-pSyj6EQ-DgkTK/view?usp=sharing



ENVIROMENT: #!/usr/aut_env/bin/python3.8

# LOGS: 
## SYSLOG
	Los log utilizan el syslog de ubuntu. Para ello agregar al archivo /etc/rsyslog.d/50-default.conf la siguiente configuracion
	<<<<<<<<<<<
		:syslogtag, contains, "AUTO_CTRL" /var/log/autoCtrl.log
		:syslogtag, contains, "AUTO_CTRL" ~
	>>>>>>>>>>>

## Logrotate: 
	Para controlar el tamamano de los logs crear un archivo en la carpeta /etc/logrotate.d con la siguiete configuracion
	<<<<<<<<<<<
		/var/log/autoCtrl.log
		{
				rotate 3
				daily
				size 1G
				missingok
				notifempty
				delaycompress
				compress
				postrotate
						invoke-rc.d rsyslog rotate > /dev/null
				endscript
		}
	>>>>>>>>>>>


# FORMA DE EJECUCION:
## DETECCION DE ERRORES DESDE EL CRONTAB
/var/etc/crontab => 
	*/1 * * * * root /datos/cgi-bin/spx/AUTOMATISMOS/serv_error_APP_selection.py > /dev/null 2>&1
	NOTA: EN EL CRONTAB SE EJECUTA TODO LO RELACIONADO A DETECCION DE ERRORES


## PROCESS DEL AUTOMATIMSO DESDE EL SERVIDOR EN PYTHON
//drbd/www/cgi-bin/SPY/spy.conf =>
	
	[CALLBACKS_PATH]
	cbk_path = /datos/cgi-bin/spx/AUTOMATISMOS

	[CALLBACKS_PROGRAM]
	cbk_program = serv_APP_selection.py
	
	NOTA: CADA VEZ QUE EL DATALOGGER TRANSMITE SE LLAMA A LA FUNCION process_perf Y SE LE PASA EL DATALOGGER ID


# TASKS
## TASK LEGEND 
	(-) => taks to do
	(*) => taks done

* actualizar el repositorio local con sus ramas y configurar el remoto
* crear el flowchart del automatismo
* descargar el automatismo que esta en el servidor .9 y hacer un merge con el automatismo actual
	* drv_config
	* drv_db_GDA
	* drv_dlg
	* drv_logs
	* drv_redis
	* mypython
	* serv_APP_config
	* serv_APP_selection
	* serv_error_APP_selection
	* ctrl_error
	* ctrl_library
	* ctrl_process
	* drv_visual
	* call_ctrl_process_frec
	* ctrl_config
	* ctrl_process_frec_DLGID
	* error_process_DLGID
- descargar el automatismo que esta en el servidor .7 y hacer un merge con el automatismo actual
	* drv_config
	* drv_db_GDA
	* drv_dlg
	* drv_logs
	* drv_redis
	* mypython
	* serv_APP_config
	* serv_APP_selection
	* serv_error_APP_selection
	* spy_log
	* ctrl_error
	* ctrl_library
	* ctrl_process
	* drv_visual
	* call_ctrl_process_frec
	* ctrl_config
	* ctrl_process_frec_DLGID
	* error_process_DLGID
* hacer que el automatismo actual funcione con recursos locales.
* implementar el test de tx
* buscar mejor solucion para el uso de los logs
* meter toda la capaa de drivers dentro de la carpeta __CORE__
* implementar todos los estados y alarmas
* poner en archivo de configuracion todo script que use la siguiente fraccion de ruta '/datos/cgi-bin/'
* comparar el serv_APP_selection de los automatismos con el de test DLG.
* en cada uno de los serv_corregir que la ruta del archivo a llama haya que ponerla a mano.
* implemetar las funciones readAutConf y WriteAutConf contra la tabla en postgres
* implementar una fucion del tipo redis.hdel(DLGID_CTRL, param) para GDA y ponerla en ambos servicios
* garantizar que las webVisualVars siempre esten disponibles con un valor por default
* optimizar as consultas en la base de datos
* ver el tema de la actualizacion de frecuencia y que la misma se ejecute cuando la tx este ok










