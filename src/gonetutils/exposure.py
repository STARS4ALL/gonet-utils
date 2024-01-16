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
def greater_or_equal(t0, t):
    return t >= t0

def log_adu_plan(t0, t1, max_adu, ppl):
    stops = int(round(math.log2(max_adu),0))
    T = list()
    log.info("STOPS = %d",stops)
    for level in range(0, stops+1):
        tseq = np.linspace(t1/(2**(level+1)), t1/(2**level), num=ppl)
        if level == 0:
            T.extend(tseq.tolist())
        else:
            # Discard the last point, as it was repeated with the previous iteration
            T.extend(tseq.tolist()[:-1]) 
    greater_or_equal_t0 = functools.partial(greater_or_equal, t0)
    log.info("Exposure time bag contains %d different exposures", len(T))
    T = list(filter(greater_or_equal_t0, T))
    log.info("After t0 filtering, only %d different exposures", len(T))
    log.info(T)
    return T

def linear_plan(t0, t1, n):
    T = np.linspace(t0, t1, num=n)
    return T

def exposure(args):
    if args.command == 'linear':
        T = linear_plan(args.t0, args.t1, args.num_images)
    else:
        T = log_adu_plan(args.t0, args.t1, args.max_adu, args.points_per_level)
    for i, t in enumerate(T, start=1):
        print(f"{i:03d}_{int(t*1000000):07d}")

# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================

def add_args(parser):
    subparser = parser.add_subparsers(dest='command')

    parser_linear = subparser.add_parser('linear', help='generate linear exposure plan')
    parser_stops  = subparser.add_parser('stops', help='generate log2 exposure plan based on saturation ADU stops')

    # ------------------------------
    # Arguments for 'linear' command
    # ------------------------------

    parser_linear.add_argument('-t0', '--t0', type=vfloat, required=True, help='Minimun exposure time [secs]')
    parser_linear.add_argument('-t1', '--t1', type=vfloat, required=True, help='Maximun exposure time [secs]')
    parser_linear.add_argument('-n', '--num-images', type=int, required=True, help='Number of images to take')

    # -----------------------------
    # Arguments for 'stops' command
    # -----------------------------

    parser_stops.add_argument('-t0', '--t0', type=vfloat, required=True, help='Minimun exposure time [secs]')
    parser_stops.add_argument('-t1', '--t1', type=vfloat, required=True, help='Minimun exposure time [secs]')
    parser_stops.add_argument('-m', '--max-adu',  type=int, required=True, help='Saturation value in image [ADU]')
    parser_stops.add_argument('-ppl', '--points-per-level',  type=int, default=5, help='Number of images per stop level')
  
# MAIN ENTRY POINT
# ================

def main():
    execute(main_func=exposure, 
        add_args_func=add_args, 
        name=__name__, 
        version=__version__,
        description ="Exposure plan for SNR study"
        )