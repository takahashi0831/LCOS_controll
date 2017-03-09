# Generate or load pattern
# The gray level to 2pi is 255 in default
# Usage:
# pattern_gen(angle of grating, int(pitch_num), [port_size_in_x,port_size_in_y])
# pattern_gen(0~360, 10~250, [resolution_x, resolution_y])
# ex: pattern_gen(270, 20, [160,240])
# return a bmp file as array objet

import numpy
import numpy.matlib
from PIL import Image
from PyQt4 import QtGui

class pattern_gen():
	def __init__(self, pol_ang, pitch_num, pattern_size, *debug_mode):
		self.pol_ang = pol_ang/180*numpy.pi
		self.pitch_num = pitch_num
		self.pattern_size = pattern_size
		self.debug_mode = debug_mode

	def pattern_load(self, pattern_path=[]):
		if pattern_path == []: pattern_path = './pattern/'
		xpitch = round(self.pitch_num*numpy.cos(self.pol_ang))
		ypitch = round(self.pitch_num*numpy.sin(self.pol_ang))
		
		if xpitch > 1:
			direction = "+x"
			filename2 = "ch_" + direction + str(self.pitch_num) + ".png"
		elif xpitch < -1:
			direction = "-x"
			filename2 = "ch_" + direction + str(self.pitch_num) + ".png"
		else:
			filename2 = "ch_0.png"
		gx = numpy.asarray(Image.open(pattern_path +filename2))
		
		if ypitch > 1:
			direction = "+y"
			filename2 = "ch_" + direction + str(self.pitch_num) + ".png"
		elif ypitch < -1:
			direction = "-y"
			filename2 = "ch_" + direction + str(self.pitch_num) + ".png"
		else:
			filename2 = "ch_0.png"
		gy = numpy.asarray(Image.open(pattern_path +filename2))
		
		bmpfile = Image.fromarray(numpy.uint8((gx+gy)))
		#bmpfile.save("test.bmp")
		#bmpfile.show()
		return bmpfile

	def blazgrating(self):
		xpitch = round(self.pitch_num*numpy.cos(self.pol_ang))
		ypitch = round(self.pitch_num*numpy.sin(self.pol_ang))
		output = numpy.zeros((self.pattern_size[1],self.pattern_size[0]))
		for m,pitch in enumerate([xpitch,ypitch]):
			if numpy.abs(pitch) <= 1:
				output = output + 0
			else:
				period = numpy.int(numpy.floor(self.pattern_size[m]/abs(pitch)))
				gpmargin = numpy.int(self.pattern_size[m] % pitch)
				
				if period == 0:up_lv = 255*(self.pattern_size[m]/pitch)
				else:up_lv = 255
				
				if pitch > 1:
					gray_up = numpy.linspace(0,up_lv,abs(pitch))
				elif pitch < -1:
					gray_up = numpy.linspace(up_lv,0,abs(pitch))
				
				temp = numpy.matlib.repmat(gray_up,1,period)
				if gpmargin != 0:
					temp2 = numpy.array(gray_up[:gpmargin]).reshape(1,len(gray_up[:gpmargin]))
					temp = numpy.concatenate((temp,temp2) , axis=1)
					
				if m == 0:
					temp = numpy.matlib.repmat(temp,self.pattern_size[1],1)
				else:
					temp = numpy.matlib.repmat(temp,self.pattern_size[0],1)
					temp = numpy.transpose(temp)
					
				output = output + temp
		"""
		if numpy.abs(xpitch) < 1:
			gx = numpy.zeros((self.pattern_size[1],self.pattern_size[0]))
		else:
			if xpitch > 1:
				gray_up = numpy.linspace(0,255,abs(xpitch))
			elif xpitch < -1:
				gray_up = numpy.linspace(255,0,abs(xpitch))
				
			period = math.floor(self.pattern_size[0]/abs(xpitch))
			gpmargin = self.pattern_size[0] % xpitch
			temp = numpy.matlib.repmat(gray_up,1,period)
			if gpmargin != 0:
				temp2 = numpy.array(gray_up[:gpmargin]).reshape(1,len(gray_up[:gpmargin]))
				temp = numpy.concatenate((temp,temp2) , axis=1)
				
			gx = numpy.matlib.repmat(temp,self.pattern_size[1],1)
			
		Image.fromarray(numpy.uint8((gx))).show()

		if -1 <ypitch < 1:
			gy = numpy.zeros((self.pattern_size[1],self.pattern_size[0]))
		else:
			if ypitch > 1:
				gray_up = numpy.linspace(0,255,abs(ypitch))
			elif ypitch < -1:
				gray_up = numpy.linspace(255,0,abs(ypitch))
				
			
			period = math.floor(self.pattern_size[1]/abs(ypitch))
			gpmargin = self.pattern_size[1] % ypitch
			temp = numpy.matlib.repmat(gray_up,1,period)
			if gpmargin != 0:
				temp2 = numpy.array(gray_up[:gpmargin]).reshape(1,len(gray_up[:gpmargin]))
				temp = numpy.concatenate((temp,temp2) , axis=1)
				
			gy = numpy.matlib.repmat(temp,self.pattern_size[0],1)
			gy = numpy.transpose(gy)
			
		Image.fromarray(numpy.uint8((gy))).show()
		output = gx+gy
"""
		
		bmpfile = Image.fromarray(numpy.uint8((output)))
		if self.debug_mode : bmpfile.save("blaztest.bmp")
			
		return bmpfile

	def singrating(self, *binary):
		xv = numpy.indices((self.pattern_size[1], self.pattern_size[0]))[1]
		sine_xv = 127.5 + 127.5*numpy.sin(xv * 2.0 *  numpy.pi * self.pitch_num)
		numpy_image = numpy.ascontiguousarray(sine_xv, dtype = numpy.uint8)
		
		if binary:
			mask = (numpy_image < 128)
			numpy_image[mask] = 0
			numpy_image[~mask] = 255

		image = QtGui.QImage(numpy_image.data, self.pattern_size[0], self.pattern_size[1], QtGui.QImage.Format_Indexed8)
		for i in range(256):
			image.setColor(i,QtGui.qRgb(i,i,i))
			
		return image
		
	def other(self, gtype):
		xoffset = 0
		yoffset = 0
		
		image = numpy.zeros((self.pattern_size[0], self.pattern_size[1])) + 127.0
		size_x = self.pattern_size[0]
		size_y = self.pattern_size[1]
		midx = int(self.pattern_size[0]/2)
		midy = int(self.pattern_size[1]/2)
		
		# focus.
		if gtype == 0:
			for i in range(size_x):
				for j in range(size_y):
					dx = (i - midx)
					dy = (j - midy)
					mag = -3.0e-2 * (dx * dx + dy * dy)
					image[i,j] += mag
		
		# horizontal astigmatism
		if gtype == 1:
			for i in range(size_y):
				dy = (i - midy) + 50
				mag = 0.07 * dy * dy
				image[:,i] += mag
			for i in range(size_x):
				dx = (i - midx) - 50
				if (abs(dx) > 200):
					image[i,:] = 127.0
		
		# vertical astigmatism
		if gtype == 2:
			for i in range(size_x):
				dx = (i - midx) + xoffset
				mag = 0.2 * dx * dx
				image[i,:] += mag
				#if (abs(dx) > 25):
				#    image[i,:] = 127
			for i in range(size_y):
				dx = (i - midy) + yoffset    
				if (abs(dx) > 100):
					image[:,i] = 127.0
		
		# light grid
		if gtype == 3:
			cx = midx + 150
			cy = midy
			temp = numpy.copy(image)
			image = numpy.zeros((size_x, size_y)) + 127.0
			image[(cx-150):(cx+150),(cy+150):(cy+200)] = temp[(cx-150):(cx+150),(cy+150):(cy+200)]
			image[(cx-150):(cx+150),(cy-200):(cy-150)] = temp[(cx-150):(cx+150),(cy-200):(cy-150)]
			image[(cx+150):(cx+200),(cy-100):(cy+100)] = temp[(cx+150):(cx+200),(cy-100):(cy+100)]
			image[(cx-200):(cx-150),(cy-100):(cy+100)] = temp[(cx-200):(cx-150),(cy-100):(cy+100)]
		
		# hole
		if gtype == 4:
			cx = midx + xoffset
			cy = midy + yoffset
			for i in range(size_x):
				for j in range(size_y):
					dx = (i - cx)
					dy = (j - cy)
					if ((dx*dx + dy*dy) < (150*150)):
						image[i,j] = 127.0
		
		# reduce na
		if gtype == 5:
			cx = midx + xoffset
			cy = midy + yoffset
			for i in range(size_x):
				for j in range(size_y):
					dx = (i - cx)
					dy = (j - cy)
					if ((dx*dx + dy*dy) > (100*100)):
						image[i,j] = 127.0
		
		# ring
		if gtype == 6:
			cx = midx + 150
			cy = midy
			for i in range(size_x):
				for j in range(size_y):
					dx = (i - cx)
					dy = (j - cy)
					if ((dx*dx + dy*dy) > (300*300)):
						image[i,j] = 127.0
					elif ((dx*dx + dy*dy) < (250*250)):
						image[i,j] = 127.0
		
		# airy beam
		if gtype == 7:
			cx = midx + 50
			cy = midy - 50
			for i in range(size_x):
				for j in range(size_y):
					dx = (i - cx)
					dy = (j - cy)
					mag = 1.0e-4 * (dx * dx * dx + dy * dy * dy)
					image[i,j] += mag
					
		image = numpy.round(image).astype(numpy.uint8)
		image = Image.fromarray(image)
		return image
		

	def __str__(self):
		return pattern_gen({0},{1},{2}).format(self.azi.ang, self.pitch, self.pattern_size)
