#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 21:12:58 2019

@author: pablo
"""
import re
from spy_log import log

# ------------------------------------------------------------------------------
class APP_TANQUE():


    def __init__(self, dlgid):
        self.dlgid = dlgid


    def init_from_payload(self, d):
        return

    def init_from_bd(self, d):
        return

    def log(self, tag=''):
        log(module=__name__, function='log', level='SELECT', dlgid=self.dlgid, msg='{0} app=TANQUE'.format(tag))
        return

    def __eq__(self, other):
        return True

    def get_response_string(self):
        response = 'AP0:TANQUE;'
        return response

