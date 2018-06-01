class XSimResult:

	def __init__(self, *args, **kwargs):
		self.setTitle('')
		self.setMethod(None)
		self.setStatus(False)
		self.setExtraString(None)
		self._x = None
		self._y = None

		for key, value in kwargs.items():
			if key == 'title':
				self.setTitle(value)
			elif key == 'method':
				self.setMethod(value)
			elif key == 'extra':
				self.setExtraString(value)
			elif key == 'status':
				self.setStatus(value)
			elif key == 'x':
				self._x = value
			elif key == 'y':
				self._y = value
			elif key == 'data':
				self._x = value[0]
				self._y = value[1]

	def __str__(self):
		string = '{:s} | '.format(self.title)

		if (self.getMethod()):
			string += 'Method: "{:s}" | '.format(self.getMethod())

		if (self.getExtraString()):
			string += '{:s} | '.format(self.getExtraString())

		if (self.getStatus()):
			string += 'PASSED'
		else:
			string += "FAILED"

		return string

	def setTitle(self, title):
		self.title = title

	def getTitle(self):
		return self.title

	def setStatus(self, sts):
		self.status = sts

	def getStatus(self):
		return self.status

	def setExtraString(self, extra):
		self.extra = extra
	
	def getExtraString(self):
		return self.extra

	def setData(self, xy):
		self._x = xy[0]
		self._y = xy[1]
	
	def getData(self):
		return [self.getXAxis(), self.getYAxis()]

	def getXAxis(self):
		return self._x
	
	def getYAxis(self):
		return self._y
	
	def setMethod(self, m):
		self.method = m

	def getMethod(self):
		return self.method
