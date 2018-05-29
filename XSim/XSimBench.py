from XSimParam import *

class XSimBench:
	"""
	Simulation bench object
	"""

	def __init__(self, dicts):
		# required default attributes
		self.lang = "vhdl"
	
		self.libs = []
		self.libs.append(["ieee","std_logic_1164"]) # always needed
		
		self.dicts = dicts
		self.params = []

		for d in dicts:
			ptype = d['type']
			if (ptype == 'attribute'):
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

			elif (ptype == 'parameter'):
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
					self.params.append(XSimFloatParam(key, value, help=d['help'], allowed=d['values']))
					self.addSimulationLibrary(['ieee_proposed', "float_pkg"])

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

	def __len__(self):
		return len(self.dicts)

	def getParams(self):
		return self.params

	def searchByType(self, _type):
		results = []
		for param in self.params:
			if (type(param) == _type):
				results.append(param)
		return results

	def getFixedPointParams(self):
		return self.searchByType(XSimParam.XSimFixedPointParam)

	def getBooleanParams(self):
		return self.searchByType(XSimParam.XSimBoolParam)
	
	def getStringParams(self):
		return self.searchByType(XSimParam.XSimStringParam)
	
	def getFloatParams(self):
		return self.searchByType(XSimParam.XSimFloatParam)

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
		for param in self.params:
			param.declare(fd, lang=self.lang)
		
		"""
		if (self.simulateTUSER()):
			fd.write('\tconstant SUPPORT_TUSER: std_logic := "1";\n')
			fd.write('\tconstant TUSER_SIZE: natural := {:d};\n'.format(self.tuser))
		
		fd.write("\t ---- XSIM stimuli ----- \n")
		for lut in self.luts:
			lut.declare(fd)

		for lut in self.luts:
			fd.write(str(lut))
		"""
		
		fd.write("\t ------ end XSIM params -------\n")

		fd.write("end package package_tb;\n\n")
		
		fd.write("package body package_tb is\n")
		fd.write("end package body package_tb;\n")
		fd.close()
