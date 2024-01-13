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

def exposure(args):
    exposure_bag = set()
    stops = int(round(math.log2(args.dn_max),0))
    t0 = args.t_min,
    tf = args.t_max
    log.info("STOPS = %d",stops)
    for level in range(0,stops+1):
        tseq = np.linspace(t0, tf/(2**level), num=stops).reshape(-1)
        log.info("tseq shape is %s", tseq.shape)
        for t in tseq:
            exposure_bag.add(t)
    log.info("Exposure bag contains %d different exposures", len(exposure_bag))
    T = sorted(list(exposure_bag))
    if args.time:
        for t in T:
            print(t)
    else:
        for i in range(1,len(T)+1):
            print(f"{i:03d}")



# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================

def add_args(parser):
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--time',  action='store_true', help='display image and section statistics')
    group1.add_argument('--index', action='store_true', help='display image histogram plot')
    parser.add_argument('-t0', '--t_min', type=vfloat, default=0.001, help='Minimun exposure time in seconds')
    parser.add_argument('-tf', '--t_max', type=vfloat, required=True, help='Maximun exposure time in seconds')
    parser.add_argument('-n', '--dn_max', type=int,    required=True, help='Saturation DN value (i.e. 4095)')
  
# MAIN ENTRY POINT
# ================

def main():
    execute(main_func=exposure, 
        add_args_func=add_args, 
        name=__name__, 
        version=__version__,
        description ="Exposure plan for SNR study"
        )