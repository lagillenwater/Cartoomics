import pandas as pd
import re

# set column number and width to display all information
pd.set_option('display.max_rows', None)

# Read in the user example file and output as a pandas dataframe
def read_user_input(user_example_file):
	examples = pd.read_csv(user_example_file, sep= "|")
	return(examples)

# Get list of unique nodes
# Inputs:	examples		pandas dataframe of user input examples.
# Outputs:	nodes 			set of unique nodes
def unique_nodes(examples):
	# get unique node values
	nodes = set(pd.melt(examples)["value"].values)
	return(nodes)

# Search through labels to find nodes based on input feature
# Inputs: 	node 		string for user input example.
#			kg			knowledge graph of class Knowledge Graph
#			ontology	specific ontology to restrict search of nodes

def find_node(node, kg, ontology = ""):
	nodes = kg.labels_all

	if ontology == "":
		results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["integer_id","label","entity_uri", "description/definition"]]
	else:
		results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["integer_id","label", "description/definition"]]
	return(results)

# Create a list of nodes for input
def search_nodes(nodes, kg):
	user_nodes = []
	for node in nodes:
		print("User Search Node: ", node)
		found_nodes = find_node(node,kg)
		
		nrow = found_nodes.shape[0]
		if nrow < 20:
			print(found_nodes.iloc[0:20,])
			user_input = input("Input node integer_id: ")
		else:
			n = range(0, nrow, 20)
			user_input = ""
			i = 0
			while(type(user_input) != int):
				print(found_nodes.iloc[n[i]:n[i+1],])
				user_input = input("Input node integer_id or hit enter for the next 20 features: ")
				try:
					user_input = int(user_input)
				except ValueError:
					i+=1
		user_nodes.append(user_input)
	return(user_nodes)

