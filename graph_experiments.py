

from inputs import *
from create_graph import create_graph,create_igraph_graph,create_graph
from create_subgraph import subgraph_shortest_path_pattern
from visualize_subgraph import output_visualization
from evaluation import *
from graph import KnowledgeGraph
from tqdm import tqdm
#from Find_Common_Paths_diffKGs import *
from constants import (
    PKL_SUBSTRINGS,
    KGCOVID19_SUBSTRINGS
)

def check_for_existance(source_node,target_node,output_dir):

    filename = output_dir+"/"+source_node+"_"+target_node+"_Subgraph.csv"

    #Check for existence of output directory
    if not os.path.exists(filename):
        exists = 'false'
    else:
        exists = 'true'

    #print(exists)
    return exists


def get_nodes_from_input(input_df,s):

    
    #Commented out work for pkl and uniprot, use if need to convert labels??

    #Add only first row if length is 1
    if len(input_df) == 1:
        df = pd.DataFrame()
        df['source_label'] = [s.loc[s['source'] == input_df.iloc[0].loc['source'],'source_label'].values[0]]
        df['target_label'] = [s.loc[s['target'] == input_df.iloc[0].loc['target'],'target_label'].values[0]]
        input_df = pd.concat([input_df,df],axis=1)

    #Add other rows if there is more than 1
    elif len(input_df) > 1:
        df = pd.DataFrame()
        s1 = [s.loc[s['source'] == input_df.iloc[0].loc['source'],'source_label'].values[0]]
        t1 = [s.loc[s['target'] == input_df.iloc[0].loc['target'],'target_label'].values[0]]
        s2 = [s.loc[s['source'] == input_df.iloc[1].loc['source'],'source_label'].values[0]]
        t2 = [s.loc[s['target'] == input_df.iloc[1].loc['target'],'target_label'].values[0]]
        df['source_label'] = s1 + s2
        df['target_label'] = t1 + t2
        input_df = pd.concat([input_df,df],axis=1)
    
    return input_df


#input_df is the selected nodes we want to search, s is the original mapped file with all source/target/source_label
def one_path_search_patterns(input_df,graph,search_type,kg_type,manually_chosen_uris):
    
    #print("Finding subgraph using user input and 1 shortest path......")

    subgraph_df,manually_chosen_uris = subgraph_shortest_path_pattern(input_df,graph,False,search_type,kg_type,manually_chosen_uris)

    if len(subgraph_df) > 0:
        #Check pattern
        pattern = process_dfs(kg_type,subgraph_df,graph.labels_all)


    return manually_chosen_uris,pattern

###Start with df, assuming full pattern is wanted every time
def process_dfs(graph_type,pathway_df,labels_df):

    ont_types = get_ont_types(graph_type)

    previous_order = 'none'

    #Only return pattern if it exists
    if len(pathway_df) > 0:

        all_triples = []
        current_pattern = []
        for i in reversed(range(len(pathway_df))):
            pred = labels_df.loc[labels_df['entity_uri'] == pathway_df.iloc[i].loc['P'],'label'].values[0]
            #For first triple, only use previous order
            if i == 0:
                #Only use previous flip if the path is longer than 1 triple
                if len(pathway_df) > 1:
                    if previous_flip:
                        first_triple = [pred,check_ont_type_from_uri(pathway_df.iloc[0].loc['O'],ont_types)]
                        pattern = current_pattern + first_triple
                        pattern.reverse()
                    else:
                        first_triple = [check_ont_type_from_uri(pathway_df.iloc[0].loc['S'],ont_types),pred]
                        pattern = first_triple + current_pattern
                if len(pathway_df) == 1:
                    pattern = [check_ont_type_from_uri(pathway_df.iloc[i].loc['S'],ont_types),pred,check_ont_type_from_uri(pathway_df.iloc[i].loc['O'],ont_types)]
            if i != 0:
                current_order,current_flip = check_triple_order(pathway_df,i)
                #Add to front means add to the back of the current_front_pattern since we are counting down
                #For last triple/first to be looked at
                if previous_order == 'none':
                    p = [check_ont_type_from_uri(pathway_df.iloc[i].loc['S'],ont_types),pred,check_ont_type_from_uri(pathway_df.iloc[i].loc['O'],ont_types)]
                    current_pattern = current_pattern + p
                    if current_flip:
                        current_pattern.reverse()
                #Take P, O when previous triple is added to front
                if previous_order == 'front':
                    p = [pred,check_ont_type_from_uri(pathway_df.iloc[i].loc['O'],ont_types)]
                    current_pattern = current_pattern + p
                    if current_flip:
                        current_pattern.reverse()
                #Take S, P when previous triple is added to back
                if previous_order == 'back':
                    p = [check_ont_type_from_uri(pathway_df.iloc[i].loc['S'],ont_types),pred]
                    current_pattern = p + current_pattern 
                    if current_flip:
                        current_pattern.reverse()

                previous_order = current_order
                previous_flip = current_flip
            
        pattern = ' --- '.join(pattern)
            
    else:
        pattern = 'none'

    return pattern

def check_ont_type_from_uri(node,ont_types):

    b = 0
    for i in list(ont_types.values()):
        if i in node:
            b = 1
            ont_label = [k for k, v in ont_types.items() if v == i][0]
            return ont_label
    if b == 0:
        print(' node: ',node)

def get_ont_types(graph_type):

    if graph_type == 'kg-covid19':
        ont_types = KGCOVID19_SUBSTRINGS
    if graph_type == 'pkl':
        ont_types = PKL_SUBSTRINGS
    
    return ont_types


def check_triple_order(pathway_df,i):

    #S1 = O2, S1 = S2
    if (pathway_df.iloc[i].loc['O'] == pathway_df.iloc[i-1].loc['S']) or (pathway_df.iloc[i].loc['S'] == pathway_df.iloc[i-1].loc['S']):
        order = 'front'
    #O1 = O2, O1 = S2
    if (pathway_df.iloc[i].loc['O'] == pathway_df.iloc[i-1].loc['O']) or (pathway_df.iloc[i].loc['S'] == pathway_df.iloc[i-1].loc['O']):
        order = 'back'
    #S1 = S2, O1 = O2
    if (pathway_df.iloc[i].loc['S'] == pathway_df.iloc[i-1].loc['S']) or (pathway_df.iloc[i].loc['O'] == pathway_df.iloc[i-1].loc['O']):
        flip = True
    #S1 = O2, O1 = S2
    if (pathway_df.iloc[i].loc['O'] == pathway_df.iloc[i-1].loc['S']) or (pathway_df.iloc[i].loc['S'] == pathway_df.iloc[i-1].loc['O']):
        flip = False

    return order,flip