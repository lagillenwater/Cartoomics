#from create_graph import create_pkl_graph
from assign_nodes import *

def main():

    # User example file. This is a 2 column csv with columns for each source and target. The paths are generated based on the user cartoon example. 
    user_example_file = "/Users/lucas/OneDrive - The University of Colorado Denver/Grants/Cartoomics-Grant/Test_Data/DS/DS_example_input.csv"

    # # This should be turned into a config file I think, or CLI with a directory input and we should also add a logger
    # triples_list_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'

    # labels_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

    # identifiers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json'

    # triples_integers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt'

    # output_dir = '/Users/brooksantangelo/Documents/HunterLab/Cartoomics/Scripts/Test'

    u = read_user_input(user_example_file)
    n = map_nodes(u)
    print(n)
    
    #g = create_pkl_graph(triples_list_file,labels_file,identifiers_file,triples_integers_file)

    #p = subgraph_prioritized_path_cs(input_file,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,node2vec_script_dir,embedding_dimensions)

    #print(p)

if __name__ == '__main__':
    main()