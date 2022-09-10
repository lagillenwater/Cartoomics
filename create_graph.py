from graph import KnowledgeGraph
import pandas as pd
import csv
import json
from igraph import * 


###Read in all files, outputs triples and labels as a df
def process_pkl_files(triples_file,labels_file):
    
    triples_df = pd.read_csv(triples_file,sep = '	', quoting=csv.QUOTE_NONE)
    triples_df.columns.str.lower()

    triples_df.replace({'<': ''}, regex=True, inplace=True)
    triples_df.replace({'>': ''}, regex=True, inplace=True)

    labels = pd.read_csv(labels_file, sep = '	', quoting=csv.QUOTE_NONE)
    labels.columns.str.lower()

    #Remove brackets from URI
    labels['entity_uri'] = labels['entity_uri'].str.replace("<","")
