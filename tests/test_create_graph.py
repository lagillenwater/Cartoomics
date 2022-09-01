from create_graph import process_pkl_files
from create_graph import create_igraph_graph
from create_graph import create_pkl_graph


import unittest
import pandas as pd
import pandas.api.types as ptypes
import re
import numpy as np
import os


triples_file = "D:/PhD at Anschutz/Thesis work/Cartoomics/v3/Cartoomics-Grant-main/Input_Files/current_build_knowledge_graphs_instance_builds_relations_only_owlnets_PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt"
labels_file = 'D:/PhD at Anschutz/Thesis work/Cartoomics/v3/Cartoomics-Grant-main/Input_Files/current_build_knowledge_graphs_instance_builds_relations_only_owlnets_PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt'


class create_graph_test1(unittest.TestCase):
    
    def test_process_pkl_file_length(self):
        print ("test_process_pkl_file_length\n")

        
        '''this function is to test read of the Triples_Identifiers.txt
        and the NodeLabels.txt files 
        the read function outputs triples and labels as a df'''
        
        # expected
         
        ''' the shape of the output dataframe for the triples and the labels should
        be of the same shape as read by txt file reader '''
        
        
        #actual        
        
        print(f'triples_file Size is:   {os.stat(triples_file).st_size / (1024 * 1024)} MB')
        read_triples_file = open(triples_file, encoding='cp437')

        triples_count = 0

        for line in read_triples_file:
            # we can process file line by line here, for simplicity I am taking count of lines
            triples_count += 1

        read_triples_file.close()
        print(f'Number of Lines in the triples_file is:   {triples_count}\n')
        
        
        print(f'labels_file Size is:   {os.stat(labels_file).st_size / (1024 * 1024)} MB')
        read_labels_file = open(labels_file, encoding='cp437')

        labels_count = 0

        for line in read_labels_file:
            # we can process file line by line here, for simplicity I am taking count of lines
            labels_count += 1

        read_labels_file.close()
        print(f'Number of Lines in the labels_file is:   {labels_count}\n')
        
        
        triples_df,labels = process_pkl_files(triples_file,labels_file)
        
        # assert
        self.assertEqual(len(triples_df),triples_count-1)
        self.assertEqual(len(labels),labels_count-1)
        return None
        
    


# class create_graph_test2(unittest.TestCase):

    
    def test_process_pkl_file_find_URIs(self):
        
        '''this fuction is to test that all the nodes in the triples file 
        exist in the labels' one '''
        
        #expected
        '''at any random selection of the source/ target nodes and applying the 
        search of these selected nodes, they should be found in the labels file'''
        
        #actual
        
        print ("test_process_pkl_file_find_URIs\n")
        
        triples_df,labels = process_pkl_files(triples_file,labels_file)
        subject_random_sample = triples_df['subject'].sample(n=1).tolist()
        object_random_sample = triples_df['object'].sample(n=1).tolist()

        found_label_sub = labels.loc[labels["entity_uri"] == subject_random_sample[0]]
        found_label_obj = labels.loc[labels["entity_uri"] == object_random_sample[0]]
        
        for i in found_label_sub['entity_uri']:
            self.assertEqual(i,subject_random_sample[0])
        for j in found_label_obj['entity_uri']:
            self.assertEqual(j,object_random_sample[0])        
        return None



# class create_graph_test3(unittest.TestCase):

    
    def test_process_pkl_file_num_columns(self):
        
        '''this function is testing the framing of the read files 
        (just checking if the number of culmns of the triples and the labels 
         foloow our expectations or not)'''
        
        #expected
        '''the number of columns for the labels file is 6'''
        '''the number of columns for the triples file is 3'''
        
        
        #actual
        print ("test_process_pkl_file_num_columns\n")
        
        triples_df,labels = process_pkl_files(triples_file,labels_file)
        
        self.assertEqual(len(labels.columns),6)
        self.assertEqual(len(triples_df.columns),3)        
        
        return None



# class create_graph_test4(unittest.TestCase):

    
    def test_create_igraph_num_nodes(self):
        
        '''this function tests the number of nodes used for generating the graph'''
        
        #expected
        '''the total number of nodes in the graph = (sum(subject)+sum(object))-(subject U object)'''
        
        #actual
        print ("create_igraph_graph_num_nodes\n")
        
        triples_df,labels = process_pkl_files(triples_file,labels_file)
        
        
        subject = triples_df['subject'].astype(str)
        objects = triples_df['object'].astype(str)
        all_nodes = subject.append(objects)
        all_unique_nodes = all_nodes.drop_duplicates()
        
        g,g_nodes = create_igraph_graph(triples_df,labels)
        
        self.assertGreaterEqual(len(labels), len(all_unique_nodes))
        self.assertEqual(len(all_unique_nodes), len(g_nodes))       
        
        return None


        
    
if __name__ == '__main__':
    unittest.main()
