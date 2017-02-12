import maya.cmds as mc
import PySide2.QtCore as qc
import PySide2.QtWidgets as qw
import PySide2.QtGui as qg
import functools


class spherecutUI(qw.QDialog):

	def __init__(self, inpname, objname):
		#init the main dialog
		qw.QDialog.__init__(self)
		#set window title
		self.setWindowTitle('Sphere Section Maker')
		self.setFixedWidth(400)
		
		self.obj = objname
		self.inp = inpname

		self.sa = mc.getAttr(self.inp+'.subdivisionsAxis')
		self.sh = mc.getAttr(self.inp+'.subdivisionsHeight')

		#init the fields
		#height range min, max
		self.fn = qw.QSpinBox()
		self.fn.setMinimum(0)
		self.fn.setMaximum((self.sa * self.sh) - 1)
		self.fn.setValue(0)
		self.fn.valueChanged.connect(self.numchange)

		self.row = 1
		self.numrows = self.sh

		self.sl = [self.fn.value()]

		#init sliders,
		#connect to slideApply function to make dynamic editing possible

		#number of faces to the right of selected
		self.nr = qw.QSlider(qc.Qt.Horizontal)
		self.nr.setMinimum(0)
		self.nr.setMaximum(self.sa)
		self.nr.valueChanged.connect(self.slideApply)
		self.nr.setValue(3)

		#number of faces to bottom of selected
		self.nb = qw.QSlider(qc.Qt.Horizontal)
		self.nb.setMinimum(0)
		self.nb.setMaximum(self.row)
		self.nb.valueChanged.connect(self.slideApply)
		self.nb.setValue(0)

		#apply button, link to apply function
		btnapp = qw.QPushButton('Tear Away')
		btnapp.clicked.connect(functools.partial(self.apply))
		#Form layout - add all widgets with labels
		self.setLayout(qw.QFormLayout())
		self.layout().addRow('Selected Face:',self.fn)
		self.layout().addRow('Faces to the right:',self.nr)
		self.layout().addRow('Faces at the bottom:', self.nb)
		self.layout().addRow('',btnapp)

	def numchange(self):
		mc.select(self.obj+'.f['+str(self.fn.value())+']', r = True)
		num = self.fn.value()
		self.sa = mc.getAttr(self.inp+'.subdivisionsAxis')
		self.sh = mc.getAttr(self.inp+'.subdivisionsHeight')
		self.fn.setMaximum((self.sa * self.sh) - 1)
		self.nr.setMaximum(self.sa)
		self.nb.setValue(0)
		self.nb.setMaximum(self.row)
		total = self.sa * self.sh
		self.numrows = self.sh
		self.row = ((num+1)/self.numrows) + 1
		print self.row
		

	def getdown(self, num):
		self.sa = mc.getAttr(self.inp+'.subdivisionsAxis')
		self.sh = mc.getAttr(self.inp+'.subdivisionsHeight')
		self.fn.setMaximum((self.sa * self.sh) - 1)
		self.nr.setMaximum(self.sa)
		self.nb.setMaximum(self.row)
		sa = self.sa
		sh = self.sh
		total = (sa * sh)
		if num >= total - 2*sa -1 :
			if num <= total - sa - 1:
				return None
			else:
				return num - 2*sa
		elif num < sa:
			return num + total - 2*sa 
		else:
			return num - sa

	def getright(self, num):
		self.sa = mc.getAttr(self.inp+'.subdivisionsAxis')
		self.sh = mc.getAttr(self.inp+'.subdivisionsHeight')
		self.fn.setMaximum((self.sa * self.sh) - 1)
		self.nr.setMaximum(self.sa)
		self.nb.setMaximum(self.row)
		sa = self.sa
		right = num+1
		if(right % sa == 0):
			right-=sa
		return right

	def apply(self):
		facestokeep = self.sl

		if len(facestokeep) == 1:
			num = self.fn.value()
			facestokeep = [num]

			for i in range(self.nr.value()):
				facestokeep.append(self.getright(num))
				num = self.getright(num)

			toprow = facestokeep
			nextrow = []

			for i in range(self.nb.value()):
				for j in toprow:
					if(self.getdown(j) is not None):
						facestokeep.append(self.getdown(j))
						nextrow.append(self.getdown(j))
				toprow = nextrow
				nextrow = []

		deletethese = []
		for i in range(self.sa * self.sh):
			if i not in facestokeep:
				deletethese.append(self.obj+'.f['+str(i)+']')

		mc.delete(deletethese)

	def slideApply(self):
		num = self.fn.value()
		self.sl = [num]
		toprow = [num]

		for i in range(self.nr.value()):
			num = self.getright(num)
			self.sl.append(num)
			toprow.append(num)	


		for i in toprow:
			next = i
			for j in range(self.nb.value()):
				next = self.getdown(next)
				self.sl.append(next)


		mc.select(clear = True)
		for i in self.sl:
			mc.select(self.obj+'.f['+str(i)+']', add = True)


name = "myPolySphere"
sph = mc.polySphere(sx = 20, sy = 20, r = 10, n = name)
sphUI = spherecutUI('polySphere1', name)
sphUI.show()
