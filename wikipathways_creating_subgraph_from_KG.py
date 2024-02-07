



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

    for p in wikipathway_diagrams:
        #Generates subgraphs of wikipathways graphs once edgelists are already downloaded into corresponding folder wikipathways_graphs/<p>
        command = 'python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/' + p + '_output' + ' --knowledge-graph pkl --input-type annotated_diagram --input-substring ' + p

        if cosine_similarity == 'true': 
            command = command + ' --cosine-similarity True'
        if pdp == 'true':
            command = command + ' --pdp True'
        if guiding_term:
            command = command + ' --guiding-term True'
            
        os.system(command)
        
if __name__ == '__main__':
    main()
