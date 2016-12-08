#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


# X: Plant states

# import time

import logging
import numpy as np

import utils as U
from utils import print
import err

from graphs import graph as g
from . import state as st
from . import cellmanager as CM
from . import PACell as PA

import settings

logger = logging.getLogger(__name__)


def abstraction_factory(*args, **kwargs):
    return TopLevelAbs(*args, **kwargs)


# mantains a graph representing the abstract relation
# Each state is a tuple (abstract_plant_state, abstract_controller_state)
# Each relation is A1 -> A2, and is annotated by the concrete states
# abstraction states are a tuple (plant_state, controller_state)

class TopLevelAbs:

    # get_abs_state = collections.namedtuple('tpl_abs_state', ['plant_state', 'controller_state'], verbose=False)

    @staticmethod
    def get_abs_state(plant_state):
        return AbstractState(plant_state)

    # takes in the plant and the controller abstraction objects which are
    # instatiation of their respective parameterized abstract classes

    #TODO: split this ugly init function into smaller ones
    def __init__(
        self,
        config_dict,
        ROI,
        T,
        num_dims,
        plant_abstraction_type,
        graph_lib,
        plant_abs=None,
        prog_bar=False,
        ):

        # super(Abstraction, self).__init__()

        self.ROI = ROI
        self.graph_lib = graph_lib
        self.num_dims = num_dims
        self.G = g.factory(graph_lib)
        self.T = T
        self.N = None
        self.state = None
        self.scale = None
        self.plant_abstraction_type = plant_abstraction_type

        # The list of init_cons is interpreted as [ic0 \/ ic1 \/ ... \/ icn]
#        self.init_cons_list = init_cons_list
#        self.final_cons_list = final_cons_list

        self.eps = None
        self.delta_t = None
        self.num_samples = None

        # TODO: replace this type checking by passing dictionaries and parsing
        # outside the class. This will also avoid parsing code duplication.
        # Keep a single configuration format.

        self.parse_config(config_dict)

        plant_abs = PA.PlantAbstraction(
            self.T,
            self.N,
            self.num_dims,
            self.delta_t,
            self.eps,
            self.num_samples,
            )

        print(U.decorate('new abstraction created'))
        print('eps:', self.eps)
        print('num_samples:', self.num_samples)
        print('refine:', self.refinement_factor)
        print('deltaT:', self.delta_t)
        print('TH:', self.T)
        print('num traces:', self.N)
        print('=' * 50)

        logger.debug('new abstraction created')
        logger.debug('eps:{}'.format(self.eps))
        logger.debug('num_samples:{}'.format(self.num_samples))
        logger.debug('deltaT:{}'.format(self.delta_t))
        logger.debug('TH:{}'.format(self.T))
        logger.debug('num traces:{}'.format(self.N))
        logger.debug('=' * 50)

        # ##!!##logger.debug('==========abstraction parameters==========')
        # ##!!##logger.debug('eps: {}, refinement_factor: {}, num_samples: {},delta_t: {}'.format(str(self.eps), self.refinement_factor, self.num_samples, self.delta_t))

        self.final_augmented_state_set = set()

        # self.sanity_check()

        self.plant_abs = plant_abs

        return

    def parse_config(self, config_dict):

        # ##!!##logger.debug('parsing abstraction parameters')

        if config_dict['type'] == 'string':
            try:
                grid_eps_str = config_dict['grid_eps']
                # remove braces
                grid_eps_str = grid_eps_str[1:-1]
                self.eps = np.array([float(eps) for eps in grid_eps_str.split(',')])

                pi_grid_eps_str = config_dict['pi_grid_eps']
                # remove braces
                pi_grid_eps_str = pi_grid_eps_str[1:-1]
                #self.pi_eps = np.array([float(pi_eps) for pi_eps in pi_grid_eps_str.split(',')])

                self.refinement_factor = float(config_dict['refinement_factor'])
                self.num_samples = int(config_dict['num_samples'])
                self.delta_t = float(config_dict['delta_t'])
                self.N = int(np.ceil(self.T / self.delta_t))

                # Make the accessed data as None, so presence of spurious data can be detected in a
                # sanity check

                config_dict['grid_eps'] = None
                config_dict['pi_grid_eps'] = None
                config_dict['refinement_factor'] = None
                config_dict['num_samples'] = None
                config_dict['delta_t'] = None
            except KeyError, key:
                raise err.Fatal('expected abstraction parameter undefined: {}'.format(key))
        else:
            for attr in config_dict:
                setattr(self, attr, config_dict[attr])
            self.N = int(np.ceil(self.T / self.delta_t))
            self.refinement_factor = 2.0

        return

    def in_ROI(self, abs_state):
        """ is the abstract state in ROI?
        Only checks plant's abstract state for now. Not sure if the
        controller's state should matter.

        Returns
        -------
        True/False
        """
        return self.plant_abs.in_ROI(abs_state.ps, self.ROI) #and self.controller_abs.in_ROI()

    # TODO: remove this eventually...

    def is_terminal(self, abs_state):
        return self.plant_abs.is_terminal(abs_state.plant_state)

    # Add the relation(abs_state_src, rchd_abs_state)
    # and update the abstraction function

    def add_relation(
            self,
            abs_state_src,
            rchd_abs_state,
            pi
            ):

        # get new distance/position from the initial state
        # THINK:
        # n can be calculated in two ways
        #   - only in the abstraction world: [current implementation]
        #       Completely independant of the simulated times
        #       i.e. if A1->A2, then A2.n = A1.n + 1
        #   - get it from simulation trace:
        #       n = int(np.floor(t/self.delta_t))

        self.G.add_edge(abs_state_src, rchd_abs_state, pi=pi)
        return

    def get_reachable_states(self, abs_state, system_params):
        abs2rchd_abs_state_set = set()
        #print(abs_state.ps.cell_id)
        # TODO: RECTIFY the below GIANT MESS
        # Sending in self and the total abstract_state to plant and controller
        # abstraction!!

        logger.debug('getting reachable states for: {}'.format(abs_state))

        intermediate_state = \
            self.controller_abs.get_reachable_abs_states(abs_state, self, system_params)
        abs2rchd_abs_state_ci_pi_list = \
            self.plant_abs.get_reachable_abs_states(intermediate_state, self, system_params)

        for (rchd_abs_state, ci_cell, pi_cell) in abs2rchd_abs_state_ci_pi_list:

            self.add_relation(abs_state, rchd_abs_state, ci_cell, pi_cell)
            abs2rchd_abs_state_set.add(rchd_abs_state)

        logger.debug('found reachable abs_states: {}'.format(abs2rchd_abs_state_set))
        return abs2rchd_abs_state_set


    def compute_error_paths(self, initial_state_set, final_state_set, MAX_ERROR_PATHS):
        # length of path is num nodes, whereas N = num segments
        max_len = self.N + 1
        return self.G.get_path_generator(initial_state_set, final_state_set, max_len, MAX_ERROR_PATHS)

    # memoized because the same function is called twice for ci and pi
    # FIXME: Need to fix it
    #@U.memodict
    def get_seq_of_ci_pi(self, path):
        attr_map = self.G.get_path_attr_list(path, ['ci', 'pi'])
        #print('attr_map:', attr_map)
        return attr_map['ci'], attr_map['pi']


    def get_error_paths_not_normalized(self, initial_state_set,
                        final_state_set, pi_ref,
                        ci_ref, pi_cons, ci_cons,
                        max_paths):
        '''
        @type pi_cons: constraints.IntervalCons
        @type ci_cons: constraints.IntervalCons
        '''

        MAX_ERROR_PATHS = max_paths
        pi_dim = self.num_dims.pi
        path_list = []
        ci_seq_list = []
        pi_seq_list = []

        error_paths = self.compute_error_paths(initial_state_set, final_state_set, MAX_ERROR_PATHS)
        bounded_error_paths = error_paths

        def get_ci_seq(path):
            return self.get_seq_of_ci_pi(path)[0]

        def get_pi_seq(path):
            return self.get_seq_of_ci_pi(path)[1]

        def get_empty(_):
            return []

        get_pi = get_pi_seq if pi_dim != 0 else get_empty

        unique_paths = set()
        for path in bounded_error_paths:
            pi_seq_cells = get_pi(path)
            pi_ref.update_from_path(path, pi_seq_cells)
            pi_seq = [CM.ival_constraints(pi_cell, pi_ref.eps) for pi_cell in pi_seq_cells]
            if ci_ref is not None:
                ci_seq_cells = get_ci(path)
                ci_ref.update_from_path(path, ci_seq_cells)
                ci_seq = [CM.ival_constraints(ci_cell, ci_ref.eps) for ci_cell in ci_seq_cells]
            else:
                ci_seq = get_ci(path)

            #FIXME: Why are uniqe paths found only for the case when dim(ci) != 0?
            plant_states_along_path = tuple(state.plant_state for state in path)
            if plant_states_along_path not in unique_paths:
                unique_paths.add(plant_states_along_path)
                ci_seq_list.append(ci_seq)
                pi_seq_list.append(pi_seq)
                path_list.append(path)


        return (path_list, ci_seq_list, pi_seq_list)

    def get_error_paths(self, initial_state_set,
                        final_state_set, pi_ref,
                        ci_ref, pi_cons, ci_cons,
                        max_paths):
        '''
        @type pi_cons: constraints.IntervalCons
        @type ci_cons: constraints.IntervalCons
        '''

        MAX_ERROR_PATHS = max_paths
        ci_dim = self.num_dims.ci
        pi_dim = self.num_dims.pi
#         init_set = set()
        path_list = []
        ci_seq_list = []
        pi_seq_list = []

        error_paths = self.compute_error_paths(initial_state_set, final_state_set, MAX_ERROR_PATHS)
        #bounded_error_paths = U.bounded_iter(error_paths, MAX_ERROR_PATHS)
        bounded_error_paths = error_paths

        def get_ci_seq(path):
            return self.get_seq_of_ci_pi(path)[0]

        def get_pi_seq(path):
            return self.get_seq_of_ci_pi(path)[1]

        def get_empty(_):
            return []

        get_ci = get_ci_seq if ci_dim != 0 else get_empty
        get_pi = get_pi_seq if pi_dim != 0 else get_empty

#         if ci_dim == 0:
#             for path in bounded_error_paths:
#                 ci_seq = []
#                 ci_seq_list.append(ci_seq)
#                 init_set.add(path[0])

#             return (list(init_set), ci_seq_list)
#         else:
        max_len = -np.inf
        min_len = np.inf
        unique_paths = set()
        for path in bounded_error_paths:
#             ci_seq = self.get_seq_of_ci(path)
            pi_seq_cells = get_pi(path)
            pi_ref.update_from_path(path, pi_seq_cells)
            # convert pi_cells to ival constraints
            #pi_seq = map(self.plant_abs.get_ival_cons_pi_cell, get_pi(path))
            pi_seq = [CM.ival_constraints(pi_cell, pi_ref.eps) for pi_cell in pi_seq_cells]
            if ci_ref is not None:
                ci_seq_cells = get_ci(path)
                ci_ref.update_from_path(path, ci_seq_cells)
                ci_seq = [CM.ival_constraints(ci_cell, ci_ref.eps) for ci_cell in ci_seq_cells]
            else:
                ci_seq = get_ci(path)

            #print(pi_seq)

            #FIXME: Why are uniqe paths found only for the case when dim(ci) != 0?
            plant_states_along_path = tuple(state.plant_state for state in path)
            if plant_states_along_path not in unique_paths:
                unique_paths.add(plant_states_along_path)

                if ci_dim != 0:
                    assert(len(ci_seq) == len(path) - 1)
                else:
                    assert(len(ci_seq) == 0)
                if pi_dim != 0:
                    assert(len(pi_seq) == len(path) - 1)
                else:
                    assert(len(pi_seq) == 0)

#                 max_len = max(len(ci_seq), max_len)
#                 min_len = min(len(ci_seq), min_len)

                max_len = max(len(path), max_len)
                min_len = min(len(path), min_len)

                ci_seq_list.append(ci_seq)
                pi_seq_list.append(pi_seq)
                path_list.append(path)

        assert(max_len <= self.N + 1)

        # normalize list lens by appending 0

#         if max_len != min_len or max_len < self.N:

#             # TODO: many a times we find paths, s.t. len(path) > self.N
#             # How should those paths be handled?
#             #   - Should they be ignored, shortened, or what?
#             #   - or should nothing be done about them?

#             for (idx, ci_seq) in enumerate(ci_seq_list):
#                 # instead of zeros, use random!
#                 num_of_missing_ci_tail = max(max_len, self.N) - len(ci_seq)
#                 ci_seq_list[idx] = ci_seq \
#                     + list(np.random.random((num_of_missing_ci_tail, ci_dim)))

#             for (idx, pi_seq) in enumerate(pi_seq_list):
#                 num_of_missing_pi_tail = max(max_len, self.N) - len(pi_seq)
#                 pi_seq_list[idx] = pi_seq \
#                     + list(np.random.random((num_of_missing_pi_tail, pi_dim)))

        for (idx, (ci_seq, pi_seq)) in enumerate(zip(ci_seq_list, pi_seq_list)):
            missing_ci_len = self.N - len(ci_seq)
            missing_pi_len = self.N - len(pi_seq)
            # row, column
            r, c_ci = missing_ci_len, ci_dim
            #FIXME: default random values
            if ci_ref is not None:
                ci_seq_list[idx] = ci_seq + [ci_cons] * missing_ci_len
            else:
                ci_seq_list[idx] = ci_seq + list(np.random.uniform(ci_cons.l, ci_cons.h, (r, c_ci)))
            #pi_seq_list[idx] = pi_seq + list(np.random.uniform(pi_cons.l, pi_cons.h, (r, c_pi)))
            pi_seq_list[idx] = pi_seq + [pi_cons] * missing_pi_len


        if settings.debug:
            print('path states, min_len:{}, max_len:{}'.format(min_len, max_len))

        # ##!!##logger.debug('init_list:{}\n'.format(init_list))
        # ##!!##logger.debug('ci_seq_list:{}\n'.format(ci_seq_list))
        # print('len(init_list)', len(init_list))
        # print('len(ci_seq_list)', len(ci_seq_list))

#         for ci_seq in ci_seq_list:
#             print(ci_seq)
#         for pi_seq in pi_seq_list:
#             print(pi_seq)

        return (path_list, ci_seq_list, pi_seq_list)

    def get_initial_states_from_error_paths(self, *args):
        '''extracts the initial state from the error paths'''
        path_list, ci_seq_list, pi_seq_list = self.get_error_paths(*args)
        init_list = [path[0] for path in path_list]
        return init_list, ci_seq_list, pi_seq_list

    def get_abs_state_from_concrete_state(self, concrete_state):

        # ##!!##logger.debug(U.decorate('get_abs_state_from_concrete_state'))

        abs_plant_state = \
            self.plant_abs.get_abs_state_from_concrete_state(concrete_state)
        abs_controller_state = \
            self.controller_abs.get_abs_state_from_concrete_state(concrete_state.s)

        #TODO: why do we have the below code?
        if abs_plant_state is None or abs_controller_state is None:
            return None
        else:
            abs_state = TopLevelAbs.get_abs_state(abs_plant_state,
                    abs_controller_state)

        # ##!!##logger.debug('concrete state = {}'.format(concrete_state))
        # ##!!##logger.debug('abstract state = {}'.format(abs_state))
        # ##!!##logger.debug(U.decorate('get_abs_state_from_concrete_state done'))

        return abs_state

    def __repr__(self):
        return ''

    def draw_2d(self):
        pos_dict = {}
        for n in self.G.nodes():
            if len(n.plant_state.cell_id) != 2:
                raise err.Fatal('only 2d abstractions can be drawn, with each node representing the coordinates (x,y)!. Was given {}-d'.format(len(n.plant_state.cell_id)))
            pos_dict[n] = n.plant_state.cell_id
        self.G.draw(pos_dict)


        # nx.draw_networkx(self.G, pos=pos_dict, labels=pos_dict, with_labels=True)
        # TODO: whats the use of draw?
        # plt.draw()


def sample_abs_state(abs_state,
                     A,
                     system_params):

    samples = system_params.sampler.sample(abs_state, A, system_params, A.num_samples)

    total_num_samples = samples.n

    x_array = samples.x_array

    # print s_array

    t_array = samples.t_array
    pi_array = samples.pi_array
    ci_array = samples.ci_array

    d = np.array([abs_state.plant_state.d])
    pvt = np.array([abs_state.plant_state.pvt])

    d_array = np.repeat(d, samples.n, axis=0)
    pvt_array = np.repeat(pvt, samples.n, axis=0)

    # sanity check
    assert(len(d_array) == total_num_samples)
    assert(len(pvt_array) == total_num_samples)
    assert(len(x_array) == total_num_samples)
    assert(len(t_array) == total_num_samples)



    # can not use None because of a check in
    # get_abs_state_from_concrete_state() which silently makes
    # the entire abstract state None if a None is encountered
    # in either plant or contorller abs state.
    (s_array_, u_array) = U.inf_list(0), U.inf_list(0)

    state = st.StateArray(
        t=t_array,
        x=x_array,
        d=d_array,
        pvt=pvt_array,
        s=s_array_,
        u=u_array,
        pi=pi_array,
        ci=ci_array,
        )

    return state


class AbstractState(object):

    def __init__(self, plant_state):
        self.plant_state = plant_state
        return

    # rename/shorten name hack

    @property
    def ps(self):
        return self.plant_state

    def __eq__(self, x):

        if isinstance(x, AbstractState):
            return self.ps == x.ps
        else:
            return False

    def __hash__(self):

        return hash(self.ps)

    def __repr__(self):
        return 'p={' + self.plant_state.__repr__() + '}'
