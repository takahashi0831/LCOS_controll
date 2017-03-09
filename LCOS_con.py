# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:47:13 2017

@author: Lin
"""

import numpy
from PIL import ImageQt
from PyQt4 import QtGui, QtCore
from collections import OrderedDict
import random
import pattern_proc


class convert_f():
	def test():
		return True
		
def win_search(screen_info):
	# Usage: screen_info = screen_dict["LCOS_num"]
	a = QtGui.QApplication.widgetAt(screen_info.left()+1,screen_info.top()+1)
	X = a.parent()
	#QApplication.allWidgets()
	#
	#QWidget* TopLevelParentWidget (QWidget* widget)
	#{
	#while (widget -> parentWidget() != Q_NULLPTR) widget = widget -> parentWidget() ;
	#return widget ;
	#}
	if X == 0 :
		try:
			X = QtGui.QApplication.topLevelWidgets()
		except:
			print("Fail to search the reffered window.")
			return False
	else: return X

def pitch_to_ang(wlength, pitch):
	thin = 0 #the function of wlength
	if pitch == 0:
		return 0
	ang = numpy.arcsin(wlength/pitch/3.94+numpy.sin(thin)) - thin
	return float(ang/numpy.pi*180)
	
def ang_to_pitch(wlength, ang):
	thin = 0 #the function of wlength
	x = 3.94/wlength*(numpy.sin(thin + ang)-numpy.sin(thin))
	if x == 0:
		return 0
	pitch = int(numpy.round(1/x))
	return pitch
	
class LCOS_con(QtGui.QWidget):
	def __init__(self, LCOS_num, total_w, total_p, *debug_mode):
		QtGui.QWidget.__init__(self)
		self.LCOS_num = LCOS_num
		self.debug_mode = debug_mode
		self.total_w = total_w
		self.total_p = total_p
		for a in QtGui.QApplication.topLevelWidgets():
			if a.objectName() == "LCOS_Trimatiz":
				self.appui = a.ui
		
	def random_show(self,w):
		ch_num = random.randint(0,self.total_w*self.total_p-1)
		image = pattern_proc.pattern_gen(random.randint(0,360),random.randint(20,200),self.pattern_size).blazgrating()
		self.pattern_show(w, image, ch_num)
		if self.pattern_show(w,image,ch_num) ==False:
			print("Fail to change pattern! No such label with THIS NAME")
			return False
		else:return True
		
	def pattern_show(self, w, image, ch_num):
		a = w.findChild(QtGui.QLabel, str(self.LCOS_num)+"_"+str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
		if type(a) != None:
			image = ImageQt.ImageQt(image)
			a.setPixmap(QtGui.QPixmap.fromImage(image))
			a.repaint()
			return True
		else:
			print("Fail to change pattern! No such label with THIS NAME")
			return False
		
	def pattern_showQt(self, w, qtimage, ch_num):
		a = w.findChild(QtGui.QLabel, str(self.LCOS_num)+"_"+str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
		if type(a) != None:
			#print(str(self.LCOS_num)+"_"+str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
			a.setPixmap(QtGui.QPixmap(qtimage))
			a.repaint()
			return True
		else:
			print("Fail to change pattern! No such label with THIS NAME")
			return False
		
	def pattern_reset(self, w):
		num = w.objectName()[-1:]
		x = w.findChild(QtGui.QLabel, num +"_0_0")
		pattern_size = [0,0]
		pattern_size[0] = x.width()
		pattern_size[1] = x.height()
		off_bg = numpy.zeros(pattern_size)
		off_bg = QtGui.QImage(off_bg.data,pattern_size[0], pattern_size[1], QtGui.QImage.Format_Indexed8)
		for k in range(self.total_w):
			for m in range(self.total_p):
				try:
					x = w.findChild(QtGui.QLabel,num +"_" +str(m)+"_"+str(k))
				except:
					print("Something wrong!")
					return False
				x.setPixmap(QtGui.QPixmap(off_bg))
		w.repaint()
		return True
		
	def Initialize_LCOS(self, screen_dict):
		pattern_size = [0,0]
		pattern_size[0] = int(screen_dict[str(self.LCOS_num)].width()/self.total_w)
		pattern_size[1] = int(screen_dict[str(self.LCOS_num)].height()/self.total_p)
		w = QtGui.QWidget()
		w.setObjectName("LCOS" + str(self.LCOS_num))
		w.setWindowTitle("LCOS" + str(self.LCOS_num))
		bgcolor = QtGui.QPalette()
		bgcolor.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
		w.setPalette(bgcolor)
		
		layout = QtGui.QGridLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		
		off_bg = numpy.zeros(pattern_size)
		off_bg = QtGui.QImage(off_bg.data,pattern_size[0], pattern_size[1], QtGui.QImage.Format_Indexed8)
		for k in range(self.total_w):
			for m in range(self.total_p):
				temp = QtGui.QLabel(w)
				temp.setObjectName(str(self.LCOS_num) +"_" +str(m)+"_"+str(k))
				temp.setPixmap(QtGui.QPixmap(off_bg))
				layout.addWidget(temp,m,k)
		
		w.setLayout(layout)
		w.move(screen_dict[str(self.LCOS_num)].left(), screen_dict[str(self.LCOS_num)].top())
		w.showNormal()
		w.showFullScreen()
		w.repaint()
		return w
		
	def Initialize_pattern(self, w):
		num = w.objectName()[-1:]
		x = w.findChild(QtGui.QLabel, num +"_0_0")
		pattern_size = [0,0]
		pattern_size[0] = x.width()
		pattern_size[1] = x.height()
		
		LCOS_dict = {}
		try:
			open("LCOS.ini","r")
		except FileNotFoundError:
			print("Fail to find LCOS.ini !")
			return False
		with open("LCOS.ini","r") as f:LCOS_dict = OrderedDict(x.rstrip().split(None, 1) for x in f)
		
		n = 0
		pix_pitch = 3.96
		th = 0;
		wavelength = self.appui.wlength()
		for k, ang in LCOS_dict.items():
			ang = float(ang)/180*numpy.pi
			pitch = (pix_pitch/wavelength*(numpy.sin(th+ang)-numpy.sin(th)))
			pix_num = 0
			if pitch != 0: pix_num = int(numpy.round(1/pitch))
			
			image = pattern_proc.pattern_gen(0, pix_num,[pattern_size[0],pattern_size[1]]).blazgrating()
			image = ImageQt.ImageQt(image)
			for m in range(self.total_p):
				x = w.findChild(QtGui.QLabel,num +"_" +str(m)+"_"+str(n))
				try:
					x.setPixmap(QtGui.QPixmap.fromImage(image))
				except AttributeError:
					print(num +"_" +str(m)+"_"+str(n))
					return print("No such channel!!!")
				x.repaint()
			n = n + 1
		return True