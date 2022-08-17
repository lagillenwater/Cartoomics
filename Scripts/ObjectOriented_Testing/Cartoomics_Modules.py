import json
import csv
import pandas as pd
import networkx as nx
from igraph import * 
import os
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import numpy as np
from scipy import spatial
from scipy.spatial import distance

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

        df = self.define_mechanism(g_nodes,identifiers,labels_all,triples_df,path_nodes,search_type)

        ''' #When there is no connection in graph, path_nodes will equal 1 ([[]])
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
        '''
        return df

    def find_all_shortest_paths_igraph(self,start_node,end_node,graph,g_nodes,identifiers,labels_all,triples_df,weights,search_type):

        node1 = self.get_uri(labels_all,start_node)
        node2 = self.get_uri(labels_all,end_node)

        #Add weights if specified
        if weights:
            w = graph.es["weight"]
        else:
            w = None

        #Dict to store all dataframes of shortest mechanisms for this node pair
        mechanism_dfs = {}

        #list of nodes
        path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

        mechanism_dfs = self.define_mechanism(g_nodes,identifiers,labels_all,triples_df,path_nodes,search_type)
        '''
        #Keep track of # of mechanisms generated for this node pair in file name
        count = 1

        #When there is no connection in graph, path_nodes will equal 1 ([[]])
        if len(path_nodes[0]) != 0:
            for p in range(len(path_nodes)):
                n1 = g_nodes[path_nodes[p][0]]  
                for i in range(1,len(path_nodes[p])):
                    n2 = g_nodes[path_nodes[p][i]]
                    if search_type.lower() == 'all':
                        df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                        if len(df) == 0:
                            df = triples_df.loc[(triples_df['Object'] == n1) & (triples_df['Subject'] == n2)]
                    elif search_type.lower() == 'out':
                        df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                    n1 = n2

            #Generate df
            df.columns = ['S','P','O']
            mechanism_dfs['mech#_'+str(count)] = df
            count += 1'''

        return mechanism_dfs,path_nodes

    def define_mechanism(self,g_nodes,identifiers,labels_all,triples_df,path_nodes,search_type):

        #Dict to store all dataframes of shortest mechanisms for this node pair
        mechanism_dfs = {}
        #Keep track of # of mechanisms generated for this node pair in file name for all shortest paths
        count = 1 

        #When there is no connection in graph, path_nodes will equal 1 ([[]])
        if len(path_nodes[0]) != 0:
            for p in range(len(path_nodes)):
                n1 = g_nodes[path_nodes[p][0]]  
                for i in range(1,len(path_nodes[p])):
                    n2 = g_nodes[path_nodes[p][i]]
                    if search_type.lower() == 'all':
                        df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                        if len(df) == 0:
                            df = triples_df.loc[(triples_df['Object'] == n1) & (triples_df['Subject'] == n2)]
                    elif search_type.lower() == 'out':
                        df = triples_df.loc[(triples_df['Subject'] == n1) & (triples_df['Object'] == n2)]
                    n1 = n2

            #For shortest path search
            if len(path_nodes) == 1:
                #Generate df
                df.columns = ['S','P','O']
                return df

            #For all shortest path search
            else:
                #Generate df
                df.columns = ['S','P','O']
                mechanism_dfs['mech#_'+str(count)] = df
                count += 1

        if len(path_nodes) > 1:
            return mechanism_dfs

    def generate_graph_embeddings(self,triples_file,output_dir,node2vec_script_dir,embedding_dimensions):
        
        base_name = triples_file.split('/')[-1]
        print('base_name: ',base_name)

        output_ints_location = output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_Integers_node2vecInput')
        print(output_ints_location)

        output_ints_map_location = output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_Integer_Identifier_Map')
        print(output_ints_map_location)

        with open(triples_file, 'r') as f_in:
            #Length matches original file length
            kg_data = set(tuple(x.split('\t')) for x in f_in.read().splitlines())
        f_in.close()

        # map identifiers to integers
        entity_map = {}
        entity_counter = 0
        graph_len = len(kg_data)

        ints = open(output_ints_location, 'w', encoding='utf-8')
        ints.write('subject' + '\t' + 'predicate' + '\t' + 'object' + '\n')

        for s, p, o in kg_data:
            subj, pred, obj = s, p, o
            if subj not in entity_map: entity_counter += 1; entity_map[subj] = entity_counter
            if pred not in entity_map: entity_counter += 1; entity_map[pred] = entity_counter
            if obj not in entity_map: entity_counter += 1; entity_map[obj] = entity_counter
            ints.write('%d' % entity_map[subj] + '\t' + '%d' % entity_map[pred] + '\t' + '%d' % entity_map[obj] + '\n')
        ints.close()

        #write out the identifier-integer map
        with open(output_ints_map_location, 'w') as file_name:
            json.dump(entity_map, file_name)

        with open(output_ints_location) as f_in:
            kg_data = [x.split('\t')[0::2] for x in f_in.read().splitlines()]
        f_in.close()

        file_out = output_dir + '/' + base_name.replace('Triples_Identifiers','Triples_node2vecInput_cleaned')

        with open(file_out, 'w') as f_out:
            for x in kg_data[1:]:
                f_out.write(x[0] + ' ' + x[1] + '\n')

        f_out.close()
        
        os.chdir(node2vec_script_dir) 

        command = "python GutMGene_sparse_custom_node2vec_wrapper.py --edgelist {} --dim {} --walklen 10 --walknum 20 --window 10"
        os.system(command.format(file_out,embedding_dimensions))

        embeddings_file = file_out.split('.')[0] + '_node2vec_Embeddings' + str(embedding_dimensions) + '_None.emb'
        print(embeddings_file)
        
        emb = KeyedVectors.load_word2vec_format(embeddings_file, binary=False)

        return emb


    def get_embedding(self,emb,node):

        embedding_array = emb[str(node)]
        embedding_array = np.array(embedding_array)
    
        return embedding_array

    def calc_cosine_sim(self,emb,path_nodes,g_nodes,identifiers,labels_all,triples_df,search_type):

        print(search_type)

        target_emb = self.get_embedding(emb,path_nodes[0][len(path_nodes[0])-1])

        #Dict of all embeddings to reuse if they exist
        embeddings = defaultdict(list)

        #List of total cosine similarity for each path in path_nodes, should be same length as path_nodes
        paths_total_cs = []

        for l in path_nodes:
            cs = 0
            for i in range(0,len(l)-1):
                if l[i] not in list(embeddings.keys()):
                    e = self.get_embedding(emb,l[i])
                    embeddings[l[i]] = e
                else:
                    e = embeddings[l[i]]
                cs += 1 - spatial.distance.cosine(e,target_emb)
            paths_total_cs.append(cs)

        chosen_path_nodes_cs = self.select_path(paths_total_cs,path_nodes,g_nodes,identifiers,labels_all,triples_df,search_type)

        #Will only return 1 dataframe
        df = self.define_mechanism(g_nodes,identifiers,labels_all,triples_df,chosen_path_nodes_cs,search_type)

        return df

    def calc_pdp(self,path_nodes,graph,w,g_nodes,identifiers,labels_all,triples_df,search_type):

        #List of pdp for each path in path_nodes, should be same length as path_nodes
        paths_pdp = []

        for l in path_nodes:
            pdp = 1
            for i in range(0,len(l)-1):
                dp = graph.degree(l[i],mode='all',loops=True)
                dp_damped = pow(dp,-w)
                pdp = pdp*dp_damped

            paths_pdp.append(pdp)

        chosen_path_nodes_pdp = self.select_path(paths_pdp,path_nodes,g_nodes,identifiers,labels_all,triples_df,search_type)

        #Will only return 1 dataframe
        df = self.define_mechanism(g_nodes,identifiers,labels_all,triples_df,chosen_path_nodes_pdp,search_type)

        return df

    def select_path(self,value_list,path_nodes,g_nodes,identifiers,labels_all,triples_df,search_type):

        #Get max cs from total_cs_path, use that idx of path_nodes then create mechanism
        max_index = value_list.index(max(value_list))
        #Must be list of lists for define_mechanism function
        chosen_path_nodes = [path_nodes[max_index]]

        return chosen_path_nodes
