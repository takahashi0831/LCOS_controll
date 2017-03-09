# -*- coding: utf-8 -*-

# Usage: LCOS_optim_one(total_w, total_p)
#Ex:
#>>> import LCOS_optim
#>>> X = LCOS_optim.LCOS_optim(24,8)
#>>> X.singlech(w,9, [10,50])
#
#LCOS_num : which LCOS.1 or 2
#ch_num : channel num on LCOS
#total_w: the number of ports on LCOS
#totla_lambda: the number of lambda division on LCOS
#pitch_range: the pitch range of grating. [min, max]. minimum is at least 2, 
#
# X.one(grating_angle_in_DEG)
#

"""
Created on Tue Feb 21 11:26:00 2017

@author: Lin
"""
import numpy
import pattern_proc
from PIL import ImageQt
import xlwt
from PyQt4 import QtGui
import time
import datetime 
import os.path
from gpib.core import Q8221
from gpib.core import Q8384


class LCOS_optim():
	def __init__(self, total_w, total_p, write_mode = True):
		self.total_w = total_w
		self.total_p = total_p
		self.write_mode = write_mode
		for a in QtGui.QApplication.topLevelWidgets():
			if a.objectName() == "LCOS_Trimatiz":
				self.appui = a.ui
	
	def pitch_to_ang(self, wlength, pitch):
		thin = self.appui.thin.value() #the function of wlength
		if pitch == 0:
			return 0
		ang = numpy.arcsin(wlength/pitch/3.94+numpy.sin(thin)) - thin
		return float(ang/numpy.pi*180)
		
	def ang_to_pitch(self, wlength, ang):
		thin = 0 #the function of wlength, lambda thin: ......
		x = 3.94/wlength*(numpy.sin(thin + ang)-numpy.sin(thin))
		if x == 0:
			return 0
		pitch = int(numpy.round(1/x))
		return pitch
		
	def get_value_from_ui(self, name):
		try:
			obj = self.appui.name
			return obj.value()
		except:
				return self.error_mes_handler("No such object!")
		
	def send_value_to_ui(self, value, object):
		try:
			obj = self.appui.name
			obj.value = str(value)
			return obj.repaint()
		except:
			return self.error_mes_handler("No such object!")
			
	def error_mes_handler(self,err_text):
		self.appui.message.append(err_text)
		return self.appui.message.repaint()
		
	def scan_ASE(self,w,ch_num,ang, pitch_range):
		num = w.objectName()[-1:]
		try:
			x = w.findChild(QtGui.QLabel, num +"_" +str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
		except:
			return print("No such channel!")
		pattern_size = [0,0]
		pattern_size[0] = x.width()
		pattern_size[1] = x.height()
		Grating_pitch = numpy.linspace(pitch_range[0], pitch_range[1],(pitch_range[1] - pitch_range[0] ) )
		
		if self.write_mode:
			target_name = str(datetime.date.today()) + "_scan_ch_" + str(round(ch_num,3)) + '.xls'
			if os.path.exists("./" + target_name): target_name = target_name[:-4] + "_" + time.strftime("%H_%M") + '.xls'
			book = xlwt.Workbook(target_name)
			sheet = book.add_sheet(time.strftime("%H_%M"))
		
		pm = Q8384(int(self.appui.Q8384_ADD.value()))
		print(pm.get_wavelength(), pm.get_wavelength().types)
		print(pm.get_power())
		data = numpy.zeros([len(pm.get_wavelength())+1,len(Grating_pitch)+1])
		for k, pitch in enumerate(Grating_pitch):
			image = pattern_proc.pattern_gen(ang, int(pitch), pattern_size).blazgrating()
			image = ImageQt.ImageQt(image)
			x.setPixmap(QtGui.QPixmap.fromImage(image))
			x.repaint()
			pm.sweep()
			if self.write_mode:
				if k ==0:
					try:
						for m,n in enumerate(pm.get_wavelength()):
							sheet.write(0,m+1, float(n))
							data[0,m]= float(n)
					except : pass
				else:
					try:
						sheet.write( k, 0, round(pitch))
						for m, n in enumerate(pm.get_power()):
							sheet.write( k, m+1, float(n))
							data[k,m]= float(n)
					except IndexError:pass
		
		if self.write_mode:book.save(target_name)
		return data
		
	def scan_one(self, w, ch_num, ang, pitch_range):
		num = w.objectName()[-1:]
		try:
			x = w.findChild(QtGui.QLabel, num +"_" +str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
		except:
			return print("No such channel!")
		pattern_size = [0,0]
		pattern_size[0] = x.width()
		pattern_size[1] = x.height()
		Grating_pitch = numpy.linspace(pitch_range[0], pitch_range[1],(pitch_range[1] - pitch_range[0]))
		
		if self.write_mode:
			target_name = str(datetime.date.today()) + "_scan_ch_" + str(round(ch_num,3)) + '.xls'
			if os.path.exists("./" + target_name): target_name = target_name[:-4] + "_" + time.strftime("%H_%M") + '.xls'
			book = xlwt.Workbook(target_name)
			sheet = book.add_sheet(time.strftime("%H_%M"))
		
		try:
			pm = Q8221(int(self.appui.Q8221_ADD.value()))
		except:
			self.error_mes_handler("Connection failed!")
		data = numpy.zeros([1,2])
		for k, pitch in enumerate(Grating_pitch):
			image = pattern_proc.pattern_gen(ang, int(pitch), pattern_size).blazgrating()
			image = ImageQt.ImageQt(image)
			x.setPixmap(QtGui.QPixmap.fromImage(image))
			x.repaint()
			wlength = self.appui.wlength.value()
			wlength = self.appui.wlength.value()
			temp = str(round(self.pitch_to_ang(wlength , pitch),3 ) )
			self.appui.answer_of_cal.setText( temp )
			self.appui.answer_of_cal.repaint()
			
			value = pm.read_power()
			self.error_mes_handler("Detected value"+str(value)+"\n" )
			if self.write_mode:
				try:
					sheet.write( k, 0, round(pitch))
					sheet.write( k, 1, value)
					data = numpy.concatenate((data,numpy.array([round(pitch),value]).reshape(1,2)))
				except IndexError:	pass
		
		if self.write_mode:book.save(target_name)
		return numpy.delete(data,0,0)

	def singlech(self,w, ch_num, pitch_range):
		num = w.objectName()[-1:]
		try:
			x = w.findChild(QtGui.QLabel, num +"_" +str(int(numpy.floor(ch_num/self.total_w)))+"_"+str((ch_num%self.total_w)))
		except:
			return print("No such channel!")
		pattern_size = [0,0]
		pattern_size[0] = x.width()
		pattern_size[1] = x.height()
		pattern_gen = pattern_proc.pattern_gen
		Grating_pitch = numpy.linspace(pitch_range[0], pitch_range[1],(pitch_range[1]-pitch_range[0] ) )
		
		# Initialize instruments
		try:
			pm = Q8221(int(self.appui.Q8221_ADD.value()))
		except:
			self.error_mes_handler("Connection fail!")
		ini_power = pm.read_power() # ini_power = 0.5

		print("Make sure the optical system is well tuned and the output power is deteted")
		print("=============System information=============")
		print("LCOS num = " + str(num))
		print("Initial power = " + str(ini_power))
		print("Searching range= " + str(pitch_range[0]) + "pitch ~ " + str(pitch_range[1]) + " pitch")
		print("")
		
		## Initialization of the iteration
		pitch1 = int((pitch_range[0]+pitch_range[1])/2)
		image = pattern_gen(0, pitch1, pattern_size).blazgrating()
		step_pitch = 1;
		mid_index = int(len(Grating_pitch)/2)
		j = 0
		image = ImageQt.ImageQt(image)
		x.setPixmap(QtGui.QPixmap.fromImage(image))
		x.repaint()
		
		wlength = self.appui.wlength.value()
		temp = str(round(self.pitch_to_ang(wlength , pitch1),3 ) )
		self.appui.answer_of_cal.setText( temp )
		self.appui.answer_of_cal.repaint()
			
		ini_value = ini_power
		index = mid_index
		data = numpy.zeros([1,2])
		if self.write_mode:
			target_name = str(datetime.date.today()) + "_optim_" + str(ch_num) + '.xls'
			if os.path.exists("./" + target_name): target_name = target_name[:-4] + "_" + time.strftime("%H_%M") + '.xls'
			book = xlwt.Workbook(target_name)
			sheet = book.add_sheet(time.strftime("%H_%M"))
			
			try:
				sheet.write(j, 0, round(pitch1,3))#sheet.write( j, 0, float(str(value)[:-6][6:]))
				sheet.write(j, 1, ini_value)#sheet.write( j, 0, float(str(value)[:-6][6:]))
				data = numpy.concatenate((data,numpy.array([round(pitch1,3),ini_value]).reshape(1,2)))
			except IndexError:
				pass
		
		while True:
			if (index) > len(Grating_pitch):
				print("Local optimization might not exist in this range!")
				break
			image = pattern_gen(0, int(Grating_pitch[index]), pattern_size).blazgrating()
			image = ImageQt.ImageQt(image)
			x.setPixmap(QtGui.QPixmap.fromImage(image))
			x.repaint()
			
			wlength = self.appui.wlength.value()
			temp = str(int(self.pitch_to_ang(wlength , Grating_pitch[index]) ) )
			self.appui.answer_of_cal.setText(temp)
			self.appui.answer_of_cal.repaint()
			
			print("Loading pattern on LCOS " + str(num)+ ", Ch # = " + str(ch_num))
			value = pm.read_power() #value = random.uniform(0,0.5/(j+1))
			print(j)
			print("Grating angle =" + str(round(0)) + " DEG, Grating pitch =" + str(round(Grating_pitch[index])) + ", Power:" + str(round(value,3)))
			print("Initial value = ", str(round(ini_value,3)), "Detected value", str(round(value,3)))
			if self.write_mode:
				try:
					sheet.write( j+1, 0, round(Grating_pitch[index]))
					sheet.write( j+1, 1, value)
					data = numpy.concatenate((data,numpy.array([round(Grating_pitch[index]),value]).reshape(1,2)))
				except IndexError:	pass
			if (value -  ini_value) < 0:step_pitch = step_pitch * -1
			index = index + step_pitch
			if numpy.abs(value - ini_value) < 1e-3:break
			else:ini_value = value
			
			j = j + 1
		
		if self.write_mode:book.save(target_name)
		return numpy.delete(data,0,0)
		
	def __opt__(self):
		
		
		return True

