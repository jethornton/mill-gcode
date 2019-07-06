#!/usr/bin/env python
# -*- coding: utf-8 -*-
version = '1.7.7'

# Copyright John Thornton 2014

import os, sys

if sys.platform.startswith('linux'):
  current_path = os.path.dirname(os.path.realpath(__file__)) + '/'
  sys.path.append(current_path + '/data')
elif sys.platform.startswith('win'):
  print os.getcwd()
  print 'windoze'

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

try:
  import pygtk
  pygtk.require('2.0')
except:
  pass
try:
  import gtk
except:
  print('GTK not available')
  sys.exit(1)

import database as db
import face as face
import pocket as pocket
import files as files
import math
from decimal import *
import pango
import ConfigParser
import webbrowser

class mill:
  def __init__(self):
    self.builder = gtk.Builder()
    self.builder.add_from_file(current_path + "data/mill.glade")
    self.builder.connect_signals(self)
    self.aboutdialog = self.builder.get_object("aboutdialog")
    self.aboutdialog.set_version(version)
    self.message_dialog = self.builder.get_object("messagedialog")
    self.clipboard = gtk.clipboard_get()

    self.db = db.database()
    self.face = face.face()
    self.pocket = pocket.pocket()
    self.save = files.save()
    self.open = files.open()

    # debugging
    self.in_axis = self.builder.get_object('in_axis')
    self.in_axis.set_text('In Axis = ' + str(IN_AXIS))

    # setup prefrences page
    self.cp = ConfigParser.ConfigParser()
    self.cfgfile = current_path + 'data/mill.ini'
    self.cp.read(self.cfgfile)

    self.drill_point_preference = self.builder.get_object('drill_point_preference')
    self.drill_point_preference.set_text(self.cp.get('Tools','drill_point'))

    self.spot_point_preference = self.builder.get_object('spot_point_preference')
    self.spot_point_preference.set_text(self.cp.get('Tools','spot_point'))

    self.inch = self.builder.get_object('inch_preference')
    self.metric = self.builder.get_object('metric_preference')
    if self.cp.get('Measure', 'units') == 'Inch':
      self.inch.set_active(True)
      self.units = ' "'
    elif self.cp.get('Measure', 'units') == 'Metric':
      self.metric.set_active(True)
      self.units = ' mm'
    self.min_spindle_rpm =self.builder.get_object('min_spindle_rpm')
    self.max_spindle_rpm = self.builder.get_object('max_spindle_rpm')
    self.preamble = self.builder.get_object('preamble')

    self.precision_preference = self.builder.get_object('precision_preference')
    self.precision_preference.set_text(self.cp.get('Measure', 'precision'))
    self.precision = int(self.precision_preference.get_text())
    self.max_spindle_rpm = self.builder.get_object('max_spindle_rpm')
    self.max_spindle_rpm.set_text(self.cp.get('Machine', 'max_spindle_rpm'))
    self.min_spindle_rpm = self.builder.get_object('min_spindle_rpm')
    self.min_spindle_rpm.set_text(self.cp.get('Machine', 'min_spindle_rpm'))
    self.preamble = self.builder.get_object('preamble')
    self.preamble.set_text(self.cp.get('Machine', 'preamble'))
    self.return_x = self.builder.get_object('return_x')
    self.return_x.set_text(self.cp.get('Presets', 'return_x'))
    self.return_y = self.builder.get_object('return_y')
    self.return_y.set_text(self.cp.get('Presets', 'return_y'))
    self.return_z = self.builder.get_object('return_z')
    self.return_z.set_text(self.cp.get('Presets', 'return_z'))

    # setup hole ops
    # setup tapping page
    self.tap_formlist = gtk.ListStore(str)
    self.tap_formlist.append(["Select a Form"])
    self.tap_itemlist = self.db.tap_forms()
    for i in self.tap_itemlist:
      self.tap_formlist.append([i["form"]])
    self.tap_form_combo = self.builder.get_object("tap_form_combo")
    self.tap_form_combo.set_model(self.tap_formlist)
    self.tap_form_cell = gtk.CellRendererText()
    self.tap_form_combo.pack_start(self.tap_form_cell)
    self.tap_form_combo.add_attribute(self.tap_form_cell, 'text', 0)
    self.tap_form_combo.set_active(0)
    self.tap_form = ''

    self.tap_size_list = gtk.ListStore(str)
    self.tap_size_combo = self.builder.get_object("tap_size_combo")
    self.tap_size_combo.set_model(self.tap_size_list)
    self.tap_size_cell = gtk.CellRendererText()
    self.tap_size_combo.pack_start(self.tap_size_cell)
    self.tap_size_combo.add_attribute(self.tap_size_cell, 'text', 0)
    self.tap_size = ''

    self.tap_drill_diameter_info = self.builder.get_object("tap_drill_diameter_info")
    self.tap_enable = False
    self.tap_coolant = False
    self.tap_depth = self.builder.get_object('tap_depth')
    self.tap_rpm = self.builder.get_object('tap_rpm')
    self.tap_tool_number = self.builder.get_object('tap_tool_number')

    # setup the drilling page
    self.spot_enable = False
    self.spot_coolant = False
    self.spot_tool_number = self.builder.get_object('spot_tool_number')
    self.spot_angle = self.builder.get_object('spot_angle')
    self.spot_angle.set_text(self.spot_point_preference.get_text())
    self.spot_depth = self.builder.get_object('spot_depth')
    self.spot_diameter = self.builder.get_object('spot_diameter')
    self.spot_rpm = self.builder.get_object('spot_rpm')
    self.spot_feed = self.builder.get_object('spot_feed')

    self.drill_enable = False
    self.drill_coolant = False
    self.drill_tool_number = self.builder.get_object('drill_tool_number')
    self.drill_hole_depth = self.builder.get_object('drill_hole_depth')
    self.drill_diameter = self.builder.get_object('drill_diameter')
    self.drill_point_angle = self.builder.get_object('drill_point_angle')
    self.drill_point_angle.set_text(self.drill_point_preference.get_text())
    self.drill_total_depth = self.builder.get_object('drill_total_depth')
    self.drill_rpm = self.builder.get_object('drill_rpm')
    self.drill_feed = self.builder.get_object('drill_feed')
    self.drill_peck = self.builder.get_object('drill_peck')

    self.ream_enable = False
    self.ream_coolant = False
    self.ream_tool_number = self.builder.get_object('ream_tool_number')
    self.ream_hole_depth = self.builder.get_object('ream_hole_depth')
    self.ream_rpm = self.builder.get_object('ream_rpm')
    self.ream_feed = self.builder.get_object('ream_feed')

    # set up the 2nd Ops page
    self.counterbore_enable = False
    self.counterbore_coolant = False
    self.counterbore_finish = False
    self.counterbore_tool_number = self.builder.get_object('counterbore_tool_number')
    self.counterbore_diameter = self.builder.get_object('counterbore_diameter')
    self.counterbore_tool_diameter = self.builder.get_object('counterbore_tool_diameter')
    self.counterbore_depth = self.builder.get_object('counterbore_depth')
    self.counterbore_rpm = self.builder.get_object('counterbore_rpm')
    self.counterbore_stepover = self.builder.get_object('counterbore_stepover')
    self.counterbore_feed = self.builder.get_object('counterbore_feed')
    self.counterbore_doc = self.builder.get_object('counterbore_doc')
    self.o_word = 100
    self.restart_o_word = True

    self.chamfer_enable = False
    self.chamfer_coolant = False
    self.chamfer_tool_number = self.builder.get_object('chamfer_tool_number')
    self.chamfer_rpm = self.builder.get_object('chamfer_rpm')
    self.chamfer_feed = self.builder.get_object('chamfer_feed')
    self.chamfer_hole_diameter = self.builder.get_object('chamfer_hole_diameter')
    self.chamfer_tip_angle = self.builder.get_object('chamfer_tip_angle')
    self.chamfer_tip_width = self.builder.get_object('chamfer_tip_width')
    self.chamfer_depth = self.builder.get_object('chamfer_depth')

    # setup the XY locations tab
    self.xy_liststore = gtk.ListStore(str, str)
    self.xy_treeview = self.builder.get_object('xy-treeview')
    self.xy_treeview.set_model(self.xy_liststore)

    self.x_column = gtk.TreeViewColumn("X Coordinate")
    self.x_column.set_expand(True)
    self.x_column.set_alignment(0.5)
    self.y_column = gtk.TreeViewColumn("Y Coordinate")
    self.y_column.set_expand(True)
    self.y_column.set_alignment(0.5)

    self.xy_treeview.append_column(self.x_column)
    self.xy_treeview.append_column(self.y_column)

    self.x_cell = gtk.CellRendererText()
    self.x_cell.set_property("editable", True)
    self.x_cell.connect("edited", self.text_edited, self.xy_liststore, 0)
    self.x_cell.set_property("alignment",pango.ALIGN_CENTER)
    self.x_column.pack_start(self.x_cell, False)
    self.x_column.add_attribute(self.x_cell, "text", 0)

    self.y_cell = gtk.CellRendererText()
    self.y_cell.set_property("editable", True)
    self.y_cell.connect("edited", self.text_edited, self.xy_liststore,1)
    self.y_cell.set_alignment(0.5,0)
    self.y_column.pack_start(self.y_cell, False)
    self.y_column.add_attribute(self.y_cell, "text", 1)

    self.x_entry = self.builder.get_object('x-entry')
    self.x_entry.connect('activate', self.goto_y_entry)
    self.y_entry = self.builder.get_object('y-entry')
    self.y_entry.connect('activate', self.addto_xy)

    self.locations = []
    self.xy_list = []

    # setup the setup tab
    self.hole_preamble = True
    self.hole_preamble_cb = self.builder.get_object('hole_preamble_cb')
    self.hole_preamble_cb.set_active(True)
    self.retract_z = self.builder.get_object('retract_z')
    self.retract_z.set_text('0.1')
    self.rapid_z = self.builder.get_object('rapid_z')
    self.rapid_z.set_text('0.5')
    self.hole_return_enable = True
    self.hole_return_enable_cb = self.builder.get_object('hole_return_enable_cb')
    self.hole_return_enable_cb.set_active(True)
    self.hole_eof_enable = True
    self.hole_eof_enable_cb = self.builder.get_object('hole_eof_enable_cb')
    self.hole_eof_enable_cb.set_active(True)

    # setup the Drill Tap G code page
    self.ops_label = self.builder.get_object('ops_label')
    self.gcode_textbuffer = self.builder.get_object('gcode_textbuffer')
    self.drill_copy = self.builder.get_object('drill_copy')
    self.drill_send = self.builder.get_object('drill_send')
    self.hole_save = self.builder.get_object('hole_save')

    # setup the hole ops save tab
    self.save_tap_cb = self.builder.get_object('save_tap_cb')
    self.save_spot_cb = self.builder.get_object('save_spot_cb')
    self.save_drill_cb = self.builder.get_object('save_drill_cb')
    self.save_ream_cb = self.builder.get_object('save_ream_cb')
    self.save_counterbore_cb = self.builder.get_object('save_counterbore_cb')
    self.save_chamfer_cb = self.builder.get_object('save_chamfer_cb')

    # setup the facing page
    self.facing_coolant = False
    self.facing_tool_number = self.builder.get_object('facing_tool_number')
    self.facing_tool_diameter = self.builder.get_object('facing_tool_diameter')
    self.facing_stepover = self.builder.get_object('facing_stepover')
    self.facing_rpm = self.builder.get_object('facing_rpm')
    self.facing_feed = self.builder.get_object('facing_feed')
    self.facing_doc = self.builder.get_object('facing_doc')
    self.facing_doc.set_tooltip_text('Depth of Cut')
    self.facing_z_safe = self.builder.get_object('facing_z_safe')
    self.facing_z_top = self.builder.get_object('facing_z_top')
    self.facing_z_depth = self.builder.get_object('facing_z_depth')
    self.facing_z_final = self.builder.get_object('facing_z_final')
    self.facing_x_length = self.builder.get_object('facing_x_length')
    self.facing_y_length = self.builder.get_object('facing_y_length')
    self.facing_x_reference = self.builder.get_object('facing_x_reference')
    self.facing_x_reference.set_text('0')
    self.facing_y_reference = self.builder.get_object('facing_y_reference')
    self.facing_y_reference.set_text('0')
    self.facing_x_start = self.builder.get_object('facing_x_start')
    self.facing_y_start = self.builder.get_object('facing_y_start')
    self.facing_reference_point = '1'
    self.facing_spiral_in = True
    self.facing_zig_zag = False

    # set some presets 
    self.facing_z_top.set_text('0.000')
    self.facing_tool_diameter.set_text('1.000')
    if self.inch.get_active():self.facing_z_safe.set_text('0.100')
    if self.metric.get_active():self.facing_z_safe.set_text('2.5')

    # setup the Facing G code tab
    self.facing_textbuffer = self.builder.get_object('facing_textbuffer')
    self.facing_copy = self.builder.get_object('facing_copy')
    self.facing_send = self.builder.get_object('facing_send')
    self.facing_save = self.builder.get_object('facing_save')
    
    # for testing only
    self.facing_feed.set_text('50')
    self.facing_z_depth.set_text('0.250')
    self.facing_x_length.set_text('8')
    self.facing_y_length.set_text('5')

    # setup the Pocket page
    self.pocket_shape = 'retangle'
    self.pocket_path = 'parallel'
    self.pocket_direction = 'cw'
    self.pocket_start = 'center'
    self.pocket_entry = 'ramp'    
    self.pocket_coolant = False
    self.pocket_tool_number = self.builder.get_object('pocket_tool_number')
    self.pocket_tool_diameter = self.builder.get_object('pocket_tool_diameter')
    self.pocket_stepover = self.builder.get_object('pocket_stepover')
    self.pocket_rpm = self.builder.get_object('pocket_rpm')
    self.pocket_feed = self.builder.get_object('pocket_feed')
    self.pocket_doc = self.builder.get_object('pocket_doc')
    self.pocket_doc.set_tooltip_text('Depth of Cut')
    self.pocket_z_safe = self.builder.get_object('pocket_z_safe')
    self.pocket_z_top = self.builder.get_object('pocket_z_top')
    self.pocket_z_depth = self.builder.get_object('pocket_z_depth')
    self.pocket_z_final = self.builder.get_object('pocket_z_final')
    self.pocket_x_length = self.builder.get_object('pocket_x_length')
    self.pocket_y_length = self.builder.get_object('pocket_y_length')
    self.pocket_x_length = self.builder.get_object('pocket_x_length')
    self.pocket_y_length = self.builder.get_object('pocket_y_length')
    self.pocket_x_reference = self.builder.get_object('pocket_x_reference')
    self.pocket_x_reference.set_text('0')
    self.pocket_y_reference = self.builder.get_object('pocket_y_reference')
    self.pocket_y_reference.set_text('0')
    #self.pocket_x_start = self.builder.get_object('pocket_x_start')
    #self.pocket_y_start = self.builder.get_object('pocket_y_start')
    self.pocket_rectangle_hbox = self.builder.get_object('pocket_rectangle_hbox')
    self.pocket_diameter_hbox = self.builder.get_object('pocket_diameter_hbox')
    
    self.pocket_reference = 'center'
    self.pocket_strategy = 'center_out'
    # set some presets
    self.pocket_z_top.set_text('0.000')
    if self.inch.get_active():self.pocket_z_safe.set_text('0.100')
    if self.metric.get_active():self.pocket_z_safe.set_text('2.5')
    # set some presets for testing
    self.pocket_tool_number.set_text('1')
    self.pocket_tool_diameter.set_text('1.250')
    self.pocket_rpm.set_text('1500')
    self.pocket_feed.set_text('20')
    self.pocket_z_depth.set_text('0.25')
    self.pocket_x_length.set_text('6')
    self.pocket_y_length.set_text('4')

    # setup the Pocket G code tab
    self.pocket_textbuffer = self.builder.get_object('pocket_textbuffer')
    self.pocket_copy = self.builder.get_object('pocket_copy')
    self.pocket_send = self.builder.get_object('pocket_send')
    self.pocket_save = self.builder.get_object('pocket_save')


    # setup the calculators page
    self.tool_diameter = self.builder.get_object('tool_diameter')
    self.tool_teeth = self.builder.get_object('tool_teeth')
    self.feed_per_tooth = self.builder.get_object('feed_per_tooth')
    self.ipr_label = self.builder.get_object('ipr_label')
    self.cutting_speed = self.builder.get_object('cutting_speed')
    self.rpm_label = self.builder.get_object('rpm_label')
    self.ipm_label = self.builder.get_object('ipm_label')
    self.drill_diameter_calc = self.builder.get_object('drill_diameter_calc')
    self.drill_sfm = self.builder.get_object('drill_sfm')
    self.drill_ipr = self.builder.get_object('drill_ipr')
    self.drill_rpm_label = self.builder.get_object('drill_rpm_label')
    self.drill_ipm_label = self.builder.get_object('drill_ipm_label')

    # setup the main window
    self.window = self.builder.get_object("window1")
    self.window.set_title("Mill G code Generator")
    self.window.show_all()
    self.pocket_diameter_hbox.hide()

# Tapping Page
  def on_tap_form_combo_changed(self, widget, data=None):
    self.index = widget.get_active()
    if self.index > 0:
      self.model = widget.get_model()
      self.item = [self.model[self.index][0]]
      self.tap_form = self.item
      self.tap_size_list.clear()
      self.itemlist = self.db.tap_size(self.item)
      self.tap_size_list.append(['Select a Size'])
      for i in self.itemlist:
        self.tap_size_list.append([i["size"]])
      self.tap_size_combo.set_active(0)
      self.clear_tap_info()

  def on_tap_size_combo_changed(self, widget, data=None):
    self.index = widget.get_active()
    if self.index > 0:
      self.model = widget.get_model()
      self.item = [self.model[self.index][0]]
      self.tap_size = self.item
      self.tap_info = self.db.tap_info(self.tap_form, self.tap_size)
      for i in self.tap_info:
        self.tpi = i['pitch']
        if self.tap_form[0] == 'ISO':
          self.tap_pitch = str(round(self.tpi * 0.03937, self.precision))
        else:
          self.tap_pitch = str(round(1.0/self.tpi, self.precision))
        self.tap_major_dia = i['major_dia']
        self.tap_drill = i['tap_drill']
        self.clearance_drill_close = i['clearance_drill_close']
        self.clearance_drill_free = i['clearance_drill_free']
      self.builder.get_object("tap_pitch_label").set_text(self.tap_pitch + self.units)
      self.builder.get_object("tap_major_dia").set_text(str(round(self.tap_major_dia,self.precision)) + self.units)
      self.builder.get_object("tap_drill_75").set_text(self.tap_drill)
      self.builder.get_object("clearance_drill_close").set_text(self.clearance_drill_close)
      self.builder.get_object("clearance_drill_free").set_text(self.clearance_drill_free)
      self.tap_drill_info = self.db.drill_info(self.tap_drill)
      self.tap_drill_diameter_info.set_text(str(self.tap_drill_info[0][2]) + self.units)
      self.spot_diameter.set_text(str(self.tap_drill_info[0][2]))
      self.drill_diameter.set_text(str(self.tap_drill_info[0][2]))
      self.close_drill_info = self.db.drill_info(self.clearance_drill_close)
      self.builder.get_object("close_drill_diameter").set_text(str(self.close_drill_info[0][2]) + self.units)
      self.free_drill_info = self.db.drill_info(self.clearance_drill_free)
      self.builder.get_object("free_drill_diameter").set_text(str(self.free_drill_info[0][2]) + self.units)

  def clear_tap_info(self):
    # move the builder to the top and use self.name here
    self.builder.get_object("tap_pitch_label").set_text('')
    self.builder.get_object("tap_major_dia").set_text('')
    self.builder.get_object("tap_drill_75").set_text('')

  def goto_y_entry(self,var):
    self.y_entry.grab_focus()

  def addto_xy(self, var):
    if not self.is_number(self.x_entry.get_text(),'X coordinate '):
      self.x_entry.grab_focus()
      return
    if not self.is_number(self.y_entry.get_text(),'Y coordinate '):
      self.y_entry.grab_focus()
      return
    self.iter = self.xy_liststore.append([self.x_entry.get_text(),self.y_entry.get_text()])
    self.x_entry.set_text('')
    self.y_entry.set_text('')
    self.rebuild_xy_list()
    self.x_entry.grab_focus()

  def rebuild_xy_list(self):
    self.xy_list = []
    for i in range(len(self.xy_liststore)):
      self.iter = self.xy_liststore.get_iter(i)
      self.xy_list.append("X" + self.xy_liststore[self.iter][0] + " Y" + self.xy_liststore[self.iter][1])

  def on_spot_calculate_depth_clicked(self, var):
    if self.is_number(self.spot_diameter.get_text(),'Spot Diameter '):
      self.diameter = float(self.spot_diameter.get_text())
      self.angle = float(self.spot_angle.get_text())
      self.depth = (self.diameter/2)/math.tan(math.radians(self.angle/2))
      self.spot_depth.set_text(str(round(self.depth, self.precision)))

  def on_drill_calculate_depth_clicked(self, var):
    if not self.is_number(self.drill_hole_depth.get_text(),'Tap Hole Depth '):return
    if not self.is_number(self.drill_diameter.get_text(),'Tap Drill Diameter '):return
    if not self.is_number(self.drill_point_angle.get_text(),'Tap Drill Tip Angle '):return
    self.diameter = float(self.drill_diameter.get_text())
    self.angle = float(self.drill_point_angle.get_text())
    self.depth = float(self.drill_hole_depth.get_text())
    self.tip_depth = (self.diameter/2)/math.tan(math.radians(self.angle/2))
    self.drill_total_depth.set_text(str(round(self.tip_depth + self.depth, self.precision)))

  def on_chamfer_calculate_depth_clicked(self, var):
    if not self.is_number(self.chamfer_hole_diameter.get_text(),'Chamfer Hole Diameter '):return
    if not self.is_number(self.chamfer_tip_angle.get_text(),'Chamfer Tip Angle '):return
    if not self.is_number(self.chamfer_tip_width.get_text(),'Chamfer Tip Width '):return
    self.diameter = float(self.chamfer_hole_diameter.get_text())
    self.angle = float(self.chamfer_tip_angle.get_text())
    self.tip_width = float(self.chamfer_tip_width.get_text())
    self.depth = ((self.diameter-self.tip_width)/2)/math.tan(math.radians(self.angle/2))
    self.chamfer_depth.set_text(str(round(self.depth, self.precision)))

  def on_spot_enable_toggled(self, widget):
    self.spot_enable = widget.get_active()
    self.update_ops()

  def on_spot_coolant_toggled(self, widget):
    self.spot_coolant = widget.get_active()

  def on_drill_enable_toggled(self, widget):
    self.drill_enable = widget.get_active()
    self.update_ops()

  def on_drill_coolant_toggled(self, widget):
    self.drill_coolant = widget.get_active()

  def on_ream_enable_toggled(self, widget):
    self.ream_enable = widget.get_active()
    self.update_ops()

  def on_ream_coolant_toggled(self, widget):
    self.ream_coolant = widget.get_active()

  def on_counterbore_enable_toggled(self, widget):
    self.counterbore_enable = widget.get_active()
    self.update_ops()

  def on_counterbore_coolant_toggled(self, widget):
    self.counterbore_coolant = widget.get_active()

  def on_counterbore_finish_cb_toggled(self, widget):
    self.counterbore_finish = widget.get_active()

  def on_chamfer_enable_toggled(self, widget):
    self.chamfer_enable = widget.get_active()
    self.update_ops()

  def on_chamfer_coolant_toggled(self, widget):
    self.chamfer_coolant = widget.get_active()

  def on_tap_enable_toggled(self, widget):
    self.tap_enable = widget.get_active()
    self.update_ops()

  def on_tap_coolant_toggled(self, widget):
    self.tap_coolant = widget.get_active()

  def on_hole_preamble_cb_toggled(self, widget):
    self.hole_preamble = widget.get_active()

  def on_hole_return_enable_cb_toggled(self, widget):
    self.hole_return_enable = widget.get_active()

  def on_hole_eof_enable_cb_toggled(self, widget):
    self.hole_eof_enable = widget.get_active()

  def on_facing_coolant_toggled(self, widget):
    self.facing_coolant = widget.get_active()

  def on_facing_spiral_in_toggled(self, widget):
    self.facing_spiral_in = widget.get_active()

  def on_facing_zig_zag_toggled(self, widget):
    self.facing_zig_zag = widget.get_active()

  # not used I think
  #def on_facing_reference_toggled(self, widget):
    #if widget.get_active():
      #self.facing_reference_point = widget.get_label()

  # Pocket Tab
  def on_pocket_rectangle_rb_toggled(self, widget):
    if widget.get_active():
      self.pocket_diameter_hbox.hide()
      self.pocket_rectangle_hbox.show()
      self.pocket_shape = 'retangle'

  def on_pocket_round_rb_toggled(self, widget):
    if widget.get_active():
      self.pocket_diameter_hbox.show()
      self.pocket_rectangle_hbox.hide()
      self.pocket_shape = 'round'

  def on_pocket_path_rb_toggled(self, widget):
    if widget.get_active():
      self.pocket_path = gtk.Buildable.get_name(widget)[12:]

  def on_pocket_direction_toggled(self, widget):
    if widget.get_active():
      self.pocket_direction = gtk.Buildable.get_name(widget)[17:]

  def on_pocket_start_toggled(self, widget):
    if widget.get_active():
      self.pocket_start = gtk.Buildable.get_name(widget)[13:]

  def on_pocket_entry_toggled(self, widget):
    if widget.get_active():
      self.pocket_entry = gtk.Buildable.get_name(widget)[7:]

  def on_pocket_coolant_toggled(self, widget):
    self.pocket_coolant = widget.get_active()

  def on_pocket_reference_toggled(self, widget):
    if widget.get_active():
      self.pocket_reference = gtk.Buildable.get_name(widget)[7:]


  def update_ops(self):
    self.ops_label.set_text('')
    self.ops_list = []
    self.hole_ops = 0
    if self.spot_enable:
      self.ops_list.append('Spot')
      self.hole_ops += 1
    if self.drill_enable:
      self.ops_list.append('Drill')
      self.hole_ops += 1
    if self.ream_enable:
      self.ops_list.append('Ream')
      self.hole_ops += 1
    if self.chamfer_enable:
      self.ops_list.append('Chamfer')
      self.hole_ops += 1
    if self.tap_enable:
      self.ops_list.append('Tap')
      self.hole_ops += 1
    if self.counterbore_enable:
      self.ops_list.append('Counterbore')
      self.hole_ops += 1
    self.ops_label.set_text('\n'.join(self.ops_list))

  def text_edited(self, widget, path, text, model, column):
      model[path][column] = text
      self.rebuild_xy_list()

  def on_clear_xy_list_clicked(self, var):
    self.xy_liststore.clear()

  def on_delete_row_xy_list_clicked(self, var):
    selection = self.xy_treeview.get_selection()
    result = selection.get_selected()
    if result[1]: #result could be None
      model, iter = result
      model.remove(iter)

  # Drilling and Tapping
  def on_generate_gcode_clicked(self, widget):
    if len(self.xy_list) == 0:
      self.error_msg('Can not Generate G code without XY Coordinates!')
      return
    self.gcode = []
    if self.hole_preamble:
      if len(self.preamble.get_text()) > 0:
        self.gcode.append(self.preamble.get_text() + '\n')
      else:
        self.gcode.append('Warning No Preamble, Machine can start in an unknown state\n')

    if self.spot_enable:
      if not self.is_number(self.spot_depth.get_text(), 'Spot Depth '):return
      if not self.is_number(self.retract_z.get_text(), 'Retract Z '):return
      if not self.is_number(self.rapid_z.get_text(), 'Rapid Z '):return
      #if not self.is_number(self.spot_rpm.get_text(), 'Spot RPM '):return
      if not self.is_number(self.spot_feed.get_text(), 'Spot Feed '):return

      self.gcode.append(';Spot Drill Op ' + self.spot_diameter.get_text() + ' Diameter\n')

      if len(self.spot_tool_number.get_text()) > 0:
        if self.is_number(self.spot_tool_number.get_text(), 'Spot Tool Number '):
          self.gcode.append('T' + self.spot_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      if len(self.spot_rpm.get_text()) > 0:
        if self.is_number(self.spot_rpm.get_text(), 'Spot Spindle RPM '):
          self.gcode.append('M3 S' + self.spot_rpm.get_text() + '\n')
      else:
        self.gcode.append(';No Spindle RPM Used! \n')
      self.gcode.append('F' + self.spot_feed.get_text() + '\n')
      if self.spot_coolant: self.gcode.append('M8 \n')
      self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
      self.gcode.append('G0 ' + self.xy_list[0] + '\n')
      self.gcode.append('G81 '+self.xy_list[0]+' Z-'+self.spot_depth.get_text() \
        +' R'+self.retract_z.get_text() + '\n')
      if len(self.xy_list) > 1:
        self.xy_modified = self.xy_list[1:]
        for item in self.xy_modified:
          self.gcode.append(item + '\n')
      self.gcode.append('G80 M5 M9\n')

    if self.drill_enable:
      if not self.is_number(self.drill_total_depth.get_text(), 'Drill Depth '):return
      if not self.is_number(self.retract_z.get_text(), 'Retract Z '):return
      if not self.is_number(self.rapid_z.get_text(), 'Rapid Z '):return
      if not self.is_number(self.drill_feed.get_text(), 'Drill Feed '):return

      self.gcode.append(';Drill Op \n')
      if len(self.drill_tool_number.get_text()) > 0:
        if self.is_number(self.drill_tool_number.get_text(), 'Drill Tool Number '):
          self.gcode.append('T' + self.drill_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      if len(self.drill_rpm.get_text()) > 0:
        if self.is_number(self.drill_rpm.get_text(), 'Drill Spindle RPM '):
          self.gcode.append('M3 S' + self.drill_rpm.get_text() + '\n')
      else:
        self.gcode.append(';No Spindle RPM Used! \n')
      self.gcode.append('F' + self.drill_feed.get_text() + '\n')
      if self.drill_coolant: self.gcode.append('M8 \n')
      self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
      self.gcode.append('G0 ' + self.xy_list[0] + '\n')
      if self.drill_peck.get_text() != '':
        if not self.is_number(self.drill_peck.get_text(), 'Peck Depth '):return
        self.drill_cycle = 'G83 '+self.xy_list[0]+' Z'+self.drill_total_depth.get_text() \
        +' R'+self.retract_z.get_text() +' Q'+self.drill_peck.get_text()+'\n'
      else:
        self.drill_cycle = 'G81 '+self.xy_list[0]+' Z-'+self.drill_total_depth.get_text() \
        +' R'+self.retract_z.get_text() + '\n'
      self.gcode.append(self.drill_cycle)
      if len(self.xy_list) > 1:
        self.xy_modified = self.xy_list[1:]
        for item in self.xy_modified:
          self.gcode.append(item + '\n')
      self.gcode.append('G80 M5 M9 \n')

    if self.ream_enable:
      if not self.is_number(self.ream_hole_depth.get_text(), 'Ream Hole Depth '):return
      if not self.is_number(self.ream_feed.get_text(), 'Ream Feed '):return
      self.gcode.append(';Ream Op \n')
      if len(self.ream_tool_number.get_text()) > 0:
        if self.is_number(self.ream_tool_number.get_text(), 'Ream Tool Number '):
          self.gcode.append('T' + self.ream_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      if len(self.ream_rpm.get_text()) > 0:
        if self.is_number(self.ream_rpm.get_text(), 'Ream Spindle RPM '):
          self.gcode.append('M3 S' + self.ream_rpm.get_text() + '\n')
      else:
        self.gcode.append(';No Spindle RPM Used! \n')
      self.gcode.append('F' + self.ream_feed.get_text() + '\n')
      if self.ream_coolant: self.gcode.append('M8 \n')
      self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
      self.gcode.append('G0 ' + self.xy_list[0] + '\n')
      self.gcode.append('G81 '+self.xy_list[0]+' Z-'+self.ream_hole_depth.get_text() \
      +' R'+self.retract_z.get_text() + '\n')

      if len(self.xy_list) > 1:
        self.xy_modified = self.xy_list[1:]
        for item in self.xy_modified:
          self.gcode.append(item + '\n')
      self.gcode.append('G80 M5 M9 \n')

    if self.chamfer_enable:
      if not self.is_number(self.chamfer_depth.get_text(), 'Chamfer Depth '):return
      if not self.is_number(self.chamfer_feed.get_text(), 'Chamfer Feed '):return
      self.gcode.append(';Chamfer Op \n')
      if len(self.chamfer_tool_number.get_text()) > 0:
        if self.is_number(self.chamfer_tool_number.get_text(), 'Chamfer Tool Number '):
          self.gcode.append('T' + self.chamfer_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      if len(self.chamfer_rpm.get_text()) > 0:
        if self.is_number(self.chamfer_rpm.get_text(), 'Chamfer Spindle RPM '):
          self.gcode.append('M3 S' + self.chamfer_rpm.get_text() + '\n')
      else:
        self.gcode.append(';No Spindle RPM Used! \n')
      self.gcode.append('F' + self.chamfer_feed.get_text() + '\n')
      if self.chamfer_coolant: self.gcode.append('M8 \n')
      self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
      self.gcode.append('G0 ' + self.xy_list[0] + '\n')
      self.gcode.append('G81 '+self.xy_list[0]+' Z-'+self.chamfer_depth.get_text() \
      +' R'+self.retract_z.get_text() + '\n')
      if len(self.xy_list) > 1:
        self.xy_modified = self.xy_list[1:]
        for item in self.xy_modified:
          self.gcode.append(item + '\n')
      self.gcode.append('G80 M5 M9 \n')

    if self.tap_enable:
      self.gcode.append(';Tap Op \n')
      if len(self.tap_tool_number.get_text()) > 0:
        if self.is_number(self.tap_tool_number.get_text(), 'Tap Tool Number '):
          self.gcode.append('T' + self.tap_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      self.gcode.append('M3 S' + self.tap_rpm.get_text() + '\n')
      if self.tap_coolant: self.gcode.append('M8 \n')
      self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
      self.gcode.append('G0 ' + self.xy_list[0] + '\n')
      self.gcode.append('G0 Z' + self.retract_z.get_text() + '\n')
      self.gcode.append('G33.1 '+self.xy_list[0]+' Z-'+self.tap_depth.get_text()+' K'+self.tap_pitch+'\n')

      if len(self.xy_list) > 1:
        self.xy_modified = self.xy_list[1:]
        for item in self.xy_modified:
          self.gcode.append('G0 ' + item + '\n')
          self.gcode.append('G33.1 '+ item +' Z-'+self.tap_depth.get_text()+' K'+self.tap_pitch+'\n')
      if self.tap_coolant:self.gcode.append('M9 ')
      self.gcode.append('M5 \n')

    if self.counterbore_enable:
      if not self.is_number(self.counterbore_diameter.get_text(), 'Counterbore Diameter '):return
      self.hole_dia = Decimal(self.counterbore_diameter.get_text())
      if not self.is_number(self.counterbore_depth.get_text(), 'Counterbore Depth '):return
      self.z_depth = -Decimal(self.counterbore_depth.get_text())
      if not self.is_number(self.counterbore_tool_diameter.get_text(), 'Counterbore Tool Diameter '):return
      self.tool_dia = Decimal(self.counterbore_tool_diameter.get_text())
      if not self.is_number(self.counterbore_feed.get_text(), 'Counterbore Feed '):return
      self.tool_dia = Decimal(self.counterbore_tool_diameter.get_text())
      self.path_dia = self.hole_dia - self.tool_dia
      if len(self.counterbore_stepover.get_text()) > 0:
        if self.is_number(self.counterbore_stepover.get_text(), 'Counterbore Step Over % '):
          self.stepover_percent = Decimal(self.counterbore_stepover.get_text())*Decimal('0.01')
          self.stepover = self.tool_dia * self.stepover_percent
      else:
        self.stepover_percent = Decimal('0.50')
        self.stepover = self.tool_dia * self.stepover_percent
      if len(self.counterbore_doc.get_text()) > 0:
        self.z_step = Decimal(self.counterbore_doc.get_text())
      else:
        self.z_step = Decimal(self.counterbore_depth.get_text())
      self.circles = (self.path_dia / self.stepover) - 1
      self.polar_increment = self.stepover / Decimal('100')
      self.offset = Decimal('0.000') + self.stepover
      self.gcode.append(';Counterbore Op \n')
      if len(self.counterbore_tool_number.get_text()) > 0:
        if self.is_number(self.counterbore_tool_number.get_text(), 'Counterbore Tool Number '):
          self.gcode.append('T' + self.counterbore_tool_number.get_text() + ' M6 G43 \n')
      else:
        if self.hole_ops > 1:
          self.error_msg('A tool number must be used with multiple Ops!')
          return
        self.gcode.append(';No Tool Number Used! \n')
      if len(self.counterbore_rpm.get_text()) > 0:
        if self.is_number(self.counterbore_rpm.get_text(), 'Counterbore RPM '):
          self.gcode.append('M3 S' + self.counterbore_rpm.get_text() + '\n')
      else:
        self.gcode.append(';No Spindle Control Used! \n')
      self.gcode.append('F' + self.counterbore_feed.get_text() + '\n')
      if self.restart_o_word:self.o_word = 100
      for item in self.xy_list:
        self.gcode.append('G0 ' + item + '\n')
        self.gcode.append('G0 Z' + self.retract_z.get_text() + '\n')
        self.gcode.append('G92 X0 Y0\n')
        self.repeats = self.circles * 100
        self.z_current = Decimal('0.000')
        while self.z_current > self.z_depth:
          self.z_current -= self.z_step
          self.gcode += 'G1 Z%.4f\n' % self.z_current
          if not self.counterbore_finish:
            self.gcode += 'G1 Y%.4f\n' % self.stepover
            self.gcode += 'o%d repeat [%d]\n' % (self.o_word, self.repeats)
            self.gcode += 'G91 G1 @%.6f ^3.6\n' % self.polar_increment
            self.gcode += 'o%d endrepeat\n' % self.o_word
          else:
            self.gcode += 'G1 Y%.4f\n' % self.path_dia
          self.gcode += 'G3 J-%.4f\n' % self.path_dia
          self.gcode += 'G90\n'
          self.gcode += 'G1 X0 Y0\n'
          self.gcode += '\n'
          self.o_word += 1
        self.gcode.append('G0 Z' + self.rapid_z.get_text() + '\n')
        self.gcode.append('G92.1')
        self.gcode.append('\n')


    if self.hole_return_enable:
      self.gcode.append('G53 G0 Z' + self.return_z.get_text() + '\n')
      self.gcode.append('G0 X' + self.return_x.get_text() + ' Y' + self.return_y.get_text() + '\n')
    if self.hole_eof_enable:
      self.gcode.append('M2')
    else:
      self.restart_o_word = False
    self.gcode_textbuffer.set_text(''.join(self.gcode))
    if IN_AXIS:self.drill_send.set_sensitive(True)
    self.drill_copy.set_sensitive(True)
    self.hole_save.set_sensitive(True)

  def on_button1_clicked(self, widget):
    print self.xy_list
    print self.xy_list[1:]

  def on_drill_copy_clicked(self, widget):
    try:
      self.clipboard.set_text(''.join(self.gcode))
      self.clipboard.store()
    except AttributeError:
      self.error_msg('Nothing to Copy')

  def on_drill_send_clicked(self, widget):
    sys.stdout.write(''.join(self.gcode))
    gtk.main_quit()

  def on_hole_save_clicked(self, widget):
    self.fcd = gtk.FileChooserDialog("Save As...",
               None,
               gtk.FILE_CHOOSER_ACTION_SAVE,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      self.filename = self.fcd.get_filename()
      if not self.filename.endswith('.ngc'):
        fn += '.ngc'
      self.file = open(self.filename, 'w')
      self.file.write(''.join(self.gcode))
      self.file.close()
    self.fcd.destroy()

  # Counterbore
  def on_counterbore_generate_clicked(self, widget):
    pass

  # Facing
  def on_generate_facing_clicked(self, widget):
    # check validity of items that have to be filled in
    if not self.is_number(self.facing_tool_diameter.get_text(), 'Facing Tool Diameter '):return
    if not self.is_number(self.facing_feed.get_text(), 'Facing Feed '):return
    if not self.is_number(self.facing_z_safe.get_text(), 'Facing Safe Z '):return
    if not self.is_number(self.facing_z_top.get_text(), 'Facing Z Top '):return
    if not self.is_number(self.facing_z_depth.get_text(), 'Facing Z Depth '):return
    if not self.is_number(self.facing_x_length.get_text(), 'Facing X Length '):return
    if not self.is_number(self.facing_y_length.get_text(), 'Facing Y Length '):return
    if not self.is_number(self.facing_x_reference.get_text(), 'Facing X Reference '):return
    if not self.is_number(self.facing_y_reference.get_text(), 'Facing Y Reference '):return

    self.facing = []

    # create an empty dictionary
    self.face_info={}

    # add facing info to dictionary
    if self.facing_spiral_in:
      self.face_info['method'] = 'spiral'
    else:
      self.face_info['method'] = 'zigzag'

    if len(self.preamble.get_text()) > 0:
      self.face_info['preamble'] = self.preamble.get_text()
    else:
      self.face_info['preamble'] = 'Warning No Preamble, Machine can start in an unknown state'
    if len(self.facing_tool_number.get_text()) > 0:
      if self.is_number(self.facing_tool_number.get_text(), 'Facing Tool Number '):
        self.face_info['tool'] = self.facing_tool_number.get_text()
    else:
      self.face_info['tool'] = 'NaN'
    self.face_info['diameter'] = self.facing_tool_diameter.get_text()
    if len(self.facing_rpm.get_text()) > 0:
      if self.is_number(self.facing_rpm.get_text(), 'Facing RPM '):
        self.face_info['rpm'] = self.facing_rpm.get_text()
    else:
      self.face_info['rpm'] = 'NaN'
    if len(self.facing_stepover.get_text()) > 0:
      if self.is_number(self.facing_stepover.get_text(), 'Facing Step Over % '):
        self.face_info['step'] = self.facing_stepover.get_text()
    else:
      self.face_info['step'] = 'NaN'
    if self.facing_coolant:
      self.face_info['coolant'] = True
    else:
      self.face_info['coolant'] = False
    self.face_info['feed'] = self.facing_feed.get_text()
    if len(self.facing_doc.get_text()) > 0:
      if not self.is_number(self.facing_doc.get_text(), 'Facing DOC '):return
      self.face_info['doc'] = self.facing_doc.get_text()
    else:
      self.face_info['doc'] = 'NaN'
    self.face_info['safe-z'] = self.facing_z_safe.get_text()
    self.face_info['z-top'] = self.facing_z_top.get_text()
    self.face_info['z-depth'] = self.facing_z_depth.get_text()
    self.face_info['x-length'] = self.facing_x_length.get_text()
    if len(self.facing_z_final.get_text()) > 0:
      if not self.is_number(self.facing_z_final.get_text(), 'Facing Z Final '):return
      self.face_info['z-final'] = self.facing_z_final.get_text()
    else:
      self.face_info['z-final'] = 'NaN'
    self.face_info['y-length'] = self.facing_y_length.get_text()
    self.face_info['reference'] = self.facing_reference_point
    self.face_info['x-ref'] = self.facing_x_reference.get_text()
    self.face_info['y-ref'] = self.facing_y_reference.get_text()
    if len(self.facing_x_start.get_text()) > 0:
      if not self.is_number(self.facing_x_start.get_text(), 'Facing X Start '):return
      self.face_info['x-start'] = self.facing_x_start.get_text()
    else:
      self.face_info['x-start'] = 'NaN'
    if len(self.facing_y_start.get_text()) > 0:
      if not self.is_number(self.facing_y_start.get_text(), 'Facing Y Start '):return
      self.face_info['y-start'] = self.facing_y_start.get_text()
    else:
      self.face_info['y-start'] = 'NaN'

    # call the facing G code generator
    self.facing_code = self.face.get_gcode(self.face_info)
    print self.facing_code
    self.facing_textbuffer.set_text(''.join(self.facing_code))

    # turn on buttons
    self.facing_copy.set_sensitive(True)
    if IN_AXIS:self.facing_send.set_sensitive(True)
    self.facing_save.set_sensitive(True)

  def on_facing_copy_clicked(self, widget):
    try:
      self.clipboard.set_text(''.join(self.facing))
      self.clipboard.store()
    except AttributeError:
      self.error_msg('Nothing to Copy')

  def on_facing_send_clicked(self, widget):
    sys.stdout.write(''.join(self.facing))
    gtk.main_quit()

  def on_facing_save_clicked(self, widget):
    self.fcd = gtk.FileChooserDialog("Save As...",
               None,
               gtk.FILE_CHOOSER_ACTION_SAVE,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      self.filename = self.fcd.get_filename()
      if not self.filename.endswith('.ngc'):
        self.filename += '.ngc'
      self.file = open(self.filename, 'w')
      self.file.write(''.join(self.facing))
      self.file.close()
    self.fcd.destroy()

  # Generate Pocket G code
  def on_generate_pocket_clicked(self, var):
    self.pocket_code = []

    # create an empty dictionary
    self.pocket_info={}

    # add pocket info to dictionary
    self.pocket_info['shape'] = self.pocket_shape
    self.pocket_info['path'] = self.pocket_path
    self.pocket_info['direction'] = self.pocket_direction
    self.pocket_info['start'] = self.pocket_start
    self.pocket_info['entry'] = self.pocket_entry
    self.pocket_info['tool_number'] = self.pocket_tool_number.get_text()
    self.pocket_info['tool_diameter'] = self.pocket_tool_diameter.get_text()
    self.pocket_info['coolant'] = self.pocket_coolant
    self.pocket_info['rpm'] = self.pocket_rpm.get_text()
    if self.pocket_stepover.get_text() == '':
      self.pocket_info['stepover'] = '75'
    else:
      self.pocket_info['stepover'] = self.pocket_stepover.get_text()
    self.pocket_info['feed'] = self.pocket_feed.get_text()
    if self.pocket_doc.get_text() == '':
      self.pocket_info['doc'] = self.pocket_z_depth.get_text()
    else:
      self.pocket_info['doc'] = self.pocket_doc.get_text()
    self.pocket_info['z_safe'] = self.pocket_z_safe.get_text()
    self.pocket_info['z_top'] = self.pocket_z_top.get_text()
    self.pocket_info['z_final'] = self.pocket_z_final.get_text()
    self.pocket_info['z_depth'] = self.pocket_z_depth.get_text()
    self.pocket_info['x_length'] = self.pocket_x_length.get_text()
    self.pocket_info['y_length'] = self.pocket_y_length.get_text()
    self.pocket_info['x_reference'] = self.pocket_x_reference.get_text()
    self.pocket_info['y_reference'] = self.pocket_y_reference.get_text()
    self.pocket_info['reference'] = self.pocket_reference

    # call the pocket G code generator
    self.pocket_code = self.pocket.get_gcode(self.pocket_info)
    self.pocket_textbuffer.set_text(''.join(self.pocket_code))

    # turn on copy to clipboard button
    self.pocket_copy.set_sensitive(True)
    if IN_AXIS:self.pocket_send.set_sensitive(True)
    self.pocket_save.set_sensitive(True)


  # Copy Pocket G code to Clipboard
  def on_pocket_copy_clicked(self, var):
    try:
      self.clipboard.set_text(''.join(self.pocket))
      self.clipboard.store()
    except AttributeError:
      self.error_msg('Nothing to Copy')

  def on_pocket_send_clicked(self, widget):
    sys.stdout.write(''.join(self.pocket))
    gtk.main_quit()

  def on_pocket_save_clicked(self, widget):
    self.fcd = gtk.FileChooserDialog("Save As...",
               None,
               gtk.FILE_CHOOSER_ACTION_SAVE,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      self.filename = self.fcd.get_filename()
      if not self.filename.endswith('.ngc'):
        fn += '.ngc'
      self.file = open(self.filename, 'w')
      self.file.write(''.join(self.pocket))
      self.file.close()
    self.fcd.destroy()

  def is_number(self, s, t):
    try:
      float(s)
      return True
    except ValueError:
      if s == '':
        msg = t + 'is blank!'
      else:
        msg = t + '"' + s + '"' + ' is not a number'
      self.error_msg(msg)
      return False

  def on_save_preferences_clicked(self, var):
    self.cp.set('A Notice', '; Do Not Edit this File!', '')
    if self.inch.get_active():
      self.cp.set('Measure','units', 'Inch')
    elif self.metric.get_active():
      self.cp.set('Measure','units', 'Metric')
    self.cp.set('Measure','precision',self.precision_preference.get_text())
    self.cp.set('Tools','drill_point',self.drill_point_preference.get_text())
    self.cp.set('Tools','spot_point',self.spot_point_preference.get_text())
    self.cp.set('Machine','min_spindle_rpm',self.min_spindle_rpm.get_text())
    self.cp.set('Machine','max_spindle_rpm',self.max_spindle_rpm.get_text())
    self.cp.set('Machine','preamble',self.preamble.get_text())
    self.cp.set('Presets','return_x',self.return_x.get_text())
    self.cp.set('Presets','return_y',self.return_y.get_text())
    self.cp.set('Presets','return_z',self.return_z.get_text())
    with open(self.cfgfile, 'w') as configfile:
      self.cp.write(configfile)

  def save_ops(self, fn):
    if not fn.endswith('.ops'):
      fn += '.ops'
    self.count = 0
    self.save_op = ConfigParser.RawConfigParser()
    if self.save_tap_cb.get_active():
      self.save_op.add_section('Tap')
      self.save_op.set('Tap','tap_form',self.tap_form)
      self.save_op.set('Tap','tap_size',self.tap_size)
      self.save_op.set('Tap','tap_tool_number',self.tap_tool_number.get_text())
      self.save_op.set('Tap','tap_depth',self.tap_depth.get_text())
      self.save_op.set('Tap','tap_rpm',self.tap_rpm.get_text())
      self.count += 1
    if self.save_spot_cb.get_active():
      self.save_op.add_section('Spot')
      self.save_op.set('Spot','spot_tool_number',self.spot_tool_number.get_text())
      self.save_op.set('Spot','spot_rpm',self.spot_rpm.get_text())
      self.save_op.set('Spot','spot_feed',self.spot_feed.get_text())
      self.save_op.set('Spot','spot_diameter',self.spot_diameter.get_text())
      self.save_op.set('Spot','spot_angle',self.spot_angle.get_text())
      self.save_op.set('Spot','spot_depth',self.spot_depth.get_text())
      self.count += 1
    if self.save_drill_cb.get_active():
      self.save_op.add_section('Drill')
      self.save_op.set('Drill','drill_tool_number',self.drill_tool_number.get_text())
      self.save_op.set('Drill','drill_rpm',self.drill_rpm.get_text())
      self.save_op.set('Drill','drill_feed',self.drill_feed.get_text())
      self.save_op.set('Drill','drill_peck',self.drill_peck.get_text())
      self.save_op.set('Drill','drill_hole_depth',self.drill_hole_depth.get_text())
      self.save_op.set('Drill','drill_diameter',self.drill_diameter.get_text())
      self.save_op.set('Drill','drill_point_angle',self.drill_point_angle.get_text())
      self.save_op.set('Drill','drill_total_depth',self.drill_total_depth.get_text())
      self.count += 1
    if self.save_ream_cb.get_active():
      self.save_op.add_section('Ream')
      self.save_op.set('Ream','ream_tool_number',self.ream_tool_number.get_text())
      self.save_op.set('Ream','ream_feed',self.ream_feed.get_text())
      self.save_op.set('Ream','ream_hole_depth',self.ream_hole_depth.get_text())
      self.save_op.set('Ream','ream_rpm',self.ream_rpm.get_text())
      self.count += 1
    if self.save_counterbore_cb.get_active():
      self.save_op.add_section('Counterbore')
      self.save_op.set('Counterbore','counterbore_tool_number',self.counterbore_tool_number.get_text())
      self.save_op.set('Counterbore','counterbore_depth',self.counterbore_depth.get_text())
      self.save_op.set('Counterbore','counterbore_stepover',self.counterbore_stepover.get_text())
      self.save_op.set('Counterbore','counterbore_doc',self.counterbore_doc.get_text())
      self.save_op.set('Counterbore','counterbore_diameter',self.counterbore_diameter.get_text())
      self.save_op.set('Counterbore','counterbore_tool_diameter',self.counterbore_tool_diameter.get_text())
      self.save_op.set('Counterbore','counterbore_rpm',self.counterbore_rpm.get_text())
      self.save_op.set('Counterbore','counterbore_feed',self.counterbore_feed.get_text())
      self.count += 1
    if self.save_chamfer_cb.get_active():
      self.save_op.add_section('Chamfer')
      self.save_op.set('Chamfer','chamfer_tool_number',self.chamfer_tool_number.get_text())
      self.save_op.set('Chamfer','chamfer_rpm',self.chamfer_rpm.get_text())
      self.save_op.set('Chamfer','chamfer_feed',self.chamfer_feed.get_text())
      self.save_op.set('Chamfer','chamfer_hole_diameter',self.chamfer_hole_diameter.get_text())
      self.save_op.set('Chamfer','chamfer_tip_angle',self.chamfer_tip_angle.get_text())
      self.save_op.set('Chamfer','chamfer_tip_width',self.chamfer_tip_width.get_text())
      self.save_op.set('Chamfer','chamfer_depth',self.chamfer_depth.get_text())
      self.count += 1
    if self.count > 0:
      with open(fn, 'w') as configfile:
        self.save_op.write(configfile)
    else:
      self.error_msg('Nothing selected to Save!')

  def restore_ops(self, fn):
    self.restore_op = ConfigParser.ConfigParser()
    self.restore_op.read(fn)
    # add tap here
    if self.restore_op.has_section('Spot'):
      self.spot_tool_number.set_text(self.restore_op.get('Spot','spot_tool_number'))
      self.spot_rpm.set_text(self.restore_op.get('Spot','spot_rpm'))
      self.spot_feed.set_text(self.restore_op.get('Spot','spot_feed'))
      self.spot_diameter.set_text(self.restore_op.get('Spot','spot_diameter'))
      self.spot_angle.set_text(self.restore_op.get('Spot','spot_angle'))
      self.spot_depth.set_text(self.restore_op.get('Spot','spot_depth'))
    if self.restore_op.has_section('Drill'):
      self.drill_tool_number.set_text(self.restore_op.get('Drill','drill_tool_number'))
      self.drill_rpm.set_text(self.restore_op.get('Drill','drill_rpm'))
      self.drill_feed.set_text(self.restore_op.get('Drill','drill_feed'))
      self.drill_peck.set_text(self.restore_op.get('Drill','drill_peck'))
      self.drill_hole_depth.set_text(self.restore_op.get('Drill','drill_hole_depth'))
      self.drill_diameter.set_text(self.restore_op.get('Drill','drill_diameter'))
      self.drill_point_angle.set_text(self.restore_op.get('Drill','drill_point_angle'))
      self.drill_total_depth.set_text(self.restore_op.get('Drill','drill_total_depth'))
    if self.restore_op.has_section('Ream'):
      self.ream_tool_number.set_text(self.restore_op.get('Ream','ream_tool_number'))
      self.ream_feed.set_text(self.restore_op.get('Ream','ream_feed'))
      self.ream_hole_depth.set_text(self.restore_op.get('Ream','ream_hole_depth'))
      self.ream_rpm.set_text(self.restore_op.get('Ream','ream_rpm'))
    if self.restore_op.has_section('Counterbore'):
      self.counterbore_tool_number.set_text(self.restore_op.get('Counterbore','counterbore_tool_number'))
      self.counterbore_depth.set_text(self.restore_op.get('Counterbore','counterbore_depth'))
      self.counterbore_stepover.set_text(self.restore_op.get('Counterbore','counterbore_stepover'))
      self.counterbore_doc.set_text(self.restore_op.get('Counterbore','counterbore_doc'))
      self.counterbore_diameter.set_text(self.restore_op.get('Counterbore','counterbore_diameter'))
      self.counterbore_tool_diameter.set_text(self.restore_op.get('Counterbore','counterbore_tool_diameter'))
      self.counterbore_rpm.set_text(self.restore_op.get('Counterbore','counterbore_rpm'))
      self.counterbore_feed.set_text(self.restore_op.get('Counterbore','counterbore_feed'))
    if self.restore_op.has_section('Chamfer'):
      self.chamfer_tool_number.set_text(self.restore_op.get('Chamfer','chamfer_tool_number'))
      self.chamfer_rpm.set_text(self.restore_op.get('Chamfer','chamfer_rpm'))
      self.chamfer_feed.set_text(self.restore_op.get('Chamfer','chamfer_feed'))
      self.chamfer_hole_diameter.set_text(self.restore_op.get('Chamfer','chamfer_hole_diameter'))
      self.chamfer_tip_angle.set_text(self.restore_op.get('Chamfer','chamfer_tip_angle'))
      self.chamfer_tip_width.set_text(self.restore_op.get('Chamfer','chamfer_tip_width'))
      self.chamfer_depth.set_text(self.restore_op.get('Chamfer','chamfer_depth'))

  def on_window1_destroy(self, object, data=None):
    gtk.main_quit()

  def error_msg(self, msg):
    self.message_dialog.format_secondary_text(msg)
    self.response = self.message_dialog.run()
    self.message_dialog.hide()

  # menu items
  def on_file_open_activate(self, menuitem, data=None):
    self.fcd = gtk.FileChooserDialog("Open...",
               None,
               gtk.FILE_CHOOSER_ACTION_OPEN,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    self.filter = gtk.FileFilter()
    self.filter.set_name("Ops Files")
    self.filter.add_pattern("*.ops")
    self.fcd.add_filter(self.filter)
    self.filter = gtk.FileFilter()
    self.filter.set_name("All Files")
    self.filter.add_pattern("*")
    self.fcd.add_filter(self.filter)
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      self.restore_ops(self.fcd.get_filename())
    self.fcd.destroy()

  def on_file_save_activate(self, menuitem, data=None):
    self.fcd = gtk.FileChooserDialog("Save...",
               None,
               gtk.FILE_CHOOSER_ACTION_SAVE,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      self.save_ops(self.fcd.get_filename())
    self.fcd.destroy()

  def on_file_save_as_activate(self, menuitem, data=None):
    self.fcd = gtk.FileChooserDialog("Save As...",
               None,
               gtk.FILE_CHOOSER_ACTION_SAVE,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
    self.response = self.fcd.run()
    if self.response == gtk.RESPONSE_OK:
      print "Selected filepath: %s" % self.fcd.get_filename()
    self.fcd.destroy()

  def on_file_quit_activate(self, menuitem, data=None):
    gtk.main_quit()

  def on_help_about_activate(self, menuitem, data=None):
    self.response = self.aboutdialog.run()
    self.aboutdialog.hide()

  def on_help_contents_activate(self, menuitem, data=None):
    webbrowser.open_new('file://' + current_path + '/contents/index.html')

  # calculators
  def on_calc_speed_feed_clicked(self, widget):
    if not self.is_number(self.feed_per_tooth.get_text(), 'Feed/Tooth '):return
    if not self.is_number(self.tool_teeth.get_text(), 'Feed/Tooth '):return
    if not self.is_number(self.tool_diameter.get_text(), 'Tool Diameter '):return
    if not self.is_number(self.cutting_speed.get_text(), 'SFM '):return
    self.ipr = float(self.feed_per_tooth.get_text()) * int(self.tool_teeth.get_text())
    self.ipr_label.set_text(str('IPR\n%.3f' % self.ipr))
    self.rpm = (float(self.cutting_speed.get_text()) * 12) / (float(self.tool_diameter.get_text())*math.pi)
    self.rpm_label.set_text('Spindle RPM\n%.0f' % self.rpm)
    self.ipm_label.set_text('Feed IPM\n%.1f' %(self.ipr * self.rpm))

  def on_calc_drill_clicked(self, widget):
    if not self.is_number(self.drill_diameter_calc.get_text(), 'Drill Diameter '):return
    if not self.is_number(self.drill_sfm.get_text(), 'Drill SFM '):return
    if not self.is_number(self.drill_ipr.get_text(), 'Drill IPM '):return
    self.calc_drill_rpm = (float(self.drill_sfm.get_text()) * 12)/(float(self.drill_diameter_calc.get_text())*math.pi)
    self.calc_drill_rpm_label.set_text('Spindle RPM\n%.0f' % self.calc_drill_rpm)
    self.drill_ipm = float(self.drill_ipr.get_text()) * self.calc_drill_rpm
    self.drill_ipm_label.set_text('Drill IPM\n%.1f' % self.drill_ipm)

  def on_entry_activate(self,widget):
    widget.get_toplevel().child_focus(gtk.DIR_TAB_FORWARD)

if __name__ == "__main__":
  main = mill()
  gtk.main()
