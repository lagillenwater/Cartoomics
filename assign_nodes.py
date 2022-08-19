import pandas as pd

# Read in the user example file and output as a pandas dataframe
def read_user_input(user_example_file):
	examples = pd.read_csv(user_example_file)
	return(examples)

# Map the nodes to a dictionary
def map_nodes(examples):
	nodes = pd.melt(examples)
	return(nodes)

# Search through graph to find nodes based on input features
def find_node(node_name, nodes, ontology = ""):
	if ontology == "":
		print(nodes[nodes["name"].str.contains(node_name,flags=re.IGNORECASE, na = False)|nodes["description"].str.contains(node_name,flags=re.IGNORECASE, na = False)][["id","name", "description"]])
	else:
		print(nodes[(nodes["name"].str.contains(node_name,flags=re.IGNORECASE, na = False)|nodes["description"].str.contains(node_name,flags=re.IGNORECASE, na = False)) & nodes["id"].str.contains(ontology,flags=re.IGNORECASE, na = False) ][["id","name", "description"]])




