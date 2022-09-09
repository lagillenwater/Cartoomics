# Given a starting graph of node pairs, find all paths between them to create a subgraph
from find_path import find_shortest_path
from find_path import prioritize_path_cs
from find_path import prioritize_path_pdp
import pandas as pd
from tqdm import tqdm

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

    return df

def user_defined_edge_weights(triples_df, graph):
    edges = set(triples_df.predicate)
    print("### Unique Edges in Knowledge Graph ###")
    print('\n'.join(edges))
    still_adding = True
    to_weight= []
    print('\n')
    print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
    while(still_adding):
        user_input = input('Edge or "Done"')
        if user_input == 'Done':
            still_adding = False
        else:
            to_weight.append(user_input)
    edges= graph.es['predicate']
    graph.es['weight'] = [10 if x in to_weight else 1 for x in edges]
    return(graph)
    
def subgraph_prioritized_path_cs(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in tqdm(range(len(input_nodes_df))):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        cs_shortest_path_df = prioritize_path_cs(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions)
        all_paths.append(cs_shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df

def subgraph_prioritized_path_pdp(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in tqdm(range(len(input_nodes_df))):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        pdp_shortest_path_df = prioritize_path_pdp(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight)
        all_paths.append(cs_shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df
