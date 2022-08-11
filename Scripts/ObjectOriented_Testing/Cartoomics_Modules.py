import json
import csv
import pandas as pd
import networkx as nx
from igraph import * 

'''
classes
'''

#processes PKL files and returns corresponding data structures
class CreateGraph:

    ###Read in all files, outputs triples and labels and integers edgelist as a df, and identifiers as a dict
    def process_pkl_files(self,triples_file,labels_file,identifiers_file,triples_integers_file):

        triples_df = pd.read_csv(triples_file,sep = '	')

        labels = pd.read_csv(labels_file, sep = '	')

        #Read in identifiers file to dictionary
        f = open(identifiers_file)
        identifiers = json.load(f)

        #Read in node2vec input triples integers file as df
        edgelist_int_df = pd.read_csv(triples_integers_file, sep=" ")

        return triples_df,labels,identifiers,edgelist_int_df

    ###Read in all files, outputs triples and labels and integers edgelist as a df, and identifiers as a dict
    def process_monarch_files(self,edges_file,nodes_file):

        edges = pd.read_csv(edges_file, sep = '\t')

        nodes = pd.read_csv(nodes_file, sep = '\t')

        return edges, nodes


    def create_nx_graph(self,edgelist_df):

        edgelist_df = edgelist_df[['Subject', 'Object', 'Predicate']]

        g = nx.from_pandas_edgelist(edgelist_df, 'Subject', 'Object', 'Predicate',  create_using=nx.MultiGraph())

        g_nodes = list(g.nodes)

        return g,g_nodes

    def create_igraph_graph(self,edgelist_df,labels):

        edgelist_df = edgelist_df[['Subject', 'Object', 'Predicate']]

        uri_labels = labels[['Identifier']]

        g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

        g_nodes = g.vs()['name']  

        return g,g_nodes 


    def print_test(self,triples_list,g_nodes_nx,g_nodes_igraph):

        print('length of original triples list: ',len(triples_list))
        print('number of nx nodes: ',len(g_nodes_nx))
        print('number of igraph nodes: ',len(g_nodes_igraph))


if __name__ ==  '__main__':
    CreateGraph.main()

class ShortestPathSearch:

    #Go from label to entity_uri (for PKL original labels file) or Label to Idenifier (for microbiome PKL)
    def get_uri(self,labels,value):

        uri = labels.loc[labels['Label'] == value,'Identifier'].values[0]
        
        return uri

    def get_label(self,labels,value):

        label = labels.loc[labels['Identifier'] == value,'Label'].values[0]
        
        return label
    
    
    def get_key(self,dictionary,value):

        for key, val in dictionary.items():
            if val == value:
                return key

    def find_shortest_path_igraph(self,start_node,end_node,graph,g_nodes,identifiers,labels_all,triples_df,weights,search_type):

        node1 = self.get_uri(labels_all,start_node)
        node2 = self.get_uri(labels_all,end_node)

        #Add weights if specified
        if weights:
            w = graph.es["weight"]
        else:
            w = None

        #list of nodes
        path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

        paths = []

        #When there is no connection in graph, path_nodes will equal 1 ([[]])
        if len(path_nodes[0]) != 0:
            n1 = g_nodes[path_nodes[0][0]]
            for i in range(1,len(path_nodes[0])):
                n2 = g_nodes[path_nodes[0][i]]
                if search_type.lower() == 'all':
                    df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                    if len(df) == 0:
                        df = triples_df.loc[(triples_df['Object'] == n1) & (triples_df['Subject'] == n2)]
                elif search_type.lower() == 'out':
                    df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                n1 = n2

            #Generate df
            df.columns = ['S','P','O']

        return df2
