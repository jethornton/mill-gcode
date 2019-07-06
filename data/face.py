#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from decimal import *

class face:

  def __init__(self):
    if sys.platform.startswith('linux'):
      self.path = os.path.dirname(os.path.realpath(__file__)) + '/'
    elif sys.platform.startswith('win'):
      print os.getcwd()

  def get_gcode(self, info):
    '''
    Spiral in at step till in the center.

    info['method'] = 'spiral' or 'zigzag'
    info['preamble']
    info['tool'] NaN = No Tool
    info['diameter']
    info['rpm'] NaN = No Spindle Control
    info['step'] NaN = Use 75% of Diameter
    info['coolant'] NaN = No Coolant
    info['feed']
    info['doc'] NaN = Use Z Depth
    info['safe-z']
    info['z-top']
    info['z-depth']
    info['z-final']
    info['x-length']
    info['y-length']
    info['reference'
    info['x-ref']
    info['y-ref']
    info['x-start'] NaN = Use 1/2 of diameter
    info['y-start'] NaN = Use step
    '''

    # convert strings to decimals for calculations
    self.diameter = Decimal(info['diameter'])
    if info['step'] == 'NaN':
      self.step = self.diameter * Decimal('0.75')
    else:
      self.step = self.diameter * (Decimal(info['step']) * Decimal('0.01'))

    # if final z and no doc then subtract final z from depth
    if info['z-final'] <> 'NaN':
      self.z_final = Decimal(info['z-final'])
      self.z_final_step = True
      if info['doc']<> 'NaN':
        self.doc = Decimal(info['doc'])
      else:
        self.doc = Decimal(info['z-depth']) - self.z_final
    else:
      self.z_final = 'NaN'
      self.z_final_step = False
      if info['doc']<> 'NaN':
       self.doc = Decimal(info['doc'])
      else:
        self.doc = Decimal(info['z-depth'])

    self.z_top = Decimal(info['z-top'])
    self.z_depth = Decimal(info['z-depth'])
    if self.doc < self.z_depth:
      if self.z_final_step:
        self.cuts = ((self.z_depth - self.z_final) / self.doc).to_integral_exact(rounding=ROUND_CEILING)
        self.doc = ((self.z_depth - self.z_final) / self.cuts).quantize(Decimal('0.00000'))
        self.cuts = self.cuts + 1
      else:
        self.cuts = (self.z_depth / self.doc).to_integral_exact(rounding=ROUND_CEILING)
        self.doc = (self.z_depth / self.cuts).quantize(Decimal('0.00000'))
    else:
      self.cuts = Decimal('1')
      self.doc = self.z_depth

    self.x_length = Decimal(info['x-length'])
    self.y_length = Decimal(info['y-length'])
    self.x_ref = Decimal(info['x-ref'])
    self.y_ref = Decimal(info['y-ref'])
    if info['x-start'] == 'NaN':
      self.x_home = self.x_ref - self.diameter/2
    else:
      self.x_home = Decimal(info['x-start'])
    if info['y-start'] == 'NaN':
      self.y_home = self.y_ref - self.step
    else:
      self.y_home = Decimal(info['y-start'])
    # round up the steps to ceiling
    self.x_steps = (self.x_length / self.step).to_integral_exact(rounding=ROUND_CEILING)
    self.y_steps = (self.y_length / self.step).to_integral_exact(rounding=ROUND_CEILING)

    # get the step size and number of steps
    if self.x_steps > self.y_steps:
      self.steps = self.y_steps - 1
    if self.y_steps > self.x_steps:
      self.steps = self.x_steps - 1
    if self.y_steps == self.x_steps:
      self.steps = self.x_steps - 1

    if info['method'] == 'zigzag':self.steps = (self.steps / 2).to_integral_exact(rounding=ROUND_CEILING)

    self.gcode = []
    if info['method'] == 'spiral':
      self.gcode.append(';Facing Spiral In Path\n')
    if info['method'] == 'zigzag':
      self.gcode.append(';Facing Zig Zag Path\n')
    self.gcode.append(';Material Size = X' + info['x-length'] + ' Y' + info['y-length'] + '\n')
    if self.x_home == 0:
      self.x_home = -(self.diameter/2)
    self.gcode.append(';Start Position X' + str(self.x_home) + ' Y' + str(self.y_home) + '\n')
    self.gcode.append(info['preamble'] + '\n')
    self.gcode.append('F' + info['feed'] + '\n')

    # load tool if any
    if info['tool'] <> 'NaN':
      self.gcode.append('T' + info['tool'] + ' M6 G43\n')

    # start spindle and coolant
    if info['rpm'] <> 'NaN':self.gcode.append('M3 S' + info['rpm'] + '\n')
    if info['coolant'] == True:self.gcode.append('M7\n')

    self.current_z = self.doc
    for i in range(self.cuts):
      if i == self.cuts - 1:self.current_z = self.z_depth
      # go to start position
      self.gcode.append('G0 Z' + info['safe-z'] + '\n')
      self.gcode.append('G0 X' + str(self.x_home) + ' Y' + str(self.y_home) + '\n')
      # spindle on
      self.gcode.append('G1 Z-' + str(self.current_z) + '\n')

      # get path
      if info['method'] == 'spiral':
        self.gcode.extend(self.spiral_path(self.x_ref, self.y_ref, self.x_length, self.y_length , self.step, self.steps))
      if info['method'] == 'zigzag':
        self.gcode.extend(self.zigzag_path(self.x_ref, self.y_ref, self.x_length, self.y_length , self.step, self.steps))

      self.current_z = self.doc + self.current_z

    # turn off spindle and coolant
    if info['rpm'] <> 'NaN':self.gcode.append('M5\n')
    if info['coolant'] == True:self.gcode.append('M9\n')

    # go back to start position
    self.gcode.append('G0 Z' + info['safe-z'] + '\n')
    self.gcode.append('G0 X' + str(self.x_home) + ' Y' + str(self.y_home) + '\n')

    self.gcode.append('M2')

    return self.gcode

  def spiral_path(self, x_coord, y_coord, x_len, y_len, step, steps):
    self.x_end = (x_len - step).quantize(Decimal('0.0000'))
    self.x_start = (x_coord + step).quantize(Decimal('0.0000'))
    self.y_end = (-y_len + step).quantize(Decimal('0.0000'))
    self.y_start = (-y_coord - step).quantize(Decimal('0.0000'))

    self.path = []
    self.start = False
    self.end = True
    for i in range(steps):
      if self.end:
        if i > 0:
          self.path.append('G1 X' + str(self.x_start) + ' Y' + str(self.y_start) + '\n')
        self.path.append('G1 X' + str(self.x_end) + '\n')
        self.x_end = (self.x_end - step).quantize(Decimal('0.0000'))
        self.path.append('G1 Y' + str(self.y_end) + '\n')
        self.y_end = (self.y_end + step).quantize(Decimal('0.0000'))
      if self.start:
        self.path.append('G1 X' + str(self.x_start) + '\n')
        self.x_start = (self.x_start + step).quantize(Decimal('0.0000'))
        self.path.append('G1 Y' + str(self.y_start) + '\n')
        self.y_start = (self.y_start - step).quantize(Decimal('0.0000'))
      if self.start:
        self.start = False
        self.end = True
      else:
        self.start = True
        self.end = False

    return self.path

  def zigzag_path(self, x_coord, y_coord, x_len, y_len, step, steps):
    self.x_end = (x_len - step).quantize(Decimal('0.0000'))
    self.x_start = (x_coord + step).quantize(Decimal('0.0000'))
    self.y_end = (-y_len + step).quantize(Decimal('0.0000'))
    self.y_start = (-y_coord - step).quantize(Decimal('0.0000'))

    self.path = []
    for i in range(steps):
      self.path.append('; 1\n')
      self.path.append('G1 X' + str(self.x_end) + '\n')
      self.y_start = (self.y_start - step).quantize(Decimal('0.00000'))
      self.path.append('; 2\n')
      self.path.append('G1 Y' + str(self.y_start) + '\n')
      self.path.append('; 3\n')
      self.path.append('G1 X' + str(self.x_start) + '\n')
      self.y_start = (self.y_start - step).quantize(Decimal('0.00000'))
      self.path.append('; 4\n')
      if i < (self.steps - 1):
        self.path.append('G1 Y' + str(self.y_start) + '\n')
    return self.path
