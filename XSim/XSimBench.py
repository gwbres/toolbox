from XSimParam import *
from XSimStimulus import *

class XSimBench:
	"""
	Simulation bench object
	"""

	def __init__(self, dicts):
		# attributes
		self.lang = None
		self.sample_rate = 100E6

		self.libs = []
		self.libs.append(["ieee","std_logic_1164"]) # always needed
		
		# params
		self.dicts = dicts
		self.params = []

		self.stimuli = []

		for d in dicts:
			if (d['type'] == 'attribute'):
				try:
					lang = d['lang']
					if (lang not in(['vhdl'])):
						raise ValueError("lang {:s} is not supported yet".format(lang))
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
					fxp = XSimFixedPointParam(key, value, help=d['help'])
					
					try:
						fxp.setRange(d['Qmin'],d['Qmax'])
					except KeyError:
						pass
					
					mhelp = fxp.getHelpString()
					mhelp += ' [{:d}:{:d}]'.format(d['Qmin'],d['Qmax'])
					fxp.setHelpString(mhelp)

					self.params.append(fxp)
					self.addSimulationLibrary(['ieee_proposed', "fixed_pkg"]) # will be required
					
				elif (ptype == 'string'):
					value = d['value']
					self.params.append(XSimStringParam(key, value, help=d['help'], allowed=d['values']))

				elif (ptype == 'float'):
					value = d['value']

					allowed = None
					try:
						allowed = d['values']
					except KeyError:
						pass

					self.params.append(XSimFloatParam(key, value, help=d['help'], allowed=allowed))

				elif (ptype == 'bool'):
					value = d['value']
					self.params.append(XSimBoolParam(key, value, help=d['help']))

				elif (ptype == 'integer'):
					value = d['value']
					ipm = XSimIntParam(key, value, help=d['help'])
					
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
			
			elif (d['type'] == 'stimulus'):
				if (d['stype'] == 'sinewave'):
					a = d['amplitude']
					f = d['frequency']

					options = None
					try:
						options = d['options']
					except KeyError:
						pass

					stm = XSimSineWaveStimulus(a, f, 1024, sample_rate=self.getSampleRate(), options=options)
					self.stimuli.append(stm)
		
		self.checkEnvSanity()

	def runCLI(self):
		# build command line interface
		cli = "\n\033[91mxsim>\033[0m\n"

		validate = False

		for param in self.getParams():
			key = param.getKey()
			
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
			key = user.split(' ')[0]
			value = user.split(' ')[1]

			# replace in dict
			found = False
			for d in self.dicts:
				try:
					if (d['key'] == key):
						d['value'] = value
						found = True
				except KeyError:
					pass

			if not(found):
				print("Unknown parameter {:s}".format(key))

			user = input()

	def __str__(self):
		return str(self.dicts)

	###################
	# XSim attributes #
	###################
	def getLanguage(self):
		return self.lang

	###################
	# XSim Parameters #
	###################
	def getParams(self):
		return self.params

	def getNumberOfParams(self):
		return len(self.params)

	def searchParamsByType(self, _type):
		results = []
		for param in self.params:
			if (type(param) == _type):
				results.append(param)
		return results

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
		results = []
		for stim in self.stimuli:
			if (stim.getType() == _type):
				results.append(stim)
		return results

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
		if (self.lang == "vhdl"):
			self.writeVHDLPackage(fp)
		else:
			raise ValueError("Verilog simulation is not supported yet")

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
		lutsize = 0
		for stm in self.getStimuli():
			lutsize += stm.numberOfSymbols()
		fd.write('\tconstant N_SYMBOLS: natural := {:d};\n'.format(lutsize))
		fd.write('\ttype mem is array(0 to N_SYMBOLS-1) of real;\n')

		for i in range(0, self.numberOfStimuli()):
			fd.write('\n\tconstant {:s}lut: mem := ('.format(str(self.stimuli[i])))
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

class XSimError(Exception):
	pass