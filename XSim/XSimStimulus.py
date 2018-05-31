import random
import numpy as np
import scipy.signal as signal

class XSimStimulus:
	
	def __init__(self, key, nsymbols, sample_rate=100E6):	
		self.setKey(key)
		self.setNSymbols(nsymbols)
		self.symbols = np.zeros(nsymbols)
		self.sample_rate = sample_rate

	def numberOfSymbols(self):
		"""
		Returns number of symbols to be generated
		"""
		return self.nsymbols

	def setNSymbols(self, N):
		self.nsymbols = N
	
	def getKey(self):
		return self.key
	
	def setKey(self, key):
		self.key = key
	
	def getSymbols(self):
		"""
		Returns symbols that were generated
		"""
		return self.symbols

	def getSampleRate(self):
		return self.sample_rate

	def getType(self):
		return 'generic-stimulus'
	
	def whiteNoise(self, psd, mean=None):
		"""
		Generates pseudo random sequence at specified PSD level
		psd: required density [dBc/hz]
		mean: optionnal DC offset
		"""
		if mean is None:
			mean = 0.0

		sigma = np.sqrt(np.power(10,psd/20))
		return np.random.normal(loc=mean, scale=sigma, size=self.numberOfSymbols())

	def pinNoise(self):
		"""
		Generates pink noise (-10 dB/dec) shape
		"""
		uneven = self.numberOfSymbols()%2
		state = np.random.RandomState()
		x = state.randn(self.numberOfSymbols()//2+1+uneven)
		s = np.sqrt(np.arange(len(x))+1.)
		y = (np.fft.irfft(x/s)).real
		if uneven:
			y = y[:-1]
		return y

class XSimSineWaveStimulus (XSimStimulus):

	def __init__(self, key, a, f, nsymbols, sample_rate=100E6, options=None):
		super(XSimSineWaveStimulus, self).__init__(key, nsymbols, sample_rate=sample_rate)

		self.freq = f
		self.ampl = a

		nsymbols = self.numberOfSymbols()

		add_noise = False
		noise_type = None
		noise_density = None
		self.gamma = np.zeros(nsymbols)

		use_mod = False
		tone_type = None
		tone_power = None
		tone_freq = None
		self.alpha = np.zeros(nsymbols)
		
		if (options is not None):
			try:
				add_noise = True
				noise_type = options['addnoise']['type']
				noise_density = options['addnoise']['density']
				if (noise_type == 'white'):
					self.gamma += self.whiteNoise(noise_density, mean=None) 

				if (noise_type == 'pink'):
					self.gamma += self.pinkNoise() 
			except KeyError:
				pass

			try:
				use_mod = True
				tone_freq = options['AM-Tone']['freq']
				tone_power = options['AM-Tone']['power']
				tone_type = 'AM'
				self.alpha = 10**(tone_power/20)

			except KeyError:
				pass
		
	def getType(self):
		return 'sinewave'

	def getFrequency(self):
		return self.freq
	
	def getAmplitude(self):
		return self.ampl

	def __str__(self):
		string = "freq: {:.3e} Hz | ampl: {:.3e} \n".format(self.getFrequency(), self.getAmplitude())
		return string
	
	def _generate(self):
		t = np.arange(self.numberOfSymbols())/self.getSampleRate()
		self.symbols = (1+self.alpha)*self.getAmplitude()*np.sin(2*np.pi*self.getFrequency()*t) + self.gamma

class XSimSquareWaveStimulus (XSimStimulus):
	def __init__(self, key, a, nperiods, nsymbols, sample_rate=100E6, options=None):
		super(XSimSquareWaveStimulus, self).__init__(key, nsymbols, sample_rate=sample_rate)

		self.duty = 0.5
		self.a = a
		self.nperiods = nperiods

		self.alpha = np.zeros(nsymbols)

		if (options is not None):
			try:
				noise_type = options['addnoise']['type']
				noise_density = options['addnoise']['density']

				if (noise_type == 'white'):
					self.alpha += self.whiteNoise(noise_density)

				if (noise_type == 'pink'):
					self.alpha += self.pink()
			
			except KeyError:
				pass

			try:
				self.duty = options['options']['duty']
			except KeyError:
				pass

	def getAmplitude(self):
		return self.a

	def getDutyCycle(self):
		return self.duty

	def getNumberOfPeriods(self):
		return self.nperiods

	def _generate(self):
		t = np.linspace(0, 1, num=self.numberOfSymbols())
		self.symbols = self.alpha + self.getAmplitude() * signal.square(2*np.pi*self.getNumberOfPeriods()*t, duty=self.getDutyCycle())

class XSimRampStimulus (XSimStimulus):
	
	def __init__(self, key, a, nperiods, nsymbols, sample_rate=100E6, options=None):
		super(XSimRampStimulus, self).__init__(key, nsymbols, sample_rate=sample_rate)

		self.sign = 1.0
		self.poff = 0.0
		self.nperiods = nperiods

		add_noise = False
		noise_type = None
		noise_density = None
		self.alpha = np.zeros(nsymbols)

		if (options is not None):
			try:
				decreasing = options['down']
				if (decreasing):
					self.sign = -1.0

			except KeyError:
				pass

			try:
				noise_type = options['addnoise']['type']
				noise_density = options['addnoise']['density']
				
				if (noise_type == 'white'):
					self.alpha += self.whiteNoise(noise_density) 

				elif (noise_type == 'pink'):
					self.alpha += self.pinkNoise()
			
			except KeyError:
				pass

	def getAmplitude(self):
		return self.a
	
	def getNumberOfPeriods(self):
		return self.nperiods
	
	def getPhaseOffset(self):
		return self.poff
	
	def getSign(self):
		return self.sign

	def _generate(self):
		t = np.linspace(0, 1, num=self.numberOfSymbols())
		self.symbols = self.alpha + self.getAmplitude() * signal.sawtooth(sign*2*np.pi*self.getNumberOfPeriods()*t + self.getPhaseOffset())
