from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import itertools
import abc

import numpy as np

import settings
from constraints import IntervalCons
import cellmanager as CM
import err
from utils import print

MIN_TRAIN = 50
MIN_TEST = MIN_TRAIN
MAX_ITER = 25


class Q(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def split(self, *args):
        return

#     @abc.abstractproperty
#     def dim(self):
#         return

    @abc.abstractmethod
    def getxy_ignoramous(self, N, sim, t0=0):
        """TODO: EXPLICITLY ignores t, d, pvt, ci, pi
        """
        return

    @abc.abstractmethod
    def modelQ(self, rm):
        return

    @abc.abstractmethod
    def errorQ(self, include_err, X, Y, rm):
        return

    @abc.abstractmethod
    def __hash__(self):
        return hash((self.cell, tuple(self.eps)))

    @abc.abstractmethod
    def __eq__(self, c):
        return self.cell == c.cell and tuple(self.eps) == tuple(c.eps)


class Qxw(Q):
    # wic is the pi_cons of the overall system and has nothing to
    # do with wcell (of course wcell must be \in wic, but that is
    # all.
    wic = None

    @classmethod
    def init(cls, wic):
        cls.wic = wic

    def __init__(self, xcell, wcell):
        """__init__

        Parameters
        ----------
        abs_state : abstract states
        w_cells : cells associated with the abstract state defining
        range of inputs
        """
        if Qxw.wic is None:
            raise ValueError('Class was not initialized. wic is None')

        assert(isinstance(xcell, CM.Cell))
        assert(isinstance(wcell, CM.Cell))

        self.xcell = xcell
        self.wcell = wcell
        self.xwcell = CM.Cell.concatenate(xcell, wcell)
        self.sample_UR_x = self.xcell.sample_UR
        self.sample_UR_w = self.wcell.sample_UR
        self.xdim = xcell.dim
        self.wdim = wcell.dim
        self.ival_constraints = self.xwcell.ival_constraints
        return

    def split(self, *args):
        xwsplits = self.xwcell.split(*args)
        return [Qxw(xcell, wcell)
                for xwcell in xwsplits
                for xcell, wcell in xwcell.un_concatenate(self.xcell.dim)
                ]

    def getxy_ignoramous(self, N, sim, t0=0):
        """TODO: EXPLICITLY ignores t, d, pvt, ci, pi
        """
        d, pvt, s = [np.array([])]*3
        ci = np.array([])
        t0 = 0
        Yl = []

        x_array = self.sample_UR_x(N)
        pi_array = self.sample_UR_w(N)
        for x, pi in zip(x_array, pi_array):
            (t_, x_, s_, d_, pvt_, u_) = sim(t0, x, s, d, pvt, ci, pi)
            Yl.append(x_)

        return np.hstack((x_array, pi_array)), np.vstack(Yl)

    def modelQ(self, rm):

        #print('error%:', rm.max_error_pc(X, Y))
        # Matrices are extended to include w/pi
        # A = [AB]
        #     [00]
        # AB denotes matrix concatenation.
        # Hence a reset: x' =  Ax + Bw + b
        # can be mimicked as below
        #
        # [x']   = [a00 a01 a02...b00 b01...] * [x] + b + [e0]
        # [w']     [     ...  0 ...         ]   [w]       [e1]
        #
        # This makes x' \in Ax + Bw + b + [el, eh], and
        # makes w' \in [el, eh]
        # We use this to incorporate error and reset w to new values,
        # which in the case of ZOH are just the ranges of w (or pi).

        q = self
        A = np.vstack((rm.A, np.zeros((q.wdim, q.xdim + q.wdim))))
        b = np.hstack((rm.b, np.zeros(q.wdim)))
        C, d = q.ival_constraints.poly()
        try:
            assert(A.shape[0] == b.shape[0])    # num lhs (states) is the same
            assert(A.shape[1] == C.shape[1])    # num vars (states + ip) are the same
            assert(C.shape[0] == d.shape[0])    # num constraints are the same
        except AssertionError as e:
            print('\n', A, '\n', b)
            print('\n', C, '\n', d)
            print(A.shape[0], b.shape[0], C.shape[1], d.shape[0])
            raise e
        return A, b, C, d

    def errorQ(self, include_err, X, Y, rm):
        q = self
        xic = (rm.error(X, Y) if include_err
               else IntervalCons([0.0]*q.xdim, [0.0]*q.xdim))

        e = IntervalCons.concatenate(xic, Qxw.wic)
        return e

    def __hash__(self):
        return hash(self.xwcell)

    def __eq__(self, q):
        return self.xwcell == q.xwcell


class Qx(Q):
    def __init__(self, xcell):
        assert(isinstance(xcell, CM.Cell))

        self.xcell = xcell
        self.ival_constraints = xcell.ival_constraints
        self.xdim = xcell.dim
        return

    def split(self, *args):
        return [Qx(c) for c in self.xcell.split(*args)]

    def getxy_ignoramous(self, N, sim, t0=0):
        """TODO: EXPLICITLY ignores t, d, pvt, ci, pi
        """
        d, pvt, s = [np.array([])]*3
        ci, pi = [np.array([])]*2
        t0 = 0
        Yl = []

        x_array = self.xcell.sample_UR(N)
        for x in x_array:
            (t_, x_, s_, d_, pvt_, u_) = sim(t0, x, s, d, pvt, ci, pi)
            Yl.append(x_)

        return x_array, np.vstack(Yl)

    def getxy_rel_ignoramous(self, force, N, sim, t0=0):
        """getxy_rel_ignoramous

        Parameters
        ----------
        force : force to return non-zero samples. Will loop for infinitiy
                if none exists.
        """
        xl = []
        yl = []
        sat_count = 0
        iter_count = itertools.count()
        if settings.debug:
            obs_cells = set()
        while next(iter_count) <= MAX_ITER:
            x_array, y_array = self.getxy_ignoramous(N, sim, t0=0)
            if settings.debug:
                for i in y_array:
                    obs_cells.add(CM.cell_from_concrete(i, self.xcell.eps))
                print('reachable cells:', obs_cells)
            # satisfying indexes
            sat_array = cell2.ival_constraints.sat(y_array)
            sat_count += np.sum(sat_array)
            xl.append(x_array[sat_array])
            yl.append(y_array[sat_array])
            if sat_count >= MIN_TRAIN:
                break
            # If no sample is found and force is True, must keep sampling till
            # satisfying samples are found
        if settings.debug:
            if sat_count < MIN_TRAIN:
                err.warn('Fewer than MIN_TRAIN samples found!')
        print('found samples: ', sat_count)
        return np.vstack(xl), np.vstack(yl)

    def modelQ(self, rm):
        A, b = rm.A, rm.b
        C, d = self.ival_constraints.poly()
        return A, b, C, d

    def errorQ(self, include_err, X, Y, rm):
        # TODO: guess the dimensions. Fix it
        e = (rm.error(X, Y) if include_err
             else IntervalCons([0.0]*self.xdim, [0.0]*self.xdim))
        return e

    def __hash__(self):
        return hash(self.xcell)

    def __eq__(self, q):
        return self.xcell == q.xcell
