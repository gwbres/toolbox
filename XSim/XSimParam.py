class XSimParam:

	def __init__(self, key, value, help=None, allowed=None, hidden=False):
		self.key = key
		self.value = value
		self.setDefaultValue(value)
		self.setHelpString(help)
		self.setAllowedValues(allowed)
		self.setHidden(hidden)
	
	def getKey(self):
		return self.key
	
	def getDefaultValue(self):
		return self.default
	
	def setDefaultValue(self, v):
		self.default = v

	def setAllowedValues(self, v):
		self.aValues = v 
	
	def getAllowedValues(self):
		return self.aValues
	
	def setValue(self, v):
		allowed = self.getAllowedValues()
		if (allowed is None):
			self.value = v
		else:
			if (v in allowed):
				self.value = v
	
	def getValue(self):
		return self.value

	def getHelpString(self):
		return self.help
	
	def setHelpString(self, string):
		self.help = string

	def setHidden(self, h):
		self.hidden = h
	
	def isHidden(self):
		return self.hidden
	
	def declare(self, fd, lang='vhdl'):
		if (lang != "vhdl"):
			raise ValueError('verilog not supported yet')

		if (type(self) == XSimStringParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: string := "{:s}";\n'.format(self.getKey().upper(),self.getValue())) 
		
		elif (type(self) == XSimFixedPointParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant Q0: natural := {:d};\n'.format(self.q)) 
				fd.write('\tconstant M0: natural := {:d};\n'.format(self.m)) 

		elif (type(self) == XSimBoolParam):
			if (lang == 'vhdl'):
				fd.write("\tconstant {:s}: std_logic := '{:d}';\n".format(self.getKey().upper(), self.getValue())) 

		elif (type(self) == XSimFloatParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: real := {:.6e};\n'.format(self.getKey().upper(), self.getValue())) 

		elif (type(self) == XSimIntParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: natural := {:d};\n'.format(self.getKey().upper(), self.getValue())) 
class XSimStringParam (XSimParam):
	def __init__(self, key, value, help=None, allowed=None, hidden=False):
		super(XSimStringParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)

class XSimFloatParam (XSimParam):
	def __init__(self, key, value, help=None, allowed=None, hidden=False):
		super(XSimFloatParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)
	
class XSimBoolParam (XSimParam):
	def __init__(self, key, value, help=None, hidden=False):
		super(XSimBoolParam, self).__init__(key, value, help=help, allowed=[0,1], hidden=hidden)
		self.setValue(value)

	def setValue(self, v):
		v = int(v)
		if not(v in [0,1]):
			raise ValueError("Boolean value should either be 0 or 1")

		self.value = v
	
class XSimIntParam (XSimParam):
	def __init__(self, key, value, help=None, Range=None, hidden=False):
		super(XSimIntParam, self).__init__(key, value, help=help, hidden=hidden)

		self.setRange(['-inf','+inf'])
		self.setValue(value)

		if (Range):
			self.setRange(Range)

	def setValue(self, v):
		[m, M] = self.getRange()
		_ranged = False

		if (m != '-inf'):
			if (v < int(m)):
				self.value = int(m)
				_ranged = True

		if (M != '+inf'):
			if (v > int(M)):
				self.value = int(M)
				_ranged = True

		if not(_ranged):
			self.value = int(v)

	def getRange(self):
		return self.range

	def setRange(self, R):
		"""
		R: [min,max]
		"""
		self.range = R
	
class XSimFixedPointParam (XSimParam):

	def __init__(self, key, value, help=None, allowed=None, Range=None, hidden=False):
		"""
		(Un)Signed Fixed point object
		Q: integer part including sign bit
		M: fractionnal part
		"""
		super(XSimFixedPointParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)

		self.setValue(value)

		if (Range):
			self.setRange(range)

	def setRange(self, Qmin, Qmax):
		self.setQmin(Qmin)
		self.setQmax(Qmax)

	def getRange(self):
		return [self.Qmin,self.Qmax]

	def setValue(self, string):
		if (string[0] == 's'):
			self.signed = True
		else:
			self.unsigned = False

		self.q = int(string[1:].split('.')[0])
		self.m = int(string[1:].split('.')[-1])

	def qmax(self):
		return self.Qmax

	def qmin(self):
		return self.Qmin

	def setQmin(self, q):
		self.Qmin = q
	
	def setQmax(self, q):
		self.Qmax = q

	def __str__(self):
		if (self.isSigned()):
			string = "sfix "
		else:
			string = "ufix "
		string += "{:d}.{:d}".format(self.q,self.m)
		return string
	
	def isSigned(self):
		return self.signed
