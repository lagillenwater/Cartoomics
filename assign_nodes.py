import pandas as pd
import re
import os
import math
import sys
import glob
import logging.config
from pythonjsonlogger import jsonlogger
import itertools

# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})

# set column number and width to display all information
pd.set_option('display.max_rows', None)



# Read in the user example file and output as a pandas dataframe
def read_user_input(user_example_file):
	try:
		examples = pd.read_csv(user_example_file, sep= "|")
		print(examples.columns)
	#Check for poorly formatted file
	except pd.errors.ParserError:
		print('Error in format of ' + user_example_file + ', ensure that only "source" and "target" columns exist in each row.')
		logging.error('Error in format of %s, ensure that only "source" and "target" columns exist in each row.',user_example_file)
		sys.exit(1)
	#Check for extra columns or blank values or absence of source/target columns
	if (len(examples.columns) != 2) | (examples.isna().values.any()) | (len([item for item in examples.columns if item not in ['source','target']]) > 0):
		print('Error in format of ' + user_example_file + ', ensure that only "source" and "target" columns exist in each row.')
		logging.error('Error in format of %s, ensure that only "source" and "target" columns exist in each row.',user_example_file)
		sys.exit(1)
	return(examples)

def read_ocr_input(user_input_file):
    df = pd.read_csv(user_input_file, sep = "\t")
    if "genes" in user_input_file:
        df = df.loc[df["organism_name"] == "Homo sapiens"]
    return(df)

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
	### Check for exact matches first
	exact_matches = nodes[(nodes["label"].str.lower() == node.lower())][["label", "entity_uri"]]

	### All caps input is probably a gene or protein. Either search in a case sensitive manner or assign to specific ontology.
	if node.isupper(): #likely a gene or protein
		results = nodes[(nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)) & nodes["entity_uri"].str.contains("gene|PR|GO",flags=re.IGNORECASE, na = False) ][["label", "entity_uri"]]
		#Remove exact matches from this df
		results = results[(~results.label.isin(exact_matches.label))]
	else:
		results = nodes[nodes["label"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["synonym"].str.contains(node,flags=re.IGNORECASE, na = False)|nodes["description/definition"].str.contains(node,flags=re.IGNORECASE, na = False)][["label", "entity_uri"]]
		#Remove exact matches from this df
		results = results[(~results.label.isin(exact_matches.label))]

        # sort results by ontology
	results = results.sort_values(['entity_uri'])

        #Concat both dfs so that exact matches are presented first
	all_results = pd.concat([exact_matches, results], axis=0)

	return(all_results)
                

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
	logging.info('Found %s features in KG',nrow)

	return found_nodes,nrow

def manage_user_input(found_nodes,user_input,kg):

	if node_in_search(found_nodes,user_input):
		#Manage if there are 2 duplicate label names
		if len(found_nodes[found_nodes['label'] == user_input][['label','entity_uri']]) > 1:
			dup_node = True
			logging.info('Duplicate label names found: %s',user_input)
			while(dup_node):
				user_id_input = input("Input node 'id': ")
				print(found_nodes[found_nodes['label'] == user_input]['entity_uri'].values.tolist())
				if user_id_input in found_nodes[found_nodes['label'] == user_input]['entity_uri'].values.tolist():
					node_label = kg.labels_all.loc[kg.labels_all['entity_uri'] == user_id_input,'label'].values[0]
					bad_input = False
					dup_node = False
					logging.info('ID chosen: %s',user_id_input)

				else:
					print("Input id does not correspond with selected label.... try again")
					logging.info('Input id does not correspond with selected label: %s',user_id_input)
				
		else:
			node_label = user_input
			bad_input = False
			dup_node = False

	elif node_in_labels(kg,user_input):
		node_label= user_input
		bad_input = False
	else:
		print("Input not in search results.... try again")
		logging.info('Input not in search results: %s',user_input)
		node_label = ""
		bad_input = True

	return node_label,bad_input

def search_nodes(nodes, kg, examples):
	examples["source_label"] = ""
	examples["target_label"] = ""

	vals_per_page = 20

	for node in nodes:
		logging.info('Searching for node: %s',node)
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
				logging.info('Input new node search term: %s.',node)
				examples = examples.replace(['REPLACE'],node)
				found_nodes,nrow = map_input_to_nodes(node,kg)
				i = 1
			else:
				node_label,bad_input = manage_user_input(found_nodes,user_input,kg)

		logging.info('Node label chosen for %s: %r',node,node_label)
		node_label
		examples.loc[examples["source"] == node,"source_label"] = node_label
		examples.loc[examples["target"] == node,"target_label"] = node_label
	
	logging.info('All input nodes searched.')
	
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
def create_input_file(examples,output_dir,input_type):
	input_file = output_dir+"/_" + input_type + "_Input_Nodes_.csv"
	logging.info('Input file created: %s',input_file)
	
	examples.to_csv(input_file, sep = "|", index = False)



# Check if the input_nodes file already exists
def check_input_existence(output_dir,input_type):
    exists = 'false'
    mapped_file = ''
    for fname in os.listdir(output_dir):
        if bool(re.match("/_" + input_type + "_Input_Nodes_",fname)):
            exists = 'true'
            mapped_file = fname
    return exists,mapped_file



# Wrapper function
def interactive_search_wrapper(g,user_input_file, output_dir, input_type):
	#Check for existence based on input type
	exists = check_input_existence(output_dir,input_type)
	if(exists[0] == 'false'):
            print('Interactive Node Search')
            logging.info('Interactive Node Search')
            #Interactively assign node
            if input_type == 'annotated_diagram':
                u = read_user_input(user_input_file[0])
                n = unique_nodes(u)
                s = search_nodes(n,g,u)
            if input_type == 'pathway_ocr':
                n = []
                for i in user_input_file:
                    ocr_frame = read_ocr_input(i)
                    nodes = unique_nodes(ocr_frame["word"].to_frame())
                    n.append(nodes)
                n = [item for items in n for item in items]
                u = pd.DataFrame(itertools.permutations(n,2))
                u = u.rename(columns = {0: "source", 1:"target"})
                print(u)
                s = search_nodes(n,g,u)
                        
            create_input_file(s,output_dir,input_type)
	else:
		print('Node mapping file exists... moving to embedding creation')
		logging.info('Node mapping file exists... moving to embedding creation')
		mapped_file = output_dir + '/'+ exists[1]
		s = pd.read_csv(mapped_file, sep = "|")
		logging.info('Node mapping file: %s',mapped_file)
	return(s)

                              
