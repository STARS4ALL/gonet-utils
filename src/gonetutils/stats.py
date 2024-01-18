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
from .util.validators import vfile, vfloat01
from .util.rawimage import RawImage

# ---------
# Constants
# ---------

log = logging.getLogger(__name__)

# =================
# MAIN ENTRY POINTS
# =================

def stats(args):
    image = RawImage(args.input_file)
    roi = image.roi(args.x0, args.y0, args.width, args.height)
    stats = image.statistics(roi)
    aver = dict()
    std = dict()
    for i , ch in enumerate(image.CHANNELS):
        aver[ch] = stats[i][0]
        std[ch]  = stats[i][1]
    log.info("ROI %s (%dx%d)", roi, roi.width(), roi.height())
    log.info("[R]=%.1f \u03C3=%.2f, [G1]=%.1f \u03C3=%.2f, [G2]=%.1f \u03C3=%.2f, [B]=%.1f \u03C3 = %.2f", 
        aver['R'], std['R'], aver['G1'], std['G1'], aver['G2'], std['G2'], aver['B'], std['B'])

# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================

def add_args(parser):
    parser.add_argument('-i', '--input-file', type=vfile, required=True, help='Input RAW file')
    parser.add_argument('-x', '--x0', type=vfloat01, default=None, help='Normalized ROI start point, x0 coordinate [0..1]')
    parser.add_argument('-y', '--y0', type=vfloat01, default=None, help='Normalized ROI start point, y0 coordinate [0..1]')
    parser.add_argument('-wi', '--width',  type=vfloat01, default=1.0, help='Normalized ROI width [0..1]')
    parser.add_argument('-he', '--height', type=vfloat01, default=1.0, help='Normalized ROI height [0..1]')
    
# MAIN ENTRY POINT
# ================

def main():
    execute(main_func=stats, 
        add_args_func=add_args, 
        name=__name__, 
        version=__version__,
        description ="Basic image statistics for exposure time optimization"
        )