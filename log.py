'''
Created on Feb 10, 2012

@author: tufan
'''
import logging

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'

dp_log = logging.getLogger()
dp_log.setLevel(logging.DEBUG)

_dp_log_sh = logging.StreamHandler()
_dp_log_sh.setFormatter(logging.Formatter(LOG_FORMAT))

dp_log.addHandler(_dp_log_sh)