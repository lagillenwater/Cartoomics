''' testing how to build and run a class of more than one function
    for the run: referece the file that defines the class in your script ''' 


'''
Classes
'''

from Cartoomics_Modules import *

triples_list_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'

labels_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

identifiers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json'

triples_integers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt'

output_dir = '/Users/brooksantangelo/Documents/HunterLab/Cartoomics/Scripts/Test'

node2vec_script_dir = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Scripts/' #/sparse_custom_node2vec_wrapper.py'

embedding_dimensions = 42

search_type = 'all'

pdp_weight = 0.4


# Created a class object
graphObject = CreateGraph()
   
# Calling and printing class methods
triples_df,labels,identifiers,edgelist_int_df = graphObject.process_pkl_files(triples_list_file,labels_file,identifiers_file,triples_integers_file)

g_nx,g_nodes_nx = graphObject.create_nx_graph(triples_df)

g_igraph,g_nodes_igraph = graphObject.create_igraph_graph(triples_df,labels)

graphObject.print_test(triples_df,g_nodes_nx,g_nodes_igraph)

# Created a class object
pathObject = ShortestPathSearch()

df = pathObject.find_shortest_path_igraph('prostaglandin E synthase (human)','prostaglandin E2',g_igraph,g_nodes_igraph,identifiers,labels,triples_df,False,'all')

print('shortest path result')
print(df)

dict_df,path_nodes = pathObject.find_all_shortest_paths_igraph('prostaglandin E synthase (human)','prostaglandin E2',g_igraph,g_nodes_igraph,identifiers,labels,triples_df,False,'all')

print('all shortest paths result')
print(dict_df)

emb = pathObject.generate_graph_embeddings(triples_list_file,output_dir,node2vec_script_dir,embedding_dimensions)

chosen_path_cs = pathObject.calc_cosine_sim(emb,path_nodes,g_nodes_igraph,triples_df,search_type)
chosen_path_cs_labels = pathObject.convert_to_labels(chosen_path_cs,labels)

print('cosine similarity')
print(chosen_path_cs)
print(chosen_path_cs_labels)

chosen_path_pdp = pathObject.calc_pdp(path_nodes,g_igraph,pdp_weight,g_nodes_igraph,triples_df,search_type)
chosen_path_pdp_labels = pathObject.convert_to_labels(chosen_path_pdp,labels)

print('pdp')
print(chosen_path_pdp)
print(chosen_path_pdp_labels)

