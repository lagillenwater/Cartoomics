import pandas as pd
import re
import os
import math
import sys

# set column number and width to display all information
pd.set_option('display.max_rows', None)



# Read in the user example file and output as a pandas dataframe
def read_user_input(user_example_file):
	try:
		examples = pd.read_csv(user_example_file, sep= "|")
	#Check for poorly formatted file
	except pd.errors.ParserError:
		print('Error in format of ' + user_example_file + ', ensure that only "source" and "target" columns exist in each row.')
		sys.exit(1)
	#Check for extra columns or blank vlaues
	if (len(examples.columns) > 2) | (examples.isna().values.any()):
		print('Error in format of ' + user_example_file + ', ensure that only "source" and "target" columns exist in each row.')
		sys.exit(1)
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
    if node.isupper(): #likely a gene or protein
        results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains("gene|PR|GO",flags=re.IGNORECASE, na = False) ][["label", "entity_uri"]]
    else:
        results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["label", "entity_uri"]]

    return(results)
                

# Create a list of nodes for input

# Could potentially find several features for a single input example. Need a way to be able to select multiple feaures for a search. 
# Need a way to go back through search terms. 

def map_input_to_nodes(node,kg):

	search_loop = True
	while(search_loop):
		print("User Search Node: ", node)
		found_nodes = find_node(node,kg)
		nrow = found_nodes.shape[0]
		if nrow == 0:
			print("No search terms returned")
			node = input("Please try another input term: ")
		else:
			search_loop = False	
	print("Found", nrow, "features in KG")

	return found_nodes,nrow

def manage_user_input(found_nodes,user_input,kg):

	if node_in_search(found_nodes,user_input):
		
		#Manage if there are 2 duplicate label names
		if len(found_nodes[found_nodes['label'] == user_input][['label','entity_uri']]) > 1:
			dup_node = True
			while(dup_node):
				user_id_input = input("Input node 'id': ")
				print(found_nodes[found_nodes['label'] == user_input]['entity_uri'].values.tolist())
				if user_id_input in found_nodes[found_nodes['label'] == user_input]['entity_uri'].values.tolist():
					node_label = kg.labels_all.loc[kg.labels_all['entity_uri'] == user_id_input,'label'].values[0]
					bad_input = False
					dup_node = False

				else:
					print("Input id does not correspond with selected label.... try again")
				
		else:
			node_label = user_input
			bad_input = False
			dup_node = False

	elif node_in_labels(kg,user_input):
		node_label= user_input
		bad_input = False
	else:
		print("Input not in search results.... try again")
		node_label = ""
		bad_input = True

	return node_label,bad_input

def search_nodes(nodes, kg, examples):
	examples["source_label"] = ""
	examples["target_label"] = ""

	vals_per_page = 20

	for node in nodes:
		bad_input = True
		found_nodes,nrow = map_input_to_nodes(node,kg)
		i = 1
		while(bad_input):
			high = min(nrow,(i)*vals_per_page)
			print(found_nodes.iloc[(i-1)*vals_per_page:high,].to_string())
			user_input = input("Input node 'label' or 'f' for the next " + str(vals_per_page) + " features, 'b' for the previous " + str(vals_per_page) + ", or 'u' to update the node search term: ")
			if user_input == 'f':
				if (nrow / i ) > vals_per_page:
					i+=1
			elif user_input == 'b':
				if i > 1:
					i-=1
			elif user_input == 'u':
				#Will replace the original node label in examples file with new one
				examples = examples.replace([node],'REPLACE')
				node = input("Input new node search term: ")
				examples = examples.replace(['REPLACE'],node)
				found_nodes,nrow = map_input_to_nodes(node,kg)
				i = 1
			else:
				node_label,bad_input = manage_user_input(found_nodes,user_input,kg)

		examples.loc[examples["source"] == node,"source_label"] = node_label
		examples.loc[examples["target"] == node,"target_label"] = node_label
	return(examples)


# Check if search input is in the list of integer_ids
def node_in_search(found_nodes, user_input):
	if user_input in found_nodes[["label"]].values:
		return(True)
	else:
		return(False)

# Check if search input is in the list of integer_ids
def node_id_in_search(found_nodes, user_input):
	if user_input in found_nodes[["entity_uri"]].values:
		return(True)
	else:
		return(False)

# Check if search input is in the all nodes
def node_in_labels(kg, user_input):
	labels = kg.labels_all

	if user_input in labels[["label"]].values:
		return(True)
	else:
		return(False)

#subgraph_df is a dataframe with source,targe headers and | delimited
def create_input_file(examples,output_dir):
    input_file = output_dir+"/_Input_Nodes_.csv"
    #examples = examples[["source_label","target_label"]]
    #examples.columns = ["source", "target"]
    examples.to_csv(input_file, sep = "|", index = False)



# Check if the input_nodes file already exists
def check_input_existence(output_dir):
    exists = 'false'
    mapped_file = ''
    for fname in os.listdir(output_dir):
        if bool(re.match("_Input_Nodes_",fname)):
            exists = 'true'
            mapped_file = fname
    return exists,mapped_file



# Wrapper function
def interactive_search_wrapper(g,user_input_file, output_dir):
    exists = check_input_existence(output_dir)
    if(exists[0] == 'false'):
        print('Interactive Node Search')
        #Interactively assign node
        u = read_user_input(user_input_file)
        n = unique_nodes(u)
        s = search_nodes(n,g,u)
        create_input_file(s,output_dir)
    else:
        print('Node mapping file exists... moving to embedding creation')
        mapped_file = output_dir + '/'+ exists[1]
        s = pd.read_csv(mapped_file, sep = "|")
    return(s)

                              
