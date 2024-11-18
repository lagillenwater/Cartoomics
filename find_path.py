import os
import re

import duckdb
from tqdm import tqdm
from constants import METAPATH_SEARCH_MAPS, PKL_SUBSTRINGS
from duckdb_utils import create_subject_object_pair_table, drop_table, duckdb_load_table, get_table_count, join_tables_subject_object, output_table_to_file, remove_character_from_table
from graph_embeddings import Embeddings
import numpy as np
import pandas as pd
from scipy import spatial
from scipy.spatial import distance
from collections import Counter, defaultdict
from assign_nodes import unique_nodes
import igraph
import networkx as nx
from functools import reduce
from operator import itemgetter


#Go from label to entity_uri (for PKL original labels file) or Label to Idenifier (for microbiome PKL)
# kg_type adds functionality for kg-covid19
def get_uri(labels,value, kg_type):

    if kg_type == 'pkl':
        uri = labels.loc[labels['label'] == value,'entity_uri'].values[0]
    if kg_type == 'kg-covid19':
        uri = labels.loc[labels['label'] == value,'id'].values[0]
    
        
    return uri

def get_label(labels,value,kg_type):
    if kg_type == 'pkl':
        label = labels.loc[labels['entity_uri'] == value,'label'].values[0]
    if kg_type == 'kg-covid19':
        label = labels.loc[labels['id'] == value,'label'].values[0]        
    return label



def get_key(dictionary,value):

    for key, val in dictionary.items():
        if val == value:
            return key

def process_path_nodes_value(graph,value):

    if isinstance(graph.graph_object,igraph.Graph):
        n = graph.graph_nodes[value]
    if isinstance(graph.graph_object, nx.Graph):
        n = value

    return n


def define_path_triples(graph,path_nodes,search_type):

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #Keep track of # of mechanisms generated for this node pair in file name for all shortest paths
    count = 1 
    #When there is no connection in graph, path_nodes will equal 1 ([[]]) or when there's a self loop
    if len(path_nodes[0]) != 0:
        for p in range(len(path_nodes)):
            #Dataframe to append each triple to
            full_df = pd.DataFrame()
            # path_nodes contains integers for igraph, uris for networkx
            n1 = process_path_nodes_value(graph,path_nodes[p][0])
            for i in range(1,len(path_nodes[p])):
                n2 = process_path_nodes_value(graph,path_nodes[p][i])
                if search_type.lower() == 'all':
                    #Try first direction which is n1 --> n2
                    df = graph.edgelist.loc[(graph.edgelist['subject'] == n1) & (graph.edgelist['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                    if len(df) == 0:
                        #If no results, try second direction which is n2 --> n1
                        df = graph.edgelist.loc[(graph.edgelist['object'] == n1) & (graph.edgelist['subject'] == n2)]
                        full_df = pd.concat([full_df,df])
                elif search_type.lower() == 'out':
                    #Only try direction n1 --> n2
                    df = graph.edgelist.loc[(graph.edgelist['subject'] == n1) & (graph.edgelist['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                full_df = full_df.reset_index(drop=True)
                n1 = n2
                                        
            #For all shortest path search
            if len(path_nodes) > 1:
                #Generate df
                full_df.columns = ['S_ID','P_ID','O_ID']
                mechanism_dfs['mech#_'+str(count)] = full_df
                count += 1
                
            #For shortest path search
        if len(path_nodes) == 1:
            #Generate df
            full_df.columns = ['S_ID','P_ID','O_ID']
            return full_df

    # Return empty df if no path found
    else:
        df = pd.DataFrame()
        return df

    #Return dictionary if all shortest paths search
    if len(path_nodes) > 1:
        return mechanism_dfs

def convert_to_node_uris(node_pair,graph,kg_type):

    try:
        if node_pair['source_id'] != 'not_needed':
            node1 = node_pair['source_id']
        else:
            node1 = get_uri(graph.labels_all,node_pair['source_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError: 
        node1 = get_uri(graph.labels_all,node_pair['source_label'], kg_type)
   
    try:
        if node_pair['target_id'] != 'not_needed':
            node2 = node_pair['target_id']
        else:
            node2 = get_uri(graph.labels_all,node_pair['target_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError:
        node2 = get_uri(graph.labels_all,node_pair['target_label'], kg_type)

    return node1, node2

### networkx implementation of find all shortest paths. Still uses both graphs (3/21/24)(LG)

def find_all_shortest_paths(node_pair,graph,weights,search_type, kg_type):

    w = None
    node1, node2 = convert_to_node_uris(node_pair,graph,kg_type)
    
    #Add weights if specified # only igraph supported
    # if weights:
    #     w = graph.es["weight"]

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    if isinstance(graph.graph_object, nx.Graph):
        path_nodes = nx.all_shortest_paths(graph.graph_object,node1,node2)

    if isinstance(graph.graph_object, igraph.Graph):
        path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    #Remove duplicates for bidirectional nodes, only matters when search type=all for mode
    path_nodes = list(set(tuple(x) for x in path_nodes))
    path_nodes = [list(tup) for tup in path_nodes]
    path_nodes = sorted(path_nodes,key = itemgetter(1))

    #Dictionary of all triples that are shortest paths, not currently used
    #mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes


def convert_path_nodes(path_node,entity_map):

    n = entity_map[path_node]

    return n

def get_embedding(emb,node):

    embedding_array = emb[str(node)]
    embedding_array = np.array(embedding_array)

    return embedding_array

def calc_cosine_sim(emb,entity_map,path_nodes,graph,search_type,kg_type,guiding_term,input_nodes_df):

    # Handle when no paths were found
    if len(path_nodes[0]) == 0:
        chosen_path_nodes_cs = [[]]
        all_paths_cs_values = []
    elif len(path_nodes[0]) > 1:
        # Set target embedding value to target node if no guiding term is provided and target node is the same for every path
        if guiding_term.empty:
            # Check if target node is the same for every path
            all_identical = all(sublist[-1] == path_nodes[0][-1] for sublist in path_nodes)
            # Set n1 to target node for cases where all_identical is false
            n1 = process_path_nodes_value(graph,path_nodes[0][len(path_nodes[0])-1])

        #Set target embedding value to guiding term if it exists
        else:
            try:
                n1 = guiding_term['term_id']
            except KeyError:
                n1 = get_uri(graph.labels_all,guiding_term['term_label'], kg_type)

        n1_int = convert_path_nodes(n1,entity_map)
        target_emb = get_embedding(emb,n1_int)

        #Dict of all embeddings to reuse if they exist
        embeddings = defaultdict(list)
        
        #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
        all_paths_cs_values = []
        print("iterating through path_nodes")
        for l in path_nodes:
            cs = []
            # Set target emb to new final node if not all identical
            if not all_identical:
                n1 = process_path_nodes_value(graph,l[-1])
                n1_int = convert_path_nodes(n1,entity_map)
                target_emb = get_embedding(emb,n1_int)
            for i in range(0,len(l)-1):
                n1 = process_path_nodes_value(graph,l[i])
                n1_int = convert_path_nodes(n1,entity_map)
                if n1_int not in list(embeddings.keys()):
                    e = get_embedding(emb,n1_int)
                    embeddings[n1_int] = e
                else:
                    e = embeddings[n1_int]
                cs.append(1 - spatial.distance.cosine(e,target_emb))
            all_paths_cs_values.append(cs)

        #Get sum of all cosine values in value_list
        value_list = list(map(sum, all_paths_cs_values))
        chosen_path_nodes_cs = select_max_path(value_list,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(graph,chosen_path_nodes_cs,search_type)

    df = convert_to_labels(df,graph.labels_all,kg_type,input_nodes_df)

    return df,all_paths_cs_values,chosen_path_nodes_cs[0]

def calc_cosine_sim_from_label_list(emb,entity_map,node_labels,annotated_nodes,labels_all,kg_type,embeddings,guiding_term):

    annotated_node_labels = unique_nodes(annotated_nodes[['source','target']])

    #Set target embedding value to guiding term if it exists
    try:
        n1 = guiding_term['term_id']
    except KeyError:
        n1 = get_uri(labels_all,guiding_term['term_label'], kg_type)

    #Dict of all embeddings to reuse if they exist
    #embeddings = defaultdict(list)

    n1_int = convert_path_nodes(n1,entity_map)
    if n1_int not in list(embeddings.keys()):
        target_emb= get_embedding(emb,n1_int)
        embeddings[n1_int] = target_emb
    else:
        target_emb = embeddings[n1_int]
    
    #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_cs_values = []

    #Searches for cosine similarity between each node and the guiding term
    for node in node_labels:
        if node in annotated_node_labels:
            try:
                n1 = annotated_nodes.loc[annotated_nodes['source'] == node,'source_id'].values[0]
            except IndexError:
                n1 = annotated_nodes.loc[annotated_nodes['target'] == node,'target_id'].values[0]
        else:
            n1 = get_uri(labels_all,node, kg_type)
        n1_int = convert_path_nodes(n1,entity_map)
        if n1_int not in list(embeddings.keys()):
            e = get_embedding(emb,n1_int)
            embeddings[n1_int] = e
        else:
            e = embeddings[n1_int]
        cs = 1 - spatial.distance.cosine(e,target_emb)
        all_paths_cs_values.append(cs)

    #Calculate average cosine similarity to this guiding term for entire subgraph
    avg_cosine_sim = sum(all_paths_cs_values) / len(all_paths_cs_values)

    return avg_cosine_sim,embeddings

def calc_cosine_sim_from_uri_list(emb,entity_map,node_uris,labels_all,kg_type,embeddings,guiding_term):

    #Set target embedding value to guiding term if it exists
    try:
        n1 = guiding_term['term_id']
    except KeyError:
        n1 = get_uri(labels_all,guiding_term['term_label'], kg_type)
    
    #Dict of all embeddings to reuse if they exist
    #embeddings = defaultdict(list)

    n1_int = convert_path_nodes(n1,entity_map)
    if n1_int not in list(embeddings.keys()):
        target_emb= get_embedding(emb,n1_int)
        embeddings[n1_int] = target_emb
    else:
        target_emb = embeddings[n1_int]
    
    #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_cs_values = []

    #Searches for cosine similarity between each node and the guiding term
    for n1 in node_uris:
        n1_int = convert_path_nodes(n1,entity_map)
        if n1_int not in list(embeddings.keys()):
            e = get_embedding(emb,n1_int)
            embeddings[n1_int] = e
        else:
            e = embeddings[n1_int]
        cs = 1 - spatial.distance.cosine(e,target_emb)
        all_paths_cs_values.append(cs)

    #Calculate average cosine similarity to this guiding term for entire subgraph
    avg_cosine_sim = sum(all_paths_cs_values) / len(all_paths_cs_values)

    return avg_cosine_sim,embeddings

def calc_pdp(path_nodes,graph,w,search_type,kg_type,input_nodes_df):

    #List of pdp for each path in path_nodes, should be same length as path_nodes
    #paths_pdp = []

    #List of lists of pdp for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_pdp_values = []

    for l in path_nodes:
        pdp = 1
        for i in range(0,len(l)-1):
            if isinstance(graph.graph_object, igraph.Graph):
                dp = graph.graph_object.degree(l[i],mode='all',loops=True)
            if isinstance(graph.graph_object, nx.Graph):
                # Get node name first which is uri
                node = l[i]
                dp = graph.graph_object.degree(node)
            dp_damped = pow(dp,-w)
            pdp = pdp*dp_damped

        #paths_pdp.append(pdp)
        all_paths_pdp_values.append(pdp)

    chosen_path_nodes_pdp = select_max_path(all_paths_pdp_values,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(graph,chosen_path_nodes_pdp,search_type)

    df = convert_to_labels(df,graph.labels_all,kg_type,input_nodes_df)

    return df,all_paths_pdp_values,chosen_path_nodes_pdp

def select_max_path(value_list,path_nodes):

    #Get max value from value_list, use that idx of path_nodes then create mechanism
    max_index = value_list.index(max(value_list))
    #Must be list of lists for define_path_triples function
    chosen_path_nodes = [path_nodes[max_index]]

    return chosen_path_nodes

def convert_to_labels(df,labels_all,kg_type,input_nodes_df):

    all_s = []
    all_p = []
    all_o = []

    if kg_type == 'pkl':
        for i in range(len(df)):
            try:
                S = input_nodes_df.loc[input_nodes_df['source_id'] == df.iloc[i].loc['S_ID'],'source_label'].values[0]
            except IndexError:
                S = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S_ID'],'label'].values[0]
            P = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P_ID'],'label'].values[0]
            try:
                O = input_nodes_df.loc[input_nodes_df['target_id'] == df.iloc[i].loc['O_ID'],'target_label'].values[0]
            except IndexError:
                O = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O_ID'],'label'].values[0]
            all_s.append(S)
            all_p.append(P)
            all_o.append(O)
    #Need to test for kg-covid19 that S_ID/P_ID/O_ID addition to df works 
    if kg_type == 'kg-covid19' or kg_type == 'kg-microbe':
        for i in range(len(df)):
            try:
                S = input_nodes_df.loc[input_nodes_df['source_id'] == df.iloc[i].loc['S_ID'],'source_label'].values[0]
            except IndexError:
                s_label =  labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S_ID'],'label'].values[0]
                if s_label != "":
                    S = s_label
            P = df.iloc[i].loc['P_ID'].split(':')[-1]
            try:
                O = input_nodes_df.loc[input_nodes_df['target_id'] == df.iloc[i].loc['O_ID'],'target_label'].values[0]
            except IndexError:
                o_label =  labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O_ID'],'label'].values[0]
                if o_label != "":
                    O = o_label 
            all_s.append(S)
            all_p.append(P)
            all_o.append(O)

    df['S'] = all_s
    df['P'] = all_p
    df['O'] = all_o
    #Reorder columns
    df = df.reindex(columns=['S', 'P', 'O', 'S_ID', 'P_ID', 'O_ID'])
    # df = df[['S','P','O','S_ID','P_ID','O_ID']]
    df = df.reset_index(drop=True)
    return df

# Wrapper functions
#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path(start_node,end_node,graph,weights,search_type, kg_type, input_nodes_df):

    node1 = get_uri(graph.labels_all,start_node,kg_type)
    node2 = get_uri(graph.labels_all,end_node,kg_type)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    df = define_path_triples(graph,path_nodes,search_type)

    df = convert_to_labels(df,graph,kg_type,input_nodes_df)

    return df

#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path_pattern(start_node,end_node,graph,weights,search_type, kg_type,s,manually_chosen_uris):

    node1 = start_node
    node2 = end_node

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    if len(path_nodes[0]) > 0:

        df = define_path_triples(graph,path_nodes,search_type)

    else:
        df = pd.DataFrame()

    return df,manually_chosen_uris

def prioritize_path_cs(input_nodes_df,node_pair,graph,weights,search_type,triples_file,input_dir,embedding_dimensions, kg_type, search_algorithm, id_keys_df, path_nodes = 'none', guiding_term=pd.Series()):
  
    if path_nodes == 'none':
        if search_algorithm == "Shortest_Path":
            path_nodes = find_all_shortest_paths(node_pair,graph,False,'all', kg_type)
        elif search_algorithm == "Metapath" or search_algorithm == "Metapath_Neighbors":
            # Convert node pair into prefixes to search existing metapath files
            # path_nodes = find_all_metapaths_files(node_pair,graph,kg_type,input_dir,triples_file)
            path_nodes,id_keys_df = find_all_metapaths_duckdb(node_pair,graph,kg_type,input_dir,triples_file,id_keys_df,graph.labels_all)

    ### Removing embeddings path prioritization for now
    # if len(path_nodes[0]) > 0:
    #     e = Embeddings(triples_file,input_dir,embedding_dimensions, kg_type)
    #     emb,entity_map = e.generate_graph_embeddings(kg_type)
    #     df,all_paths_cs_values,chosen_path_nodes_cs = calc_cosine_sim(emb,entity_map,path_nodes,graph,search_type, kg_type, guiding_term,input_nodes_df)

    else:
        df = pd.DataFrame()
        all_paths_cs_values = []
        chosen_path_nodes_cs = []

    # Temp solution to not using embeddings
    all_paths_cs_values = [[0] for _ in range(len(path_nodes))]
    chosen_path_nodes_cs = [path_nodes[0]]
    # Taken from calc_cosine_sim
    df = define_path_triples(graph,chosen_path_nodes_cs,search_type)
    df = convert_to_labels(df,graph.labels_all,kg_type,input_nodes_df)
    return path_nodes,df,all_paths_cs_values,chosen_path_nodes_cs,id_keys_df

def generate_comparison_terms_dict(subgraph_cosine_sim,term_row,avg_cosine_sim,algorithm,wikipathway,compared_pathway):

    #Add average cosine similarity of subgraph for this term to dictionary
    l = {}
    l['Term'] = term_row['term_label']
    l['Term_ID']= term_row['term_id']
    l['Average_Cosine_Similarity'] = avg_cosine_sim
    l['Algorithm'] = algorithm
    l['Pathway_ID'] = wikipathway
    l['Compared_Pathway'] = compared_pathway

    subgraph_cosine_sim.append(l)
    
    return subgraph_cosine_sim


def prioritize_path_pdp(input_nodes_df,node_pair,graph,weights,search_type,triples_file,input_dir,pdp_weight, kg_type, search_algorithm, path_nodes = 'none'):

    if path_nodes == 'none':
        path_nodes = find_all_shortest_paths(node_pair,graph,False,search_type, kg_type)
        if search_algorithm == "Shortest_Path":
            path_nodes = find_all_shortest_paths(node_pair,graph,False,'all', kg_type)
        elif search_algorithm == "Metapath":
            # Convert node pair into prefixes to search existing metapath files
            path_nodes = find_all_metapaths(node_pair,graph,kg_type,input_dir,triples_file)
            print("after metapath search")
            print(path_nodes)
    

    df,all_paths_pdp_values,chosen_path_nodes_pdp = calc_pdp(path_nodes,graph,pdp_weight,search_type, kg_type,input_nodes_df)

    return path_nodes,df,all_paths_pdp_values,chosen_path_nodes_pdp[0]

# expand nodes by drugs 1 hop away # only for igraph object
def drugNeighbors(graph,nodes, kg_type,input_nodes_df):
    neighbors = []
    if kg_type == 'kg-covid19':
        nodes = list(graph.labels_all[graph.labels_all['label'].isin(nodes)]['id'])
    for node in nodes:
        tmp_nodes = graph.graph_object.neighbors(node,mode = "in")
        tmp = graph.graph_object.vs(tmp_nodes)['name']
        drug_neighbors = [i for i in tmp if re.search(r'Drug|Pharm',i)]
        if len(drug_neighbors) != 0:
            for source in drug_neighbors:
                path = graph.graph_object.get_shortest_paths(v = source, to = node)
                path_triples = define_path_triples(graph.graph_nodes,graph.edgelist,path, 'all')
                path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type,input_nodes_df)
                neighbors.append(path_labels)
    all_neighbors = pd.concat(neighbors)
    return all_neighbors
    


def drug_neighbors_wrapper(input_nodes_df, subgraph_df,graph,kg_type):
    subgraph_nodes = unique_nodes(subgraph_df[['S','O']])
    all_neighbors = drugNeighbors(graph,subgraph_nodes,kg_type,input_nodes_df)
    updated_subgraph = pd.concat([subgraph_df,all_neighbors])
    for_input = pd.concat([all_neighbors[['S','O']],all_neighbors[['S','O']]],axis = 1)
    for_input.columns = ['source', 'target', 'source_label', 'target_label']
    updated_input_nodes_df = pd.concat([input_nodes_df, for_input])
    return updated_input_nodes_df, updated_subgraph

def get_metapaths(metapath_filepath):

    # Input metapath template
    metapaths_df = pd.read_csv(metapath_filepath, sep="|")
    path_list = metapaths_df.values.tolist()
    metapaths_df = metapaths_df.replace(METAPATH_SEARCH_MAPS)
    metapaths_list = metapaths_df.values.tolist()

    # Break metapath into list of lists of triples excluding predicate ([[s,o]])
    for template in path_list:
        template_list = [list(template[i:i+3]) for i in range(0, len(template) - 2, 2)]
    for metapath in metapaths_list:
        triples_list = [list(metapath[i:i+3]) for i in range(0, len(metapath) - 2, 2)]

    return triples_list,template_list

def duckdb_metapath_search(filepath, metapaths_list, output_table_name, output_dir):

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")

    duckdb_load_table(conn, filepath, "edges", ["subject", "predicate", "object"])

    ct = get_table_count(conn, "edges")

    tables = []

    for s, p, o in metapaths_list:

        create_subject_object_pair_table(
            conn,
            table_name = "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]),
            base_table_name = "edges",
            subject = re.sub(r'[/_]', '', s).replace('-','_'),
            object = re.sub(r'[/_]', '', o).replace('-','_'),
            subject_prefix = "%" + s + "%",
            predicate_prefix = "%" + p + "%",
            object_prefix = "%" + o + "%"
        )

        ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))
        if ct == 0:

            drop_table(conn, "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))

            # Swap direction of search
            create_subject_object_pair_table(
                conn,
                table_name = "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]),
                base_table_name = "edges",
                subject = re.sub(r'[/_]', '', o).replace('-','_'),
                object = re.sub(r'[/_]', '', s).replace('-','_'),
                subject_prefix = "%" + o + "%",
                predicate_prefix = "%" + p + "%",
                object_prefix = "%" + s + "%"
            )

            ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))

        tables.append("_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))

    tables_paired = [list(pair) for pair in zip(tables, tables[1:])]

    for t in tables_paired:

        join_tables_subject_object(
            conn, 
            base_table_name = t[1], 
            compared_table_name = t[0], 
            output_table_name = output_table_name,
            output_subject = t[0].split("_")[0].replace('-','_'), 
            output_object = t[1].split("_")[1].replace('-','_'), 
            comparison = t[0].split("_")[1].replace('-','_')
        )

        ct = get_table_count(conn, output_table_name)

    output_table_to_file(conn, output_table_name, output_dir + "/" + output_table_name + "_pairs.tsv")

def convert_genes_to_proteins(conn,base_table_name,gene_uri,id_key_df,labels,kg_type):

    # Convert general uri to protein if search metapath_neighbors
    if gene_uri == METAPATH_SEARCH_MAPS["gene"]:
        protein = METAPATH_SEARCH_MAPS["protein"]

    else:
        # Remove special characters from uri since duckdb doesn't handle them
        gene_id = re.search(r'http://(.*)', gene_uri).group(1)
        gene_tag = gene_id.replace("/","_").replace(".","_")

        create_subject_object_pair_table(
                conn,
                table_name = "gene_match", #gene_tag+"_protein",
                base_table_name = base_table_name,
                subject = "gene", #gene_tag,
                object = "PR",
                subject_prefix = "%" + gene_id,
                predicate_prefix = "%RO_0002205%",
                object_prefix = "%PR_%"
            )

        result = conn.execute(
            f"""
            SELECT "gene","PR" FROM gene_match;
            """
        ).fetchall()

        # Replace IDs with labels so that they can later on be matched to final mechanism to ensure Extra/Original nodes are labeled
        result_list = [list(t) for t in result]
        for r in result_list:
            s = r[0]
            o = r[1]
            s_label = get_label(labels,s,kg_type)
            o_label = get_label(labels,o,kg_type)
            r[0] = s_label
            r[1] = o_label

        # ct = get_table_count(conn, "gene_match")
        result_df = pd.DataFrame(result_list, columns = ["Original","New"])
        id_key_df = pd.concat([id_key_df, result_df], ignore_index=True)
        protein = result[0][1]

        drop_table(conn, "gene_match")

    return protein,id_key_df

def get_metapath_key(label):

    for i in METAPATH_SEARCH_MAPS.values():
        if i in label:
            prefix = i

    metapath_key = next(k for k, v in METAPATH_SEARCH_MAPS.items() if v == prefix)

    return metapath_key

def find_all_metapaths_files(node_pair,graph,kg_type,input_dir,triples_list_file):

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])

    node1, node2 = convert_to_node_uris(node_pair,graph,kg_type)
    if "gene" in node1:
        node1 = convert_genes_to_proteins(conn,"edges",node1)
    if "gene" in node2:    
        node2 = convert_genes_to_proteins(conn,"edges",node2)
    if node1 is None or node2 is None:
        path_nodes = [[]]

    else:
        # Doing this using files

        # Search existing metapaths by node pair to return [[source,target]] pairs
        metapath_filenames = [str(f) for f in os.listdir(input_dir + "/metapaths") if "_pairs" in f]
        path_nodes = []
        for f_name in metapath_filenames:
            # Get source_target prefixes from filename
            pairs = f_name.split("_")
            # See if given node uris match those prefixes
            if pairs[0] == get_metapath_key(node1) and pairs[1] == get_metapath_key(node2):
                # Doing this using a file, takes too long
                metapath_df = pd.read_csv(input_dir + "/metapaths/" + f_name,sep="\t")
                for index, row in tqdm(metapath_df.iterrows(), total=len(metapath_df)):
                    source = row.iloc[0]
                    target = row.iloc[-1]
                    # nodes_row = [i.replace("<", "").replace(">","") for i in nodes_row]
                    # Search for node relationship in forward direction, only append source and target not predicate
                    if node1 == source and node2 == target:
                        # Only include nodes, not predicates, in row
                        nodes_row =  [row[i] for i in range(len(row)) if i % 2 == 0]
                        path_nodes.append(nodes_row)
                    # Search for node relationship in reverse direction, only append source and target not predicate
                    if node2 == source and node1 == target:
                        # Only include nodes, not predicates, in row
                        nodes_row =  [row[i] for i in range(len(row)) if i % 2 == 0]
                        path_nodes.append(nodes_row)

        path_nodes = sorted(path_nodes,key = itemgetter(1))
        if len(path_nodes) == 0:
            path_nodes = [[]]

    return path_nodes

def get_all_input_metapaths(input_dir):
    """
    Args:
        input_dir (str): Input directory

    Returns:
        list: list of metapaths as triples
    """

    metapaths_file = input_dir+'/metapaths/Input_Metapaths.csv'
    # Get list of triples in metapath by prefix, e.g. [['PR_', '', 'CHEBI_'], ['CHEBI_', '', 'MONDO_']]
    # Input metapath template
    metapaths_df = pd.read_csv(metapaths_file, sep="|")
    metapaths_df = metapaths_df.replace(METAPATH_SEARCH_MAPS)
    metapaths_list = metapaths_df.values.tolist()

    return metapaths_list

def replace_target_node_type(start_node_uri, input_dir):
    """
    Args:
        start_node (str): label of input node to search for neighbors around
        input_dir (str): Input directory

    Returns:
        end_nodes: List of node types of end_node based on metapaths and start_node type.
    """

    metapaths_list = get_all_input_metapaths(input_dir)

    # Define the start_node node type
    start_node_type = [i for i in list(METAPATH_SEARCH_MAPS.values()) if i in start_node_uri][0]

    # Match node type to metapaths that include it as the source node
    relevant_metapaths = [sublist for sublist in metapaths_list if sublist[0] == start_node_type]
    end_nodes = [metapath[-1] for metapath in relevant_metapaths]

    # Remove duplicates
    end_nodes = list(set(end_nodes))

    return end_nodes

def find_all_metapaths_duckdb(node_pair,graph,kg_type,input_dir,triples_list_file,id_keys_df,labels):

    metapaths_list = get_all_input_metapaths(input_dir)

    # List of each metapath by the given triples, eg: [[['NCBITaxon', '%', 'CHEBI'], ['CHEBI', '%', 'MONDO']]]
    triples_list = []
    for metapath in metapaths_list:
        l = [list(metapath[i:i+3]) for i in range(0, len(metapath) - 2, 2)]
        triples_list.append(l)

    print("triples_list")
    print(triples_list)

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")
    conn.execute("PRAGMA memory_limit='64GB'")
    # List of paths found that match metapaths, will match length of filtered_metapaths
    all_path_nodes = []

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])

    node1, node2 = convert_to_node_uris(node_pair,graph,kg_type)
    if "gene" in node1:
        node1,id_keys_df = convert_genes_to_proteins(conn,"edges",node1,id_keys_df,labels,kg_type)
    if "gene" in node2:    
        node2,id_keys_df = convert_genes_to_proteins(conn,"edges",node2,id_keys_df,labels,kg_type)
    if node1 is None or node2 is None:
        path_nodes = [[]]


    else:
        print("search duckdb")

        # Doing this using Duckdb

        # First only get metapaths that match the input nodes
        # Filter the metapaths based on the first and last values, eg: [[['NCBITaxon', '%', 'CHEBI'], ['CHEBI', '%', 'MONDO']]]
        filtered_metapaths = [m for m in triples_list if m[0][0] in node1 and m[-1][-1] in node2]
        print("filtered_metapaths")
        print(filtered_metapaths)

        # Search existing metapaths by node pair/triple to return [[source,target]] pairs
        # Go through each metapath that matches node1, node2
        for m in filtered_metapaths:
            # List of each paired table found with duckdb, eg: CHEBI_MONDO:XX, UniprotKB:MONDO:XX
            tables = []
            # Go through each triple that is in the metapath
            for i, (s, p, o) in enumerate(m):
                #if get_metapath_key(node1) == s and get_metapath_key(node2) == o:
                if i == len(m) - 1:
                    # read in table with this protein as s or o, r, and and PR_ as o or s
                    create_subject_object_pair_table(
                        conn,
                        table_name = "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', node2)]),
                        base_table_name = "edges",
                        subject = re.sub(r'[/_]', '', s),
                        object = re.sub(r'[/_]', '', node2),
                        subject_prefix = "%" + s + "%",
                        predicate_prefix = "%" + p + "%",
                        object_prefix = "%" + node2 + "%"
                    )

                    ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', node2)]))
                    print("num paths last triple: ",s,node2,ct)

                    if ct > 0:
                        tables.append("_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', node2)]))

                    if ct == 0:
                        # read in table with this protein as s or o, r, and and PR_ as o or s
                        create_subject_object_pair_table(
                            conn,
                            table_name = "_".join([re.sub(r'[/_]', '', node2),re.sub(r'[/_]', '', s)]),
                            base_table_name = "edges",
                            subject = re.sub(r'[/_]', '', node2),
                            object = re.sub(r'[/_]', '', s),
                            subject_prefix = "%" + node2 + "%",
                            predicate_prefix = "%" + p + "%",
                            object_prefix = "%" + s + "%"
                        )

                        ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', node2),re.sub(r'[/_]', '', s)]))
                        print("num paths last triple: ",node2,s,ct)

                        if ct > 0:
                            tables.append("_".join([re.sub(r'[/_]', '', node2),re.sub(r'[/_]', '', s)]))

                elif i == 0:
                    # read in table with this protein as s or o, r, and and PR_ as o or s
                    create_subject_object_pair_table(
                        conn,
                        table_name = "_".join([re.sub(r'[/_]', '', node1),re.sub(r'[/_]', '', o)]),
                        base_table_name = "edges",
                        subject = re.sub(r'[/_]', '', node1),
                        object = re.sub(r'[/_]', '', o),
                        subject_prefix = "%" + node1 + "%",
                        predicate_prefix = "%" + p + "%",
                        object_prefix = "%" + o + "%"
                    )

                    ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', node1),re.sub(r'[/_]', '', o)]))
                    print("num paths first triple: ",node1,o,ct)

                    if ct > 0:
                        tables.append("_".join([re.sub(r'[/_]', '', node1),re.sub(r'[/_]', '', o)]))
                    
                    if ct == 0:
                        # read in table with this protein as s or o, r, and and PR_ as o or s
                        create_subject_object_pair_table(
                            conn,
                            table_name = "_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', node1)]),
                            base_table_name = "edges",
                            subject = re.sub(r'[/_]', '', o),
                            object = re.sub(r'[/_]', '', node1),
                            subject_prefix = "%" + o + "%",
                            predicate_prefix = "%" + p + "%",
                            object_prefix = "%" + node1 + "%"
                        )

                        ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', node1)]))
                        print("num paths first triple: ",o,node1,ct)
                        if ct > 0:
                            tables.append("_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', node1)]))

                else:
                    create_subject_object_pair_table(
                        conn,
                        table_name = "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]),
                        base_table_name = "edges",
                        subject = re.sub(r'[/_]', '', s),
                        object = re.sub(r'[/_]', '', o),
                        subject_prefix = "%" + s + "%",
                        predicate_prefix = "%" + p + "%",
                        object_prefix = "%" + o + "%"
                    )

                    ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))
                    print("num paths middle triple: ",s,o,ct)

                    if ct > 0:
                        tables.append("_".join([re.sub(r'[/_]', '', s),re.sub(r'[/_]', '', o)]))
                    
                    if ct == 0:
                        # read in table with this protein as s or o, r, and and PR_ as o or s
                        create_subject_object_pair_table(
                            conn,
                            table_name = "_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', s)]),
                            base_table_name = "edges",
                            subject = re.sub(r'[/_]', '', o),
                            object = re.sub(r'[/_]', '', s),
                            subject_prefix = "%" + o + "%",
                            predicate_prefix = "%" + p + "%",
                            object_prefix = "%" + s + "%"
                        )

                        ct = get_table_count(conn, "_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', s)]))
                        print("num paths middle triple: ",o,s,ct)
                        if ct > 0:
                            tables.append("_".join([re.sub(r'[/_]', '', o),re.sub(r'[/_]', '', s)]))

            print("tables")
            print(tables)
            # 
            tables_paired = [list(pair) for pair in zip(tables, tables[1:])]
            print("tables_paired")
            print(tables_paired)

            # Confirm that values were found for each triple in metapath, ex: [['NCBITaxon:165179_CHEBI', 'CHEBI_MONDO:0005180']]
            if len(tables_paired) < (len(m) - 1): path_nodes = []
            else:
                # Get complete metapaths
                for t in tables_paired:
                    # List of path nodes for given triple
                    # triples_path_nodes = []
                    print(t)
                    # Compare over the prefix that matches
                    t_prefixes = [s.split('_') for s in t]
                    comparison_prefix = list(set(t_prefixes[0]) & set(t_prefixes[1]))[0]
                    subject_prefix = [i for i in t[0].split("_") if i != comparison_prefix][0]
                    object_prefix = [i for i in t[1].split("_") if i != comparison_prefix][0]

                    join_tables_subject_object(
                        conn, 
                        base_table_name = t[1], 
                        compared_table_name = t[0], 
                        output_table_name = "full_metapath",
                        output_subject = subject_prefix, #t[0].split("_")[0], 
                        output_object = object_prefix, #t[1].split("_")[1], 
                        comparison = comparison_prefix #t[0].split("_")[1]
                    )

                    ct = get_table_count(conn, "full_metapath")
                    print("full_metapath: ",ct)

                    # query = (
                    #     f"""
                    #     SELECT "{subject_prefix}", "{comparison_prefix}","{object_prefix}" FROM full_metapath;
                    #     """
                    # )
                    ################ WORKING HERE ##################
                    query = (
                        f"""
                        SELECT * FROM full_metapath;
                        """
                    )

                    result = conn.execute(query).fetchall()
                    print(query)
                    print(result)

                    # Returns path from the given triple t
                    path_nodes = conn.execute(query).df().values.tolist()
                    all_path_nodes.extend(path_nodes)

                    drop_table(conn, "full_metapath")
            
                # When more than 2 triples were involved, need to combine by object/subject aligning prefixes
                print("before combining")
                print(all_path_nodes)
                if len(m) > 2:
                    all_path_nodes = combine_paths_in_metapath(all_path_nodes,m[0][0])
                    print("after combining")
                    print(all_path_nodes)

    print("all_path_nodes")
    print(all_path_nodes)
    # Don't know why this is necessary, removed for now
    # all_path_nodes = sorted(all_path_nodes,key = itemgetter(1))
    
    if len(all_path_nodes) == 0:
        all_path_nodes = [[]]

    return all_path_nodes,id_keys_df

# def find_matching_triples(given_list, rest_of_lists):
#     matching_triples = []
    
#     # Iterate through each list of triples in rest_of_lists
#     for triple in rest_of_lists:
#         # Check if the second value in the triple exists in the given_list
#         if triple[1] in given_list:
#             matching_triples.append(triple)
    
#     return matching_triples

def merge_lists_on_overlap(list1, list2):
    """_summary_

    Args:
        list1 (list): A list of combined triples
        list2 (list): A list of combined triples

    Returns:
        list: Merged lists based on overlapping values if the values before the overlapping values between the 2 lists don't match and the values after the overlapping values between the 2 lists don't match.
    """
    merged_lists = []
    
    # Iterate through list1 and list2 to find consecutive overlapping elements
    for i in range(len(list1) - 1):  # Loop through list1
        for j in range(len(list2) - 1):  # Loop through list2
            # Check for consecutive overlap
            if list1[i] == list2[j] and list1[i+1] == list2[j+1]:
                # Check if the elements before the overlap in both lists do not match
                if i > 0 and j > 0 and list1[i-1] == list2[j-1]:
                    continue  # Skip if the elements before overlap match
                
                # Check if the elements after the overlap in both lists do not match
                if i + 2 < len(list1) and j + 2 < len(list2):
                    if list1[i+2] == list2[j+2]:
                        continue  # Skip if the elements after overlap match
                
                # Combine list1 before the overlap and list2 after the overlap
                merged_list1 = list1[:i+2] + list2[j+2:]
                merged_lists.append(merged_list1)

    return merged_lists

def combine_paths_in_metapath(data, starting_prefix):
    """_summary_

    Args:
        data (list of lists): A list of lists of combined triples.
    """
        # Initialize a list to store combinations of lists
    combined_lists = []
    
    # Iterate over each possible pair of lists in the list_of_lists
    for i, list1 in enumerate(data):
        if list1[0].startswith(starting_prefix):  # Check if list1 starts with starting_prefix
            for j, list2 in enumerate(data):
                if not list2[0].startswith(starting_prefix): 
                    result = merge_lists_on_overlap(list1, list2)
                    if not result in combined_lists:
                        combined_lists.extend(result)
    combined_lists = [list(tup) for tup in set(tuple(lst) for lst in combined_lists)]

    return combined_lists

def expand_neighbors(input_nodes_df,input_dir,triples_list_file,id_keys_df,labels,kg_type):
    """
    Args:
        input_nodes_df (df): Input nodes from original subgraph.

    Returns:
        df: All unique nodes with the relevant node type as target based on the given metapaths.
        example: 
            ERK1,MAPK1
            MAPK1,SNP

            ERK1,PR_
            ERK1,R-HSA
            SNP,PR_
            SNP,R-HSA
    """

    all_nodes = unique_nodes(input_nodes_df[["source","target"]])
    all_nodes_uri = [
    input_nodes_df.loc[input_nodes_df["source"] == node, "source_id"].values[0]
    if not input_nodes_df[input_nodes_df["source"] == node].empty
    else input_nodes_df.loc[input_nodes_df["target"] == node, "target_id"].values[0]
    for node in all_nodes
    ]

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])


    for i in range(len(all_nodes)):
        start_node = all_nodes[i]
        start_node_uri = all_nodes_uri[i]
        # Convert genes to protein
        if "gene" in start_node_uri:
            # Remove row with that gene
            input_nodes_df = input_nodes_df[~input_nodes_df['source_id'].str.contains(start_node_uri)]
            start_node_uri,id_keys_df = convert_genes_to_proteins(conn,"edges",start_node_uri,id_keys_df,labels,kg_type)
            start_node = get_label(labels,start_node_uri,kg_type)
        end_nodes = replace_target_node_type(start_node_uri,input_dir)
        for end_node in end_nodes:
            rows_to_add = []
            # Add a new row with the new relevant end_node_types
            rows_to_add.append(
                {
                    input_nodes_df.columns[0]: start_node,
                    input_nodes_df.columns[1]: end_node,
                    input_nodes_df.columns[2]: start_node,
                    input_nodes_df.columns[3]: end_node,
                    input_nodes_df.columns[4]: start_node_uri,
                    input_nodes_df.columns[5]: end_node
                })
            input_nodes_df = pd.concat([input_nodes_df, pd.DataFrame(rows_to_add)], ignore_index=True)

    # Remove duplicates that may come if multiple metapaths match start_node_uri
    input_nodes_df = input_nodes_df.drop_duplicates()

    return input_nodes_df,id_keys_df
