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
	### All caps input is probably a gene or protein. Either search in a case sensitive manner or assign to specific ontology. 


	if ontology == "":
		results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["integer_id","label","entity_uri", "description/definition"]]
	else:
		results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["integer_id","label", "description/definition"]]
	return(results)

# Create a list of nodes for input

# Could potentially find several features for a single input example. Need a way to be able to select multiple feaures for a search. 
# Need a way to go back through search terms. 

def search_nodes(nodes, kg, examples):
	examples["source_label"] = ""
	examples["target_label"] = ""
	for node in nodes:
		print("User Search Node: ", node)
		found_nodes = find_node(node,kg)
		
		nrow = found_nodes.shape[0]
		if nrow < 20:
			print(found_nodes.iloc[0:nrow,])
			user_input = input("Input node integer_id: ")
		else:
			user_input = ""
			bad_input = True
			i = 0
			while(bad_input):
				high = min(nrow,(i+1)*20)
				print(found_nodes.iloc[i*20:high,])
				user_input = input("Input node integer_id or hit enter for the next 20 features: ")

				if user_input in list(found_nodes["integer_id"]):
					print("found it")
					bad_input = False
				elif user_input == int(user_input):
					print("integer_id not found. Try again.")
				else:
					print("Next 20")
					i+=1


		# examples["source" == node]["source_label"] = node_label
		# examples["target" == node]["target_label"] = node_label

	return(examples)

	

# Map list 



