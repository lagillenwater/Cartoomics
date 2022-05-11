

#Input a table of source and target nodes with their correspoding labels in PKL and generate the full pathway of triples. The Input nodes file format is: Source (PKL Node Label), Target (PKL Node Label), "|" delimited. Output will be 1 csv file of triples, 1 noa file of node attributes (Mechanism, Extra), and a Results file including the Path Length and result (exists, nonexistant) for each source/target pair. Input weighted edges as a string in the for of a list of edges, i.e. '[relationship_1, relationship_2]'

#python Mechanism_Predictions_FullPathway.py --triples-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt --triples-integers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt --pkl-labels-file /Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt --gutmgene-labels-file /Users/brooksantangelo/Documents/Rotation2/Rocky/PKL_Additions/GutMGene/LabelTypes_gutMGene_URI_LABEL_MAP_contextual_manualRelationLabels.csv --pkl-identifiers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json --input-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv --output-dir /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant

#python Mechanism_Predictions_FullPathway.py --triples-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt --triples-integers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt --pkl-labels-file /Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt --gutmgene-labels-file /Users/brooksantangelo/Documents/Rotation2/Rocky/PKL_Additions/GutMGene/LabelTypes_gutMGene_URI_LABEL_MAP_contextual_manualRelationLabels.csv --pkl-identifiers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json --input-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/UpdatedPathway/Kynurenine_Pathway_Input_Nodes_Updated.csv --output-dir /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/UpdatedPathway/KynurenineUnweightedResult --mechanism-name Kynurenine_Pathway --original-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/kynurenine_pathway_original_pklv3.csv

import pandas as pd
import csv
import copy
import json
from igraph import *
from tqdm import tqdm
import os
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import numpy as np
from scipy import spatial
from scipy.spatial import distance
import copy

import argparse


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--triples-file",dest="TriplesFile",required=True,help="TriplesFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'

    parser.add_argument("--triples-integers-file",dest="TriplesIntegersFile",required=True,help="TriplesIntegersFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt'

    parser.add_argument("--pkl-microbiome-labels-file",dest="PklMicrobiomeLabelsFile",required=True,help="PklMicrobiomeLabelsFile")
    #"/Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt"

    #parser.add_argument("--gutmgene-labels-file",dest="GutMGeneLabelsFile",required=True,help="GutMGeneLabelsFile")
    #'/Users/brooksantangelo/Documents/Rotation2/Rocky/PKL_Additions/GutMGene/LabelTypes_gutMGene_URI_LABEL_MAP_contextual_manualRelationLabels.csv'

    parser.add_argument("--pkl-identifiers-file",dest="PklIdentifiersFile",required=True,help="PklIdentifiersFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json'

    parser.add_argument("--input-nodes-file",dest="InputNodesFile",required=True,help="InputNodesFile")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv

    parser.add_argument("--original-nodes-file",dest="OriginalNodesFile",required=False,help="OriginalNodesFile")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv

    parser.add_argument("--weight-important-edges",dest="WeightImportantEdges",required=False,help="WeightImportantEdges")
    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant
    parser.add_argument("--mechanism-name",dest="MechanismName",required=True,help="MechanismName")

    parser.add_argument("--search-type",dest="SearchType",required=False,default='OUT',help="SearchType")

    parser.add_argument("--embeddings-file",dest="EmbeddingsFile",required=False,help="EmbeddingsFile")

    #Will be "cosine similarity" or "pdp"
    parser.add_argument("--semantic-action",dest="SemanticAction",required=True,help="SemanticAction")

    #True or false, determines whether semantic action of transforming paths into shorter metapaths will be used
    parser.add_argument("--include-metapaths",dest="IncludeMetapaths",required=False,default='false',help="IncludeMetapaths")

    return parser


###Read in all files
def process_files(triples_file,pkl_microbiome_labels_file,pkl_identifiers_file,triples_integers_file,input_nodes_file):

    #Read in triples file to list
    with open(triples_file, 'r') as f_in:
        #Length matches original file length
        triples = set(tuple(x.split('\t')) for x in f_in.read().splitlines())
        f_in.close()

    triples_list = list(triples)

    triples_list = [ x for x in triples_list if "subject" not in x ]
    triples_list = [ x for x in triples_list if "Subject" not in x ]

    labels_all = {}

    with open(pkl_microbiome_labels_file) as f_in:
        for line in f_in:
            vals = line.strip().split("\t")
            try:
                #key, value = vals[2:4]
                key, value = vals[0:2]
                labels_all[key] = value
            except: pass

    #Read in identifiers file to dictionary
    f = open(pkl_identifiers_file)
    identifiers = json.load(f)

    #Read in node2vec input triples integers file as df
    edgelist_int = pd.read_csv(triples_integers_file, sep=" ")

    #Read in input nodes file as df
    input_nodes = pd.read_csv(input_nodes_file, sep=',')  #'|')

    return triples_list,labels_all,identifiers,edgelist_int,input_nodes

def generate_graph(triples_integers_file):

    #Read in edge list to igraph
    g = Graph.Read_Ncol(triples_integers_file, directed=True)
    g_nodes = g.vs()['name']  

    return g,g_nodes 

def get_url(labels,value):

    for key, val in labels.items(): 
        if val == value:
            return key

def get_key(dictionary,value):
    for key, val in dictionary.items():
        if val == value:
            return key


def weight_edges(g,triples_list,labels,weight_important_edges):

    #important_edges = ['participates in','molecularly interacts with','has gene product','has function']

    g_weights_list = []

    for i in range(len(triples_list)):
        if labels[triples_list[i][1]] in weight_important_edges:
            g_weights_list.append(1)
        else:
            g_weights_list.append(99)

    g.es["weight"] = g_weights_list

    return g

def find_all_shortest_path(start_node,end_node,graph,g_nodes,identifiers,labels_all,triples_list,weights,search_type):

    node1 = str(identifiers[get_url(labels_all,start_node)])
    node2 = str(identifiers[get_url(labels_all,end_node)])
    
    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    return path_nodes

def find_all_simple_paths(start_node,end_node,graph,g_nodes,identifiers,labels_all,triples_list,search_type):

    node1 = str(identifiers[get_url(labels_all,start_node)])
    node2 = str(identifiers[get_url(labels_all,end_node)])

    #list of nodes
    path_nodes = graph.get_all_simple_paths(v=node1, to=node2, cutoff = 3, mode=search_type)

    return path_nodes

def get_embedding(emb,node):

    embedding_array = emb[str(node)]
    embedding_array = np.array(embedding_array)
    
    return embedding_array

def calc_cosine_sim(path_nodes,target_emb,emb):

    #Dict of all embeddings to reuse if they exist
    embeddings = defaultdict(list)

    #List of total cosine similarity for each path in path_nodes, should be same length as path_nodes
    total_cs = []

    for l in path_nodes:
        cs = 0
        for i in range(0,len(l)-1):
            if l[i] not in list(embeddings.keys()):
                e = get_embedding(emb,l[i])
                embeddings[l[i]] = e
            else:
                e = embeddings[l[i]]
            cs += 1 - spatial.distance.cosine(e,target_emb)
        total_cs.append(cs)

    return total_cs

def calc_pdp(path_nodes,graph,w):

    #List of pdp for each path in path_nodes, should be same length as path_nodes
    all_pdp = []

    for l in path_nodes:
        pdp = 1
        for i in range(0,len(l)-1):
            dp = graph.degree(l[i],mode='all',loops=True)
            dp_damped = pow(dp,-w)
            pdp = pdp*dp_damped

        all_pdp.append(pdp)

    return all_pdp


def select_path(value_list,path_nodes,g_nodes,identifiers,labels_all,triples_list,full_mechanism_list):

    #Get max cs from total_cs_path, use that idx of path_nodes then create mechanism
    max_index = value_list.index(max(value_list))
    chosen_path_nodes = path_nodes[max_index]

    full_mechanism_list = get_mechanism_df(g_nodes,identifiers,labels_all,triples_list,chosen_path_nodes,full_mechanism_list)

    return full_mechanism_list

def get_mechanism_df(g_nodes,identifiers,labels_all,triples_list,chosen_path_nodes,paths):

    n1 = labels_all[get_key(identifiers,int(g_nodes[chosen_path_nodes[0]]))]
    for i in range(1,len(chosen_path_nodes)):
        idx = chosen_path_nodes[i]
        n2 = labels_all[get_key(identifiers,int(g_nodes[idx]))]
        for i in range(len(triples_list)):
            l = []
            if n1 == labels_all[triples_list[i][0]] and n2 == labels_all[triples_list[i][2]]:
                l.append(labels_all[triples_list[i][0]])
                l.append(labels_all[triples_list[i][1]])
                l.append(labels_all[triples_list[i][2]])
                paths.append(l)
            elif n1 == labels_all[triples_list[i][2]] and n2 == labels_all[triples_list[i][0]]:
                l.append(labels_all[triples_list[i][0]])
                l.append(labels_all[triples_list[i][1]])
                l.append(labels_all[triples_list[i][2]])
                paths.append(l)
        n1 = n2

    return paths

def create_node_attributes(list_of_pairs,full_mechanism_df):
    
    all_nodes = [j for i in list_of_pairs for j in i]

    full_mechanism_attribute_list = []
        
    for i in range(len(full_mechanism_df)):
        #Only add subject and object columns, not the predicate
        for col in [0,2]:
            node = full_mechanism_df.iloc[i,col]
            if node in all_nodes:
                att = 'Mechanism'
            else:
                att = 'Extra'
            l = [node,att]
            full_mechanism_attribute_list.append(l)

    full_mechanism_attribute_df = pd.DataFrame(full_mechanism_attribute_list,columns = ['Node','Attribute'])
    full_mechanism_attribute_df = full_mechanism_attribute_df.drop_duplicates(subset=['Node'])
    full_mechanism_attribute_df = full_mechanism_attribute_df.reset_index(drop=True)
    
    return full_mechanism_attribute_df

def del_list_inplace(l, idx_to_del):

    for i in sorted(idx_to_del, reverse=True):
        del(l[i])

    return l

def subset_by_metapaths(full_mechanism_list,nodes):

    new_list = copy.deepcopy(full_mechanism_list)

    triples_to_add = []
    triples_to_remove = []

    #drug interaction: A <-- interacts with --> B -- is a substance that treats --> C
    for i in range(len(full_mechanism_list)):
        
        current_triple = full_mechanism_list[i]
        
        #Don't affect edges that connect 2 input nodes
        if current_triple[0] in nodes and current_triple[2] in nodes:
            continue

        for j in range(len(full_mechanism_list)):
            #Check all other triples except this one
            if full_mechanism_list[j] != full_mechanism_list[i]:

                if current_triple[1] == "interacts with" and full_mechanism_list[j][1] == "is substance that treats":
                    # A -- interacts with --> B -- is a substance that treats --> C
                    if current_triple[2] == full_mechanism_list[j][0]:
                        new_triple = [current_triple[0],'METAPATH drug interaction',full_mechanism_list[j][2]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
                        #new_list = del_list_inplace(new_list,[i,j])
                        #new_list.insert(i,new_triple)
                        
                    # B -- interacts with --> A -- is a substance that treats --> C
                    if current_triple[0] == full_mechanism_list[j][0]:
                        new_triple = [full_mechanism_list[i][2],'METAPATH drug interaction',full_mechanism_list[i+1][2]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
                        #new_list = del_list_inplace(new_list,[i,j])
                        #new_list.insert(i,new_triple)

    triples_to_remove = list(set(triples_to_remove))

    #print('full_mechanism_list start: ',len(full_mechanism_list))
    #Remove necessary triples
    full_mechanism_list = del_list_inplace(full_mechanism_list,triples_to_remove)

    #Add new triples
    for i in triples_to_add:
        full_mechanism_list.append(i)

    #print('full_mechanism_list part 1: ',len(full_mechanism_list))

    triples_to_add = []
    triples_to_remove = []

    #subclass of: A -- … --> B <-- subClassOf (x n) --> C
    for i in range(len(full_mechanism_list)):
            
        current_triple = full_mechanism_list[i]

        #Don't affect edges that connect 2 input nodes
        if current_triple[0] in nodes and current_triple[2] in nodes:
            continue

        for j in range(len(full_mechanism_list)):
            #Check all other triples except this one
            #print(i,j,len(full_mechanism_list),len(new_list))
            if full_mechanism_list[j] != full_mechanism_list[i]:

                # A -- ... --> B -- subClassOf --> C
                if full_mechanism_list[j][1] == "subClassOf":
                    if 'METAPATH' not in current_triple[1]:
                        rel = 'METAPATH '+ current_triple[1]
                    else:
                        rel = current_triple[1]
                    if current_triple[2] == full_mechanism_list[j][0]:
                        new_triple = [current_triple[0],rel,full_mechanism_list[j][2]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
                    # A -- ... --> B <-- subClassOf -- C
                    elif current_triple[2] == full_mechanism_list[j][2]:
                        new_triple = [current_triple[0],rel,full_mechanism_list[j][0]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
                    
    triples_to_remove = list(set(triples_to_remove))

    #print('full_mechanism_list start2: ',len(full_mechanism_list))
    #Remove necessary triples
    full_mechanism_list = del_list_inplace(full_mechanism_list,triples_to_remove)

    #Add new triples
    for i in triples_to_add:
        full_mechanism_list.append(i)

    #print('full_mechanism_list part 2: ',len(full_mechanism_list))

    triples_to_add = []
    triples_to_remove = []

    participates_patterns = ['molecularly interacts with','interacts with','has component']

    #A <-- molecularly interacts with --> B -- participates_in --> C
    for i in range(len(full_mechanism_list)):
            
        current_triple = full_mechanism_list[i]
        #Don't affect edges that connect 2 input nodes
        if current_triple[0] in nodes and current_triple[2] in nodes:
            continue

        for j in range(len(full_mechanism_list)):
            #Check all other triples except this one
            #print(i,j,len(full_mechanism_list),len(new_list))
            if full_mechanism_list[j] != full_mechanism_list[i]:

                if current_triple[1] in participates_patterns and full_mechanism_list[j][1] == "participates_in":
                    # A -- interacts with --> B -- is a substance that treats --> C
                    if current_triple[2] == full_mechanism_list[j][0]:
                        new_triple = [current_triple[0],'METAPATH participates_in',full_mechanism_list[j][2]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
                        #new_list = del_list_inplace(new_list,[i,j])
                        #new_list.insert(i,new_triple)
                        
                    # B -- interacts with --> A -- is a substance that treats --> C
                    if current_triple[0] == full_mechanism_list[j][0]:
                        new_triple = [full_mechanism_list[i][2],'METAPATH participates_in',full_mechanism_list[i+1][2]]
                        triples_to_add.append(new_triple)
                        triples_to_remove.append(i)
                        triples_to_remove.append(j)
    

    triples_to_remove = list(set(triples_to_remove))

    #print('full_mechanism_list start3: ',len(full_mechanism_list))
    #Remove necessary triples
    full_mechanism_list = del_list_inplace(full_mechanism_list,triples_to_remove)

    #Add new triples
    for i in triples_to_add:
        full_mechanism_list.append(i)

    #print('full_mechanism_list part 3: ',len(full_mechanism_list))

    return full_mechanism_list

def create_csv_file(df,output_dir,mechanism_name,delimiter_used):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_csv(output_dir+"/"+mechanism_name+'.csv',sep=delimiter_used,index=False)

def create_noa_file(df,output_dir,mechanism_name):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    l = df.values.tolist()

    with open(output_dir+"/"+mechanism_name+'_attributes.noa', "w", newline="") as f:
        writer = csv.writer(f,delimiter='|')
        writer.writerow(["Node","Attribute"])
        writer.writerows(l)

def show_original_nodes(full_mechanism_attribute_df,orig_nodes):

    orig_nodes_list =  orig_nodes.values.tolist()

    full_mechanism_attribute_df_new = copy.deepcopy(full_mechanism_attribute_df)

    for i in range(len(full_mechanism_attribute_df_new)):
        if full_mechanism_attribute_df_new.iloc[i].loc['Node'] in orig_nodes_list:
            full_mechanism_attribute_df_new.iloc[i].loc['Attribute'] = 'Mechanism'
        else:
            full_mechanism_attribute_df_new.iloc[i].loc['Attribute'] = 'Extra'

    return full_mechanism_attribute_df_new

def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    

    triples_file = args.TriplesFile
    pkl_microbiome_labels_file = args.PklMicrobiomeLabelsFile
    #gutmgene_labels_file = args.GutMGeneLabelsFile
    pkl_identifiers_file = args.PklIdentifiersFile
    triples_integers_file = args.TriplesIntegersFile
    input_nodes_file = args.InputNodesFile
    original_nodes_file = args.OriginalNodesFile
    weight_important_edges = args.WeightImportantEdges
    mechanism_name = args.MechanismName
    output_dir = args.OutputDir
    search_type = args.SearchType
    embeddings_file = args.EmbeddingsFile
    semantic_action = args.SemanticAction
    include_metapaths = args.IncludeMetapaths

    #Establish if edge weights are desired
    if weight_important_edges:
        weights = True
    else:
        weights = False

    triples_list, labels_all, identifiers, edgelist_int, input_nodes = process_files(triples_file,pkl_microbiome_labels_file,pkl_identifiers_file,triples_integers_file,input_nodes_file)

    g, g_nodes = generate_graph(triples_integers_file)

    if weights:
        g = weight_edges(g,triples_list,labels_all,weight_important_edges)

    list_of_pairs = input_nodes.values.tolist()

    #Log of what mechanisms were generated
    mechanisms_generated = pd.DataFrame(columns = ['Source','Target','Path_Length','Result'])
    results_list = []

    #Full mechanism will be all sub networks between list of pairs
    full_mechanism_df = pd.DataFrame(columns = ['S','P','O'])

    path_length = 0

    #A list of triples for the mechanism, will become a df
    full_mechanism_list = []

    #list_of_pairs is a list of lists
    for i in tqdm(list_of_pairs):
        print(i)

        #Specific case for a triple that is not useful:
        if i[0] == 'myeloid differentiation primary response protein MyD88 (human)' and i[1] == 'NF-kappaB p50/p65 complex (human)':
            path_nodes = find_all_simple_paths(i[0],i[1],g,g_nodes,identifiers,labels_all,triples_list,search_type)
        else:
            path_nodes = find_all_shortest_path(i[0],i[1],g,g_nodes,identifiers,labels_all,triples_list,weights,search_type)

        #Select mechanism based on highest total cosine similarity to the target node
        if semantic_action == 'cosine_similarity':

            emb = KeyedVectors.load_word2vec_format(embeddings_file, binary=False)

            target_emb = get_embedding(emb,path_nodes[0][len(path_nodes[0])-1])

            #List of each cosine similarity score for all mechanisms
            total_cs_path = calc_cosine_sim(path_nodes,target_emb,emb)

            #Get max cs from total_cs_path, use that idx of path_nodes then create mechanism
            full_mechanism_list = select_path(total_cs_path,path_nodes,g_nodes,identifiers,labels_all,triples_list,full_mechanism_list)

        #Select mechanism based on highest path-degree product for the given mechanisms
        if semantic_action == 'pdp':

            w = 0.4
            #List of pdp for all mechanisms
            pdp_path = calc_pdp(path_nodes,g,w)

            #Get max pdp from pdp+path, use that idx of path_nodes then create mechanism
            full_mechanism_list = select_path(pdp_path,path_nodes,g_nodes,identifiers,labels_all,triples_list,full_mechanism_list)

        '''
        results_list.append(result)

        #Log results
        d = {}
        d['Source'] = i[0]
        d['Target'] = i[1]
        d['Path_Length'] = len(full_mechanism_df) - path_length_start
        d['Result'] = result
        mechanisms_generated = mechanisms_generated.append(d,ignore_index=True)
        '''

    if include_metapaths == 'true':

        nodes = pd.unique(input_nodes[["Source", "Target"]].values.ravel())

        full_mechanism_list = subset_by_metapaths(full_mechanism_list,nodes)

    #Generate df
    full_mechanism_df = pd.DataFrame(full_mechanism_list,columns = ['S','P','O'])
    full_mechanism_df = full_mechanism_df.drop_duplicates(subset=['S','P','O'])
    full_mechanism_df = full_mechanism_df.reset_index(drop=True)
    create_csv_file(full_mechanism_df,output_dir,mechanism_name,'|')

    #Create attribute file 
    full_mechanism_attribute_df = create_node_attributes(list_of_pairs,full_mechanism_df)

    if original_nodes_file:
        #Read in original nodes file as df
        orig_nodes = pd.read_csv(original_nodes_file, sep='|')
        full_mechanism_attribute_df_orig = show_original_nodes(full_mechanism_attribute_df,orig_nodes)
        create_noa_file(full_mechanism_attribute_df_orig,output_dir,mechanism_name+'_orig')
    else:
        create_noa_file(full_mechanism_attribute_df,output_dir,mechanism_name)
    '''
    create_csv_file(mechanisms_generated,output_dir,mechanism_name+'_Input_Nodes_Result',',')
    '''
if __name__ == '__main__':
    main()