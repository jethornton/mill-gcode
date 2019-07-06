#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import sqlite3 as lite

class database:

  def __init__(self):
    if sys.platform.startswith('linux'):
      self.path = os.path.dirname(os.path.realpath(__file__)) + '/'
    elif sys.platform.startswith('win'):
      print os.getcwd()
    self.con = lite.connect(self.path + 'sfc.sqlite')

  def thread_forms(self):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT DISTINCT form FROM threads")
      return self.cur.fetchall()

  def thread_size(self, selected):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT DISTINCT size FROM threads WHERE form = ? ORDER BY major_dia ASC", selected)
      return self.cur.fetchall()

  def thread_class(self, selected):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT DISTINCT class FROM threads WHERE size = ? ORDER BY major_dia ASC", selected)
      return self.cur.fetchall()

  def thread_info(self, thread_form, thread_size, thread_class):
    self.items = []
    self.items.append(''.join(thread_form))
    self.items.append(''.join(thread_size))
    self.items.append(''.join(thread_class))
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT * FROM threads WHERE form=? AND size=? AND class=?",self.items)
      return self.cur.fetchall()

  def tap_forms(self):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT DISTINCT form FROM tap")
      return self.cur.fetchall()

  def tap_size(self, selected):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT DISTINCT size FROM tap WHERE form = ? ORDER BY major_dia ASC", selected)
      return self.cur.fetchall()

  def tap_info(self, thread_form, thread_size):
    self.items = []
    self.items.append(''.join(thread_form))
    self.items.append(''.join(thread_size))
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT * FROM tap WHERE form=? AND size=?",self.items)
      return self.cur.fetchall()

  def drill_info(self, drill_size):
    with self.con:
      self.con.row_factory = lite.Row
      self.cur = self.con.cursor()
      self.cur.execute("SELECT * FROM drills WHERE size=?",[drill_size])
      self.result = self.cur.fetchall()
      return self.result

  def drill_list(self, query, itemlist):
      with self.con:
        self.con.row_factory = lite.Row
        self.cur = self.con.cursor()
        self.cur.execute(query,itemlist)
        return self.cur.fetchall()

  def list_append(self,data):
    print data
