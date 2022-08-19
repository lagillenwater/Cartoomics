# Given a starting graph of node pairs, find all paths between them to create a subgraph
from find_path import find_shortest_path
from find_path import prioritize_path_cs
from find_path import prioritize_path_pdp
import pandas as pd

def subgraph_shortest_path(input_file,graph,g_nodes,labels_all,triples_df,weights,search_type):

    input_nodes = pd.read_csv(input_file,sep='|')

    all_paths = []

    for i in range(len(input_nodes)):
        start_node = input_nodes.iloc[i].loc['Source']
        end_node = input_nodes.iloc[i].loc['Target']
        shortest_path_df = find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type)
        all_paths.append(shortest_path_df)

    df = pd.concat(all_paths)

    return df

def subgraph_prioritized_path_cs(input_file,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,node2vec_script_dir,embedding_dimensions):

    input_nodes = pd.read_csv(input_file,sep='|')

    all_paths = []

    for i in range(len(input_nodes)):
        start_node = input_nodes.iloc[i].loc['Source']
        end_node = input_nodes.iloc[i].loc['Target']
        cs_shortest_path_df = prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,node2vec_script_dir,embedding_dimensions)
        all_paths.append(cs_shortest_path_df)

    df = pd.concat(all_paths)

    return df

def subgraph_prioritized_path_pdp(input_file,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight):

    input_nodes = pd.read_csv(input_file,sep='|')

    all_paths = []

    for i in range(len(input_nodes)):
        start_node = input_nodes.iloc[i].loc['Source']
        end_node = input_nodes.iloc[i].loc['Target']
        pdp_shortest_path_df = prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight)
        all_paths.append(cs_shortest_path_df)

    df = pd.concat(all_paths)

    return df