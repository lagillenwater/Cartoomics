



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
from graph_similarity_metrics import *
import argparse


def main():

    #l = ['WP5373','WP5071','WP554'] #
    parser = define_graphsim_arguments()
    args = parser.parse_args()
    wikipathway_diagrams = args.wikipathway_diagrams

    for p in wikipathway_diagrams:
        #First download wikipathways edgelists
        #Next generate subgraphs of wikipathways graphs
        command = 'python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/' + p + '_output' + ' --knowledge-graph pkl --input-type annotated_diagram'
        os.system(command)

    results_df = compare_wikipathways_subgraphs(wikipathway_diagrams)

    visualize_graph_metrics(results_df)

if __name__ == '__main__':
    main()