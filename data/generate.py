#!/usr/bin/env python

class generate:
  def __init__(self):
    print 'e'

  def gen_ini(self, name):
    self.file = open(name+'.ini', 'w')
    self.file.write('this is a test\n')
    self.file.close()




