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
import math
import logging

# ---------------------
# Thrid-party libraries
# ---------------------

import rawpy
import exifread

# ------------------------
# Own modules and packages
# ------------------------

from .roi import Rect

# ---------
# Constants
# ---------


log = logging.getLogger(__name__)




class UnsupportedCFAError(ValueError):
    '''Unsupported Color Filter Array type'''
    def __str__(self):
        s = self.__doc__
        if self.args:
            s = ' {0}: {1}'.format(s, str(self.args[0]))
        s = '{0}.'.format(s)
        return s

class BiasError(ValueError):
    '''Value differs much from power of two'''
    def __init__(self, bias, levels, *args):
        self.bias = bias
        self.levels = levels

    def __str__(self):
        s = self.__doc__
        if self.args:
            s = ' {0}: {1} '.format(s, self.args[0], self.levels)
        s = '{0}.'.format(s)
        return s


class NotPowerOfTwoErrorBiasError(BiasError):
    '''Value differs much from a power of two'''
    pass
 

class TooDifferentValuesBiasError(BiasError):
    '''Differences in counts between channels exceed threshold'''
    pass

def nearest_power_of_two(bias):
    if bias == 0:
        return 0, False
    warning = False
    N1 = math.log10(bias)/math.log10(2)
    N2 = int(round(N1,0))
    #log.debug("N1 = {n1}, N2 = {n2}",n1=N1, n2=N2)
    nearest = 2**N2
    if (math.fabs(N1-N2) > 0.012):  # determined empirically for bias=127
        warning = True
    return nearest, warning
 

class Image:

    BAYER_LETTER = ['B','G','R','G']
    BAYER_PTN_LIST = ('RGGB', 'BGGR', 'GRBG', 'GBRG')
    CFA_OFFSETS = {
        # Esto era segun mi entendimiento
        'RGGB' : {'R':{'x': 0,'y': 0}, 'G1':{'x': 1,'y': 0}, 'G2':{'x': 0,'y': 1}, 'B':{'x': 1,'y': 1}}, 
        'BGGR' : {'R':{'x': 1,'y': 1}, 'G1':{'x': 1,'y': 0}, 'G2':{'x': 0,'y': 1}, 'B':{'x': 0,'y': 0}},
        'GRBG' : {'R':{'x': 1,'y': 0}, 'G1':{'x': 0,'y': 0}, 'G2':{'x': 1,'y': 1}, 'B':{'x': 0,'y': 1}},
        'GBRG' : {'R':{'x': 0,'y': 1}, 'G1':{'x': 0,'y': 0}, 'G2':{'x': 1,'y': 1}, 'B':{'x': 1,'y': 0}},
    }

    def __init__(self, path):
        self._path = path
        self._metadata()

    def _metadata(self):
        '''Gather as much rawpy img access as possible for efficiency'''
        with rawpy.imread(self._path) as img:
            self._color_desc = img.color_desc.decode('utf-8')
            self._shape = img.raw_image.shape
            self._cfa = ''.join([ self.BAYER_LETTER[img.raw_pattern[row,column]] for row in (1,0) for column in (1,0)])
            self._biases = img.black_level_per_channel
            self._white_levels = img.camera_white_level_per_channel


    def camera(self):
        with open(self._path, 'rb') as f:
            exif = exifread.process_file(f, details=False)
        # This ensures that non EXIF images are detected and an exeption is raised
        if not exif:
            raise ValueError('Could not open EXIF metadata')
        return str(exif.get('Image Model', None)).strip()


    def cfa_pattern(self):
        '''Returns the Bayer pattern as RGGB, BGGR, GRBG, GBRG strings '''
        if self._color_desc != 'RGBG':
            raise UnsupporteCFAError(self._color_desc)
        return self._cfa


    def bias(self):
        global_bias = min(self._biases)
        if max(self._biases) - global_bias > 4:
            raise TooDifferentValuesBiasError(global_bias, self._biases, 4)
        tuples   = [nearest_power_of_two(bias) for bias in self._biases]
        biases   = [item[0] for item in tuples]
        warnings = [item[1] for item in tuples]
        if any(warnings):
            raise NotPowerOfTwoErrorBiasError(global_bias, self._biases)
        global_bias = biases[0]
        return self._biases, global_bias

    def saturation_levels(self):
        return self._white_levels

    def dimensions(self):
        return self._shape

    def statistics(self, roi):
        '''Debayer and trim all channels for efficiency'''
        cfa_pattern = self.cfa_pattern()
        with rawpy.imread(self._path) as img:
            # very imporatnt to be under the image context manager
            # for all pixel handling incluidng statistics
            average, stdev = dict(), dict()
            for channel in ('R', 'G1', 'G2', 'B'):
                x = self.CFA_OFFSETS[cfa_pattern][channel]['x']
                y = self.CFA_OFFSETS[cfa_pattern][channel]['y']
                raw_pixels = img.raw_image[y::2, x::2] # This is the real debayering thing
                y1 = roi.y1 ; y2 = roi.y2
                x1 = roi.x1 ; x2 = roi.x2
                raw_pixels = raw_pixels[y1:y2, x1:x2]  # Extract ROI
                average[channel], stdev[channel] = round(raw_pixels.mean(),1), round(raw_pixels.std(),3)
        return average, stdev


# =================
# MAIN ENTRY POINTS
# =================

def stats(options):
    roi = Rect.from_image(options.file, width=options.width, height=options.height)
    image = Image(options.file)
    camera = image.camera()
    log.info("Camera model: %s",camera)
    levels, global_bias = image.bias() # Not really used
    saturation = image.saturation_levels()
    log.info("Bias: per channel = %s, global = %d, Saturation levels = %s", levels, global_bias, saturation)
    bayer = image.cfa_pattern()
    aver, std = image.statistics(roi)
    log.info("File %s: %s ROI %s (%dx%d)", os.path.basename(options.file), image.dimensions(), roi, options.width, options.height)
    log.info("[R]=%.1f \u03C3=%.2f, [G1]=%.1f \u03C3=%.2f, [G2]=%.1f \u03C3=%.2f, [B]=%.1f \u03C3 = %.2f", 
        aver['R'], std['R'], aver['G1'], std['G1'], aver['G2'], std['G2'], aver['B'], std['B'])
