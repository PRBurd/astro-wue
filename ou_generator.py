import numpy as np


class DimensionError(Exception):
    pass


# iterates over all indices of an n-dimensional array, which shape is given in the 'size' argument
class Iterator:

    def __init__(self, size):
        self.size = size
        self.itlist = [0]*len(size)

    def __iter__(self):
        while self.itlist[-1] < self.size[-1]:
            for i in range(len(self.size)):
                if self.itlist[i] >= self.size[i]:
                    self.itlist[i] = 0
                    self.itlist[i+1] += 1
            yield tuple(self.itlist)
            self.itlist[0] += 1


# converts multiple types into the type np.ndarray
def to_nparray(para, size, all_para_floats):
    if callable(para):
        para = para(size)
    elif type(para) == np.ndarray:
        if not para.shape == size:
            raise DimensionError("shape of parameter is not equal to size")
    elif hasattr(para, '__iter__'):
        para = np.array(para)
        if not para.shape == size:
            raise DimensionError("shape of parameter is not equal to size")
    elif not all_para_floats:
        para = np.full(size, para)
    return para


# Main-function generates a MC simulated noise by the Ornstein-Uhlenbeck-SDE
def ou_generate(iterations, theta, sigma, mu, x0, dt=1, noise_generator=np.random.standard_normal, noise_parameters={}, size=(1, ), unpack=True):
    # validation and preparation of the parameters

    # size is forced into a tuple
    if type(size) == int:
        size = (size, )
    size = tuple(size)

    # check if all run parameters (theta, sigma, mu) are float if not make them all to arrays
    all_para_floats = isinstance(theta, (int, float)) and isinstance(sigma, (int, float)) and isinstance(mu, (int, float))
    theta = to_nparray(theta, size, all_para_floats)
    sigma = to_nparray(sigma, size, all_para_floats)
    mu = to_nparray(mu, size, all_para_floats)

    # theta is only used with dt, so it will be once resized here
    theta = theta * dt
    # mu is only used with theta, so this value is calculated once here
    mu = theta * mu

    # generate the noise and iter_size
    noise_parameters['size'] = size+(iterations, )
    noise = noise_generator(**noise_parameters)
    # iter_size is an iterator, that iterates over a slice of the size 'size'. So it can be used to iterate over the
    # complete theta, sigma, mu arrays or over a slice, that represents one time step, of the noise array
    iter_size = tuple([slice(0, length, 1) for length in size])

    # resize noise with time step length
    noise = noise*dt**0.5

    # initialize start values in the noise array, where t=0 (last index = 0)
    if x0 is None:
        pass
    elif callable(x0):
        x0 = x0(size)
        noise[iter_size+(0, )] = x0[iter_size]
    elif type(x0) == np.ndarray:
        if x0.shape == size:
            noise[iter_size+(0, )] = x0[iter_size]
        else:
            raise DimensionError("parameter shape is not equal to size")
    elif hasattr(x0, '__iter__'):
        x0 = np.array(x0)
        if x0.shape == size:
            noise[iter_size+(0, )] = x0[iter_size]
        else:
            raise DimensionError("parameter shape is not equal to size")
    else:
        noise[iter_size+(0, )] = x0

    # main iteration process
    if all_para_floats:
        for i in range(iterations-1):
            noise[iter_size+(i+1, )] = noise[iter_size+(i, )] * (1-theta) + mu + sigma*noise[iter_size+(i+1, )]
    else:
        for i in range(iterations-1):
            noise[iter_size+(i+1, )] = noise[iter_size+(i, )] * (1-theta[iter_size]) + mu[iter_size] + sigma[iter_size]*noise[iter_size+(i+1, )]

    # discards the wrapping array in case size = (1, ) and feature is enables
    if size == (1, ) and unpack:
        return noise[0, 0:iterations]
    else:
        return noise


# These are wrappers, to make functions usable as arguments in ou_generate, that do not full fill it prerequisites

# Use this if your function has no size argument, but also doesn't need more arguments.
# It works by calculating the function once per cell in an size shaped array,
# saving the result in an array and returning that array.
def wrap_no_size(func):
    def wrapper(size, *args, **kwargs):
        result = np.zeros(size, dtype=float)
        for i in Iterator(size):
            result[i] = func(*args, **kwargs)
        return result
    return wrapper


# This wrapper is useful, when the method has size, but also needs additional arguments. This is not necessary,
# when the noise function needs additional arguments, these can be given as kwargs in noise_parameter

# sizepos is the position of size in args (if in args). Dummy value must be given.
# If size not in args, sizepos needs to be set to -1
def wrap_additional_arguments(func, args, kwargs, sizepos=-1):
    def wrapper(size):
        if sizepos != -1:
            args[sizepos] = size
        else:
            kwargs['size'] = size
        return func(*args, **kwargs)
    return wrapper


# This wrapper is useful when the function already has a size argument, but it is named differently.
def wrap_rename_size(func, name):
    def wrapper(*args, **kwargs):
        kwargs[name] = kwargs['size']
        del kwargs['size']
        return func(*args, **kwargs)
    return wrapper


# This combines the need of additional arguments and the lack of a size argument. This was implemented,
# because it is not trivial to wrap no_size and additonal_arguments into each other.
def wrap_no_size_and_additional_arguments(func, args, kwargs):
    def wrapper(size):
        result = np.zeros(size, dtype=float)
        for i in Iterator(size):
            result[i] = func(*args, **kwargs)
        return result
    return wrapper
