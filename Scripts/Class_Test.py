

import Processing_Files_Class


triples_list_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'

labels_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels_NewEntities.txt'

identifiers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json'

triples_integers_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt'

input_nodes_file = '/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/0803_Test/Microglia_Astroctye_Activation_Input_Nodes_Test.csv'


# Created a class object
object = Processing_Files_Class.preprocess_files()
   
# Calling and printing class methods
triples_list,labels_all,identifiers,edgelist_int,input_nodes = object.process_files(triples_list_file,labels_file,identifiers_file,triples_integers_file,input_nodes_file)


# Calling the function
print(object.print_test(triples_list))
#triples_list,labels_all,identifiers,edgelist_int,input_nodes = preprocess_files.process_files(triples_list_file,labels_file,identifiers_file,triples_integers_file,input_nodes_file)
