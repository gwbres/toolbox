from XSimParam import *
from XSimStimulus import *

import datetime

# Qt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel

# pyqtgraph
import pyqtgraph as pg
from pyqtgraph.dockarea import *

class XSimBench:
	"""
	Test bench object
	"""

	def __init__(self, dicts):
		self.descriptor = dicts

		# attributes
		self.lang = None
		self.sample_rate = 100E6
		self.libs = []
		self.libs.append(["ieee","std_logic_1164.all"]) # always needed
		
		self.params = []

		self.stimuli = []

		for d in dicts:
			self.addFromDictionnary(d)

		self.checkEnvSanity()

		# custom PRE/POST package hooks
		self._customPrePackageHook = None
		self._customPostPackageHook = None
		
		# custom method to retrieve results 
		self._customDataParsingHook = None

		# custom method to analyze sim. results
		self._customAnalysisMethod = None

	def addFromDictionnary(self, d):
		"""
		Adds either
			+ an attribute
			+ a simulation parameter
			+ a signal to be generated
		from a dictionnary/JSON descriptor
		"""
		
		if (d['type'] == 'attribute'):
			try:
				lang = d['language']
				if (lang not in(['vhdl'])):
					raise ValueError("{:s} language is not supported yet".format(lang.upper()))
				else:
					self.lang = lang 
			except KeyError:
				pass

			try:
				lib = d['library']
				self.addSimulationLibrary(lib)

			except KeyError:
				pass

		elif (d['type'] == 'parameter'):
			ptype = d['ptype']
			key = d['key']
			value = d['value']
				
			if (ptype == 'fixed_point'):
				mhelp = None
				try:
					mhelp = d['help']
				except KeyError:
					pass
				
				hidden = False	
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				fxp = XSimFixedPointParam(key, value, help=mhelp, hidden=hidden)
					
				try:
					fxp.setRange(d['Qmin'],d['Qmax'])
				except KeyError:
					pass
					
				mhelp = fxp.getHelpString()
				try:
					mhelp += ' [{:d}:{:d}]'.format(d['Qmin'],d['Qmax'])
				except KeyError:
						pass

				fxp.setHelpString(mhelp)

				self.params.append(fxp)
				self.addSimulationLibrary(['ieee_proposed', "fixed_pkg"]) # will be required
					
			elif (ptype == 'string'):
				mhelp = None
				try:
					mhelp = d['help']
				except KeyError:
						pass
			
				allowed = None
				try:
					allowed = d['values']
				except KeyError:
						pass

				hidden = False
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				self.params.append(XSimStringParam(key, value, help=mhelp, allowed=allowed, hidden=hidden))

			elif (ptype == 'float'):
				allowed = None
				try:
					allowed = d['values']
				except KeyError:
					pass

				mhelp = None
				try:
					mhelp = d['help']
				except KeyError:
					pass

				hidden = False
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				formatstr = None
				try:
					formatstr = d['formatstr']
				except KeyError:
					pass

				self.params.append(XSimFloatParam(key, value, help=mhelp, allowed=allowed, hidden=hidden, formatstr=formatstr))

			elif (ptype == 'bool'):
				hidden = False
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				self.params.append(XSimBoolParam(key, value, help=d['help'], hidden=hidden))

			elif (ptype == 'integer'):
				mhelp = None
				try:
					mhelp = d['help']
				except KeyError:
					pass

				hidden = False
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				ipm = XSimIntParam(key, value, help=mhelp, hidden=hidden)
					
				try:
					rm = d['min']
					rM = d['max']
					ipm.setRange([d['min'],d['max']])
					
					mhelp = ipm.getHelpString()
					mhelp += ' [{:s}:{:s}]'.format(rm,rM)
					ipm.setHelpString(mhelp)

				except KeyError:
					pass

				self.params.append(ipm)

			elif (ptype == 'time'):
				unit = None
				try:
					unit = d['unit']
				except KeyError:
					pass

				mhelp = None
				try:
					mhelp = d['help']
				except KeyError:
					pass

				hidden = False
				try:
					hidden = d['hidden']
				except KeyError:
					pass

				self.params.append(XSimTimeParam(key, value, unit=unit, help=mhelp, hidden=hidden))
			
		elif (d['type'] == 'stimulus'):
			if (d['stype'] == 'sinewave'):
				key = d['key']
				a = d['amplitude']
				f = d['frequency']
				nsymbols = d['n-symbols']

				options = None
				try:
					options = d['options']
				except KeyError:
					pass

				stm = XSimSineWaveStimulus(key, a, f, nsymbols, sample_rate=self.getSampleRate(), options=options)
				self.stimuli.append(stm)

			elif (d['stype'] == 'ramp'):
				key = d['key']
				a = d['amplitude']
				nperiods = d['n-periods']
				nsymbols = d['n-symbols']
					
				options = None
				try:
					options = d['options']
				except KeyError:
					pass

				self.stimuli.append(XSimRampStimulus(key, a, nperiods, nsymbols, sample_rate=self.getSampleRate(), options=options))

			elif (d['stype'] == 'squarewave'):
				key = d['key']
				a = d['amplitude']
				nperiods = d['n-periods']
				nsymbols = d['n-symbols']
					
				options = None
				try:
					options = d['options']
				except KeyError:
					pass

				self.stimuli.append(XSimSquareWaveStimulus(key, a, nperiods, nsymbols, sample_rate=self.getSampleRate(), options=options))

	def runCLI(self):
		"""
		Runs command line interface
		CLI regroups all simulation parameters
		and allows user to modify all of them
		before running simulation
		"""

		# build interface
		cli = "\n\033[91mxsim>\033[0m\n"

		cli += "\t\033[94mlang\033[0m: {:s}\n".format(self.getLanguage())

		for stm in self.getStimuli():
			cli += "\t\033[93m{:s}\033[0m: {:s}".format(stm.getType(),str(stm))

		validate = False
		for param in self.getParams():
			key = param.getKey()

			if param.isHidden():
				continue
			
			if (key == "validate"):
				validate = True
				cli += "\t\033[91m{:s}\033[0m".format(key)
			else:
				cli += "\t\033[92m{:s}\033[0m".format(key)
				
			if (param.getHelpString()):
				cli += ": {:s}".format(param.getHelpString())

			if (param.getAllowedValues()):
				cli += " {:s}".format(str(param.getAllowedValues()))
			cli += "\n"

		if not(validate):
			cli += "\t\033[91mvalidate\033[0m: validate current sim. environment\n"

		user = input(cli)
		while (user != "validate"):
			key = user.split(' ')[0].strip()
			value = user.split(' ')[1].strip()
			self.modify(key, value)
			user = input()

	def __str__(self):
		return str(self.descriptor)

	def modify(self, key, value):
		"""
		Modifies given parameter identified by key
		"""
		# replace in descriptor
		found = None 

		for d in self.descriptor:
			
			keyValue = None
			try:
				keyValue = d['key']
			except KeyError:
				pass

			if keyValue == key:
				
				if (d['ptype'] == 'float'):
					nValue = float(value)
					d['value'] = nValue 
					found = d

				elif (d['ptype'] == 'bool'):
					nValue = int(value)
					d['value'] = nValue 
					found = d

				elif (d['ptype'] == 'integer'):
					nValue = int(value)
					d['value'] = nValue 
					found = d

				elif (d['ptype'] == 'string'):
					nValue = str(value)
					d['value'] = nValue 
					found = d

		if (found is None):
			print("Parameter {:s} not found in descriptor".format(key))
			return -1
	
		# replace in self 
		if found['type'] == 'attribute':
			raise ValueError('not ready yet!!')

		elif found['type'] == 'parameter':
			param = self.searchParamsByKey(key)	
			param.setValue(nValue)

		elif found['type'] == 'stimulus':
			raise ValueError('not ready yet!!')

		return 0

	###################
	# XSim attributes #
	###################
	def getLanguage(self):
		"""
		Returns simulator language
		to be used
		"""
		return self.lang

	###################
	# XSim Parameters #
	###################
	def getParams(self):
		return self.params

	def getNumberOfParams(self):
		return len(self.params)
	
	def searchParamsByType(self, ptype):
		results = []
		for param in self.params:
			if (type(param) == ptype):
				results.append(param)
		return results

	def searchParamsByKey(self, key):
		for param in self.params:
			if (param.getKey() == key):
				return param
		return None

	def getFixedPointParams(self):
		return self.searchParamsByType(XSimFixedPointParam)

	def getBooleanParams(self):
		return self.searchParamsByType(XSimBoolParam)
	
	def getStringParams(self):
		return self.searchParamsByType(XSimStringParam)
	
	def getFloatParams(self):
		return self.searchParamsByType(XSimFloatParam)

	def getSampleRate(self):
		params = self.getFloatParams()
		for p in params:
			if (p.getKey() == 'sample_rate'):
				return p.getValue()
		return None

	################
	# XSim stimuli #
	################
	def getStimuli(self):
		return self.stimuli

	def searchStimuliByType(self, _type):
		"""
		Returns list of stimulus with matching type 
		"""
		results = []
		for stim in self.stimuli:
			if (stim.getType() == _type):
				results.append(stim)
		return results

	def searchStimulusByKey(self, key):
		"""
		Returns stimulus for with key did match
		"""
		for stim in self.stimuli:
			if (stim.getKey() == key):
				return stim
		return None

	def numberOfStimuli(self):
		"""
		Returns number of stimuli to be generated
		"""
		return len(self.stimuli)

	def addSimulationLibrary(self, lib):
		"""
		Adds one library to be used
		if not already added
		"""
		already_included = False
		for _lib in self.libs:
			if (_lib[0] == lib[0]):
				already_included = True
		
		if not(already_included):
			self.libs.append(lib)

	def getLibraries(self):
		"""
		Returns libraries used in current simulation env.
		"""
		return self.libs

	def checkEnvSanity(self):
		"""
		Checks whether fundamental stuff has been declared
		"""
		if (self.getLanguage is None):
			raise XSimError("Simulation language has not been declared")

		if (self.getSampleRate() is None):
			raise XSimError('Sample rate has not been declared')

		if (self.numberOfStimuli == 0):
			print('Stimuli to be generated by test bench')

	def writePackage(self, fp):
		if (self._customPrePackageHook is not None):
			self._customPrePackageHook()

		# generate stimuli
		for stim in self.stimuli:
			stim._generate()

		if (self.lang == "vhdl"):
			self.writeVHDLPackage(fp)
		else:
			raise ValueError("Verilog simulation is not supported yet")
			
		if (self._customPrePackageHook is not None):
			self._customPostPackageHook()

	def writeVHDLPackage(self, fp):
		fd = open(fp,"w")
		
		# retrieve library headers
		headers = []
		for lib in self.getLibraries():
			if not(lib[0] in headers):
				headers.append(lib[0])

		# declare & include all libraries 
		for header in headers:
			fd.write("library {:s};\n".format(header))
			for lib in self.getLibraries():
				if (lib[0] == header):
					fd.write("use {:s}.{:s};\n".format(lib[0],lib[1]))
			fd.write("\n")

		fd.write("package package_tb is \n")

		fd.write("\t ---- XSIM params ---- \n")
		for param in self.getParams():
			param.declare(fd, lang=self.getLanguage())
		fd.write("\t ------ end XSIM params -------\n")

		fd.write("\t ---- XSIM stimuli ---- \n")
		lutsize = self.stimuli[0].numberOfSymbols()
		fd.write('\tconstant N_SYMBOLS: natural := {:d};\n'.format(lutsize))
		fd.write('\ttype mem is array(0 to N_SYMBOLS-1) of real;\n')
		for i in range(0, self.numberOfStimuli()):
			fd.write('\n\tconstant lut{:d}: mem := ('.format(i))
			symbols = self.stimuli[i].getSymbols()
			string = ''
			for j in range(0, len(symbols)-1):
				string += '{:.6e},'.format(symbols[j])
			string += '{:.6e});\n'.format(symbols[-1])
			fd.write(string)

		fd.write("\t ---- end XSIM stimuli ---- \n")

		fd.write("end package package_tb;\n\n")
		
		fd.write("package body package_tb is\n")
		fd.write("end package body package_tb;\n")
		fd.close()

	def postSimRun(self):
		
		if (self._customDataParsingHook is None):
			raise ValueError("_customDataParsingHook has not been defined in XSimBench object")

		data = self._customDataParsingHook() # retrieve data

		results = [] # passed to UI
		for i in range(0, len(data)): # run for all data sets
			if (self._customAnalysisMethod is not None):
				results.append(self._customAnalysisMethod(self, i, data[i]))
		
		self.buildUIBase()
		self.UIStackSimResults(results)
		self.exec()

	def buildUIBase(self):
		self.ui = QApplication([])
		self.ui.setStyle('plastique')

		self.uiWidget = QMainWindow()
		date = datetime.datetime.now()
		self.uiWidget.setWindowTitle("{:s} run".format(date.strftime('%Y/%m/%d %H:%M:%S')))

		# menu bar
		bar = self.uiWidget.menuBar()
		fMenu = bar.addMenu("File")
		action = QAction("Save as", fMenu)
		action.triggered.connect(self.save)
		fMenu.addAction(action)

		action = QAction("Exit", fMenu)
		action.triggered.connect(self.exit)
		fMenu.addAction(action)

		self.uiWidget.show()

	def UIStackSimResults(self, results):
		"""
		Stacks all simulation results
		in central widget
		as a pyqtgraph.plot object
		"""
		widget = self.getUIWidget()
		
		# building central widget
		area = DockArea()

		for i in range(0, len(results)):
			d = Dock("Result{:d}".format(i), size=(1,1))
			d.addWidget(self.makeDockWidget(results[i]))
			area.addDock(d)

		widget.setCentralWidget(area)
		widget.resize(500,500)

	def getUIWidget(self):
		return self.uiWidget

	def makeDockWidget(self, args):
		"""
		Builds docked widget
		Displays simulation result in a frame
		Optionnal data plot
		"""
		passed = args[0]
		data = args[1]

		widget = QWidget()
		layout = QVBoxLayout()

		widget1 = QWidget()
		l1 = QVBoxLayout()
		label = QLabel()

		if (passed):
			color = "#04FF9D"
			label.setText("Test PASSED")
		
		else:
			color = "red"
			label.setText("Test FAILED")

		label.setAlignment(Qt.AlignTop|Qt.AlignCenter)
		l1.addWidget(label)
		widget1.setLayout(l1)
		
		css = "background-color: {:s};\n".format(color)
		css += "padding-left: 0px;\n"
		css += "margin-bottom: 0px;\n"
		css += "margin-top: 0px;\n"
		widget1.setStyleSheet(css)
		layout.addWidget(widget1)

		if (data is not None):
			# add plot widget item
			plot = pg.PlotWidget()
			plot.enableAutoRange()
			plot.showGrid(x=True, y=True)
			
			pItem = plot.getPlotItem()
			pItem.setLabel('left', 'Power', units='dB')
			pItem.setLabel('bottom', 'Frequency', units='Hz')
			
			plot.plot(data[0], data[1])
			layout.addWidget(plot)

		widget.setLayout(layout)
		return widget

	def save(self, clicked):
		"""
		Called when file->save has been clicked
		"""
		return clicked

	def exit(self, clicked):
		"""
		Called when file->exit has been clicked
		"""
		return clicked
	
	def exec(self):
		self.ui.exec_()

class XSimError(Exception):
	pass
