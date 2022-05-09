# cartoomics_utils is a file of utility functions
import pandas as pd
import numpy as np
import pickle
import time
import networkx as nx
import re



#### load in the COVID-19 knowledge graph, obtained from https://kg-hub.berkeleybop.io/kg-covid-19/current/kg-covid-19.tar.gz
#### COVID 19 knowledge graph, edges and node metadata
def graphFromEdgelist(edgelist_file):
	start = time.time()
	print("Reading in edgelist...")
	edges = pd.read_table(edgelist_file)
	print("Complete.")
	end = time.time()
	print("Total time: ", end-start)
	return(edges)


# Loading the COVID-19 knowledge graph from a pickle to save time (2X as fast as TSV)
def edgelistFromPickle(edgelist_file ):
	start = time.time()
	print("Reading in edgelist...")
	edges = pd.read_pickle(edgelist_file)
	print("Complete.")
	end = time.time()
	print("Total time: ", end-start)
	return(edges)

# Convert edgelist to multi-digraph
#di = nx.from_pandas_edgelist(edgelist,"subject", "object", "predicate", create_using=nx.MultiDiGraph())
#with open("../data/multi_di_graph.pkl", 'wb') as f:
#  	pickle.dump(di,f)


# Loading in the COVID-19 multiDigraph to save time -- Didn't really save time in the loading, but does in the reformatting.
def graphFromPickle(KG_pkl):
	start = time.time()
	print("Reading in networkx graph...")
	with open(KG_pkl, 'rb') as f:
 		graph = pickle.load(f)
	print("Complete.")
	end = time.time()
	print("Total time: ", end-start)
	return(graph)


# Read in the node metadata
def parseNodeData(node_tsv):
	print("Reading in node metadata file...")
	start = time.time()
	nodes = pd.read_table(node_tsv)
	print("Complete.")
	end = time.time()
	print("Total time: ", end-start)
	return(nodes)


# search for nodes with mathching labels in the graph
# Needs a node list and the nodes that it contains

def findNode(node_name, nodes, ontology = ""):
	if ontology == "":
		print(nodes[nodes["name"].str.contains(node_name,flags=re.IGNORECASE, na = False)|nodes["description"].str.contains(node_name,flags=re.IGNORECASE, na = False)][["id","name", "description"]])
	else:
		print(nodes[(nodes["name"].str.contains(node_name,flags=re.IGNORECASE, na = False)|nodes["description"].str.contains(node_name,flags=re.IGNORECASE, na = False)) & nodes["id"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["id","name", "description"]])



# Search for path between two nodes using the various types of search algorithms. 

def findPath(graph, source, target, search_type = "simple", cutoff = 3, power = .5):
	if search_type == "simple":
		return(nx.all_simple_paths(graph, source, target, cutoff = 3))
	elif search_type == "shortest":
		return(nx.all_shortest_paths(graph, source, target))
	elif search_type == "PDP":
		return(nx.all_shortest_paths(graph, source, target, weight = lambda u,v,d: pow(graph.degree(u),-power) * pow(graph.degree(v),-power)))



# Create an output for cytoscape from the subpaths
def toSIF(subgraph, nodes):
	edgelist = nx.to_pandas_edgelist(subgraph)
	edgelist["source_label"] = [nodes.loc[nodes["id"] ==i]["name"].values[0] for i in edgelist["source"]]
	edgelist["target_label"] = [nodes.loc[nodes["id"] ==i]["name"].values[0] for i in edgelist["target"]]
	edgelist = edgelist[["source_label", "predicate", "target_label"]]
	edgelist = edgelist.rename(columns = {"source_label": "source", "target_label": "target"})
	return(edgelist)

# create node attribute file for cytoscape
def toNOA(subpaths, nodes, input_nodes):
	noa = nodes[nodes["id"].isin(subpaths)][["id","name"]]
	noa["input"] = np.where(noa["id"].isin(input_nodes),1,0)
	noa = noa[["name", "input"]]
	return(noa)