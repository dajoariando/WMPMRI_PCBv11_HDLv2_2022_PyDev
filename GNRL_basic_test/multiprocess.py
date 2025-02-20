import itertools
import numpy as np
import multiprocessing as mp
import time

def calc_mp(indices, data):
    # construct pool
    pool = mp.Pool(mp.cpu_count())

    # we are going to populate the matrix; organize all the inputs; then map them
    matrix = [[0] * len(indices) for i in range(len(indices))]
    args = [(data[i_a], data[i_b]) for i_a, i_b in list(itertools.combinations(indices, 2))]
    results = pool.starmap(algorithm, args)

    # unpack the results into the matrix
    for i_tuple, result in zip([(i_a, i_b) for i_a, i_b in list(itertools.combinations(indices, 2))], results):
        # unpack
        i_a, i_b = i_tuple
        a_res, b_res = result

        # set it in the matrix
        matrix[i_b][i_a] = a_res
        matrix[i_a][i_b] = b_res

    return matrix

def calc_single(indices, data):
    # do the simple single process version
    matrix = [[0] * len(indices) for i in range(len(indices))]
    for i_a, i_b in list(itertools.combinations(indices, 2)):
        a_res, b_res = algorithm(data[i_a], data[i_b])
        matrix[i_b][i_a] = a_res
        matrix[i_a][i_b] = b_res

    return matrix

def algorithm(a,b):
    # Very slow and complex
    time.sleep(2)
    return a + b, a - b

if __name__ == "__main__":
    # generate test data;
    indices = range(5)
    data = range(len(indices))

    # test single
    time_start = time.time()
    print(calc_single(indices, data))
    print("Took {}".format(time.time() - time_start))

    # mp
    time_start = time.time()
    print(calc_mp(indices, data))
    print("Took {}".format(time.time() - time_start))