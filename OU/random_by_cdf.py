import numpy as np


# Iterator class, used in random_array to iterate over a n-dimesional np array - copied from ou_generator
# iterates over all indices of an array, which shape is given in the 'size' argument
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


def random(cdf, min_limit, max_limit):
    ran = np.random.random()
    # gets the position where the cdf is the first time bigger then random value
    over_ran = np.where(cdf>ran)[0][0]
    # the value before that is the last where random is bigger
    under_value = cdf[over_ran-1]
    # calculates the "flaot position" ran would have, if cdf would be contious sampled
    #       last pos bigger then ran :: linear interpolation between the points bigger and smaller then ran
    float_pos = (over_ran-1) + (ran - under_value) / (cdf[over_ran] - under_value)
    # because a min and a length is known the position in the random variable space can be calculated from the "float array position"
    return min_limit + (max_limit - min_limit) * (float_pos / (len(cdf)-1))


def random_array(cdf, min_limit, max_limit, size):
    result = np.zeros(size, dtype=float)
    # calculates a random number for each cell in result
    for i in Iterator(size):
        result[i] = random(cdf, min_limit, max_limit)
    return result


def cdf_by_pdf(pdf):
    cdf = np.zeros(len(pdf)+1, dtype=float)
    for i in range(len(pdf)):
        cdf[i+1] = cdf[i] + pdf[i] 
    cdf[0] = 0
    cdf[-1] = 1
    return cdf


if __name__ == "__main__":
    cdf = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    print(random(cdf, 0, 1))
    pdf = np.array([0.1]*10)
    print(cdf_by_pdf(pdf))
