# Qt5
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem 

SUPPORTED_STATUS = ['PASSED', 'FAILED', 'NOT VERIFIED']
STATUS_COLORS = ["#04FF9D", "red", "#0487FF"]

class XSimResult:

	def __init__(self, *args, **kwargs):
		self.setTitle('')
		self.setMethod(None)
		self.setStatus('NOT VERIFIED')
		self.setExtraString(None)

		# plot
		self._xy = None
		self.plotSettings = None

		for key, value in kwargs.items():
			if key == 'title':
				self.setTitle(value)
			elif key == 'method':
				self.setMethod(value)
			elif key == 'extra':
				self.setExtraString(value)
			elif key == 'status':
				self.setStatus(value)

	def header(self):
		tree = QTreeWidget()
		items = ['Test']
		data = [self.getTitle()]

		if (self.getMethod()):
			items.append('Method')
			data.append(self.getMethod())

		if (self.getExtraString()):
			items.append('Infos')
			data.append(self.getExtraString())

		items.append('Status')
		data.append(self.getStatus())

		head = QTreeWidgetItem(items)
		tree.setHeaderItem(head)

		line = QTreeWidgetItem(data)
		tree.addTopLevelItem(line)
		for i in range(0, tree.columnCount()):
			tree.resizeColumnToContents(i)

		return tree

	def setTitle(self, title):
		self.title = title

	def getTitle(self):
		return self.title

	def setStatus(self, sts):
		if (not sts in SUPPORTED_STATUS):
			raise ValueError('Status value {:s} is not supported'.format(sts))

		self.status = sts

	def getStatus(self):
		return self.status

	def getStatusColor(self):
		return STATUS_COLORS[SUPPORTED_STATUS.index(self.getStatus())]

	def setExtraString(self, extra):
		self.extra = extra
	
	def getExtraString(self):
		return self.extra

	def addDataSet(self, xy):
		if (self._xy is None):
			self._xy = [xy]
		else:
			self._xy.append(xy)
	
	def getDataSets(self):
		return self._xy 

	def getDataSet(self, index):
		return self._xy[index]

	def addPlotSettings(self, Dict):
		if (self.plotSettings is None):
			self.plotSettings = [Dict]
		else:
			self.plotSettings.append(Dict)

	def getPlotSettings(self, index):
		try:
			return self.plotSettings[index]
		except TypeError:
			return None

	def setMethod(self, m):
		self.method = m

	def getMethod(self):
		return self.method
