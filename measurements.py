# In this module we perform our simulations.

import hexagonal_lattice as hl
import time
import helpful_functions as hf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from scipy.optimize import curve_fit
from math import sqrt
from helpful_functions import round_sig


def measure_time(n0, n_max, digit=2):
    times = np.zeros(n_max - n0 + 1)

    for n in range(n0, n_max+1):
        start_time = time.time()
        res = hl.run(n, stretch_factor=5, plot=False).fun
        end_time = time.time()
        delta_t = round((end_time - start_time)/60, digit)
        print(f'With dim = {n}, i.e. {len(hl.create_lattice(n)[0])} nodes,'
              f' it took {delta_t}min to calculate the minimal energy {res}J.')
        times[n - n0] = delta_t
    return times


def energy_func_speedtest(dim, num, dv, d=1, k=2):
    lattice = hl.create_lattice(dim)
    l = hl.manipulate_lattice_absolute_value(lattice[0], lattice[1], 0.3)
    t1 = 0
    t2 = 0
    for i in range(num):
        start_time = time.time()
        energy1 = hl.run_absolute_displacement(dim, dv, jac_func=hl.energy_func_jac).fun
        end_time = time.time()
        dt = end_time - start_time
        print(dt)
        t1 += dt

        start_time = time.time()
        energy2 = hl.run_absolute_displacement(dim, dv, jac_func=hl.energy_func_jac_opt).fun
        end_time = time.time()
        dt = end_time - start_time
        print(dt)
        t2 += end_time - start_time

    return energy1, energy2, t1, t2


def energy_continuous_stretching(dim, max_stretch, min_stretch=0, export=False):
    results = []

    for i in range(min_stretch, max_stretch+1):
        results.append([i, hl.run(dim, stretch_factor=i, plot=False).fun])
        print(results[i-min_stretch])

    if export:
        df = pd.DataFrame(data=results, columns=['i', 'min energy'])
        time_now = time.localtime()
        time_now = time.strftime('%H:%M:%S', time_now)
        path = f'/home/jurij/Python/Physik/Bachelorarbeit/measurements/dim={dim}_min={min_stretch}_max={max_stretch}_{time_now}.csv'
        df.to_csv(path)

    return results


def x2(x, a):
    return a*x**2


def x4(x, a):
    return a*x**4


def plot_from_csv(path, fit=False):
    df = pd.read_csv(path)
    df.i = df.i*0.25
    df.plot(x='i', y='min energy', marker='o')
    plt.xlabel('Auslenkung in % der Gitterbreite')
    plt.ylabel('berechnete minimale Energie')

    if fit:
        x = df['i']
        y = df['min energy']
        pars4, cov4 = curve_fit(x4, x, y)

        residuals = y - x4(x, pars4)
        plt.plot(x, pars4[0]*x**4, color='red', label='x^4')
    plt.legend()
    plt.grid()
    plt.show()


def absolute_stretching(dim, displace_value, d=1, k=2):
    # dims is a list that contains dimensions to create multiple lattices.
    res = hl.run_absolute_displacement(dim, displace_value, d, k, plot=False)

    return res.fun


def absolute_stretching_multi_lattice(dims, displace_value, num, d=1, k=2):
    displace_values = np.linspace(0, displace_value, num=num)
    all_y = []

    for i in range(0, len(dims)):
        y = []
        for j in range(0, len(displace_values)):
            print(dims[i], displace_values[j])
            y.append(absolute_stretching(dims[i], displace_values[j], d, k))
        all_y.append(y)

    return displace_values, all_y


def plot_multiple_absolute_stretching(values, dims, fit=True):
    x = values[0]
    ys = values[1]

    for i in range(0, len(ys)):
        plt.plot(x, ys[i], label=f'dim={dims[i]}', marker='o', linestyle='none')
        pars, cov = curve_fit(x4, x, ys[i])
        ss_res = np.sum((ys[i] - x4(x, pars[0]))**2)
        ss_tot = np.sum((ys[i]-np.mean(ys[i]))**2)
        r2 = round(1 - (ss_res / ss_tot), 2)

        plt.plot(x, x4(x, pars[0]), label=f'fit dim={dims[i]} with a*x^4, a={round_sig(pars[0])}, error of a={round_sig(sqrt(cov), 1)}')
    plt.legend()
    plt.xlabel('\u03B4')
    plt.ylabel('minimale Energie')
    plt.show()


def energy_convergence(min_dim, max_dim, dv, method='CG'):
    x = list(range(min_dim, max_dim+1))
    y = np.zeros(max_dim - min_dim+1)
    for i in x:
        print(f'current dim={i}')
        y[i-min_dim] = hl.run_absolute_displacement(i, dv, method=method, true_convergence=True, percentile=0).fun

    plt.scatter(x, y)
    plt.show()


    # 'CG', 'BFGS', 'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP'
    # 'trust-ncg', 'trust-krylov', 'trust-exact'
    # 'Newton-CG'

    # energy_convergence(5, 22, .5, gtol=1.e-08)
    # energy_convergence(5, 22, .5, gtol=1.e-05)
    # plt.legend()
    # plt.show()


def export_pickle(dim, dv, gtol=1.e-10):
    path = f'/home/jurij/Python/Physik/Bachelorarbeit/measurements/dim={dim}_dv={dv}_gtol={gtol}.pickle'
    result = hl.run_absolute_displacement(dim, dv, plot=False, gtol=gtol)
    pickle_out = open(path, 'wb')
    pickle.dump(result, pickle_out)
    pickle_out.close()


def import_pickle(dim, dv, gtol=1.e-10, perc=0):
    path = f'/home/jurij/Python/Physik/Bachelorarbeit/measurements/dim={dim}_dv={dv}_gtol={gtol}_perc={perc}.pickle'
    pickle_in = open(path, 'rb')
    return pickle.load(pickle_in)


def number_of_links(dim):
    ps = list(range(0, 47, 2))
    y = []
    for p in ps:
        seed = None
        ls = hl.create_lattice(dim, 1)
        l = ls[0]
        # sumA1 = []
        sumA2 = []
        # sumA3 = []
        print(p)

        for i in range(10):
            print(i)
            adj = hl.adjacency_matrix(l)
            # adj = dilute_lattice(adj, percentile)
            A = hl.dilute_lattice_point(adj, p, l, seed)
            # AA = dilute_lattice_point2(adj, percentile, l, seed)
            A1 = adj[0] + adj[1]
            A2 = A[0] + A[1]
            # A3 = AA[0] + AA[1]

            # sumA1.append(np.sum(A1))
            sumA2.append(np.sum(A2)/np.sum(A1))
            print(sumA2)
            # sumA3.append(np.sum(A3))
        y.append(hf.round_sig(np.mean(sumA2)))

    ps100 = [i/100 for i in ps]
    ps100m = [1-i / 100 for i in ps]
    fig = plt.figure(figsize=(15, 10), facecolor='white')
    ax = fig.add_subplot()
    ax.plot(ps100, ps100m, label='$g$')
    ax.scatter(ps100, y, color='orange', label=r"$g'$")
    ax.legend(fontsize=15)
    # ax.set_title('Minimale Energie aufgetragen gegen dv', size=20)
    ax.set_ylabel('', size=20)
    ax.set_xlabel('p in %', size=20)
    ax.tick_params(axis="x", labelsize=15)
    ax.tick_params(axis="y", labelsize=15)
    #ax.set_aspect(.4)
    plt.show()
