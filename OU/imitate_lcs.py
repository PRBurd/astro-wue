import numpy as np 
import ou_generator as ou 
import random_by_cdf as rcdf 

size = (100, )

# load cdf of the parameters, estimated before hand
cdf_mu = np.load('cdf_mu_TS9.npy')
cdf_sigma = np.load('cdf_sigma_TS9.npy')
cdf_theta = np.load('cdf_theta_TS9.npy')

# sets seed of all np.random, that is used for all random numbers in the rcdf and ou modules
np.random.seed(666)
mu = rcdf.random_array(cdf_mu, -9, -7, size)
theta = rcdf.random_array(cdf_theta, 0, 2, size)
sigma = rcdf.random_array(cdf_sigma, 0, 0.5, size)

print('parameters generated - now running mcs')

time_steps = 1000
pre_run = 100

# slicing in the end only works for 1-dim size 
time_series = ou.ou_generate(time_steps+pre_run, theta, sigma, mu, mu, size=size)[:, pre_run:]

print('ou finished - repacking arrays')

result = np.empty((size + (4, )), dtype=object)
# this for loop works only for 1-dim size
for i in range(size[0]):
	result[i, 0] = time_series[i, :]
	result[i, 1] = theta[i]
	result[i, 2] = mu[i]
	result[i, 3] = sigma[i]

np.save('OU_fermi_TS9_subsample.npy', result)
print('finished')
