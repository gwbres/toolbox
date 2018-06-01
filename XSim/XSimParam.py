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
	
	def getFormatStr(self):
		return self.formatstr
	
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

		formatstr = self.getFormatStr()

		if (type(self) == XSimStringParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: string := "{:s}";\n'.format(self.getKey().upper(),self.getValue())) 
		
		elif (type(self) == XSimFixedPointParam):
			name = self.getKey()
			name = name.split('_')

			if (lang == 'vhdl'):
				name.insert(1,'q')
				fd.write('\tconstant {:s}: natural := {:d};\n'.format('_'.join(name).upper(), self.q)) 
				name[1] = 'm'
				fd.write('\tconstant {:s}: natural := {:d};\n'.format('_'.join(name).upper(), self.m)) 

		elif (type(self) == XSimBoolParam):
			if (lang == 'vhdl'):
				fd.write("\tconstant {:s}: std_logic := '{:d}';\n".format(self.getKey().upper(), self.getValue())) 

		elif (type(self) == XSimFloatParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: real := {:s};\n'.format(self.getKey(), formatstr.format(self.getValue())))

		elif (type(self) == XSimIntParam):
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: natural := {:d};\n'.format(self.getKey().upper(), self.getValue())) 

		elif (type(self) == XSimTimeParam):
			value = self.getValue()
			if (self.getUnit() == 'ns'):
				value /= 1e-9
			elif (self.getUnit() == 'us'):
				value /= 1e-6
			elif (self.getUnit() == 'ms'):
				value /= 1e-3
			
			if (lang == 'vhdl'):
				fd.write('\tconstant {:s}: time := {:.3f} {:s};\n'.format(self.getKey().upper(), value, self.getUnit()))
				
class XSimStringParam (XSimParam):
	def __init__(self, key, value, help=None, allowed=None, hidden=False, formatstr=None):
		super(XSimStringParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)

		self.setFormatStr(formatstr)

	def setFormatStr(self, string):
		if (string is None):
			self.formatstr = '{:s}'
		else:
			self.formatstr = string

class XSimFloatParam (XSimParam):
	def __init__(self, key, value, help=None, allowed=None, hidden=False, formatstr=None):
		super(XSimFloatParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)

		self.setFormatStr(formatstr)
	
	def setFormatStr(self, string):
		if (string is None):
			self.formatstr = '{:.3e}'
		else:
			self.formatstr = string
	
class XSimBoolParam (XSimParam):
	def __init__(self, key, value, help=None, hidden=False, formatstr=None):
		super(XSimBoolParam, self).__init__(key, value, help=help, allowed=[0,1], hidden=hidden)
		self.setValue(value)
		self.setFormatStr(formatstr)

	def setValue(self, v):
		v = int(v)
		if not(v in [0,1]):
			raise ValueError("Boolean value should either be 0 or 1")

		self.value = v	

	def setFormatStr(self, string):
		if (string is None):
			self.formatstr = '{:d}'
		else:
			self.formatstr = string
	
class XSimIntParam (XSimParam):
	def __init__(self, key, value, help=None, Range=None, hidden=False, formatstr=None):
		super(XSimIntParam, self).__init__(key, value, help=help, hidden=hidden)

		self.setRange(['-inf','+inf'])
		self.setValue(value)

		if (Range):
			self.setRange(Range)

		self.setFormatStr(formatstr)

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

	def setFormatStr(self, string):
		if (string is None): 
			self.formatstr = '{:d}' 
		else:
			self.formatstr = string
	
class XSimFixedPointParam (XSimParam):

	def __init__(self, key, value, help=None, allowed=None, Range=None, hidden=False, formatstr=None):
		"""
		(Un)Signed Fixed point object
		Q: integer part including sign bit
		M: fractionnal part
		"""
		super(XSimFixedPointParam, self).__init__(key, value, help=help, allowed=allowed, hidden=hidden)

		self.setValue(value)

		if (Range):
			self.setRange(range)

		self.setFormatStr(formatstr)

	def setRange(self, Qmin, Qmax):
		self.setQmin(Qmin)
		self.setQmax(Qmax)

	def getRange(self):
		return [self.Qmin,self.Qmax]

	def setValue(self, string):
		"""
		Assigns Q.M value from 'sQ.M' string
		"""
		if (string[0] == 's'):
			self.signed = True
		else:
			self.unsigned = False

		self.q = int(string[1:].split('.')[0])
		self.m = int(string[1:].split('.')[-1])

	def setQMValue(self, q, m):
		"""
		Assigns Q.M value 
		"""
		self.q = q
		self.m = m

	def getQ(self):
		return self.q
	
	def getM(self):
		return self.m

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

	def setFormatStr(self, string):
		if (string is None):
			self.formatstr = '{:d}'
		else:
			self.formatstr = string
	
	def isSigned(self):
		return self.signed

class XSimTimeParam (XSimParam):
	def __init__(self, key, value, help=None, hidden=False, unit='ns'):
		super(XSimTimeParam, self).__init__(key, value, help=help, hidden=hidden)
		self.setFormatStr('{:.3f}')
		self.setUnit(unit)
	
	def setFormatStr(self, formatstr):
		self.formatstr = formatstr 

	def setUnit(self, unit):
		self.unit = unit

	def getUnit(self):
		return self.unit

	def getValue(self):
		if (self.unit == 'ns'):
			return self.value * 1e-9
		elif (self.unit == 'us'):
			return self.value * 1e-6
		elif (self.unit == 'ms'):
			return self.value * 1e-3
		else:
			return self.value
