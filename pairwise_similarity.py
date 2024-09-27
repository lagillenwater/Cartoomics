import numpy as np
import time
from numba import njit, prange
from scipy.spatial.distance import cdist

@njit(parallel=True)
def pairwise_cosine_sim_numba(A, B):
    n = A.shape[0]
    m = B.shape[0]
    similarity_matrix = np.zeros((n, m))

    for i in prange(n):
        for j in range(m):
            dot_product = np.dot(A[i], B[j])
            norm_a = np.linalg.norm(A[i])
            norm_b = np.linalg.norm(B[j])
            similarity_matrix[i, j] = dot_product / (norm_a * norm_b)
    
    return similarity_matrix


def pairwise_cosine_sim(A,B):
    
    # Calculate pairwise cosine similarity
    similarity_matrix = 1 - cdist(A, B, metric='cosine')
    return similarity_matrix


def main():
    # Example matrices
    A = np.random.rand(100000, 128)  # Matrix of shape (n, p)
    B = np.random.rand(100000, 128)  # Matrix of shape (m, p)

    start_time = time.time()

    sim = pairwise_cosine_sim_numba(A,B)
        
    end_time = time.time()

    runtime = end_time - start_time
    print(f"Parallel Runtime: {runtime} seconds")

    # start_time = time.time()

    # sim = pairwise_cosine_sim(A,B)
        
    # end_time = time.time()

    # runtime = end_time - start_time
    # print(f"Runtime: {runtime} seconds")


if __name__ == '__main__':
    main()


