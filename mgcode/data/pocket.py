#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from decimal import *

class pocket:

  def __init__(self):
    if sys.platform.startswith('linux'):
      self.path = os.path.dirname(os.path.realpath(__file__)) + '/'
    elif sys.platform.startswith('win'):
      print os.getcwd()

  def get_gcode(self, info):
    ''' info
    {'feed': '20', 'y_reference': '0', 'direction': 'cw',
    'z_depth': '0.25', 'z_final': '', 'reference': 'center',
    'start': 'center', 'coolant': False, 'z_safe': '0.100',
    'tool_diameter': '1.250', 'x_length': '6', 'tool_number': '1',
    'shape': 'retangle', 'doc': '0.25', 'x_reference': '0',
    'entry': 'ramp', 'stepover': '75', 'path': 'parallel',
    'z_top': '0.000', 'rpm': '1500', 'y_length': '4'}'''

    self.gcode = []
    self.gcode.append(';Pocket\n')
    # load tool if any
    if info['tool_number'] <> '':
      self.gcode.append('T' + info['tool_number'] + ' M6 G43\n')
    if info['rpm'] <> '':
      self.gcode.append('M3 S' + info['rpm'] + '\n')
    if info['coolant'] == True:
      self.gcode.append('M8\n')
    if info['shape'] == 'retangle':
      self.retangle(info)
    if info['shape'] == 'circle':
      self.circle(info)

    if info['coolant'] == True:
      self.gcode.append('M9\n')

    # rapid to home here
    self.gcode.append('G53 G0 Z0\n')
    self.gcode.append('G0 X' + info['x_reference'] + ' Y' + info['y_reference'] + '\n')
    self.gcode.append('M2')
    return self.gcode

  def retangle(self, info = None):
    # find the center of the pocket
    self.gcode.append('; ' + info['start'] + '\n')
    
    self.x_reference = Decimal(info['x_reference'])
    self.y_reference = Decimal(info['y_reference'])
    self.x_length = Decimal(info['x_length'])
    self.y_length = Decimal(info['y_length'])
    self.z_safe = Decimal(info['z_safe'])
    self.feed = Decimal(info['feed'])
    self.z_depth = Decimal(info['z_depth'])
    #self.z_final = Decimal(info['z_final'])
    self.doc = Decimal(info['doc'])
    self.tool_diameter = Decimal(info['tool_diameter'])
    self.stepover = Decimal(info['stepover'])
    self.z_top = Decimal(info['z_top'])
    self.entry = info['entry']
    #self. = Decimal(info[''])
    self.gcode.append('G0 X' + str((self.x_length / 2) + self.x_reference)
        + ' Y' + str((self.y_length / 2) + self.y_reference)+ '\n')

  def circle(self, info = None):
    # find the edge of the pocket
    self.gcode = []
    self.gcode.append(';Edge In\n')
    return self.gcode

