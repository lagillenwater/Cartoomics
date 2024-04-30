from graph import KnowledgeGraph
import pandas as pd
import csv
import json
from igraph import *
import networkx as nx

###Read in all files, outputs triples and labels as a df
def process_pkl_files(triples_file,labels_file):
    
    triples_df = pd.read_csv(triples_file,sep = '	', quoting=csv.QUOTE_NONE)
    triples_df.columns.str.lower()

    triples_df.replace({'<': ''}, regex=True, inplace=True)
    triples_df.replace({'>': ''}, regex=True, inplace=True)

    labels = pd.read_csv(labels_file, sep = '	', quoting=csv.QUOTE_NONE)
    labels.columns.str.lower()
    for c in labels.columns:
        labels[[c]] = labels[[c]]. fillna('None')

    #Remove brackets from URI
    labels['entity_uri'] = labels['entity_uri'].str.replace("<","")
    labels['entity_uri'] = labels['entity_uri'].str.replace(">","")


    return triples_df,labels

#Creates igraph object and a list of nodes
def create_igraph_graph(edgelist_df):

    edgelist_df = edgelist_df[['subject', 'object', 'predicate']]

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    g_nodes = g.vs()['name']

    return g,g_nodes 

#Creates igraph object and a list of nodes
def create_networkx_graph(edgelist_df):

    edgelist_df = edgelist_df[['subject', 'object', 'predicate']]
    g = nx.from_pandas_edgelist(edgelist_df, source='subject', target='object', edge_attr='predicate', create_using=nx.Graph())
    # Networkx takes the actual uri as the node label, so don't need to use 'name' here
    g_nodes = [node for node, data in g.nodes(data=True)]

    return g,g_nodes

# Wrapper function
# Includes a "kg_type" parameter for graph type. Options include 'pkl' for PheKnowLator and 'kg-covid19' for KG-Covid19
def create_graph(triples_file,labels_file, kg_type = "pkl"):
    if kg_type == "pkl":
        triples_df,labels = process_pkl_files(triples_file,labels_file)
    elif kg_type == "kg-covid19":
        triples_df,labels = process_kg_covid19_files(triples_file,labels_file)
    else:
        raise Exception('Invalid graph type! Please set kg_type to "pkl" or "kg-covid19"')

    g_igraph,g_nodes_igraph = create_igraph_graph(triples_df)
    g_networkx_graph,g_nodes_networkx_graph = create_networkx_graph(triples_df)
    # Created a PKL class instance
    pkl_graph = KnowledgeGraph(triples_df,labels,g_networkx_graph,g_nodes_networkx_graph)

    return pkl_graph





###Read in all kg_covid19 files, outputs triples and labels as a df
def process_kg_covid19_files(triples_file,labels_file):
    triples_df = pd.read_csv(triples_file,sep = '\t', usecols = ['subject', 'object', 'predicate'])
    triples_df.columns.str.lower()

    labels = pd.read_csv(labels_file, sep = '\t', usecols = ['id','name','description','xrefs','synonym'])
    labels.columns = ['id','label', 'description/definition','synonym','entity_uri']
    labels.loc[pd.isna(labels["label"]),'label'] = labels.loc[pd.isna(labels["label"]),'id']
    labels.loc[pd.isna(labels["entity_uri"]),'entity_uri'] = labels.loc[pd.isna(labels["entity_uri"]),'id']

    
    return triples_df,labels



### convert igraph to networkx graph
# def kg_to_undirected_networkx(g,triples_df,labels):
#     import pdb;pdb.set_trace()
#     kg_igraph = g.graph_object
#     G = kg_igraph.to_networkx()
#     G = G.to_undirected()
#     G_nodes = [data['name'] for node, data in G.nodes(data=True)]
#     # Created a PKL class instance
#     pkl_graph = KnowledgeGraph(triples_df,labels,G,G_nodes)
#     return pkl_graph
