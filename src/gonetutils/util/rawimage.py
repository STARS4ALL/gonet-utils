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
import fractions
import logging

# ---------------------
# Thrid-party libraries
# ---------------------

import rawpy
import exifread
import numpy as np

log = logging.getLogger(__name__)

# ----------
# Exceptions
# ----------

class UnsupportedCFAError(ValueError):
    '''Unsupported Color Filter Array type'''
    def __str__(self):
        s = self.__doc__
        if self.args:
            s = ' {0}: {1}'.format(s, str(self.args[0]))
        s = '{0}.'.format(s)
        return s

# ----------------------
# Module utility classes
# ----------------------

class Point:
    """ Point class represents and manipulates x,y coords. """

    PATTERN = r'\((\d+),(\d+)\)'

    @classmethod
    def from_string(cls, point_str):
        pattern = re.compile(Point.PATTERN)
        matchobj = pattern.search(Rect_str)
        if matchobj:
            x = int(matchobj.group(1))
            y = int(matchobj.group(2))
            return cls(x,y)
        else:
            return None

    def __init__(self, x=0, y=0):
        """ Create a new point at the origin """
        self.x = x
        self.y = y

    def __add__(self, rect):
        return NotImplementedError

    def __repr__(self):
        return f"({self.x},{self.y})"

class Rect:
    """ Region of interest """

    PATTERN = r'\[(\d+):(\d+),(\d+):(\d+)\]'

    @classmethod
    def from_string(cls, Rect_str):
        '''numpy sections style'''
        pattern = re.compile(Rect.PATTERN)
        matchobj = pattern.search(Rect_str)
        if matchobj:
            y1 = int(matchobj.group(1))
            y2 = int(matchobj.group(2))
            x1 = int(matchobj.group(3))
            x2 = int(matchobj.group(4))
            return cls(x1,x2,y1,y2)
        else:
            return None

    @classmethod
    def from_normalized(cls, width, height, n_x0=None, n_y0=None, n_width=1.0, n_height=1.0, debayered=True):
        if n_x0 is not None:
            assert n_x0 + n_width <= 1.0, f"normalized x0(={n_x0}) + width(={n_width}) = {n_x0 + n_width} exceeds 1.0"
        if n_y0 is not None:
            assert n_y0 + n_height <= 1.0, f"normalized x0(={n_y0}) + width(={n_height}) = {n_y0 + n_height} exceeds 1.0"
        # If debayered, we'll adjust to each image plane dimensions
        if debayered:
            height = height //2  
            width  = width  //2 
        # From normalized ROI to actual image dimensions ROI
        w = int(width * n_width) 
        h = int(height * n_height)
        x0 = (width  - w)//2 if n_x0 is None else int(width * n_x0)
        y0 = (height - h)//2 if n_y0 is None else int(height * n_y0)
        return cls(x0, x0+w ,y0, y0+h)

    @classmethod
    def from_dict(cls, Rect_dict):
        return cls(Rect_dict['x1'], Rect_dict['x2'],Rect_dict['y1'], Rect_dict['y2'])
    
    def __init__(self, x1 ,x2, y1, y2):        
        self.x1 = min(x1,x2)
        self.y1 = min(y1,y2)
        self.x2 = max(x1,x2)
        self.y2 = max(y1,y2)

    def to_dict(self):
        return {'x1':self.x1, 'y1':self.y1, 'x2':self.x2, 'y2':self.y2}
        
    def xy(self):
        '''To use when displaying Rectangles in matplotlib'''
        return(self.x1, self.y1)

    def width(self):
        return abs(self.x2 - self.x1)

    def height(self):
        return abs(self.y2 - self.y1)
        
    def dimensions(self):
        '''returns width and height'''
        return abs(self.x2 - self.x1), abs(self.y2 - self.y1)

    def __add__(self, point):
        return Rect(self.x1 + point.x, self.x2 + point.x, self.y1 + point.y, self.y2 + point.y)

    def __radd__(self, point):
        return self.__add__(point)
        
    def __repr__(self):
        '''string in NumPy section notation'''
        return f"[{self.y1}:{self.y2},{self.x1}:{self.x2}]"
      

# ----------------
# Auxiliar classes
# ----------------

class RawImage:

    LABELS = (('Red', 'R'), ('Green 1','G1'), ('Green 2', 'G2'), ('Blue', 'B') )
    BAYER_LETTER = ['B','G','R','G']
    BAYER_PTN_LIST = ('RGGB', 'BGGR', 'GRBG', 'GBRG')
    CFA_OFFSETS = {
        # Esto era segun mi entendimiento
        'RGGB' : {'R':{'x': 0,'y': 0}, 'G1':{'x': 1,'y': 0}, 'G2':{'x': 0,'y': 1}, 'B':{'x': 1,'y': 1}}, 
        'BGGR' : {'R':{'x': 1,'y': 1}, 'G1':{'x': 1,'y': 0}, 'G2':{'x': 0,'y': 1}, 'B':{'x': 0,'y': 0}},
        'GRBG' : {'R':{'x': 1,'y': 0}, 'G1':{'x': 0,'y': 0}, 'G2':{'x': 1,'y': 1}, 'B':{'x': 0,'y': 1}},
        'GBRG' : {'R':{'x': 0,'y': 1}, 'G1':{'x': 0,'y': 0}, 'G2':{'x': 1,'y': 1}, 'B':{'x': 1,'y': 0}},
    }

    CHANNELS = ('R', 'G1', 'G2', 'B')

    def __init__(self, path):
        self._path = path
        self._metadata()

    def _metadata(self):
        '''Gather as much rawpy stack access as possible for efficiency'''
        with rawpy.imread(self._path) as stack:
            self._color_desc = stack.color_desc.decode('utf-8')
            self._shape = stack.raw_image.shape
            self._cfa = ''.join([ self.BAYER_LETTER[stack.raw_pattern[row,column]] for row in (1,0) for column in (1,0)])
            self._biases = stack.black_level_per_channel
            self._white_levels = stack.camera_white_level_per_channel


    def exif(self):
        with open(self._path, 'rb') as f:
            exif = exifread.process_file(f, details=False)
        # This ensures that non EXIF images are detected and an exeption is raised
        metadata = dict()
        if not exif:
            raise ValueError('Could not open EXIF metadata')
        metadata['exposure'] = fractions.Fraction(str(exif.get('EXIF ExposureTime', 0)))
        metadata['iso'] = str(exif.get('EXIF ISOSpeedRatings', None))
        metadata['camera'] = str(exif.get('Image Model', None)).strip()
        metadata['focal_length'] = fractions.Fraction(str(exif.get('EXIF FocalLength', 0)))
        metadata['f_number'] = fractions.Fraction(str(exif.get('EXIF FNumber', 0)))
        metadata['datetime'] = str(exif.get('Image DateTime', None))

        return metadata

    def label(self, i):
        return self.LABELS[i]

    def name(self):
        return os.path.basename(self._path)

    def cfa_pattern(self):
        '''Returns the Bayer pattern as RGGB, BGGR, GRBG, GBRG strings '''
        if self._color_desc != 'RGBG':
            raise UnsupporteCFAError(self._color_desc)
        return self._cfa

    def saturation_levels(self):
        return self._white_levels

    def black_levels(self):
        return self._biases

    def shape(self):
        return (self._shape[0]//2,  self._shape[1]//2) # Debayered image total dimensions

    def roi(self, n_x0=None, n_y0=None, n_width=1.0, n_heigth=1.0):
        return Rect.from_normalized(self._shape[1], self._shape[0], n_x0, n_y0, n_width, n_heigth)

    def debayered(self, roi=None, channels=None):
        '''Get a stack of Bayer colour planes selected by the channels sequence'''
        cfa_pattern = self.cfa_pattern()
        with rawpy.imread(self._path) as img:
            raw_pixels_list = list()
            for channel in self.CHANNELS:
                x = self.CFA_OFFSETS[cfa_pattern][channel]['x']
                y = self.CFA_OFFSETS[cfa_pattern][channel]['y']
                raw_pixels = img.raw_image[y::2, x::2].copy() # This is the real debayering thing
                if roi:
                    y1 = roi.y1 ; y2 = roi.y2
                    x1 = roi.x1 ; x2 = roi.x2
                    raw_pixels = raw_pixels[y1:y2, x1:x2]  # Extract ROI
                raw_pixels_list.append(raw_pixels)
        if channels is None:
            custom_list = raw_pixels_list
        else:
            custom_list = list()
            for i, ch in enumerate(channels):
                if ch == 'G':
                    aver_green = (raw_pixels_list[1] + raw_pixels_list[2]) // 2
                    custom_list.append(aver_green)
                else:
                    k = self.CHANNELS.index(ch)
                    custom_list.append(raw_pixels_list[k])
        return np.stack(custom_list)

    def statistics(self, roi=None, channels=None):
        '''In-place statistics calculation for RPi Zero'''
        cfa_pattern = self.cfa_pattern()
        channels = self.CHANNELS if channels is None else channels
        if 'G' in channels:
            raise NotImplementedError(f"In-place statistics on G=(G1+G2)/2 channel not available")
        with rawpy.imread(self._path) as img:
            # very imporatnt to be under the image context manager
            # when doing manipulations on img.raw_image
            average, stdev = dict(), dict()
            for channel in channels:
                x = self.CFA_OFFSETS[cfa_pattern][channel]['x']
                y = self.CFA_OFFSETS[cfa_pattern][channel]['y']
                raw_pixels = img.raw_image[y::2, x::2]
                if roi:
                    y1 = roi.y1 ; y2 = roi.y2
                    x1 = roi.x1 ; x2 = roi.x2
                    raw_pixels = raw_pixels[y1:y2, x1:x2]  # Extract ROI
                average[channel], stdev[channel] = round(raw_pixels.mean(),1), round(raw_pixels.std(),3)
        return average, stdev

