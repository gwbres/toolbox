################
# class ip-core
################

from Signal import *
from Generic import *

class IPCore:
	"""
	Entity
	list of ports
	list of generic parameters
	"""

	def __init__(self, entity, ports, generics=None):
		self.entity = entity 
		self.ports = ports
		self.generics = generics

	def __init__(self, fp):
		ext = fp.split(".")[1] 
		if (ext == "vhd"):
			[entity, ports, generics] = self._vhdl_parser(fp)
		else:
			print("{:s} file type is not supported yet".format(ext))

		self.entity = entity
		self.ports = ports
		self.generics = generics
	
	def _vhdl_parser(self, fp):
		fd = open(fp,"r")
		done = False
		signals = []
		generics = []
		parsing_ports = False
		parsing_generics = False
		
		for line in fd:
			line = line.strip()
			line = line.strip('\n')
			content = line.split(" ")

			if (parsing_ports):	
				if (len(content) > 2):
					name = content[0].strip(":").strip()
					_dir = content[1]
					if "vector" in line:
						_type = content[2].split("(")[0].strip(";")
						try:
							size = int(content[2].split("(")[1].split("downto")[0])+1
						except ValueError: # std_logic_vector($generic-1)
							size = None
					
						signals.append(Signal(name,_dir,size=size))

					elif "std_logic" in line:
						size = None
						signals.append(Signal(name,_dir,size=size))
				else:
					parsing_ports = False

			elif (parsing_generics):
				if (len(content) > 2):
					name = content[0].strip(":").strip()
					_type = "std_logic"
					generics.append(Generic(name))

				else:
					parsing_generics = False

			else:
				if ");" in content:
					if "end" in content:
						parsing = False
			
				elif "port" in content:
					parsing_ports = True

				elif "generic" in content:
					parsing_generics = True

				elif "entity" in content:
					if "is" in content:
						entity = content[1]
					elif "end" in content:
						break
					
		fd.close()
		return [entity, signals, None]
	
	def __str__(self):
		"""
		Prints IP core in human readable format
		"""
		string = "---- IP core ----\n"
		string += "Entity: {:s}\n".format(self.entity)
		
		if (self.generics is not None):
			string += "Generics: {:s}\n".format(",".join(tuple(self.getGenerics())))

		string += "Ports: \n"
		for port in self.getPorts():
			string += "\t{:s}".format(str(port))
		string += "-----------------\n"
		return string

	def printPorts(self):
		str = "ports: "
		for port in self.ports:
			str += str(port)
		return str

	def printGenerics(self):
		str = "generics: "
		for generic in self.generics:
			str += str(generic)
		return str

	def __eq__(self, coreB):
		"""
		CoreA == CoreB comparison operator
		returns true if self & coreB have same instance name
		"""
		if (self.getEntity() == coreB.getEntity()):
			return True
		else:
			return False

	def hasSignal(self, sig):
		"""
		Returns true if self
		does have a signal with matching name & type
		"""
		for port in self.getPorts():
			if (port.getName() == sig.getName()):
				if (port.getType() == sig.getType()):
					return True
		return False

	def hasGeneric(self, gen):
		"""
		Returns true if self
		does have a generic with matching name & type
		"""
		for gen in self.getGenerics():
			if (gen.getName() == gen.getName()):
				if (gen.getType() == gen.getType()):
					return True
		return False

	def getEntity(self):
		return self.entity

	def getPorts(self):
		return self.ports

	def getGenerics(self):
		return self.generics

	def isMapped(self):
		"""
		self is declared as mapped when
		all of its signals & parameters have been mapped
		"""
		for port in self.getPorts():
			if not(port.isMapped()):
				return False

		if (self.getGenerics() is not None):
			for gen in self.getGenerics():
				if not(gen.isMapped()):
					return False

		return True

	def declareAsComponent(self, fd):
		"""
		Declares self in .vhdl file
		as a component
		"""
		fd.write("\tcomponent {:s} is\n".format(self.getName()))
		fd.write("\tport (\n")
		for port in self.getPorts()[:-1]:
			fd.write("\t\t{:s}: {:s} {:s};\n".format(port.getName(),port.getDir(),port.getType()))
		fd.write("\t\t{:s}: {:s} {:s};\n".format(ports[-1].getName(),ports[-1].getDir(),ports[-1].getType()))
	
	def map(self, fd, inst, core):
		"""
		Maps self to another core in fd
		will only map signals that match
		core: can either be another IP core
		or a list of signals

		#TODO: add isMapped() logic
		"""
		if (type(core) is IPCore):
			fd.write("\n\t{:s}_{:d}: entity work.{:s}\n".format(self.getEntity(),inst,self.getEntity()))

			if (self.getGenerics() is not None):
				fd.write("\tgeneric map (\n")
				for gen in self.getGenerics()[:-1]:
					if (core.hasGeneric(gen)):
						fd.write("\t\t{:s} => {:s},\n".format(gen.getName(),gen.getName()))
				if (core.hasGeneric(self.getGenerics()[-1])):
					fd.write("\t\t{:s} => {:s},\n".format(self.getGenerics()[-1].getName(),self.getGenerics()[-1].getName()))
				fd.write("\t) port map (\n")
			else:
				fd.write("\tport map (\n")

			for port in self.getPorts()[:-1]:
				if (core.hasSignal(port)):
					fd.write("\t\t{:s} => {:s},\n".format(port.getName(),port.getName()))
			if (core.hasSignal(ports[-1])):
				fd.write("\t\t{:s} => {:s}\n".format(ports[-1].getName(),ports[-1].getName()))
			fd.write("\t);\n")
			return 0

		elif (type(core) is list):
			fd.write("\n\t{:s}_{:d}: entity work.{:s}\n".format(self.getEntity(),inst,self.getEntity()))

			_genericMap = False
			for sig in core:
				if (type(sig) is Generic):
					if (not(_genericMap)):
						fd.write("\tgeneric map (\n")
						_genericMap = True
					
					lastGen = sig

			for sig in core[:-1]:
				if (type(sig) is Generic):
					if (self.hasGeneric(sig)):
						if sig == lastGen:
							fd.write("\t\t{:s} => {:s}\n".format(sig.getName(),sig.getName()))
						else:
							fd.write("\t\t{:s} => {:s},\n".format(sig.getName(),sig.getName()))
			
			if (_genericMap):
				fd.write("\t) port map (\n")
			else:
				fd.write("\tport map (\n")

			for sig in core[:-1]:
				if (type(sig) is Signal):
					if (self.hasSignal(sig)):
						fd.write("\t\t{:s} => {:s},\n".format(sig.getName(),sig.getName()))

			if (type(core[-1]) is Signal):
				if (self.hasSignal(core[-1])):
					fd.write("\t\t{:s} => {:s}\n".format(core[-1].getName(),core[-1].getName()))
				fd.write("\t);\n")

			return 0

		else:
			print("Can only map an IP core to either")
			print("another IP core or a list of matching signals\n")
			return -1
