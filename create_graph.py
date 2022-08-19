
from graph import PKLGraph
import pandas as pd
import csv
import json
from igraph import * 


#Class: ThisClass
#Modules: this_module
#Functions: this_function

###Read in all files, outputs triples and labels and integers edgelist as a df, and identifiers as a dict
def process_pkl_files(triples_file,labels_file,identifiers_file,triples_integers_file):

    triples_df = pd.read_csv(triples_file,sep = '	')

    labels = pd.read_csv(labels_file, sep = '	')

    #Read in identifiers file to dictionary
    f = open(identifiers_file)
    identifiers = json.load(f)

    #Read in node2vec input triples integers file as df
    edgelist_int_df = pd.read_csv(triples_integers_file, sep=" ")

    return triples_df,labels,identifiers,edgelist_int_df

def create_igraph_graph(edgelist_df,labels):

    edgelist_df = edgelist_df[['Subject', 'Object', 'Predicate']]

    uri_labels = labels[['Identifier']]

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    g_nodes = g.vs()['name']  

    return g,g_nodes 

# Wrapper function
def create_pkl_graph(triples_file,labels_file,identifiers_file,triples_integers_file):

    triples_df,labels,identifiers,edgelist_int_df = process_pkl_files(triples_file,labels_file,identifiers_file,triples_integers_file)

    g_igraph,g_nodes_igraph = create_igraph_graph(triples_df,labels)

    # Created a PKL class instance
    pkl_graph = PKLGraph(triples_df,identifiers,labels,g_igraph,g_nodes_igraph)

    return pkl_graph
