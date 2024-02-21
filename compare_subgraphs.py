



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
from graph_similarity_metrics import *
import argparse
import ast

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

#python compare_subgraphs.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4829','WP5372','WP5283']" --enable-skipping True

def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    subgraph_types = []

    for wikipathway in wikipathways:

        #Generates subgraphs of wikipathways graphs once edgelists are already downloaded into corresponding folder wikipathways_graphs/<p>
        if cosine_similarity == 'true': 
            subgraph_types.append('CosineSimilarity')
        if pdp == 'true':
            subgraph_types.append('PDP')
        if guiding_term:
            subgraph_types.append('GuidingTerm_'+guiding_term)

    #Evaluates graph similarity between original edgelist and subgraph generated
    for algorithm in subgraph_types:
        results_df = compare_wikipathways_subgraphs(wikipathways,algorithm,all_wikipathways_dir)

        visualize_graph_metrics(results_df,all_wikipathways_dir,algorithm)

if __name__ == '__main__':
    main()