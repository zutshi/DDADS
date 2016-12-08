#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#external deps
import blessed
import tqdm
from IPython import embed

#core deps
#import logging
import collections

# pyutils
from utils import print_function
import utils as U
import fileops as fops
#import err

# internal deps
from core import traces as T
import globalopts
import cmdline
import setup_output
from core import cellmanager as CM

# def concrete(params, astate):
#     return


def abstract(params, cstate):
    return CM.cell_from_concrete(cstate, params.eps)


def analyze_graph(params, G, traces):
    import constraints as Cons

    print(U.decorate('concrete stats'))
    traces = traces #list(trace_gen)
    print('Total number of paths: {}'.format(len(traces)))

    initial_set = [[-0.4, -0.4], [0.4, 0.4]]
    error_set = [[-1, -6.5], [-0.7, -5.6]]
    X0 = Cons.IntervalCons(*initial_set)
    Xf = Cons.IntervalCons(*error_set)
    nvio = sum(1 for t in traces if t.x_array[-1, :] in Xf)
    print('Number of concrete violations: {}'.format(nvio))

    print(U.decorate('abstract stats'))
    print('Total number of nodes/edges: {}/{}, beta={}'.format(G.num_nodes(), G.num_edges(), G.num_edges()/G.num_nodes()))
    C0 = {n for n in G.nodes_iter() if CM.ival_constraints(n, params) & X0}
    Cf = {n for n in G.nodes_iter() if CM.ival_constraints(n, params) & Xf}
    print('Number of abstract initial (C0) and final (Cf) states: {}, {}'.format(len(C0), len(Cf)))
    graph_vios = set(map(tuple, G.get_all_path_generator(C0, Cf)))
    num_graph_vios = len(graph_vios)
    print('Number of violations in the graph: {}'.format(num_graph_vios))

    tC0 = {abstract(params, t.x_array[0, :]) for t in traces}
    tCf = {abstract(params, t.x_array[-1, :]) for t in traces}
#     # Due to scatter-and-simulate
#     assert(len(tC0) == len(C0))
    graph_paths = set(map(tuple, G.get_all_path_generator(tC0, tCf)))
    ngraph_paths = len(graph_paths)

    print(U.decorate('Analysis'))
    graph_vios = {tuple(gp) for gp in G.get_all_path_generator(C0, Cf)}
    num_graph_vios = len(graph_vios)

    # TODO: Instead of counting simple paths, should be counting
    # comlplex paths of bounded length?
    all_abspaths = {tuple(abstract(params, x) for x in t.x_array) for t in traces}
    #num_existing_paths = sum(gp in all_abspaths for gp in graph_paths)
    #num_new_paths = ngraph_paths - num_existing_paths
    new_paths = [gp for gp in graph_paths if gp not in all_abspaths]
    # wont work due to loops
    #assert(num_existing_paths == all_abspaths)
    print('existing paths: {}'.format(len(all_abspaths)))
    print('simple paths in graph: {}'.format(ngraph_paths))
    print('Newly created simple paths: {}'.format(len(new_paths)))
    print()

    # TODO: Instead of counting simple paths, should be counting
    # comlplex paths of bounded length?
    all_absvios = {tuple(abstract(params, x) for x in t.x_array if t.x_array[-1, :] in Xf)
                   for t in traces}
    num_unique_absvios = len(all_absvios)
    #num_existing_absvios = sum(ep in all_absvios for ep in graph_vios)
    #num_new_absvios = num_graph_vios - num_existing_absvios
    new_absvios = {gep for gep in graph_vios if gep not in all_absvios}
    # wont work due to loops
    #assert(num_existing_absvios == all_absvios)
    print('existing error paths: {}'.format(num_unique_absvios))
    print('simple error paths in abstract graph: {}'.format(num_graph_vios))
    print('Newly created error simple paths: {}'.format(len(new_absvios)))
    print()

    # find the distance metric


def build_graph(params, traces):
    gopts = globalopts.opts

    G = gopts.graph_factory()

#     for trace in tqdm.tqdm(traces, total=10000):
#         for xi, xj in U.pairwise(trace.x_array):
#             G.add_edge(abstract(params, xi), abstract(params, xj))

    edges = ((abstract(params, xi), abstract(params, xj))
             for trace in tqdm.tqdm(traces)#, total=10000)
                for xi, xj in U.pairwise(trace.x_array))
    G.add_edges_from(edges)
    return G


def secam():
    import scamr
    scamr.run_secam()


def create_abstraction(sys, prop):
    num_dims = sys.num_dims
    plant_config_dict = sys.plant_config_dict
    controller_path_dir_path = sys.controller_path_dir_path
    controller_object_str = sys.controller_object_str

    T = prop.T

    METHOD = globalopts.opts.METHOD

    plant_abstraction_type = 'cell'
    if METHOD == 'concolic':
        controller_abstraction_type = 'concolic'

        # Initialize concolic engine

        var_type = {}

        # state_arr is not symbolic in concolic exec,
        # with concrete controller states

        var_type['state_arr'] = 'int_arr'
        var_type['x_arr'] = 'int_arr'
        var_type['input_arr'] = 'int_arr'
        concolic_engine = CE.concolic_engine_factory(
            var_type,
            num_dims,
            controller_object_str)

        # sampler = sample.Concolic(concolic_engine)

        sampler = sample.IntervalConcolic(concolic_engine)
    elif METHOD == 'concrete':
        sampler = sample.IntervalSampler()
        controller_abstraction_type = 'concrete'
        controller_sym_path_obj = None

    elif METHOD == 'concrete_no_controller':
        sampler = sample.IntervalSampler()
        controller_abstraction_type = 'concrete_no_controller'
        controller_sym_path_obj = None

        # TODO: manual contruction of paths!!!!
        # use OS independant APIs from fileOps
    elif METHOD == 'symbolic':
        sampler = None
        if globalopts.opts.symbolic_analyzer == 'klee':
            controller_abstraction_type = 'symbolic_klee'
            if globalopts.opts.cntrl_rep == 'smt2':
                controller_path_dir_path += '/klee/'
            else:
                raise err.Fatal('KLEE supports only smt2 files!')
        elif globalopts.opts.symbolic_analyzer == 'pathcrawler':
            controller_abstraction_type = 'symbolic_pathcrawler'
            if globalopts.opts.cntrl_rep == 'smt2':
                controller_path_dir_path += '/pathcrawler/'
            elif globalopts.opts.cntrl_rep == 'trace':
                controller_path_dir_path += '/controller'
            else:
                raise err.Fatal('argparse should have caught this!')

            # TAG:PCH_IND
            # Parse PC Trace
            import CSymLoader as CSL
            controller_sym_path_obj = CSL.load_sym_obj((globalopts.opts.cntrl_rep, globalopts.opts.trace_struct), controller_path_dir_path)
        else:
            raise err.Fatal('unknown symbolic analyzer requested:{}'.format(globalopts.opts.symbolic_analyzer))

    else:
        raise NotImplementedError

    # TODO: parameters like controller_sym_path_obj are absraction dependant
    # and should not be passed directly to abstraction_factory. Instead a
    # flexible structure should be created which can be filled by the
    # CAsymbolic abstraction module and supplied as a substructure. I guess the
    # idea is that an abstraction module should be 'pluggable'.
    current_abs = abstraction.abstraction_factory(
        plant_config_dict,
        prop.ROI,
        T,
        num_dims,
        controller_sym_path_obj,
        sys.min_smt_sample_dist,
        plant_abstraction_type,
        controller_abstraction_type,
        globalopts.opts.graph_lib,
        )
    return current_abs, sampler


def main():

    globalopts.opts = cmdline.parse()
    params = AbsParams(eps=1.0)

    trace_gen = T.get_simdump_gen(globalopts.opts.sys_path)
    traces = list(trace_gen)
    G = build_graph(params, traces)
    analyze_graph(params, G, traces)

    print('num nodes: {}'.format(G.num_nodes()))
    print('num edges: {}'.format(G.num_edges()))


#######################################################################
# GLobals: is there a better way to do this?

TIME_STR = fops.time_string()
logger = setup_output.setup_logger(TIME_STR)
AbsParams = collections.namedtuple('AbsParams', ('eps'))
term = blessed.Terminal()

if __name__ == '__main__':
    main()
