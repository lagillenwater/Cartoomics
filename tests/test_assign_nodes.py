

from create_graph import process_pkl_files
from create_graph import create_igraph_graph
from create_graph import create_pkl_graph

import unittest
import pandas as pd
import pandas.api.types as ptypes
import re


sample_labels = "D:/PhD_at_Anschutz/Thesis_work/Cartoomics/tests/data/sample_labels.txt"
triples_file = "D:/PhD_at_Anschutz/Thesis_work/Cartoomics/v6/Cartoomics-Grant-main/Input_Files/current_build_knowledge_graphs_instance_builds_relations_only_owlnets_PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt"
labels_file = "D:/PhD_at_Anschutz/Thesis_work/Cartoomics/v6/Cartoomics-Grant-main/Input_Files/current_build_knowledge_graphs_instance_builds_relations_only_owlnets_PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt"



class assign_nodes_test1(unittest.TestCase):
    
    def test_find_node(self):
        
        #Testing the output of the find node function from the assign note script, where we prepare a sample file of labels and we test the three cases of finding nodes:
        #1. When we input the name of the note and we count the number of the hits that exist in the sample file. 
        #The sample file does not have any duplicate note existence in the same row. For example we will be searching the word "lncRNA", 
        #it only exists once in each found row. 
        #2. includes finding the word "protein", which happened to exist twice in the same row multiple times,
        #So the total number of hits found in the actual labels files is more than the actual number of target rows,
        #However we will count only the actual unique rows and compare them to the found ones by our built function.
        #3 .In the third case we will just finding a word that doesn't exist in our sample file.
        
        print ("test_find_node_function\n")
        
        # total graph search:
        '''
        triples_df,labels = process_pkl_files(triples_file,labels_file)
        edgelist_df = triples_df
        g,g_nodes = create_igraph_graph(edgelist_df,labels)
        kg = create_pkl_graph(triples_file,labels_file)
        
        node  = "towards"
        
        def find_node(node, kg, ontology = ""):
        	nodes = kg.labels_all
        	### All caps input is probably a gene or protein. Either search in a case sensitive manner or assign to specific ontology. 
        	if ontology == "":
        		if node.isupper(): #likely a gene or protein
        			results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains("gene|PR|GO",flags=re.IGNORECASE, na = False) ][["entity_type","integer_id","label", "entity_uri"]]
        		else:
        			results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["entity_type","integer_id","label", "entity_uri"]]
        	else:
        		results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["entity_type","integer_id","label", "entity_uri"]]
        	return(results)
        
        results = find_node(node, kg, ontology = "")
        '''
        
        #Actual
        # sample graph search: 
        s_triples_df,s_labels = process_pkl_files(triples_file,sample_labels)
        s_edgelist_df = s_triples_df
        s_kg = create_pkl_graph(triples_file,sample_labels)
        print("Sample graph built")
        
        def find_node(node, s_kg, ontology = ""):
        	nodes = s_kg.labels_all
        	### All caps input is probably a gene or protein. Either search in a case sensitive manner or assign to specific ontology. 
        	if ontology == "":
        		if node.isupper(): #likely a gene or protein
        			results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains("gene|PR|GO",flags=re.IGNORECASE, na = False) ][["entity_type","integer_id","label", "entity_uri"]]
        		else:
        			results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["entity_type","integer_id","label", "entity_uri"]]
        	else:
        		results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["entity_type","integer_id","label", "entity_uri"]]
        	return(results)

        #example 1
        node = "lncRNA"
        print("testing the presence of the node:", node)
        results1 = find_node(node, s_kg, ontology = "")
        # the number of nodes in the samples file (sample_labels) that carry the word "lncRNA" is 2
        
        #example 2
        node = "protein"
        print("testing the presence of the node:", node)
        results2 = find_node(node, s_kg, ontology = "")
        # the number of nodes in the samples file (sample_labels) that carry the word "protein"
        # -after removing the dumplecates- is 2
        
        #example 3
        node = "existence"
        print("testing the presence of the node:", node)
        results3 = find_node(node, s_kg, ontology = "")
        # the number of nodes in the samples file (sample_labels) that carry the word "existence" is 0

        # assert
        self.assertEqual(len(results1),2)
        self.assertEqual(len(results2),12)
        self.assertEqual(len(results3),0)
        return None
    

        
    
if __name__ == '__main__':
    unittest.main()    
    
    
    
    
