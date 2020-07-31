import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors


"""
This program will get the maximum for each test. It also includes some plotting (I know that isn't a nice separation)
"""


# repackaging into [test, alpha, sigma, extraction]
def get_2dmesh(d4array):
    d2mesh = np.zeros((d4array.shape[0] - 1, 3, d4array.shape[1] - 1, d4array.shape[2] - 1))
    zeroed = d4array[1:, 1:, 1:, :]
    for i in range(zeroed.shape[0]):
        for k in range(zeroed.shape[1]):
            for m in range(zeroed.shape[2]):
                for n in range(zeroed.shape[3]):
                    d2mesh[i, n, k, m] = zeroed[i, k, m, n][0]
    return d2mesh


# calculates the minimum of an array in sigma direction, by summing over alpha space
def get_sigma_minimum(mesh):
    return np.argmin([np.sum(mesh[:, i]) for i in range(mesh.shape[1]-1)])


def plot(raw_data, mesh, path, test_index, para_index, test, para):
    plt.pcolormesh(raw_data[0, 0, 1:, 0], raw_data[0, 1:, 0, 0], mesh[i, k], cmap='RdBu')
    plt.xlabel('$m_{\\sigma}$')
    plt.ylabel('$m_{\\alpha}$')
    plt.title(f'extraction quality, tested with {test}')
    cbar = plt.colorbar()
    cbar.set_label(f'{test}')
    plt.savefig(f'{path}{test_index}-{para_index}.pdf', dpi=300)
    plt.close()


def plot_grad(raw_data, mesh, path, test, test_index, para, para_index):
    print(mesh.shape)
    plt.pcolormesh(raw_data[0, 0, 1:, 0], raw_data[0, 1:, 0, 0], mesh[test_index, para_index], cmap='gist_yarg',norm=colors.LogNorm(vmin=1E-5,vmax =1E-1))
    plt.xlabel('$m_{\\sigma}$')
    plt.ylabel('$m_{\\alpha}$')
    plt.title(f'gradient of the extraction quality, tested with {test}')
    plt.colorbar()
    plt.savefig(f'{path}{test_index}-{para_index}-grad.pdf', dpi=300)
    plt.close()


if __name__ == '__main__':
    raw_data = np.load('stat-std-std-more.npy', allow_pickle=True)
    mesh = get_2dmesh(raw_data)

    plt.pcolormesh(raw_data[0, 0, 1:, 0], raw_data[0, 1:, 0, 0], mesh[0, 0], cmap='RdBu')
    plt.show()

    # calculate the absolutes gradients of all 3 tests in both (alpha and sigma) direction
    gradients = np.zeros(mesh.shape + (2,), dtype=float)
    for i in range(mesh.shape[0]):
        for k in range(mesh.shape[1]):
            # gradient indizes: [test, parameter, x, y, direction]
            gradients[i, k, :, :, 0], gradients[i, k, :, :, 1] = np.abs(np.gradient(mesh[i, k]))
    #print(gradients[0, 1, :, :, 0])
    #plt.pcolormesh(raw_data[0, 0, 1:, 0], raw_data[0, 1:, 0, 0], gradients[1, 1, :, :, 1], cmap='gist_yarg',norm=colors.LogNorm(vmin=1E-5,vmax =1E-1))
    #plt.show()

    # gets sigma, where the gradient is as small as possible
    # averaged over all tests, this is the best parameter for sigma
    best_sigma = [get_sigma_minimum(gradients[i, 1, :, :, 1]) for i in range(3)]
    best_sigma_values = [raw_data[0, 0, 1:, 0][i] for i in best_sigma]
    print(best_sigma_values)
    print(f'{np.mean(best_sigma_values)}±{np.std(best_sigma_values)}')

    # for the best sigma (not the averaged, but for each test), the minimum of the gradient in alpha direction is computed
    # here also is averaged over all tests
    best_theta = [np.argmin(gradients[i, 1, :, best_sigma[i], 0]) for i in range(3)]
    best_theta_values = [raw_data[0, 1:, 0, 0][i] for i in best_theta]
    print(best_theta_values)
    print(f'{np.mean(best_theta_values)}±{np.std(best_theta_values)}')

    testlist = ['Spearmen-R', 'Pearson-R', 'Kendall-$\\tau$']
    paralist = ['$\\sigma$', '$\\theta$', '$\\theta_{giv}$']

    # visulizes the results from above as plots
    for i in range(len(testlist)):
        for k in range(len(paralist)):
            #plt.pcolormesh(raw_data[0, 0, 1:, 0], raw_data[0, 1:, 0, 0], mesh[i, k], cmap='RdBu')
            #plt.show()
            plot(raw_data, mesh, './', i, k, testlist[i], paralist[k])

            plot_grad(raw_data, gradients[:, :, :, :, 0], './0-', testlist[i], i, paralist[k], k)
            plot_grad(raw_data, gradients[:, :, :, :, 1], './1-', testlist[i], i, paralist[k], k)







