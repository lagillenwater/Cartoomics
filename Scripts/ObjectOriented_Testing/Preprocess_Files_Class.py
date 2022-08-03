import json
import csv
import pandas as pd

'''
classes
'''

#processes PKL files and returns corresponding data structures
class preprocess_files:

    ###Read in all files
    def process_files(self,triples_file,labels_file,identifiers_file,triples_integers_file,input_nodes_file):

        #Read in triples file to list
        with open(triples_file, 'r') as f_in:
            #Length matches original file length
            triples = set(tuple(x.split('\t')) for x in f_in.read().splitlines())
            f_in.close()

        triples_list = list(triples)

        triples_list = [ x for x in triples_list if "subject" not in x ]
        triples_list = [ x for x in triples_list if "Subject" not in x ]

        labels_all = {}

        with open(labels_file) as f_in:
            for line in f_in:
                vals = line.strip().split("\t")
                try:
                    #key, value = vals[2:4]
                    key, value = vals[0:2]
                    labels_all[key] = value
                except: pass

        #Read in identifiers file to dictionary
        f = open(identifiers_file)
        identifiers = json.load(f)

        #Read in node2vec input triples integers file as df
        edgelist_int = pd.read_csv(triples_integers_file, sep=" ")

        #Read in input nodes file as df
        input_nodes = pd.read_csv(input_nodes_file, sep=',')  #'|')

        return triples_list,labels_all,identifiers,edgelist_int,input_nodes

    def print_test(self,triples_list):

        print(len(triples_list))
        print('it worked')

    

if __name__ ==  '__main__':
    preprocess_files.main()
