import random
import numpy as np
import scipy.signal as signal

class XSimStimulus:
	
	def __init__(self, nsymbols, sample_rate=100E6):	
		self.symbols = np.zeros(nsymbols)
		self.nsymbols = nsymbols
		self.sample_rate = sample_rate

	def numberOfSymbols(self):
		"""
		Returns number of symbols to be generated
		"""
		return self.nsymbols
	
	def getSymbols(self):
		"""
		Returns symbols that were generated
		"""
		return self.symbols
	
	def getSampleRate(self):
		return self.sample_rate

	def getType(self):
		return 'generic-stimulus'
	
	def whiteNoise(self, psd, fs, mean=None):
		"""
		Generates pseudo random sequence at specified PSD level
		psd: required density [dBc/hz]
		fs: sample rate
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

	def __init__(self, a, f, nsymbols, sample_rate=100E6, options=None):
		super(XSimSineWaveStimulus, self).__init__(nsymbols, sample_rate=sample_rate)

		nsymbols = self.numberOfSymbols()
		t = np.arange(nsymbols)/sample_rate

		add_noise = False
		noise_type = None
		noise_density = None
		gamma = np.zeros(nsymbols)

		use_mod = False
		tone_type = None
		tone_power = None
		tone_freq = None
		alpha = np.zeros(nsymbols)
		
		if (options is not None):
			try:
				add_noise = True
				noise_type = options['addnoise']['type']
				noise_density = options['addnoise']['density']
				if (noise_type == 'white'):
					gamma += self.whiteNoise(noise_density, sample_rate, mean=None) 

				if (noise_type == 'pink'):
					gamma += self.pinkNoise() 
			except KeyError:
				pass

			try:
				use_mod = True
				tone_freq = options['AM-Tone']['freq']
				tone_power = options['AM-Tone']['power']
				tone_type = 'AM'
				alpha = 10**(tone_power/20)

			except KeyError:
				pass
		
		self.symbols = (1+alpha)*a*np.sin(2*np.pi*f*t) + gamma
	
	def getType(self):
		return 'sinewave'

	def __str__(self):
		return 'sine'

class XSimRampStimulus (XSimStimulus):
	
	def __init__(self, a, N, nsymbols, sample_rate=100E6, options=None):
		super(XSimRampStimulus, self).__init__(nsymbols, sample_rate=sample_rate)

		sign = 1.0
		poff = 0.0

		add_noise = False
		noise_type = None
		noise_density = None
		alpha = np.zeros(nsymbols)

		if (options is not None):
			try:
				decreasing = options['down']
				if (decreasing):
					sign = -1.0

			except KeyError:
				pass

			try:
				noise_type = options['addnoise']['type']
				noise_density = options['addnoise']['density']
				
				if (noise_type == 'white'):
					alpha += self.whiteNoise(noise_density, sample_rate) 

				elif (noise_type == 'pink'):
					alpha += self.pinkNoise()
			
			except KeyError:
				pass

		t = np.linspace(0, 1, num=nsymbols)

		self.symbols = alpha + a * signal.sawtooth(sign*2*np.pi*N*t + poff)
