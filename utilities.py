from numpy import asarray,iinfo,dtype,log10,power

def pcm2float(x,dt='float64'):
	"""Convert a PCM signal to floating point data with a range from -1 to 1.
	
	ARGUMENTS
	x : array
		Input array of integral type.
	dtype : data type, optional
		Desired (floating point) data type.
	
	RETURNS
	numpy.ndarray
		Normalised floating point data.
				
	"""
	x = asarray(x) # Convert to numpy array
	if x.dtype.kind not in 'iu': # Check that x is a signed (i) or unsinged (u) integer
		raise TypeError("x must be an array of integers")
	dt = dtype(dt) # Convert string to data type object
	if dt.kind != 'f': # Check that dtype is a floating point type
		raise TypeError("'dtype' must be a floating point type")
	i = iinfo(x.dtype) # Find machine limits for data type
	abs_max = 2**(i.bits-1) # Find absolute max limits
	offset = i.min + abs_max # Find offset
	return (x.astype(dt)-offset)/abs_max # Convert signal to floating point type

def float2pcm(x, dt='int16'):
	x = asarray(x)
	if x.dtype.kind != 'f':
		raise TypeError("x must be a float array")
	dt = dtype(dt)
	if dt.kind not in 'iu':
		raise TypeError("'dtype' must be an integer type")
	i = iinfo(dt)
	abs_max = 2**(i.bits-1)
	offset = i.min+abs_max
	return (x*abs_max+offset).clip(i.min,i.max).astype(dtype)

def amp2dB(x):
	y = 20*log10(x)
	return y

def dB2amp(x):
	y = power(10,x/20)
	return y