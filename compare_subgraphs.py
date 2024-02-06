



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
from graph_similarity_metrics import *
import argparse
import ast


def main():

    cosine_similarity,pdp,guiding_term,wikipathway_diagrams = generate_graphsim_arguments() 

    #Convert string input to list
    wikipathway_diagrams = ast.literal_eval(wikipathway_diagrams)

    subgraph_types = []
    for p in wikipathway_diagrams:
        #Generates subgraphs of wikipathways graphs once edgelists are already downloaded into corresponding folder wikipathways_graphs/<p>
        if cosine_similarity == 'true': 
            subgraph_types.append('CosineSimilarity')
        if pdp == 'true':
            subgraph_types.append('PDP')
        if guiding_term:
            subgraph_types.append('GuidingTerm_'+guiding_term)

    #Evaluates graph similarity between original edgelist and subgraph generated
    for algorithm in subgraph_types:
        results_df,w_dir = compare_wikipathways_subgraphs(wikipathway_diagrams,algorithm)

        visualize_graph_metrics(results_df,w_dir,algorithm)

if __name__ == '__main__':
    main()