



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
from graph_similarity_metrics import *
import argparse
import ast


def main():

    parser = define_graphsim_arguments()
    args = parser.parse_args()
    wikipathway_diagrams = args.wikipathway_diagrams

    #Convert string input to list
    wikipathway_diagrams = ast.literal_eval(wikipathway_diagrams)

    for p in wikipathway_diagrams:
        #Generates subgraphs of wikipathways graphs once edgelists are already downloaded into corresponding folder wikipathways_graphs/<p>
        command = 'python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/' + p + '_output' + ' --knowledge-graph pkl --input-type annotated_diagram --input-substring ' + p
        os.system(command)

    #Evaluates graph similarity between original edgelist and subgraph generated
    results_df,w_dir = compare_wikipathways_subgraphs(wikipathway_diagrams)

    visualize_graph_metrics(results_df,w_dir)

if __name__ == '__main__':
    main()