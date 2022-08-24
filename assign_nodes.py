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
	nodes = list(set(pd.melt(examples)["value"].values))
	return(nodes)

# Search through labels to find nodes based on input feature
# Inputs: 	node 		string for user input example.
#			kg			knowledge graph of class Knowledge Graph
#			ontology	specific ontology to restrict search of nodes

def find_node(node, kg, ontology = ""):
	nodes = kg.labels_all
	### All caps input is probably a gene or protein. Either search in a case sensitive manner or assign to specific ontology. 


	if ontology == "":
		if node.isupper(): #likely a gene or protein
			results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains("gene|PR|GO",flags=re.IGNORECASE, na = False) ][["integer_id","label", "description/definition"]]
		else:
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
		print("Found", nrow, "features in KG")
		user_input = ""
		bad_input = True
		if nrow < 20:
			while(bad_input):
				print(found_nodes.iloc[0:nrow,])
				user_input = input("Input node integer_id: ")
				try:
					user_input = int(user_input)
				except ValueError:
					print("Input not an input_id.... try again")
				else:
					if node_in_search(found_nodes,user_input):
						print("Input is an input_id")
						node_label = found_nodes[found_nodes["integer_id"] == user_input]["label"].item()
						bad_input = False
					else:
						print("Input not an input_id.... try again")
		else:	
			i = 0
			while(bad_input):
				high = min(nrow,(i+1)*20)
				print(found_nodes.iloc[i*20:high,])
				user_input = input("Input node integer_id or 'f' for the next 20 features or 'b' for the previous 20: ")
				try:
					user_input = int(user_input)
				except:
					if user_input == 'f':
						i+=1
					elif user_input == 'b':
						i-=1
					else:
						i+=1
				else:
					if node_in_search(found_nodes,user_input):
						print("Input is an input_id")
						node_label = found_nodes[found_nodes["integer_id"] == user_input]["label"].item()
						bad_input = False
					else:
						print("Input not an input_id.... try again")
		examples.loc[examples["source"] == node,"source_label"] = node_label
		examples.loc[examples["target"] == node,"target_label"] = node_label
	return(examples)


# Check if search input is in the list of integer_ids
def node_in_search(found_nodes, user_input):
	if user_input in list(found_nodes["integer_id"]):
		return(True)
	else:
		return(False)

#subgraph_df is a dataframe with source,targe headers and | delimited
def create_input_file(examples,output_dir):
    input_file = output_dir+"/_Input_Nodes_.csv"
    examples = examples[["source_label","target_label"]]
    examples.columns = ["source", "target"]
    examples.to_csv(input_file, sep = "|", index = False)


