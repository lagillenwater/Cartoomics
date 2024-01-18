
#Outputs the patterns of nodes that describe the shortest path between a specific set of pairs (microbe - metabolite). Skim only lists each node type once, full lists every occurance of a node type in the shortest path found. 

import csv
import pandas as pd
import argparse
import os
import glob
from collections import Counter
from create_graph import create_graph
from collections import defaultdict
import tqdm as tqdm


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--directory",dest="Directory",required=True,help="Directory")
    parser.add_argument("--graph-type",dest="GraphType",required=True,help="GraphType")
    parser.add_argument("--full-or-skim",dest='FullOrSkim',required=False,help="FullOrSkim",default='skim')
    parser.add_argument("--output-patterns",dest='OutputPatterns',required=False,help="OutputPatterns",default=True)

    return parser

###Read in all files
def process_files(csv_file,labels_df,full_or_skim,ont_types,output_patterns):

    pathway_df = pd.read_csv(csv_file,sep='|')

    previous_order = 'none'

    #Only return pattern if it exists
    if len(pathway_df) > 0:

        if full_or_skim == 'skim':

            
            #### To look at content of all paths easily ####
            if not output_patterns:
                pattern = pathway_df.iloc[0].loc['S']  #'P']  for checking edge types

                for i in range(0,len(pathway_df)):
                    if pathway_df.iloc[i].loc['S'] not in pattern:   #'P'] not in pattern:
                        pattern = pattern + " --- " + pathway_df.iloc[i].loc['S']  #'P']
                    if pathway_df.iloc[i].loc['O'] not in pattern:   #'P'] not in pattern:
                        pattern = pattern + " --- " + pathway_df.iloc[i].loc['O']  #'P']

            
            if output_patterns:
                #### To look at patterns of paths ###
                pattern = check_ont_type(pathway_df.iloc[0].loc['S'],ont_types,labels_df)  

                for i in range(0,len(pathway_df)):
                    if check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df) not in pattern:   
                        pattern = pattern + " --- " + check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df) 
                    if check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df) not in pattern:   
                        pattern = pattern + " --- " + check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df) 

                #alphabetize order of patterns so that there are no duplicates, only interested in the content not the order
                i_list = sorted(pattern.split(' --- '))
                pattern = i_list[0]
                for i in range(1,len(i_list)):
                    pattern = pattern + " --- " + i_list[i]
        

        elif full_or_skim == 'full':

            all_triples = []
            current_pattern = []
            for i in reversed(range(len(pathway_df))):
                #For first triple, only use previous order
                if i == 0:
                    #Only use previous flip if the path is longer than 1 triple
                    if len(pathway_df) > 1:
                        if previous_flip:
                            first_triple = [pathway_df.iloc[0].loc['P'],check_ont_type(pathway_df.iloc[0].loc['O'],ont_types,labels_df)]
                            pattern = current_pattern + first_triple
                            pattern.reverse()
                        else:
                            first_triple = [check_ont_type(pathway_df.iloc[0].loc['S'],ont_types,labels_df),pathway_df.iloc[0].loc['P']]
                            pattern = first_triple + current_pattern
                    if len(pathway_df) == 1:
                        pattern = [check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df),pathway_df.iloc[i].loc['P'],check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df)]
                if i != 0:
                    current_order,current_flip = check_triple_order(pathway_df,i)
                    #Add to front means add to the back of the current_front_pattern since we are counting down
                    #For last triple/first to be looked at
                    if previous_order == 'none':
                        p = [check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df),pathway_df.iloc[i].loc['P'],check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df)]
                        current_pattern = current_pattern + p
                        if current_flip:
                            current_pattern.reverse()
                    #Take P, O when previous triple is added to front
                    if previous_order == 'front':
                        p = [pathway_df.iloc[i].loc['P'],check_ont_type(pathway_df.iloc[i].loc['O'],ont_types,labels_df)]
                        current_pattern = current_pattern + p
                        if current_flip:
                            current_pattern.reverse()
                    #Take S, P when previous triple is added to back
                    if previous_order == 'back':
                        p = [check_ont_type(pathway_df.iloc[i].loc['S'],ont_types,labels_df),pathway_df.iloc[i].loc['P']]
                        current_pattern = p + current_pattern 
                        if current_flip:
                            current_pattern.reverse()

                    previous_order = current_order
                    previous_flip = current_flip

            pattern = ' --- '.join(pattern)
            
    else:
        pattern = 'none'
        
    name = csv_file.split('.csv')[0]

    return pattern,name


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

def check_ont_type(node,ont_types,labels_df):

    b = 0
    label = labels_df.loc[labels_df['label'] == node,'entity_uri'].values[0]
    for i in list(ont_types.keys()):
        if i in label:
            b = 1
            return ont_types[i]
    if b == 0:
        print('node: ',node,' label: ',label)

def check_ont_type_from_uri(node,ont_types):

    b = 0
    for i in list(ont_types.keys()):
        if i in node:
            b = 1
            return ont_types[i]
    if b == 0:
        print(' node: ',node)

def get_path_length(csv_file):

    pathway_df = pd.read_csv(csv_file,sep='|')

    path_length = len(pathway_df)

    return path_length

def get_ont_types(graph_type):

    if graph_type == 'kg-covid19':
        ont_types = {'CHEBI:':'CHEBI','PR:':'PRO','MONDO:':'MONDO','/hgnc/':'hgnc','CL:':'CLO','CARO:':'CARO','BSPO:':'BSPO','NCBITaxon:':'NCBITaxon/ContextualMicrobe','BTO:':'BTO','GO:':'GO','CHR:':'CHR','FBbt:':'FBbt','FMA:':'FMA','HP:':'HPO','MA:':'MA','MP:':'MPO','OBA:':'OBA','PATO:':'PATO','PLANA:':'PLANA','UBERON:':'UBERON','UPHENO:':'UPHENO','WBbt:':'WBbt','ZP:':'ZP','ENSEMBL:':'ENSEMBL','CHEMBL.':'CHEMBL','NBO:':'MONDO','ENVO:':'ENVO','ECOCORE:':'ECOCORE','MFOMD:':'MONDO','BFO:':'BFO'}
    
    if graph_type == 'pkl':
        ont_types = {'pkt/':'NCBITaxon/ContextualMicrobe','/CHEBI_':'CHEBI','/PR_':'PRO','/PW_':'REACTOME_PW','/gene':'gene','/MONDO_':'MONDO','/HP_':'HPO','/VO_':'VO','/EFO_':'EFO','FAKEURI_':'other chemical','NCBITaxon_':'NCBITaxon/ContextualMicrobe','/GO_':'GO','/DOID_':'MONDO','NBO_':'MONDO','SO_':'SO','CHR_':'CHR','R-HSA-':'REACTOME_PW','UBERON_':'UBERON','MPATH_':'MPATH','PATO_':'PATO','/snp/':'snp', 'NCIT_':'NCIT','CARO_':'CARO','ECTO_':'ECTO'}
    
    return ont_types


def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    
    directory = args.Directory
    graph_type = args.GraphType
    full_or_skim = args.FullOrSkim
    output_patterns = args.OutputPatterns

    #For multiple folders within directory
    all_folders = []
    os.chdir(directory)
    for folder in os.listdir():
        if 'pkl_shortest_path' in folder:
            all_folders.append(folder)

    #For testing
    #all_folders = [all_folders[0]]
    ##
    for fold in all_folders:
        csv_files = []
        fold_directory = directory + '/' + fold 
        csv_files += glob.glob(os.path.join(fold_directory, "*Subgraph*.csv"))

        #To create 1 file for all patterns, don't indent here
        print('total subgraph files for ',fold, ': ',len(csv_files))

        patterns_all = []
        names_all = []
        path_lengths = defaultdict(list)
        
        if os.path.exists(fold_directory+'/Pattern_Counts_Full.csv'): continue
        for f in tqdm.tqdm(csv_files):

            pattern,name = process_files(f,g.labels_all,full_or_skim,ont_types,output_patterns)
            path_length = get_path_length(f)
            if pattern != 'none':
                patterns_all.append(pattern)
                path_lengths[pattern].append(path_length)
                names_all.append(name)

        #Get count of each pattern
        patterns_count = dict(Counter(patterns_all))

        #Create df of Pattern/Name/count
        patterns_all_df = pd.DataFrame({'Pattern':patterns_all})
        patterns_all_df['Name'] = names_all
        counts = []
        for i in range(len(patterns_all_df)):
            counts.append(patterns_count[patterns_all_df.iloc[i].loc['Pattern']])

        path_lengths_str = []
        patterns_all_df['Count'] = counts
        for i in range(len(patterns_all_df)):
            p = patterns_all_df.iloc[i].loc['Pattern']
            p_str = ','.join(map(str,path_lengths[p]))
            path_lengths_str.append(p_str)
        patterns_all_df['Path_Length'] = path_lengths_str
        patterns_all_df = patterns_all_df.sort_values(by=['Pattern','Count'])

        #Generate df of only the patterns/no filename to get unique patterns
        patterns_all_unique = patterns_all_df.Pattern.drop_duplicates()

        if full_or_skim == 'skim':
            patterns_all_df.to_csv(fold_directory+'/Patterns_Counts_Skim.csv',sep=',',index=False)  #Patterns_ #PathLabel_ if outputting the actual paths, not the patterns
            patterns_all_unique.to_csv(fold_directory+'/Patterns_Counts_Skim_Unique.csv',sep=',',index=False) #Patterns_ #PathLabel_ if outputting the actual paths, not the patterns
            print(fold_directory+'/Patterns_Counts_Skim.csv')
        elif full_or_skim == 'full':
            patterns_all_df.to_csv(fold_directory+'/Pattern_Counts_Full.csv',sep=',',index=False)
            patterns_all_unique.to_csv(fold_directory+'/Pattern_Counts_Full_Unique.csv',sep=',',index=False)

if __name__ == '__main__':
    main()