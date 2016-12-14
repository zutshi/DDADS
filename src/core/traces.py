#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
from scipy import io


import fileops as fops
from streampickle import PickleStreamReader

## commented off because matplotlib is not installed for python installation
## used with matlab
#import matplotlib
## Force GTK3 backend. By default GTK2 gets loaded and conflicts with
## graph-tool
#matplotlib.use('GTK3Agg')
#global plt
#import matplotlib.pyplot as plt

plot_figure_for_paper = False


class Trace(object):

    def __init__(self, num_dims, num_points):
        self.idx = 0
        self.t_array = np.empty(num_points)
        self.x_array = np.empty((num_points, num_dims.x))
        self.s_array = np.empty((num_points, num_dims.s))
        self.u_array = np.empty((num_points, num_dims.u))
        self.d_array = np.empty((num_points, num_dims.d))
        self.ci = np.empty((num_points, num_dims.ci))
        self.pi = np.empty((num_points, num_dims.pi))

    def getxat(self, idx):
        return self.x_array[idx, :]

    def append(
            self,
            s=None,
            u=None,
            x=None,
            ci=None,
            pi=None,
            t=None,
            d=None,
            ):
        #if s is None or u is None or r is None or x is None or ci is None \
        #    or pi is None or t is None or d is None:
        #    raise err.Fatal('one of the supplied arguement is None')

        i = self.idx
        self.t_array[i] = t
        self.x_array[i, :] = x
        self.s_array[i, :] = s
        self.u_array[i, :] = u
        self.ci[i, :] = ci
        self.pi[i, :] = pi
        self.idx += 1

    def dump_matlab(self):
        data = {'T': self.t_array,
                'X': self.x_array,
                'S': self.s_array,
                'U': self.u_array,
                'CI': self.ci,
                'PI': self.pi}
        io.savemat('mat_file.mat', data, appendmat=False, format='5',
                   do_compression=False, oned_as='column')

    def __str__(self):
        s = '''t:{},\nx:{},\ns:{},\nu:{},\nci:{},\npi:{}'''.format(
            self.t_array,
            self.x_array,
            self.s_array,
            self.u_array,
            self.ci,
            self.pi,
            )
        return s
    def serialize(self):
        s = '''{}\n{}\n{}\n{}\n{}\n{}'''.format(
            self.t_array.tobytes(),
            self.x_array.tobytes(),
            self.s_array.tobytes(),
            self.u_array.tobytes(),
            self.ci.tobytes(),
            self.pi.tobytes(),
            )
        return s


def get_simdump_gen(sysname, dirpath):
    files = fops.get_file_list_matching(sysname + '.simdump*', dirpath)

    for f in files:
        reader = PickleStreamReader(f)
        for trace in reader.read():
            yield trace
