import pandas as pd
import numpy as np
import argparse
import pickle
import time
import networkx as nx
import cartoomics_util
from cartoomics_util import *
from importlib import reload


# Collect the arguments for the program. 
# Inputs

def defineArguments():
    parser=argparse.ArgumentParser(description = "Collect Inputs")
    #parser.add_argument("--e", dest = "edgelist_file", required=True,help="edgelist pickle")
    parser.add_argument("--p", dest = "KG_pkl", required=True,help="knowledge graph pickle")
    return parser


# interactive testing.....
reload(cartoomics_util)
from cartoomics_util import *
graph = graphFromPickle("../data/covid_multi_di_graph.pkl")
nodes = parseNodeData("../data/COVID/merged-kg_nodes.tsv")
findNode("IL6", nodes) # ENSEMBL:ENSG00000136244
findNode("cytokine storm", nodes) # HP:0033041
findNode("TNF", nodes) # ENSEMBL:ENSG00000232810
findNode("NFKB", nodes) #  ENSEMBL:ENSG00000109320 # ENSEMBL:ENSG00000077150 # subunits 1 & 2
findNode("IKBKG", nodes) # NEMO # ENSEMBL:ENSG00000269335
findNode("double stranded RNA", nodes) # GO:0039691


def main():
	#Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()

    KG_pkl = args.KG_pkl
    graph = graphFromPickle(KG_pkl)
    print(nx.info(graph))





if __name__ == '__main__':
    main()


#covid_nodes = pd.read_table("../data/COVID/merged-kg_nodes.tsv")
#covid_nodes = covid_nodes[["id", "category", "name", "description"]]








# #search the graph for nodes related to figure 1 in https://doi.org/10.1016/j.patter.2020.100155
# #identifiers = covid_nodes[covid_nodes["name"].str.contains("IL6",flags=re.IGNORECASE, na = False)|covid_nodes["description"].str.contains("IL6",flags=re.IGNORECASE, na = False)][["id","name", "description"]]

# input_features = ["UniProtKB:P19838",  "UniProtKB:P01375","UniProtKB:Q9BYF1", "UniProtKB:P05231","DrugCentral:4904", "DrugCentral:4974"] #  NFKB, TNF, adalimumab
# input_metadata = covid_nodes[covid_nodes["id"].isin(input_features)]

# #subpaths = list(nx.all_simple_paths(covid,input_features[0], input_features[2], cutoff = 5))
# #subpaths = [item for sublist in subpaths for item in sublist]


# # Find all paths between two nodes
# # Shortest paths
# # takes as an input the knowledge graph, the input features found in the KG, and the cutoff for path length
# # returns a nested list of path nodes

# def simple_paths_selection(kg,input_features, cutoff):
# 	feature_simple_paths = list()
# 	for i in range(0,len(input_features)):
# 		print(i)
# 		for j in range(0,len(input_features)):
# 			print(j)
# 			feature_simple_paths.append(list(nx.all_simple_paths(covid, input_features[i], input_features[j], cutoff = cutoff )))
# 	feature_simple_paths = [item for sublist in feature_simple_paths for item in sublist]
# 	return(feature_simple_paths)




# # Annotation
# # Need to annotate the path nodes by the feature name, not just the identifier in the KG (e.g. 'UniProtKB:xxxxxx')
# # Takes as an input a nested list of paths and a pandas data frame containing the node metadata
# def path_features(paths, covid_nodes):
# 	return_paths = list()
# 	for i in paths:
# 		tmp_path = [covid_nodes.loc[covid_nodes["id"] ==x]["name"].values[0] for x in i] 
# 		# some of the paths contain NA values, should remove these
# 		return_paths.append(tmp_path)
# 	return(return_paths)

# # Need to annotate the path nodes by the feature type, not just the identifier in the KG (e.g. 'UniProtKB:xxxxxx')
# # Takes as an input a nested list of paths and a pandas data frame containing the node metadata

# def path_metadata(paths, covid_nodes):
# 	return_paths = list()
# 	for i in paths:
# 		tmp_path = [covid_nodes.loc[covid_nodes["id"] ==x]["category"].values[0] for x in i]
# 		return_paths.append(tmp_path)
# 	return(return_paths)

# def get_metapath_di(paths, metadata, covid_edges):
# 	metapaths = list()
# 	for i in range(0, len(paths)):
# 		tmp_path = paths[i]
# 		tmp_meta = metadata[i]
# 		metapath = []
# 		tmp_subject = str.split(str.split(tmp_meta[0], '|')[0], ':')[1] 
# 		tmp_predicate = str.split(covid_edges.loc[(covid_edges["subject"] == tmp_path[0])&(covid_edges["object"] == tmp_path[1] )]["predicate"].values[0],":")[1]
# 		tmp_object = str.split(str.split(tmp_meta[1], '|')[0], ':')[1]
# 		metapath.extend([tmp_subject,tmp_predicate, tmp_object])
# 		for x in range(1,(len(tmp_path)-1)):
# 			y = x+1
# 			tmp_predicate = str.split(covid_edges.loc[(covid_edges["subject"] == tmp_path[x])&(covid_edges["object"] == tmp_path[y] )]["predicate"].values[0],":")[1]
# 			tmp_object = str.split(str.split(tmp_meta[y], '|')[0], ':')[1]
# 			metapath.extend([tmp_predicate, tmp_object])
# 		metapaths.append(metapath)
# 	return(metapaths)



# paths = simple_paths_selection(covid_di, input_features, 7)
# simple_names = path_features(paths, covid_nodes)
# metadata = path_metadata(paths)
# metapaths = get_metapath_di(paths, metadata, covid_edges)

# metapath_counts = Counter(str(e) for e in metapaths)
# metapath_counts = pd.DataFrame.from_dict(metapath_counts, orient = "index").reset_index()
# metapath_counts.to_csv("../data/covid_metapath_counts.csv")

# subpaths = [item for sublist in paths for item in sublist]

# tmp_subgraph = covid_di.subgraph(subpaths)
# tmp_edgelist = nx.to_pandas_edgelist(tmp_subgraph)
# tmp_edgelist["source_label"] = [' '.join(covid_nodes.loc[covid_nodes["id"] ==i].name.tolist()) for i in tmp_edgelist["source"]]
# tmp_edgelist["target_label"] = [' '.join(covid_nodes.loc[covid_nodes["id"] ==i].name.tolist()) for i in tmp_edgelist["target"]]
# tmp_edgelist["source_type"] = [' '.join(covid_nodes.loc[covid_nodes["id"] ==i].category.tolist()) for i in tmp_edgelist["source"]]
# tmp_edgelist["target_type"] = [' '.join(covid_nodes.loc[covid_nodes["id"] ==i].category.tolist()) for i in tmp_edgelist["target"]]
# tmp_edgelist["source_type"] = [i.split("|",1)[0] for i in tmp_edgelist['source_type']]
# tmp_edgelist["source_type"] = [i.split(":",1)[1] for i in tmp_edgelist['source_type']]
# tmp_edgelist["predicate"] = [i.split(":",1)[1] for i in tmp_edgelist['predicate']]
# tmp_edgelist["target_type"] = [i.split("|",1)[0] for i in tmp_edgelist['target_type']]
# tmp_edgelist["target_type"] = [i.split(":",1)[1] for i in tmp_edgelist['target_type']]


# tmp_edgelist.to_csv("../data/covid_di_edgelist.csv")



# metapath = []

# for x in range(0,len(tmp_edgelist)):

# metapath = metapath.append(tmp_edgelist.iloc[x,6]






# subpaths = [item for sublist in feature_simple_paths for item in sublist]




# # create sub graph based on predecessors
# covid_sub = covid.subgraph(subpaths)

# # convert to table
# covid_sub_edgelist = nx.to_pandas_edgelist(covid_sub)
# covid_sub_edgelist.head(3)
# covid_sub_edgelist["source_label"] = [covid_nodes.loc[covid_nodes["id"] ==i].name.tolist() for i in covid_sub_edgelist["source"]]
# covid_sub_edgelist["target_label"] = [covid_nodes.loc[covid_nodes["id"] ==i].name.tolist() for i in covid_sub_edgelist["target"]]
# covid_sub_edgelist["source_type"] = [covid_nodes.loc[covid_nodes["id"] ==i].category.tolist() for i in covid_sub_edgelist["source"]]

# covid_sub_edgelist["target_type"] = [covid_nodes.loc[covid_nodes["id"] ==i].category.tolist() for i in covid_sub_edgelist["target"]]
# covid_sub_edgelist[["source_label", "predicate", "target_label"]]



# # output for cytoscape
# covid_sub_edgelist.to_csv("../data/covid_feature_edgelist.csv", sep=";")



# all_simple_edge_paths = list()
# for i in input_features[0:3]:
# 	print(i)
# 	for j in input_features[0:3]:
# 		print(j)
# 		all_simple_edge_paths.append(list(nx.all_simple_edge_paths(covid_sub, i, j, cutoff = 4)))


# edge_paths = [item for sublist in all_simple_edge_paths for item in sublist]
# subpaths = [item for sublist in feature_simple_paths for item in sublist]







# # Problem, the paths always go through subclass nodes. removing the subclass nodes greatly reduces the graph. 
# # current solution, weight these nodes more to avoid going through these paths

# # pkl_int["weight"] = 1

# # def upweight (df, predicate, weight, value):
# # 	df[weight] = np.where(df[weight] != 1, 99,df[weight])
# # 	df[weight] = np.where(df[predicate] == value, 99,df[weight])
# # 	return df


# # pkl_int = upweight(pkl_int,"predicate", "weight", 2)
# # pkl_int = upweight(pkl_int,"predicate", "weight", 10)
# # pkl_int = upweight(pkl_int,"predicate", "weight", 5)




# # identifying the degree sequence in the covid graph
# degree_sequence = sorted((d for n, d in covid.degree()), reverse=True)
# dmax = max(degree_sequence)

# fig = plt.figure("Degree of a KG-COVID", figsize=(8, 8))
# # Create a gridspec for adding subplots of different sizes

# ax1 = fig.add_subplot()
# ax1.plot(degree_sequence, "b-", marker="o")
# ax1.set_title("Degree Rank Plot")
# ax1.set_ylabel("Degree")
# ax1.set_xlabel("Rank")


# fig.tight_layout()
# plt.savefig("../data/covid-KG-degree.jpg")


# ### Node dictionary
# node_dict = pickle.load(open('../data/current_owlnets/node_metadata_dict.pkl', 'rb'))

# ### This is a nested dictionary, so need to get the separate nodes and relations for filtering 
# nodes = node_dict["nodes"]
# relations = node_dict["relations"]
# nodes_edges = {**nodes,**relations}
# dict(list(nodes_edges.items())[0:3])



# # Get graph OBO identifiers
# identifiers = pd.read_json("../data/current_owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_INSTANCE_purified_Triples_Integer_Identifier_Map.json", typ = "series")
# identifiers_frame = identifiers.to_frame()
# identifiers_frame["IRI"]  = identifiers_frame.index
# identifiers_frame["IRI"] = identifiers_frame["IRI"].str.replace("<|>","")
# identifiers_frame.head
# # identifiers_frame.shape

# #### getting the keys for the most recent metadata shared 4/12/21
# filtered_identifiers = identifiers_frame[identifiers_frame["IRI"].isin(nodes_edges.keys())]
# filtered_identifiers["Label"] =  [nodes_edges.get(key, "none")["Label"] for key in filtered_identifiers["IRI"]]
# filtered_identifiers["Description"] =  [nodes_edges.get(key, "none")["Description"] for key in filtered_identifiers["IRI"]]
# filtered_identifiers["Synonym"] =  [nodes_edges.get(key, "none")["Synonym"] for key in filtered_identifiers["IRI"]]
# filtered_identifiers["URI"] = filtered_identifiers["IRI"].apply(lambda x: URIRef(x))
# edges = filtered_identifiers[filtered_identifiers[0].isin(pkl_int["predicate"])][["Label",0]]
# edges.to_csv("../data/edges.csv")


# # convert to multigraph
# pkl_int = pkl_int[['subject', 'object', 'predicate']]
# pkl = nx.from_pandas_edgelist(pkl_int, 'subject', 'object', 'predicate',  create_using=nx.MultiGraph())


# # Identifying the features from https://www.frontiersin.org/articles/10.3389/fnins.2020.00670/pdf, Figure 2. 
# # Focus specifically on AKT, mTOR, and GSK-3-beta, autophagy, energy production, and oxidative stress
# IDs= filtered_identifiers[filtered_identifiers['Description'].str.contains("PI3 kinase",flags=re.IGNORECASE, na = False) & filtered_identifiers['IRI'].str.contains("gene",flags=re.IGNORECASE, na = False)]
# IDs[["Label",0]]


# # subset to these input_features
# features = [258976,74637,165173,24191,55841, 73148,55773, 19836, 4697, 7084,70190,51994,  4880 ]
# input_features = filtered_identifiers[filtered_identifiers[0].isin(features)]
# input_features[["Label", "Description"]]


# # # For all paths between features
# # paths = list()
# # for i in range(0,len(input_features)-1):
# # 	print(i)
# # 	for j in range(i+1, len(input_features)):
# # 		print(j)
# # 		paths.append(list(nx.shortest_path(pkl, input_features.iloc[i,0], input_features.iloc[j,0], "weight")))


# # Just need to find paths represented in the knowledge graph
# # AKT -> mTOR
# pkl[features[0]]


# # descendents 2 hops away
# descendents = list()
# for i in range(0,len(input_features)-1):
# 	print(i)
# 	descendents.append(list(nx.dfs_successors(pkl, features[i],2)))


# descendents = [item for sublist in descendents for item in sublist]

# pkl_descendents = pkl.subgraph(descendents)

# ## Change graph to tabular form
# pkl_desc_edgelist = nx.to_pandas_edgelist(G = pkl_descendents)

# # filter interger pkl data
# pkl_desc_edgelist["source_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_desc_edgelist["source"]]
# pkl_desc_edgelist["target_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_desc_edgelist["target"]]
# pkl_desc_edgelist["predicate_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_desc_edgelist["predicate"]]
# pkl_desc_edgelist[["source_label", "target_label", "predicate_label"]]
# pkl_desc_edgelist["original"] = np.where(pkl_desc_edgelist["source"].isin(list(input_features[0])), 1, 0)

# # output for cytoscape
# pkl_desc_edgelist.to_csv("../data/pkl_desc_edgelist.csv", sep = ";")




# shortest_paths = list()
# for i in range(0,len(input_features)-1):
# 	print(i)
# 	for j in range(i+1, len(input_features)):
# 		print(j)
# 		shortest_paths.append(list(nx.shortest_path(pkl, features[i], features[j] ,weight=lambda u, v, d: 10 if d[0]['predicate'] == 5 else 1)))



# #test = nx.all_shortest_paths(pkl, features[0], features[7] ,weight=lambda u, v, d: 5 if d[0]['predicate'] == 5 else 1)
# #subpaths = list(test)

# # combine the lists of lists into a single list (for paths)
# subpaths = [item for sublist in shortest_paths for item in sublist]
# #subpaths = [item for sublist in subpaths for item in sublist]

# len(subpaths)

# # create subgraph of these nodes
# pkl_sub = pkl.subgraph(subpaths)

# ## Change graph to tabular form
# pkl_sub_edgelist = nx.to_pandas_edgelist(G = pkl_sub)

# # filter interger pkl data
# pkl_sub_edgelist["source_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_sub_edgelist["source"]]
# pkl_sub_edgelist["target_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_sub_edgelist["target"]]
# pkl_sub_edgelist["predicate_label"] = ["".join(filtered_identifiers.loc[filtered_identifiers[0] ==i].Label.tolist()) for i in pkl_sub_edgelist["predicate"]]
# pkl_sub_edgelist[["source_label", "target_label", "predicate_label"]]
# pkl_sub_edgelist["original"] = np.where(pkl_sub_edgelist["source"].isin(list(input_features[0])), 1, 0)



# # output for cytoscape
# pkl_sub_edgelist.to_csv("../data/pkl_sub_edgelist_updated.csv", sep=";")




#pkl_sub.size() # still very large graph at this point

# # # Visualizing
# pos = nx.spring_layout(pkl_sub)
# # draw graph
# nx.draw(pkl_sub, pos=pos, font_size=0, node_color='blue', font_color='white', node_size = 50, with_labels = False, edge_color = "blue", alpha = .6)
# # draw subgraph for highlights
# nx.draw(pkl_sub.subgraph(features), pos=pos, font_size=12, node_color='yellow', font_color='purple', with_labels = False, labels = nodes_edges)
# plt.savefig("akt_mtor_gsk_fullplot.pdf")
# plt.clf() # not sure which of these is doing the work
# plt.cla()






################################# OLD CODE


# pkl.size()
#pkl_nodes = list(pkl.nodes)
#str(pkl_nodes[0:1])
# pkl_edges = list(pkl.edges)
# pkl_edges[10]

# Need to now create a subgraph that includes the defined nodes
# Approach, create a list of iterable objects containing the terms identified in a depth first search


# akt_pred = list(nx.dfs_predecessors(pkl,features[0],2))
# akt_desc = list(nx.dfs_successors(pkl,features[0],2))
# mtor_pred = list(nx.dfs_predecessors(pkl,features[1],2))
# mtor_desc = list(nx.dfs_successors(pkl,features[1],2))
# gsk_pred = list(nx.dfs_predecessors(pkl,features[2],1))
# gsk_desc = list(nx.dfs_successors(pkl,features[2],2))


# # # dumb way to do this, but for the worked example
# sub_graph = akt_pred + akt_desc + mtor_pred + mtor_desc + gsk_pred +gsk_desc
# len(sub_graph)


# map rdflib nodes to labels that indicate what a feature is 
# 
# features = list(set(list(pkl_sub.nodes())+(list(pkl_sub.edges()))))
# mapping = filtered_identifiers[["URI","Label"]] 
# mapping = mapping[mapping["URI"].isin(features)]
# mapping = mapping.set_index('URI').T.to_dict('list')



# #write subgraph to edgelsit file for reading into cytoscape
# nx.write_gml(pkl_sub, "../akt_mtor_gsk_1.gml")



# pkl_sub.size()
# attr = nx.get_node_attributes(pkl_sub, "Label")


# # Visualizing
# pos = nx.spring_layout(pkl_sub)
# # draw graph
# nx.draw(pkl_sub, pos=pos, font_size=0, node_color='blue', font_color='white', node_size = 50, with_labels = False, edge_color = "blue", alpha = .6)
# # draw subgraph for highlights
# nx.draw(pkl_sub.subgraph(list(input_features["URI"])), pos=pos, font_size=12, node_color='yellow', font_color='purple', with_labels = True, labels = nodes_edges)
# plt.savefig("akt_mtor_gsk_fullplot.pdf")
# plt.clf() # not sure which of these is doing the work
# plt.cla()

# print(i)



# #print(list(AKT_desc))


# ### Approach1 again find all predecessors and descendents
# pred_desc = list()
# for i in range(0,len(input_features)-1):
# 	print(i+1)
# 	pred_desc.append(nx.dfs_predecessors(pkl,features[i],4))	
# 	pred_desc.append(nx.dfs_successors(pkl,features[i],4))	

# len(pred_desc)





# #filtered_identifiers = [identifiers[i] for i in nodes_edges.keys() if i in identifiers]

# # switch key and id for finding iri based on the key 
# identifiers_switch = {y:x for x,y in identifiers.iteritems()}
# dict(list(identifiers_switch.items())[0:3])


# # Filter the graph to only include subject nodes in the genomic, chemical, phenotype and disease ontologies.
# IDs= filtered_identifiers.filter(regex = "DOID|GO|CHEBI|EFO|HP", axis = 0) 
# #IDs = filtered_identifiers

# #IDs= filtered_identifiers 
# IDs["class"] = IDs["IRI"].apply(lambda x: x.rsplit('/',1)[1])
# IDs["class"] = IDs["class"].apply(lambda x: x.rsplit("_",1)[0])

# # Subset the graph to only include nodes from these ontologies. May include all relation ontologies. 
# Graph = Graph[(Graph["subject"].isin(IDs[0])) | (Graph["object"].isin(IDs[0]))]
# Graph.shape
# Graph.head


# ############################ This part filters based on relations


# # relations = Graph["predicate"].unique()

# # rel = filtered_identifiers[filtered_identifiers[0].isin(relations)]
# # rel.to_csv("relations.csv")

# # rel = pd.read_csv("relations1.csv")
# # rel_to_keep = rel[rel["Flag"] == 1]["0"]
# # #rel_to_keep = rel_to_keep[rel_to_keep != 30]


# # Graph = Graph[Graph["predicate"].isin(rel_to_keep)]
# # Graph.shape
# # Graph.head



# #######################################


# # get all the features in the graph to subset the embeddings
# features = pd.melt(Graph)
# features.head

# # get the unique values
# feature_index = features["value"].unique()
# feature_index[:5]


# #Loading in the embeddings
# embeddings = pd.read_csv("../data/PheKnowLator_Instance_RelsOnly_NoOWL_node2vec_Embeddings_07Sept2020.emb",  skiprows = 1, sep = " " , index_col = 0, header = None)
# embeddings.head
# embeddings.shape

# # subset embeddings based on the defined features
# sub_embeddings =embeddings.reindex(feature_index)
# sub_embeddings.head
# sub_embeddings.shape

# ### Drop NA embeddings. WHY ARE THERE NA EMBEDDINGS? - due to not having relation embeddings
# np.any(np.isnan(sub_embeddings))
# sub_embeddings = sub_embeddings.dropna()
# sub_embeddings.shape

# # umap embeddings
# reducer = um.UMAP(n_components = 3)

# emb = reducer.fit_transform(sub_embeddings)
# emb = pd.DataFrame(emb)
# emb["index"] = sub_embeddings.index
# IRI = filtered_identifiers[(filtered_identifiers[0].isin(emb["index"]))]
# emb["IRI"] = [identifiers_switch[key] for key in emb["index"]]
# emb = emb[emb["IRI"].isin(nodes_edges.keys())]




# emb["label"] = [nodes_edges[key]["Label"] for key in emb["IRI"]]
# emb["description"] = [nodes_edges[key]["Description"] for key in emb["IRI"]]
# emb["synonyms"] = [nodes_edges[key]["Synonym"] for key in emb["IRI"]]
# emb["class"] = emb["IRI"].apply(lambda x: x.rsplit('/',1)[1])
# emb["class"] = emb["class"].apply(lambda x: x.rsplit("_",1)[0])
# emb.to_csv("umap_embeddings.csv")


# Graph = Graph[(Graph["subject"].isin(emb.index)) & (Graph["object"].isin(IDs[0]))]
# Graph.to_csv("subGraph.csv")


# ### Identifying chronic lung diseae
# lung_sub = emb[emb["label"].str.contains("trypsin")][["index", "label", "description", "class"]]



# #### Finding the nodes within the graph that contain chronic lung disease as the subject or as the object. 


# lung_graph = Graph[(Graph["subject"] ==11)|(Graph["object"] == 11) ]
# lung_graph = Graph[(Graph["subject"].isin(lung_sub["index"]))|(Graph["object"].isin(lung_sub["index"])) ]


# filtered_identifiers[filtered_identifiers[0].isin(lung_graph["predicate"].unique())]
# filtered_identifiers[filtered_identifiers[0] == 26]






# lung_nodes = emb[emb["index"].isin(lung_graph["subject"])]
# lung_nodes["class"].unique()
# lung_nodes["label"].unique()


# lung_graph[lung_graph["predicate"] == 13]




# nodes = pd.melt(lung_graph[["subject"]])["value"].unique()

# nodes = 45719
# newnodes =[nodes]
# n = 0
# while n < 3:
# 	newnodes = Graph[Graph['subject'].isin(newnodes)]["object"]
# 	nodes = np.append(nodes, newnodes)
# 	n += 1
# 	print(newnodes)


# tempGraph = Graph[Graph['subject'].isin(nodes)]
# tempGraph["subject1"] = [emb[emb["index"]==key]["label"] for key in tempGraph["subject"]]
# tempGraph["predicate1"] =  [emb[emb["index"]==key]["label"] for key in tempGraph["predicate"]]
# tempGraph["object1"] =  [emb[emb["index"]==key]["label"] for key in tempGraph["object"]]







# filtered_identifiers[filtered_identifiers[0].isin(tempGraph["predicate"].unique())]



# ##### Filter graph relations


# relations = Graph["predicate"].unique()

# rel = filtered_identifiers[filtered_identifiers[0].isin(relations)]
# rel.to_csv("relations.csv")



# #### 













# nodes['http://purl.obolibrary.org/obo/DOID_850']

# nodes.get("http://purl.obolibrary.org/obo/DOID_2740")

# nodes.get("http://purl.obolibrary.org/obo/DOID_2740")["Label"]
# key = "http://purl.obolibrary.org/obo/GO_0034282"

# ############## OLD CODE
# identifiers["http://purl.obolibrary.org/obo/GO_2320"]

# identifiers_t = {y:x for x,y in identifiers.iteritems()}
# nodes[identifiers_t[18467]]
# relations[identifiers_t[5]]

# ##### Diabetes Graph
# DG = Graph_map[Graph_map["subject"] == 5161 ]


# # OLD - node_edge dictionary - another dictionary used for finding the proper labels for the node and edge types
# # node_edge_dict = pd.read_json("../data/PheKnowLator_Master_Node_Edge_List_Dict.json")
# # node_edge_dict.head
# # node_edge_dict = node_edge_dict.transpose()
# # node_edge_dict[node_edge_dict["node_type"] == "disease"]





# GO_Graph = Graph_map[Graph_map["subject"].isin(GO_IDs) ]


# # Invert the identifiers so that the number is the key and the OBO link is the value
# identifiers_t = {y:x for x,y in identifiers.iteritems()}
# dict(list(identifiers_t.items())[0:3])


# # melt to get list of graph nodes
# Graph_nodes = pd.melt(GO_Graph)
# Graph_nodes["URL"] = Graph_nodes["value"].apply(lambda x:identifiers_t.get(x))
# Graph_nodes["ID"] = Graph_nodes["URL"].apply(lambda x: x.rsplit("/",1)[1])
# Graph_nodes = pd.merge(Graph_nodes, node_edge_dict, left_on = "ID", right_index = True, how = "left" )
# Graph_nodes.head


# # map the identifiers dictionary onto the graph
# GO_Graph["subject1"] = GO_Graph["subject"].apply(lambda x:identifiers_t.get(x))
# GO_Graph["predicate1"] = GO_Graph["predicate"].apply(lambda x:identifiers_t.get(x))
# GO_Graph["object1"] = GO_Graph["object"].apply(lambda x:identifiers_t.get(x))
# GO_Graph["subject2"] = GO_Graph["subject1"].apply(lambda x: x.rsplit('/',1)[1])
# GO_Graph["predicate2"] = GO_Graph["predicate1"].apply(lambda x: x.rsplit('/',1)[1])
# GO_Graph["object2"] = GO_Graph["object1"].apply(lambda x: x.rsplit('/',1)[1])

# GO_Graph.to_csv("GO_Graph.csv")

# #map ontology data
# go = get_ontology("/home/lucas/CPBS/KG/data/ontologies/go_with_imports.owl")
# go.load()
# obo = get_namespace("http://purl.obolibrary.org/obo/")
# print(obo.GO_0015233.object_properites())

# obo = get_namespace("http://purl.obolibrary.org/obo/")
# print(obo.GO_1903326.get_properties)

# rel = get_ontology("http://www.w3.org/2000/01/")
# rel.load()
# print(rel.rdf-schema)#subClassOf)
# # 

# #G = joblib.load( open("/home/lucas/CPBS/KG/data/model.pckl", "rb"))

# #Loading in the embeddings
# embeddings = pd.read_csv("../data/PheKnowLator_Instance_RelsOnly_NoOWL_node2vec_Embeddings_07Sept2020.emb",  skiprows = 1, sep = " " , index_col = 0, header = None)
# embeddings.head
# embeddings.shape

# # filter embeddings to only include GO_terms
# GO_embeddings =embeddings.reindex(Graph_nodes["value"])
# GO_embeddings.head
# GO_embeddings.shape

# # Tried to get TSNE embeddings, but was getting an error that included NA values
# np.any(np.isnan(GO_embeddings))

# GO_embeddings = GO_embeddings.dropna()
# GO_embeddings.shape

# # subsetting for testing
# test_embeddings = GO_embeddings[:84347]
# test_embeddings.shape

# # umap embeddings
# reducer = umap.UMAP(n_components = 3)

# tracemalloc.start()
# umap = reducer.fit_transform(GO_embeddings)
# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
# tracemalloc.stop()

# umap = pd.DataFrame(umap)
# umap["source"] = "source.node"
# umap["target"] = "target.node"



# ##### clustering umap embeddings
# umap_emb = pd.read_csv("umap_embeddings.csv")

# model = DBSCAN(eps = .3, min_samples = 30)

# yhat = model.fit_predict(umap_emb)

