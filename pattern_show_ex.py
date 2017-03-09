# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 15:02:32 2017

@author: Lin
"""

from PyQt4 import QtGui,QtCore
import sys
import pattern_proc
import LCOS_con
import random
import pattern_show_ex

total_lambda = 25
total_port = 4
LCOS_num =1
ch_num = 5

app = QtGui.QApplication(sys.argv)
pDesktop = app.desktop()
screen_dict = {}
for k in range(pDesktop.screenCount()):
	screen_dict[str(k)] = pDesktop.screenGeometry(k)
pattern_size = [0,0]
pattern_size[0] = int(screen_dict[str(LCOS_num)].width()/total_lambda)
pattern_size[1] = int(screen_dict[str(LCOS_num)].height()/total_port)

random.seed()

lcos1 = LCOS_con.LCOS_con(LCOS_num, total_lambda, total_port)
w1 = lcos1.Initialize_LCOS(screen_dict)
a1 = lcos1.Initialize_pattern(w1)

sys.exit(exec(pattern_show_ex.randshow(w1)))

def randshow(w1):
	while type(a1)!=None:
		ch_num = random.randint(0,total_port*total_lambda-1)
		print("Channel # = " + str(ch_num))
		image = pattern_proc.pattern_gen(0,random.randint(20,200),pattern_size).blazgrating()
		lcos1.pattern_show(w1,image,ch_num)
		if lcos1.pattern_show(w1,image,ch_num) ==False:
			print("Fail to change pattern! No such label with THIS NAME")
			break
		image = pattern_proc.pattern_gen(0,random.randint(-200,200),pattern_size).blazgrating()