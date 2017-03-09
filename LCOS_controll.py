# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 11:23:00 2017

@author: Lin
"""

import sys
import pattern_proc
import numpy
from PyQt4 import QtCore, QtGui, uic
import LCOS_con
import LCOS_optim
import opticalswitch.opticalswitch as opts
from gpib.core import T100sHP
import matplotlib.pyplot as plt
from matplotlib import mlab, cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import qt_compat

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

qtCreatorFile = "LCOS_controll.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		super(MyApp, self).__init__()
		self.ui = Ui_MainWindow()
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.ui.setupUi(self)
		self.ui.scan.clicked.connect(self.scandata)
		self.ui.message.append("Welcome!")
		self.ui.message.repaint()
		#self.ui.Initialization.clicked.connect(self.Initialize)
		QtCore.QObject.connect(self.ui.Initialization, QtCore.SIGNAL(_fromUtf8("clicked()")),self.Initialize)
		QtCore.QObject.connect(self.ui.All_ch_off, QtCore.SIGNAL(_fromUtf8("clicked()")),self.all_off)
		QtCore.QObject.connect(self.ui.Optimize, QtCore.SIGNAL(_fromUtf8("clicked()")),self.optimize)
		QtCore.QObject.connect(self.ui.pfocus, QtCore.SIGNAL(_fromUtf8("clicked()")),self.focus)
		QtCore.QObject.connect(self.ui.ASE, QtCore.SIGNAL(_fromUtf8("clicked()")),self.ASE)
		QtCore.QObject.connect(self.ui.TEST_plot, QtCore.SIGNAL(_fromUtf8("clicked()")),self.__2d_plot__)
		
		self.ui.wlength.valueChanged.connect(self.get_lcos_ang)
		self.ui.pitch.valueChanged.connect(self.get_lcos_ang)
		self.ui.Voltage.valueChanged.connect(self.get_mems_ang)
		self.ui.Ang_of_MEMS.valueChanged.connect(self.get_mems_vol)
		self.w1 = None
		self.w2 = None
		self.data = None
	
	def __2d_plot__(self):
		fig1 = plt.figure()
		ax1f1=fig1.add_subplot(111).plot(self.data[:,0],self.data[:,1],'o-')
		return ax1f1
		
	def __3d_plot__(self):
		x = numpy.delete(self.data[0,:],0,0)
		y = numpy.delete(self.data[:,0],0,0)
		X, Y = numpy.meshgrid(x, y)
		Z = self.data[1:,][:,1:]
		norm = cm.colors.Normalize(vmax=abs(Z).max(), vmin=-abs(Z).max())
		
		fig, ax = plt.subplots()
		cset1 = ax.contourf(X, Y, Z,norm=norm)
		return fig
		
	@QtCore.pyqtSlot(float)
	def get_lcos_ang(self):
		thin = self.ui.thin.value()
		a = LCOS_optim.LCOS_optim.pitch_to_ang(self.ui.wlength.value(), self.ui.pitch.value())
		self.ui.answer_of_cal.setText(str(round(a,4)))
		self.ui.answer_of_cal.repaint()
		return True
		
	@QtCore.pyqtSlot(float)
	def get_mems_ang(self):
		x = self.ui.Voltage.value()
		if x < 0:
			a = -0.00070
			b = 0.00227
			c = -0.00537
		else:
			a = 0.00069
			b = -0.00164
			c = -0.00328
		self.ui.Ang_of_MEMS.setValue(a*x*x + b*x + c)
		return True
	
	@QtCore.pyqtSlot(float)
	def get_mems_vol(self):
		y = self.ui.Ang_of_MEMS.value()
		if y >=0:
			a = 0.00069
			b = -0.00164
			c = -0.00328
		else:
			a = -0.00070
			b = 0.00227
			c = -0.00537
#		self.ui.Ang_of_MEMS.setValue((-b+numpy.sqrt(b*b - 4*a*(c -y) ))/2/a)
		return True
		
	def focus(self):
		image = pattern_proc.pattern_gen(self.ui.p_ang.value(),self.ui.scanrange_max.value(),self.pattern_size).other(0)
		if self.ui.LCOS1.isChecked():
			self.lcos1.pattern_show(self.w1,image,self.ui.ch_num.value())
		if self.ui.LCOS2.isChecked():
			self.lcos1.pattern_show(self.w1,image,self.ui.ch_num.value())
			
		return True
		
	def ASE(self):
		if self.ui.LCOS1.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.scan_ASE(self.w1, self.ui.ch_num.value(),self.ui.p_ang.value(),[self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__3d_plot__()

		if self.ui.LCOS2.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.scan_ASE(self.w2, self.ui.ch_num.value(),self.ui.p_ang.value(),[self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__3d_plot__()
		return True
		
	def scandata(self):
		if self.ui.LCOS1.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.scan_one(self.w1, self.ui.ch_num.value(),self.ui.p_ang.value(),[self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__2d_plot__()

		if self.ui.LCOS2.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.scan_one(self.w2, self.ui.ch_num.value(),self.ui.p_ang.value(),[self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__2d_plot__()
		return True
	
	def optimize(self):
		if self.ui.LCOS1.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.singlech(self.w1, self.ui.ch_num.value(), [self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__2d_plot__()
		if self.ui.LCOS2.isChecked():
			x = LCOS_optim.LCOS_optim(self.ui.total_w.value(),self.ui.total_p.value(),True)
			self.data = x.singlech(self.w2, self.ui.ch_num.value(), [self.ui.scanrange_min.value(),self.ui.scanrange_max.value()])
			self.__2d_plot__()
		return True
		
	def all_off(self):
		if self.ui.LCOS1.isChecked():
			self.lcos1.pattern_reset(self.w1)
		if self.ui.LCOS2.isChecked():
			self.lcos1.pattern_reset(self.w2)
		return True
		
	def Initialize(self):
		self.pattern_size = [0,0]
		self.pattern_size[0] = int(screen_dict[str(1)].width()/self.ui.total_w.value())
		self.pattern_size[1] = int(screen_dict[str(1)].height()/self.ui.total_p.value())
		self.lcos1 = LCOS_con.LCOS_con(1, self.ui.total_w.value(), self.ui.total_p.value())
		self.w1 = self.lcos1.Initialize_LCOS(screen_dict)
		try:
			screen_dict[str(2)]
			self.lcos2 = LCOS_con.LCOS_con(2, self.ui.total_w.value(), self.ui.total_p.value())
			self.w2 = self.lcos2.Initialize_LCOS(screen_dict)
		except:
			self.ui.message.append("No second LCOS! \n")
			self.ui.message.repaint()
			self.ui.LCOS2.setChecked(False)
			self.ui.LCOS2.setCheckable(False)
		#self.lcos1.Initialize_pattern(self.w1)
		#self.w1 = LCOS_win()
		#self.w1 = self.w1.Initialize_LCOS(screen_dict)
		#lcos1.Initialize_LCOS(screen_dict)
		#a1 = lcos1.Initialize_pattern(self.w1)
		return True

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	pDesktop = app.desktop()
	screen_dict = {}
	for k in range(pDesktop.screenCount()):
		screen_dict[str(k)] = pDesktop.screenGeometry(k)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())