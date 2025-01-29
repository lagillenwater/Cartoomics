# Given a starting graph of node pairs, find all paths between them to create a subgraph
from calculate_information_content import drop_low_information_content_nodes
from constants import FILTER_ONTOLOGIES_BY_INFORMATION_CONTENT, METAPATH_SEARCH_MAPS #, PHEKNOWLATOR_BROAD_NODES_DICT
from find_path import convert_to_labels, define_metapath_triples, define_path_triples, expand_neighbors, find_shortest_path,find_shortest_path_pattern, path_search_no_prioritization
from find_path import prioritize_path_cs,prioritize_path_pdp
from find_path import calc_cosine_sim_from_label_list,calc_cosine_sim_from_uri_list,generate_comparison_terms_dict,unique_nodes
import pandas as pd
from tqdm import tqdm
from evaluation import output_path_lists
from evaluation import output_num_paths_pairs
from igraph import * 
import os
import glob
import sys
import logging.config
from pythonjsonlogger import jsonlogger
import networkx as nx
import igraph

# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})

def subgraph_shortest_path(input_nodes_df,graph,weights,search_type,kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        shortest_path_df = find_shortest_path(start_node,end_node,graph,weights,search_type,kg_type,input_nodes_df)
        all_paths.append(shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df

def subgraph_shortest_path_pattern(input_nodes_df,graph,weights,search_type,kg_type,manually_chosen_uris):

    input_nodes_df.columns = input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source']
        end_node = input_nodes_df.iloc[i].loc['target']
        shortest_path_df,manually_chosen_uris = find_shortest_path_pattern(start_node,end_node,graph,weights,search_type,kg_type,input_nodes_df,manually_chosen_uris)
        if len(shortest_path_df) > 0:
            all_paths.append(shortest_path_df)

    if len(all_paths) > 0:
        df = pd.concat(all_paths)
        df.reset_index(drop=True, inplace=True)
        #Remove duplicate edges
        df = df.drop_duplicates(subset=['S','P','O'])

    else:
        df = pd.DataFrame()

    return df,manually_chosen_uris

# Have user define weights to upweight -igraph type only
def user_defined_edge_weights(graph, triples_df,kg_type ):
    if kg_type == 'pkl':
        edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_weight= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
        while(still_adding):
            user_input = input('Edge or "Done": ')
            if user_input == 'Done':
                still_adding = False
            else:
                to_weight.append(user_input)
        to_weight = graph.labels_all[graph.labels_all['label'].isin(to_weight)]['entity_uri'].tolist()

    if kg_type == 'kg-covid19':
        edges = set(list(graph.graph_object.es['predicate']))
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

    edges= graph.graph_object.es['predicate']
    graph.graph_object.es['weight'] = [10 if x in to_weight else 1 for x in edges]
    return(graph)

# Have user define weights to upweight - igraph type only
def user_defined_edge_exclusion(graph,kg_type ):
    if kg_type == 'pkl':
        edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_drop= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
        while(still_adding):
            user_input = input('Edge or "Done": ')
            if user_input == 'Done':
                still_adding = False
            else:
                to_drop.append(user_input)
        to_drop = graph.labels_all[graph.labels_all['label'].isin(to_drop)]['entity_uri'].tolist()
        
    if kg_type == 'kg-covid19':
        edges = set(list(graph.graph_object.es['predicate']))
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_drop= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
        while(still_adding):
            user_input = input('Edge or "Done"')
            if user_input == 'Done':
                still_adding = False
            else:
                to_drop.append(user_input)
    for edge in to_drop:
        graph.graph_object.delete_edges(graph.graph_object.es.select(predicate = edge))
    return(graph)


# Edges to remove
def automatic_defined_edge_exclusion(graph,kg_type):
    if kg_type == 'pkl':
        to_drop = ['http://purl.obolibrary.org/obo/RO_0002160','http://purl.obolibrary.org/obo/BFO_0000050','http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://purl.obolibrary.org/obo/RO_0001025','http://purl.obolibrary.org/obo/RO_0000087']
    if kg_type != 'pkl':
        to_drop = ['biolink:category','biolink:in_taxon']
    for edge in to_drop:
        # Remove from graph object
        if isinstance(graph.graph_object, igraph.Graph):
            graph.graph_object.delete_edges(graph.graph_object.es.select(predicate = edge))
        if isinstance(graph.graph_object, nx.Graph):
            edges_to_delete = [(source, target) for source, target, data in graph.graph_object.edges(data=True) if data.get("predicate") == edge]
            graph.graph_object.remove_edges_from(edges_to_delete)
        # Remove from df
        graph.edgelist = graph.edgelist[graph.edgelist["predicate"] != edge]

    return graph

# Nodes to remove
def automatic_defined_node_exclusion(graph,kg_type,output_dir,threshold = 0.3):
    if kg_type == 'pkl':
        # To drop manually defined nodes
        #to_drop = list(PHEKNOWLATOR_BROAD_NODES_DICT.values())
        to_drop = []
        # To drop nodes based on Information Content
        for ont in tqdm(FILTER_ONTOLOGIES_BY_INFORMATION_CONTENT):
            to_drop = drop_low_information_content_nodes(to_drop,ont,output_dir,threshold)
    print("Removing nodes from KG")
    # Remove from graph object
    if isinstance(graph.graph_object, igraph.Graph):
        for uri in tqdm(to_drop):
            # Get the indices of vertices with corresponding label
            indices_to_delete = [v.index for v in graph.graph_object.vs if v["name"] == uri]
            # Remove the vertices by their indices
            try:
                graph.graph_object.delete_vertices(indices_to_delete)
            except KeyError:
                print('Specified node to be removed does not exist. Update PHEKNOWLATOR_BROAD_NODES_DICT in constants.py.')
                logging.error('Specified node to be removed does not exist. Update PHEKNOWLATOR_BROAD_NODES_DICT in constants.py.')
                sys.exit(1)
    if isinstance(graph.graph_object, nx.Graph):
        # Remove nodes by their uri
        try:
            graph.graph_object.remove_nodes_from(to_drop)
        except KeyError:
            print('Specified node to be removed does not exist. Update PHEKNOWLATOR_BROAD_NODES_DICT in constants.py.')
            logging.error('Specified node to be removed does not exist. Update PHEKNOWLATOR_BROAD_NODES_DICT in constants.py.')
            sys.exit(1)
    # Remove from dfs
    graph.labels_all = graph.labels_all[~graph.labels_all["entity_uri"].isin(to_drop)]
    graph.edgelist = graph.edgelist[~(graph.edgelist["subject"].isin(to_drop) | graph.edgelist["object"].isin(to_drop))]
    print(nx.number_of_nodes(graph.graph_object))
    return graph
 
def subgraph_all_paths(input_nodes_df,graph,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type, search_algorithm, find_graph_similarity = False,existing_path_nodes = 'none'):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    #List of all chosen paths for subgraph
    #all_chosen_path_nodes = []

    #Dict of all shortest paths for subgraph
    all_path_nodes = {}

    id_keys_df = pd.DataFrame(columns = ["Original","New"])

    if search_algorithm == "Metapath_Neighbors":
        # Transform input_nodes into relevant metapath objects and append to original input_nodes_df
        input_nodes_df,id_keys_df = expand_neighbors(input_nodes_df,input_dir,triples_file,id_keys_df,graph.labels_all,kg_type)
        print("og input_nodes_df")
        print(input_nodes_df)
        input_nodes_df = input_nodes_df[~input_nodes_df["target_id"].str.contains("http:")]
        print("new input_nodes_df")
        print(input_nodes_df)


    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        start_node_uri = input_nodes_df.iloc[i].loc['source_id']
        if existing_path_nodes != 'none':
            pair_path_nodes = existing_path_nodes[start_node + end_node]
        else:
            pair_path_nodes = 'none'
        node_pair = input_nodes_df.iloc[i]
        path_nodes, id_keys_df = path_search_no_prioritization(node_pair, graph, triples_file,input_dir, kg_type, search_algorithm, id_keys_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        # Path nodes from metapath search already have predicate
        paths_dfs_dict = define_metapath_triples(path_nodes)

        paths_dfs_list = []
        for _,v in paths_dfs_dict.items():
            df = convert_to_labels(v,graph.labels_all,kg_type,input_nodes_df)
            paths_dfs_list.append(df)
        # Keep track of every path found by uri so that you can search them later
        all_path_nodes[start_node + end_node] = path_nodes

    # Write to file if data exists
    print("id_keys_df: ",id_keys_df)
    if len(id_keys_df) > 0:
        if not os.path.exists(output_dir + '/' + search_algorithm): os.mkdir(output_dir + '/' + search_algorithm)
        id_keys_df.to_csv(output_dir + '/' + search_algorithm + "/id_keys_df.csv",sep='|',index=False)

    output_num_paths_pairs(output_dir,num_paths_df,search_algorithm)

    return paths_dfs_list, all_path_nodes


def subgraph_prioritized_path_cs(input_nodes_df,graph,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type, search_algorithm, find_graph_similarity = False,existing_path_nodes = 'none'):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    #List of all chosen paths for subgraph
    #all_chosen_path_nodes = []

    #Dict of all shortest paths for subgraph
    all_path_nodes = {}

    id_keys_df = pd.DataFrame(columns = ["Original","New"])

    if search_algorithm == "Metapath_Neighbors":
        # Transform input_nodes into relevant metapath objects and append to original input_nodes_df
        input_nodes_df,id_keys_df = expand_neighbors(input_nodes_df,input_dir,triples_file,id_keys_df,graph.labels_all,kg_type)
        print("og input_nodes_df")
        print(input_nodes_df)
        input_nodes_df = input_nodes_df[~input_nodes_df["target_id"].str.contains("http:")]
        # Remove disease target nodes from example_input -- NEED to update to work with only source input
        input_nodes_df = input_nodes_df[input_nodes_df["target"] != input_nodes_df.iloc[0].loc["target"]]
        print("new input_nodes_df")
        print(input_nodes_df)


    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        start_node_uri = input_nodes_df.iloc[i].loc['source_id']
        if existing_path_nodes != 'none':
            pair_path_nodes = existing_path_nodes[start_node + end_node]
        else:
            pair_path_nodes = 'none'
        node_pair = input_nodes_df.iloc[i]
        path_nodes,cs_shortest_path_df,all_paths_cs_values,chosen_path_nodes_cs,id_keys_df = prioritize_path_cs(input_nodes_df,node_pair,graph,weights,search_type,triples_file,input_dir,embedding_dimensions,kg_type,search_algorithm,id_keys_df,pair_path_nodes)
        all_paths.append(cs_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        #Get sum of all cosine values in value_list
        path_list = list(map(sum, all_paths_cs_values))
        output_path_lists(output_dir,path_list,'CosineSimilarity_'+search_algorithm,i,path_nodes)
        #all_chosen_path_nodes.append(chosen_path_nodes_cs)
        # Keep track of every path found by uri so that you can search them later
        all_path_nodes[start_node + end_node] = path_nodes

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S_ID','P_ID','O_ID','S','P','O'])
    
    # Write to file if data exists
    print("id_keys_df: ",id_keys_df)
    if len(id_keys_df) > 0:
        if not os.path.exists(output_dir + '/CosineSimilarity_' + search_algorithm): os.mkdir(output_dir + '/CosineSimilarity_' + search_algorithm)
        id_keys_df.to_csv(output_dir + '/CosineSimilarity_' + search_algorithm + "/id_keys_df.csv",sep='|',index=False)

    output_num_paths_pairs(output_dir,num_paths_df,'CosineSimilarity_'+search_algorithm)

    return df,all_paths_cs_values,all_path_nodes

def subgraph_prioritized_path_pdp(input_nodes_df,graph,weights,search_type,triples_file,input_dir,pdp_weight,output_dir, kg_type, search_algorithm, existing_path_nodes = 'none'):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    #List of all chosen paths for subgraph
    #all_chosen_path_nodes = []

    #Dict of all shortest paths for subgraph
    all_path_nodes = {}

    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        if existing_path_nodes != 'none':
            pair_path_nodes = existing_path_nodes[start_node + end_node]
        else:
            pair_path_nodes = 'none'
        node_pair = input_nodes_df.iloc[i]
        node_pair = input_nodes_df.iloc[i]
        path_nodes,pdp_shortest_path_df,paths_pdp,chosen_path_nodes_pdp = prioritize_path_pdp(input_nodes_df,node_pair,graph,weights,search_type,triples_file,input_dir,pdp_weight,kg_type,search_algorithm,pair_path_nodes)
        all_paths.append(pdp_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        output_path_lists(output_dir,paths_pdp,'PDP',i)
        #all_chosen_path_nodes.append(chosen_path_nodes_pdp)
        all_path_nodes[start_node + end_node] = path_nodes

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S_ID','P_ID','O_ID','S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,'PDP')

    return df,paths_pdp,all_path_nodes  #all_chosen_path_nodes

def subgraph_prioritized_path_guiding_term(input_nodes_df,term_row,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type,existing_path_nodes = 'none'):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    term_foldername = 'Guiding_Term_'+term_row['term_label'].replace(" ","_").replace(".","_").replace(":","_").replace("'",'')
    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        if existing_path_nodes != 'none':
            pair_path_nodes = existing_path_nodes[start_node + end_node]
        else:
            pair_path_nodes = 'none'
        node_pair = input_nodes_df.iloc[i]
        path_nodes,cs_shortest_path_df,all_paths_cs_values,chosen_path_nodes_cs = prioritize_path_cs(input_nodes_df,node_pair,graph,weights,search_type,triples_file,input_dir,embedding_dimensions,kg_type, pair_path_nodes,term_row)
        all_paths.append(cs_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        #Get sum of all cosine values in value_list
        path_list = list(map(sum, all_paths_cs_values))
        output_path_lists(output_dir,path_list,term_foldername,i)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S_ID','P_ID','O_ID','S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,term_foldername)

    return df,all_paths_cs_values,term_foldername


def get_cosine_sim_one_pathway(g,comparison_terms_df,kg_type,embeddings,algorithm,emb,entity_map,wikipathway,subgraph_nodes,annotated_nodes,all_subgraphs_cosine_sim,node_type,compared_pathway):

    #For each guiding term calculate cosine values to all nodes in supgraph
    for t in range(len(comparison_terms_df)):
        term_row = comparison_terms_df.iloc[t]
        if node_type == 'labels':
            avg_cosine_sim,embeddings = calc_cosine_sim_from_label_list(emb,entity_map,subgraph_nodes,annotated_nodes,g.labels_all,kg_type,embeddings,term_row)
        elif node_type == 'uris':
            avg_cosine_sim,embeddings = calc_cosine_sim_from_uri_list(emb,entity_map,subgraph_nodes,g.labels_all,kg_type,embeddings,term_row)
        #Organize all path cosine similarity values into dictionary per term
        all_subgraphs_cosine_sim = generate_comparison_terms_dict(all_subgraphs_cosine_sim,term_row,avg_cosine_sim,algorithm,wikipathway,compared_pathway)

    return all_subgraphs_cosine_sim,embeddings


def compare_subgraph_guiding_terms(s,subgraph_df,g,comparison_terms,kg_type,embeddings,algorithm,emb,entity_map,wikipathway,all_subgraphs_cosine_sim,node_type):

    #Get all nodes from subgraph not in original edgelist
    subgraph_nodes = unique_nodes(subgraph_df[['S_ID','O_ID']])
    #input_nodes = unique_nodes(s[['source_id','target_id']])
    #If comparing to intermediate terms only in subgraph
    #intermediate_nodes = [i for i in subgraph_nodes if i not in input_nodes]

    #When passed only the terms of that wikipathway abstract
    if isinstance(comparison_terms,pd.DataFrame):
       all_subgraphs_cosine_sim,embeddings = get_cosine_sim_one_pathway(g,comparison_terms,kg_type,embeddings,algorithm,emb,entity_map,wikipathway,subgraph_nodes,s,all_subgraphs_cosine_sim,node_type,wikipathway)

    #When passed the terms of all wikipathway abstracts as dictionary
    elif isinstance(comparison_terms,dict):
        for w in comparison_terms.keys():
            w_comparison_terms_df = comparison_terms[w]
            all_subgraphs_cosine_sim,embeddings = get_cosine_sim_one_pathway(g,w_comparison_terms_df,kg_type,embeddings,algorithm,emb,entity_map,wikipathway,subgraph_nodes,s,all_subgraphs_cosine_sim,node_type,w)

    '''elif isinstance(comparison_terms,list):
        new_df_vals = []
        for i in range(len(subgraph_df)):
            new_df_vals.append()'''

    return all_subgraphs_cosine_sim,embeddings

def get_wikipathways_subgraph(annotated_wikipathways_subgraph_df):

    wikipathways_subgraph_df = annotated_wikipathways_subgraph_df[['source_id',  'target_id']]
    wikipathways_subgraph_df = wikipathways_subgraph_df.rename(columns={'source_id' : 'S_ID', 'target_id': 'O_ID'})

    return wikipathways_subgraph_df


