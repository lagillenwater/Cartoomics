# Given a starting graph of node pairs, find all paths between them to create a subgraph
from find_path import find_shortest_path
from find_path import prioritize_path_cs
from find_path import prioritize_path_pdp
import pandas as pd
from tqdm import tqdm
from evaluation import output_path_lists

def subgraph_shortest_path(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        shortest_path_df = find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type)
        all_paths.append(shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df

def subgraph_prioritized_path_cs(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in tqdm(range(len(input_nodes_df))):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        cs_shortest_path_df,paths_total_cs = prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions)
        all_paths.append(cs_shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    #Output path list to file
    output_path_lists(output_dir,paths_total_cs,'CosineSimilarity')

    return df,paths_total_cs

def subgraph_prioritized_path_pdp(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight,output_dir):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in tqdm(range(len(input_nodes_df))):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        pdp_shortest_path_df,paths_pdp = prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight)
        all_paths.append(pdp_shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    #Output path list to file
    output_path_lists(output_dir,paths_pdp,'PDP')
    print('output PDP list')

    return df,paths_pdp