import numpy as np
from scipy.spatial.distance import cdist
import time

def pairwise_cosine_sim(A,B):
    
    # Calculate pairwise cosine similarity
    similarity_matrix = 1 - cdist(A, B, metric='cosine')
    return similarity_matrix


def main():
    # Example matrices
    A = np.random.rand(10000, 128)  # Matrix of shape (n, p)
    B = np.random.rand(10000, 128)  # Matrix of shape (m, p)

    start_time = time.time()

    sim = pairwise_cosine_sim(A,B)
    print(sim.shape)
    
    end_time = time.time()

    runtime = end_time - start_time
    print(f"Runtime: {runtime} seconds")


if __name__ == '__main__':
    main()


