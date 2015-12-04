from numpy import multiply, power, add

def gain(x,gdB):
	y = multiply(power(10,gdB/20.0),x)
	return y

def add_feedback(input_signal,previous_output,gain):
    return add(input_signal,multiply(previous_output,gain))
	
