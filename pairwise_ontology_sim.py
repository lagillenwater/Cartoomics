import numpy as np
import time
from numba import njit, prange
from scipy.spatial.distance import cdist
import pandas as pd
import json
import argparse



def load_embeddings(e_file):
    emb = pd.read_csv(e_file, index_col = 0, skiprows = 1, sep = " ")
    return(emb)

def load_ID_map(id_map_file):
    with open(id_map_file, 'r') as file:
        file_content = file.read()
        id_map_dict = json.loads(file_content)
    return id_map_dict

def read_input_graph(input_file):
    input_graph = pd.read_csv(input_file, delimiter='\t', engine='python')
    source = input_graph.iloc[:,0].unique()
    target = input_graph.iloc[:,2].unique()
    return source,target


def lookup_int_from_uri_list(uri_list, id_map_dict):
    int_ids = []
    for key in uri_list:
        value = id_map_dict.get(key, "Key not found")
        int_ids.append(value)
    return int_ids
                            

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



def main():

    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i",dest="input",required=True,help="input")
    parser.add_argument("-o",dest="output",required=True,help="input")

    args = parser.parse_args()
    
    print("Filtering embeddings")
    
    emb = load_embeddings("./wikipathways_graphs/pkl/PheKnowLator_v3_node2vec_Embeddings128.emb")

    id_map_dict = load_ID_map("./wikipathways_graphs/pkl/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map.txt")

    source,target = read_input_graph(args.input)
    
    source_ids = lookup_int_from_uri_list(source, id_map_dict)
    target_ids = lookup_int_from_uri_list(target, id_map_dict)

    source_emb = emb.iloc[source_ids].to_numpy()
    target_emb = emb.iloc[target_ids].to_numpy()
    
    print("Calculating similarity matrix")
    sim = pairwise_cosine_sim_numba(source_emb,target_emb)
    sim = pd.DataFrame(sim, columns = target, index = source)
        
    sim.to_csv(args.output, sep = "\t", index = True)
    print("similarity matrix written to " + args.output)

if __name__ == '__main__':
    main()


