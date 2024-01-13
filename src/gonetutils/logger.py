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

import os
import csv
import math
import logging
import datetime


# ---------------------
# Thrid-party libraries
# ---------------------

import numpy as np

# ------------------------
# Own modules and packages
# ------------------------

from ._version import __version__
from .util.cli import execute
from .util.validators import vfile, vfloat01, valid_channels
from .util.rawimage import RawImage

# ---------
# Constants
# ---------

FILTER = {'R': 'OG570', 'B': 'BG38', 'I': 'RG830', 'C': 'Clear'}

log = logging.getLogger(__name__)

TSTAMP_FORMAT ="%Y-%m-%dT%H:%M:%S"

 
class CSV:

    KEYS = ('timestamp', 'wavelength [nm]', 'filter', 'exposure [ms]', 'aver[R]', 'aver[G1]', 'aver[G2]', 'aver[B]', 
        'stdev[R]', 'stdev[G1]', 'stdev[G2]', 'stdev[B]')

    def __init__(self, path):
        self._path = path
        if not os.path.exists(path):
            self._header()

    def _header(self):
        with open(self._path, 'w',newline='') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=self.KEYS)
            writer.writeheader()

    def append(self, tstamp, wavelength, filter_key, exposure, aver_dict, stdev_dict):
        row = {'timestamp': tstamp, 'wavelength [nm]': wavelength, 'filter': FILTER[filter_key], 'exposure [ms]': exposure,
            'aver[R]': aver_dict['R'], 'aver[G1]': aver_dict['G1'], 'aver[G2]': aver_dict['G1'], 'aver[B]': aver_dict['B'],
            'stdev[R]': stdev_dict['R'], 'stdev[G1]': stdev_dict['G1'], 'stdev[G2]': stdev_dict['G2'], 'stdev[B]': stdev_dict['B'],
            }
        with open(self._path, 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=self.KEYS)
            writer.writerow(row)


# =================
# MAIN ENTRY POINTS
# =================

def logger(args):
    timestamp = datetime.datetime.now().strftime(TSTAMP_FORMAT)
    image = RawImage(args.input_file)
    roi = image.roi(args.x0, args.y0, args.width, args.height)
    csv_file = CSV(args.output_file)
    levels = image.black_levels()
    saturation = image.saturation_levels()
    log.info("Black levels per channel: %s, Saturation levels: %s", levels, saturation)
    aver, std = image.statistics(roi)
    log.info("File %s: %s ROI %s (%dx%d)", os.path.basename(args.input_file), image.dimensions(), roi, roi.width(), roi.height())
    log.info("[%s] [R]=%.1f \u03C3=%.2f, [G1]=%.1f \u03C3=%.2f, [G2]=%.1f \u03C3=%.2f, [B]=%.1f \u03C3 = %.2f", 
        FILTER[args.filter], aver['R'], std['R'], aver['G1'], std['G1'], aver['G2'], std['G2'], aver['B'], std['B'])
    csv_file.append(timestamp, args.wavelength, args.filter, args.exposure, aver, std)



# ===================================
# MAIN ENTRY POINT SPECIFIC ARGUMENTS
# ===================================

def add_args(parser):
    parser.add_argument('-i', '--input-file', type=vfile, required=True, help='Input RAW file')
    parser.add_argument('-o', '--output-file', type=str, required=True, help='Output CSV file')
    parser.add_argument('-x', '--x0', type=vfloat01, default=None, help='Normalized ROI start point, x0 coordinate [0..1]')
    parser.add_argument('-y', '--y0', type=vfloat01, default=None, help='Normalized ROI start point, y0 coordinate [0..1]')
    parser.add_argument('-wi', '--width',  type=vfloat01, default=1.0, help='Normalized ROI width [0..1]')
    parser.add_argument('-he', '--height', type=vfloat01, default=1.0, help='Normalized ROI height [0..1]')
    parser.add_argument('-w', '--wavelength', type=int, required=True, help='Wavelength [nm]')
    parser.add_argument('-f', '--filter', choices=('B','O','R','C'), required=True, help='Filter (BG38|OG570|RG830|Clear)')
    parser.add_argument('-e', '--exposure', type=int, required=True, help='Exposure time [ms]')

# ================
# MAIN ENTRY POINT
# ================

def main():
    execute(main_func=logger, 
        add_args_func=add_args, 
        name=__name__, 
        version=__version__,
        description ="Log per-channel image statistics to a CSV file"
        )