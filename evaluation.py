
from find_path import get_uri
import pandas as pd
from igraph import * 
import numpy as np
import os

def ranked_comparison(output_dir,**value_dfs):

    df = pd.DataFrame()

    for i in value_dfs.items():
        paths_list = list(i[1]['Value'])
        r = [sorted(paths_list).index(x) for x in paths_list]
        df[i[0]] = r

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/ranked_comparison.csv',sep=',',index=False)
    return df

def path_length_comparison(output_dir,input_nodes_df,labels_all,search_type,**subgraph_dfs):

    df = pd.DataFrame()
    
    for sg in subgraph_dfs.items():
        sg_df = sg[1]
        #Change order of columns for igraph object
        sg_df = sg_df[['S', 'O', 'P']]
        path_lengths = []
        g = Graph.DataFrame(sg_df,directed=True,use_vids=False)
        for i in range(len(input_nodes_df)):
            #node1 = get_uri(labels_all,input_nodes_df.iloc[i].loc['source'])
            node1 = input_nodes_df.iloc[i].loc['source_label']
            node2 = input_nodes_df.iloc[i].loc['target_label']
            p = g.get_all_shortest_paths(v=node1, to=node2, weights=None, mode=search_type)
            path_lengths.append(len(p[0]))
        df[sg[0]] = path_lengths
        
    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/path_length_comparison.csv',sep=',',index=False)
    return df

def num_nodes_comparison(output_dir,**subgraph_dfs):

    df = pd.DataFrame()

    for sg in subgraph_dfs.items():
        sg_df = sg[1]

        n = pd.unique(sg_df[['S', 'O']].values.ravel())
        df[sg[0]] = [len(n)]

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/num_nodes_comparison.csv',sep=',',index=False)
    return df

def get_ontology_lables(noa_df,labels_all):

    ont_types = ['/CHEBI_','/PR_','/PW_','/gene','/MONDO_','/HP_','/VO_','/EFO_','NCBITaxon_','/GO_','/DOID_','/reactome','/SO_']

    ont_labels = []

    num_intermediate_nodes = 0

    #Get all intermediate nodes from subgraph
    for i in range(len(noa_df)):
        ont_found = 'false'
        if noa_df.iloc[i].loc['Attribute'] == 'Extra':
            uri = get_uri(labels_all,noa_df.iloc[i].loc['Node'])
            num_intermediate_nodes += 1
            for j in ont_types:
                if j in uri:
                    ont_labels.append(j)
                    ont_found = 'true'
            if ont_found == 'false':
                print('Ontology not accounted for in list: ',uri)
                raise Exception('Ontology type not accounted for in list: ',uri,', add this ontology type to get_ontology_labels function (evaluation.py).')   
    
    ont_labels, counts = np.unique(ont_labels,return_counts=True)
    ont_labels = ont_labels.tolist()
    counts = counts.tolist()

    return ont_labels, counts, num_intermediate_nodes


def intermediate_nodes_comparison(output_dir,labels_all,**noa_dfs):

    all_ont_labels = []

    df = pd.DataFrame()

    #Get all possible ontology types from all subgraphs given
    onts_used = []
    for nd in noa_dfs.items():
        n_df = nd[1]
        #Get unique ontology types from this subgraph, add to running list for each subgraph, counts not used here
        ont_labels, counts, num_intermediate_nodes = get_ontology_lables(n_df,labels_all)
        all_ont_labels.extend(ont_labels)
        
    #List of all unique ontology types from all subgraphs
    all_ont_labels = np.unique(all_ont_labels)
        
    #Get counts of each ontology type
    for nd in noa_dfs.items():
        n_df = nd[1]
        ont_labels, counts, num_intermediate_nodes = get_ontology_lables(n_df,labels_all)
        #Add any ontology types not already in subgraph
        for i in all_ont_labels:
            if i not in ont_labels:
                ont_labels.append(i)
                counts.append(0)

        #Normalize counts
        counts_norm = [i/num_intermediate_nodes for i in counts]
        df['Ontology_Type'] = ont_labels
        df[nd[0]] = counts_norm
        #Sort ontology types so that counts line up for each
        df.sort_values(by=['Ontology_Type'], ascending=(False),inplace=True)

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/intermediate_nodes_comparison.csv',sep=',',index=False)
    return df

def edge_type_comparison(output_dir,**subgraph_dfs):

    df = pd.DataFrame()

    for sg in subgraph_dfs.items():
        sg_df = sg[1]

        ###Need to account for the fact that ont types will be different for each sg_df (i.e. values)
        ###Need to divide by total # edges to normalize
        values, counts = np.unique(sg_df['P'], return_counts=True)
        counts_norm = [i/len(sg_df['P']) for i in counts]
        df['Edge_Type'] = values
        df[sg[0]] = counts_norm

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/edge_type_comparison.csv',sep=',',index=False)
    return df


#Gets subgraph df for specific algorithm, supporting types are CosineSimilarity and PDP
def get_subgraph_dfs(output_dir,subgraph_algorithm):

    input_nodes_file = output_dir+'/_Input_Nodes_.csv'
    input_nodes = pd.read_csv(input_nodes_file, sep = "|")

    subgraph_file = output_dir+'/'+subgraph_algorithm+'/Subgraph.csv'
    subgraph_df = pd.read_csv(subgraph_file, sep = "|")

    noa_file = output_dir+'/'+subgraph_algorithm+'/Subgraph_attributes.noa'
    noa_df = pd.read_csv(noa_file, sep = "|")

    path_list_file = output_dir+'/Evaluation_Files/paths_list_'+subgraph_algorithm+'.csv'
    path_list = pd.read_csv(path_list_file, sep=",")

    return input_nodes,subgraph_df,noa_df,path_list


def output_path_lists(output_dir,path_list,subgraph_algorithm):

    df = pd.DataFrame()

    df['Value'] = path_list

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/paths_list_'+subgraph_algorithm+'.csv',sep=',',index=False)

 def output_num_paths_pairs(output_dir,num_paths_df,subgraph_algorithm):

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_paths_df.to_csv(output_folder+'/num_paths_'+subgraph_algorithm+'.csv',sep=',',index=False)
