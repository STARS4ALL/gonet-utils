# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) 2021
#
# See the LICENSE file for details
# see the AUTHORS file for authors
# ----------------------------------------------------------------------

#--------------------
# System wide imports
# -------------------

import math
import logging
import functools

# ---------------------
# Thrid-party libraries
# ---------------------

import numpy as np

# ------------------------
# Own modules and packages
# ------------------------

from ._version import __version__
from .util.cli import execute
from .util.validators import vfloat
from .util.rawimage import RawImage

# ---------
# Constants
# ---------

log = logging.getLogger(__name__)

# =================
# MAIN ENTRY POINTS
# =================

def stops_plan(ti, tf, max_adu, ppl, reverse):
    stops = int(round(math.log2(max_adu),0))
    T = list()
    log.info("STOPS = %d",stops)
    if reverse:
        nti = ti; ntf = ti + (tf-ti)/2
        for level in range(0, stops):
            tseq = np.linspace(nti, ntf, num=ppl)
            nti = ntf
            ntf = nti + (tf - nti)/2
            if level == 0:
                T.extend(tseq.tolist())
            else:
                # Discard the first point, as it was repeated with the previous iteration
                T.extend(tseq.tolist()[1:]) 
    else:
        ntf = tf; nti = tf - (tf-ti)/2
        for level in range(0, stops):
            tseq = np.linspace(nti, ntf, num=ppl)
            ntf = nti
            nti = ntf - (ntf-ti)/2
            if level == 0:
                T.extend(tseq.tolist())
            else:
                # Discard the last point, as it was repeated with the previous iteration
                T.extend(tseq.tolist()[:-1]) 
    log.info("Exposure time plan contains %d different exposures", len(T))
    return T

def linear_plan(ti, tf, n, endpoint):
    T = np.linspace(ti, tf, num=n, endpoint=endpoint).tolist()
    log.info("Linear exposure time plan contains %d different exposures", len(T))
    return T

def log_plan(ti, tf, n, reverse, endpoint):
    #T = ((tf-ti)*(1-np.logspace(math.log2(ti), math.log2(tf),  num=n, base=2))).tolist()
    #T = np.geomspace(ti, tf,  num=n).tolist()
    if not reverse:
        T = np.geomspace(ti, tf,  num=n, endpoint=endpoint).tolist()
    else:
        T =  (ti + tf-np.geomspace(ti, tf,  num=n, endpoint=endpoint)).tolist()
        T.reverse()
    log.info("Log exposure time plan contains %d different exposures", len(T))
    return T

def combi_plan(ti, tf, n, tc0, tc1):
    assert (ti < tc0 < tc1 < tf) , "Time intervals are not ordered"
    T = list()
    T.extend(np.geomspace(ti, tc0,  num=n//3, endpoint=False).tolist())
    T.extend(np.linspace(tc0, tc1, num=n//3, endpoint=False).tolist())
    T3 = (tc1 + tf-np.geomspace(tc1, tf,  num=n//3, endpoint=True)).tolist()
    T3.reverse()
    T.extend(T3)
    return T


def plan(args):
    if args.command == 'linear':
        T = linear_plan(args.t_initial, args.t_final, args.num_images, endpoint=True)
    elif args.command == 'log':
        T = log_plan(args.t_initial, args.t_final, args.num_images, args.reverse, endpoint=True)
    elif args.command == 'combi':
        T = combi_plan(args.t_initial, args.t_final, args.num_images, args.t_cut_0, args.t_cut_1)
    else:
        T = stops_plan(args.t_initial, args.t_final, args.max_adu, args.points_per_level, args.reverse)
    log.info("Sequence of exposures: %s", T)
    for i, t in enumerate(T, start=1):
        print(f"{i:03d}_{int(round(t*1000000,0)):07d}")

# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================

def add_args(parser):

    subparser = parser.add_subparsers(dest='command')

    parser_linear = subparser.add_parser('linear', help='generate linear exposure plan')
    parser_log  = subparser.add_parser('log', help='generate log exposure plan')
    parser_combi  = subparser.add_parser('combi', help='combineation of log + linear exposure plan')
    parser_stops  = subparser.add_parser('stops', help='generate log2 exposure plan based on saturation ADU stops')

    # ------------------------------
    # Arguments for 'linear' command
    # ------------------------------

    parser_linear.add_argument('-ti', '--t-initial', type=vfloat, required=True, help='Initial exposure time [secs]')
    parser_linear.add_argument('-tf', '--t-final', type=vfloat, required=True, help='Final exposure time [secs]')
    parser_linear.add_argument('-n', '--num-images', type=int, required=True, help='Number of images to take')

    # ------------------------------
    # Arguments for 'log' command
    # ------------------------------

    parser_log.add_argument('-ti', '--t-initial', type=vfloat, required=True, help='Initial exposure time [secs]')
    parser_log.add_argument('-tf', '--t-final', type=vfloat, required=True, help='Final exposure time [secs]')
    parser_log.add_argument('-n', '--num-images', type=int, required=True, help='Number of images to take')
    parser_log.add_argument('-r','--reverse',  action='store_true', help='reverse point distribution')

    # ------------------------------
    # Arguments for 'combi' command
    # ------------------------------

    parser_combi.add_argument('-ti', '--t-initial', type=vfloat, required=True, help='Initial exposure time [secs]')
    parser_combi.add_argument('-tf', '--t-final', type=vfloat, required=True, help='Final exposure time [secs]')
    parser_combi.add_argument('-tc0', '--t-cut-0', type=vfloat, required=True, help='Boundary between lower log & linear [secs]')
    parser_combi.add_argument('-tc1', '--t-cut-1', type=vfloat, required=True, help='Boundary between linear and upper log [secs]')
    parser_combi.add_argument('-n', '--num-images', type=int, required=True, help='Number of images to take')

    # ------------------------------
    # Arguments for 'stops' command
    # ------------------------------

    parser_stops.add_argument('-ti', '--t-initial', type=vfloat, required=True, help='Initial exposure time [secs]')
    parser_stops.add_argument('-tf', '--t-final', type=vfloat, required=True, help='Final exposure time [secs]')
    parser_stops.add_argument('-m', '--max-adu',  type=int, required=True, help='Saturation value in image [ADU]')
    parser_stops.add_argument('-ppl', '--points-per-level',  type=int, default=5, help='Number of images per level')
    parser_stops.add_argument('-r','--reverse',  action='store_true', help='reverse point distribution')


# ================
# MAIN ENTRY POINT
# ================

def main():
    execute(main_func=plan, 
        add_args_func=add_args, 
        name=__name__, 
        version=__version__,
        description ="Exposure plan for SNR study"
        )