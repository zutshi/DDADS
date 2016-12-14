# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#external deps

#core deps
import logging

# pyutils
from utils import print_function
import fileops as fops
import err

# internal deps


# start logger
def setup_logger(time_str):
    #FORMAT = '[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s'
    FORMAT2 = '%(levelname) -10s %(asctime)s %(module)s:\
               %(lineno)s %(funcName)s() %(message)s'

    logging.basicConfig(filename='{}_secam.log'.format(time_str), filemode='w', format=FORMAT2,
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger


#side effect: creates the dir
def setup_dir(sys_name, dirname, time_str):
    # If no output folder is specified, generate one
    if dirname is None:
        dirname = '{}_{}'.format(sys_name, time_str)
    if fops.file_exists(dirname):
        err.Fatal('output dir exists! Please provide a new dir name to prevent override.')

    def construct_path(fname): return fops.construct_path(fname, dirname)
    # create otuput directory
    fops.make_dir(dirname)
    return construct_path
