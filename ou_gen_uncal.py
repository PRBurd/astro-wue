import numpy as np
import ou_generator as ou
import time


"""
The format used to save the np.array with the OU-time series is a 2d ndarray with dtype=object. 
Its shape is (amount, 4), where amount is the amount of time series saved in the array. 
In the second dimension the [time series, theta, mu, sigma] for each time series is stored in this order. 
"""


"""
While this is code is not written to be imported as a module and calling this as one will generate the exact
time series used in the thesis/paper, one can shift all the non essential code into a if __name__ == '__main__' clause. 
It might be easier to just copy the repack2 method into the program where it is needed. 
"""

"""
This code as it is generates the uncalibrated OU time series with whicht the extraction method is gauged.
"""

# set the amount, length and dt of the time series to generate
amount = 100000
length = 1190
dt = 0.1
seed = 982947937

# just renaming the fuction, so that one does not need to write np.random.normal all the time
normal = np.random.normal


# repacks the generated time series in the chosen format
def repack(theta, sigma, mu, noise):
    result = np.empty(theta.shape+(4, ), dtype=object)
    for i in ou.Iterator(theta.shape):
        one_chain = slice(0, noise.shape[-1], 1)
        result[i+(0,)] = noise[i+(one_chain, )]
        result[i+(1,)] = theta[i]
        result[i+(3,)] = sigma[i]
        result[i+(2,)] = mu[i]
    return result


# generate parameters
# the parameters are generated out of function, so that they can be saved with the generated numbers
np.random.seed(seed)
theta = normal(5, 5, amount)
sigma = normal(0, 1, amount)
mu = normal(0, 1, amount)

# for some manual checking (not required)
print(type(mu) == np.ndarray)

# generating OU time series
print('generating ou processes')
start = time.time()
# generates the OU time series with the ou_generator module
generated = ou.ou_generate(length, theta, sigma, mu, None, dt=dt, size=(amount, ))
print('finished in {}s'.format(time.time()-start))
# some prints mean to mu parameter; sanity check if generator works and doesn't mess up order.
for i in range(len(mu)):
    print('mu: {}, <x>: {}'.format(mu[i], np.mean(generated[i])))
# repack to array form needed for next step
start = time.time()
print('repackaging')
print(generated.shape)
# repacks it in the format used during the project
array = repack(theta, sigma, mu, generated)
print(array.shape)
print('finished in {}s'.format(time.time()-start))
print('saving')
start = time.time()
# saves the array using the np module
np.save('ouV4.npy', array)
print('finished in {}s'.format(time.time()-start))
print('exit')
