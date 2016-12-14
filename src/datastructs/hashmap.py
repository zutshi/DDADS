# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#external deps
from scipy.spatial import KDTree as kdtree
#from scipy.spatial import cKDTree as kdtree
from IPython import embed
import numpy as np

#core deps
#import logging
import collections
import itertools as it

# pyutils
from utils import print_function
import utils as U
#import fileops as fops
#import err

# internal deps
from globalopts import opts as gopts
from core import cellmanager as CM
DataPoint = collections.namedtuple('p', ('x', 'xid', 'tid'))


def element_from_traces(traces, tid, xid):
    return traces[tid].getxat(xid)


class Data(object):
#     def __init__(self, traces=None):
#         # create tree in one shot
#         if traces is not None:
#             self.kdtree = kdtree(
#                     it.chain(
#                         (DataPoint(x, xid, tid)
#                          for tid, trace in enumerate(traces)
#                          for xid, x in enumerate(trace.x_array))))

    def __init__(self, params, traces=None):
        c2dp = collections.defaultdict(list)
        if traces is not None:
            self.traces = traces
            for tid, trace in enumerate(traces):
                # last element should not be added as it has no
                # successor and it is reachable as the penultimate's
                # successor
                for xid, x in enumerate(trace.x_array[:-1]):
                    c2dp[CM.cell_from_concrete(x, params.eps)].append(DataPoint(x, xid, tid))

        self.c2dp = c2dp
        return

    def add_trace(self, trace):
        raise NotImplementedError

    def cell_xydata(self, cell):
        assert(cell in self.c2dp)

        dps = self.c2dp[cell]
        x_array = np.array([dp.x for dp in dps])
        y_array = np.array([element_from_traces(self.traces, dp.tid, dp.xid+1) for dp in dps])

        return x_array, y_array
