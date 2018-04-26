###############
## class signal
###############

class Signal:
	
	def __init__(self, name, _dir, 
		size=None, _type=None, _range=None
	):

		self.name = name
		self.dir = _dir
		self._isMapped = False
		self._range = _range

		if (_type is None):
			if (size is None):
				self.type = "std_logic"
				self.size = 0
			else:
				if (size == 0):
					self.type = "std_logic" 
					self.size = 0
				else:
					self.type = "std_logic_vector" 
					self.size = size
		else:
			self.size = 0
			self.type = _type

	def __str__(self):
		return "signal '{:s}', direction: {:s}, type: {:s}\n".format(self.getName(),self.getDir(),self.getType()) 

	def getName(self):
		return self.name

	def getDir(self):
		return self.dir
	
	def getType(self):
		if (self.type == "std_logic_vector"):
			return "std_logic_vector ({:d} downto 0)".format(self.getSize()-1)
		else:
			return self.type
	
	def getSize(self):
		return self.size

	def isMapped(self):
		return self._isMapped

	def declare(self, fd, default=None):
		"""
		Declares self in opened vhdl file
		default value can be optionnaly assigned
		"""
		fd.write('\tsignal {:s}: {:s}'.format(self.getName(), self.getType()))
		if (default):
			fd.write(':= {:s}'.format(default))

		if (self._range is not None):
			fd.write(' range 0 to {:d}'.format(self._range-1))

		fd.write(';\n')
