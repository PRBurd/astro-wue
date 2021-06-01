import numpy as np


# General:
# feed with np.array with time series [np.10(flux)] only, non significant values (e.g. TS not fulfilled), need to be set to np.nan
# if the flux values are given in some kind of gauged units (e.g. FACT/MAGIC crab units), be carefull about what the gauge means exactly is there already a log in any kind?

# Some basic exceptions used (subject to change)

# This exception is thrown, if some values that shouldn't are NaN (e.g. after any operation like mean())
class IsNANException(Exception):
    pass


# Implementation of the given formulas, from paper. Instead of an epsilon an upper and lower limit are given


# returns sigma*sqrt(dt) and the number of points used for calculation
def get_sigma(data, lower, upper):
    # positions of u_T, that are NOT NaN AND over lower AND under upper
    pos = np.array((~np.isnan(data))*(data > lower)*(data < upper), dtype=bool)
    # discards last element (no u_T+1 would exist)
    pos[-1] = False
    # positions of u_T+1 (shift positions by +1)
    pos1 = np.zeros(len(pos), dtype=bool)
    pos1[1:] = pos[:-1]
    # calculates u_t+1 - u_t for all u_t
    distance = data[pos1] - data[pos]
    # discards all NAN
    distance = distance[~np.isnan(distance)]
    # if no points are left, no sigma can be calculated
    if len(distance) == 0:
        return np.nan, 0
    # standard deviation is calculated and returned
    return np.std(distance), len(distance)


def get_alpha_abs(data, sigma):
    return np.sqrt(np.abs(1-(sigma**2/np.var(data[~np.isnan(data)]))))


def get_alpha_pm(data, mean, lower, upper):
    # positions of u_T, that are NOT NaN AND (over lower OR under upper)
    pos = np.array((~np.isnan(data))*((data < lower)+(data > upper)), dtype=bool)
    # discards last element (no u_T+1 would exist)
    pos[-1] = False
    # positions of u_T+1 (shift positions by +1)
    pos1 = np.zeros(len(pos), dtype=bool)
    pos1[1:] = pos[:-1]
    # calculates all the alphas at once
    alphas = (data[pos1] - mean)/(data[pos] - mean)
    if len(alphas) == 0:
        return np.nan
    # calculates the mean of all alphas that are not NaN
    return np.mean(alphas[~np.isnan(alphas)])


# auxiliary functions to easily calculate limits


# gets limits in terms of standard deviations form mean
# this is the method chosen to be used in the paper
def set_limit_by_std(data, sigma):
    mean = np.mean(data[~np.isnan(data)])
    std = np.std(data[~np.isnan(data)])
    if mean == np.nan or sigma == np.nan or std == np.nan:
        raise IsNANException()
    return mean, mean - sigma * std, mean + sigma * std


# get limits form epsilon distance
def set_limit_by_epsilon(data, epsilon):
    mean = np.mean(data[~np.isnan(data)])
    if mean == np.nan:
        raise IsNANException()
    return mean, mean - epsilon, mean + epsilon


def set_limit_by_percentage_of_mean(data, percent):
    mean = np.mean(data[~np.isnan(data)])
    if mean == np.nan:
        raise IsNANException()
    return mean, mean * (1 - percent), mean * (1 + percent)
    

# calculates alpha and/or sigma directly, with use of the functions above


def sigma_by_percentage_of_mean(data, percent):
    limits = set_limit_by_percentage_of_mean(data, percent)
    return get_sigma(data, *limits[1:])


def alpha_by_std(data, sigma_para, sigma_std):
    limits = set_limit_by_std(data, sigma_std)
    return np.sign(get_alpha_pm(data, *limits)) * get_alpha_abs(data, sigma_para)


# calculates sigma and alpha by the method described in the thesis/paper (sigma_sigma <=> m_\sigma, sigma_alpha <=> m_\alpha
def all_by_std(data, sigma_sigma, sigma_alpha):
    limits_sigma = set_limit_by_std(data, sigma_sigma)
    limits_alpha = set_limit_by_std(data, sigma_alpha)
    sigma, n = get_sigma(data, *limits_sigma[1:])
    return sigma, np.sign(get_alpha_pm(data, *limits_alpha))*get_alpha_abs(data, sigma), n
