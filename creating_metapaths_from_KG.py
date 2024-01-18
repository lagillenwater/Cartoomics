from inputs import *
from create_graph import create_graph
from create_subgraph import automatic_defined_edge_exclusion
from graph_experiments import *
import ast
from collections import defaultdict
import tqdm as tqdm
import random
import logging.config
from pythonjsonlogger import jsonlogger
import sys

from collections import Counter
from constants import (
    PKL_SUBSTRINGS
)

def main():

    #Only works for PKL
    input_dir,output_dir,kg_types,num_iterations,batch_size,node_input1,node_input2,embedding_dimensions,weights,search_type,pdp_weight = generate_arguments_metapaths()

    kg_types = ast.literal_eval(kg_types)

    metapath_dir = '/MetapathEvaluation/'
    metapath_outdir = output_dir + metapath_dir
    if not os.path.isdir(metapath_outdir):
        os.makedirs(metapath_outdir)

    for kg_type in kg_types:
        triples_list_file,labels_file = get_graph_files_metapaths(input_dir,output_dir, kg_type)

        print("Creating knowledge graph object from inputs.....")

        path_nums_dict = {}
        print('Graph: ',kg_type)

        g = create_graph(triples_list_file,labels_file, kg_type)
        if weights == True:
            g = automatic_defined_edge_exclusion(g,kg_type)

        manually_chosen_uris = {}

        all_iterations_patterns = defaultdict()

        #Determines number of iterations
        for c in tqdm.tqdm(range(0,int(num_iterations))):  #300)):

            #Check for existence of output directory
            if os.path.exists(output_dir+ metapath_dir + str(c) + '_Pattern_Counts_Full.csv'):
                logging.error('File exists: ' + output_dir + metapath_dir + str(c) + '_Pattern_Counts_Full.csv' + ', continuing to next iteration.')
                continue

            patterns_all = []

            #Find all microbe to disease pairs
            if kg_type != 'pkl':
                print('Unsupported graph type: ' + kg_type + ', only "pkl" is supported.')
                logging.error('Unsupported graph type: ' + kg_type + ', only "pkl" is supported.')
                sys.exit(1)

            if kg_type == 'pkl':

                #Define the node types to search between
                node_substring1 = PKL_SUBSTRINGS[node_input1]
                node_substring2 = PKL_SUBSTRINGS[node_input2]

                node_type1 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring1)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                random.seed(4)
                node_type1 = random.choices(node_type1, k=3)  #20)
                node_type2 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring2)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                node_type2 = random.choices(node_type2, k=3)  #20)

            for m in tqdm.tqdm(range(len(node_type1))):
                for d in range(len(node_type2)):
                    all_pairs = {}
                    all_pairs['source'] = node_type1[m] 
                    all_pairs['target'] = node_type2[d] 
                    input_df = pd.DataFrame.from_dict([all_pairs])
                    manually_chosen_uris,pattern = one_path_search_patterns(input_df,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,search_type,kg_type,manually_chosen_uris)

                    patterns_all.append(pattern)
    
                #Get count of each pattern
                patterns_count = dict(Counter(patterns_all))

                #Create df of Pattern/Name/count
                patterns_all_df = pd.DataFrame({'Pattern':patterns_all})
                counts = []
                for i in range(len(patterns_all_df)):
                    counts.append(patterns_count[patterns_all_df.iloc[i].loc['Pattern']])
                patterns_all_df['Count'] = counts
                patterns_all_df = patterns_all_df.drop_duplicates(subset=['Pattern','Count'])

                patterns_all_df.to_csv(output_dir + metapath_dir + str(c) + '_Pattern_Counts_Full.csv',sep=',',index=False)
            c += 1


if __name__ == '__main__':
    main()
