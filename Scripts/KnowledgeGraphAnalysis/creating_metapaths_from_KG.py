from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper
from create_subgraph import automatic_defined_edge_exclusion
from graph_experiments import *
import ast
from collections import defaultdict
import tqdm as tqdm
import random

def main():

    #Define the node types to search between
    node_substring1 = '/gene/'
    node_substring2 = '/MONDO_'

    #Only works for PKL
    input_dir,output_dir,kg_types,embedding_dimensions,weights,search_type,pdp_weight,experiment_type,input_type = generate_arguments()

    kg_types = ast.literal_eval(kg_types)

    for kg_type in kg_types:
        triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type, input_type)

        print("Creating knowledge graph object from inputs.....")

        path_nums_dict = {}
        print('Graph: ',kg_type)

        g = create_graph(triples_list_file,labels_file, kg_type)

        if weights == True:
            g = automatic_defined_edge_exclusion(g,kg_type)
        
        if input_type == 'file':
            #Input file will have one microbe, one disease
            s = interactive_search_wrapper(g,input_file,output_dir,kg_type,experiment_type,input_type,pd.DataFrame())


        if experiment_type == 'one_path':

            manually_chosen_uris = {}

            all_iterations_patterns = defaultdict()

            #Determines number of iterations
            for c in tqdm.tqdm(range(0,1)):  #300)):

                print(c)

                #Check for existence of output directory
                if os.path.exists(output_dir+'/' + str(c) + '_Pattern_Counts_Full.csv'):
                    continue

                patterns_all = []

                if input_type == 'file':
                    #Update to do all shortest paths search
                    one_path_search(s,s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,search_type,triples_list_file,output_dir,kg_type,c)
                if input_type != 'file':
                    #Find all microbe to disease pairs
                    if kg_type != 'pkl':
                        node_type1 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring1)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                        node_type2 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring2)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                    if kg_type == 'pkl':
                        node_type1 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring1)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                        #random.seed(4)
                        node_type1 = random.choices(node_type1, k=1)  #20)
                        node_type2 = g.labels_all['entity_uri'][(g.labels_all['entity_uri'].str.contains(node_substring2)) & (g.labels_all['entity_type'] == 'NODES')].values.tolist()
                        node_type2 = random.choices(node_type2, k=1)  #20)

                    
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
                    print('pattern length after ct: ',c, ': ',len(patterns_all_df))  
                    patterns_all_df.to_csv(output_dir+'/' + str(c) + '_Pattern_Counts_Full.csv',sep=',',index=False)
                c += 1


if __name__ == '__main__':
    main()