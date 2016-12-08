#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#external deps
import numpy as np
import cytoolz.functoolz as ftz

#core deps
#import logging
import argparse
import collections

# pyutils
from utils import print_function

# internal deps
from plot import plotting
import globalopts
from graphs import graph

Opts = collections.namedtuple('Opts',
                              ('sys_path',
                               'graph_factory',
                               'graph_class',
                               'max_model_error',
                               'plotting',
                               'model_err',
                               'lp_engine',
                               'par',
                               )
                              )


def parse():

    LIST_OF_GRAPH_LIBS = ['nx', 'gt', 'g']
    LIST_OF_PLOT_LIBS = ['mp', 'pg']
    LIST_OF_LP = ['scipy', 'glpk', 'gurobi']

    DEF_LP = 'glpk'
    DEF_GRAPH_LIB = 'nx'

    parser = argparse.ArgumentParser(
            description='S3CAM',
            usage='%(prog)s <filename>',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-f', '--filename', default=None, metavar='file_path.tst')

    parser.add_argument('--seed', type=int, metavar='integer_seed_value',
                        help='seed for the random generator')

    parser.add_argument('--incl-error', action='store_true',
                        help='Include errors in model for bmc')

    parser.add_argument('-g', '--graph-lib', type=str,
                        default=DEF_GRAPH_LIB,
                        choices=LIST_OF_GRAPH_LIBS,
                        help='graph library')

    parser.add_argument('-p', '--plot', type=str, nargs='?',
                        default=None, const='mp',
                        choices=LIST_OF_PLOT_LIBS, help='plot library')

    parser.add_argument('--plots', type=plotting.plot_opts_parse, default='',
                        nargs='+', help='plots x vs y: t-x1 x0-x1')

    # TODO: This error can be computed against the cell sizes?
    parser.add_argument('--max-model-error', type=float, default=float('inf'),
                        help='split cells till model error (over a single step) <= max-error')

    parser.add_argument('--plot-opts', type=str, default=(),
                        nargs='+', help='additional lib specific plotting opts')

    parser.add_argument('--lp-engine', type=str,
                        choices=LIST_OF_LP,
                        default=DEF_LP,
                        help='Choose the LP engine')

    # TODO: fix this hack
    parser.add_argument('--debug', action='store_true',
                        help='Enables debug flag')

    parser.add_argument('--par', action='store_true',
                        help='parallel simulation')

    parser.add_argument('-o', '--output', type=str,
                        default=None,
                        help='output directory')

#    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.filename is None:
        print('Specify test file using -f/--filename <filename>')
        exit()
    else:
        filepath = args.filename

    if args.seed is not None:
        np.random.seed(args.seed)

    # TODO put plot hack as a switch in globalopts
    globalopts.debug = args.debug

    opts = Opts(sys_path = filepath,
                graph_factory = ftz.partial(graph.factory, args.graph_lib),
                graph_class = graph.class_factory(args.graph_lib),
                max_model_error = args.max_model_error,
                plotting = plotting.factory(args.plot, args.plots, *args.plot_opts),
                model_err = args.incl_error,
                lp_engine = args.lp_engine,
                par = args.par)

    #sys, prop = loadsystem.parse(filepath, args.pvt_init_data)

    #opts.construct_path = setup_dir(sys, args.output)

    return opts
