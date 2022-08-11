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

print(df)