from collections import defaultdict
import os
import re
import duckdb
import pandas as pd
import requests

from assign_nodes import get_label
from constants import ALL_WIKIPATHWAYS, LITERATURE_SEARCH_TYPES, METAPATH_SEARCH_MAPS, NODE_NORMALIZER_URL, WIKIPATHWAYS_SUBFOLDER
from create_graph import create_graph
from duckdb_utils import create_subject_object_pair_table, drop_table, duckdb_load_table, join_tables_subject_object
from graph_similarity_metrics import get_wikipathways_graph_files
from wikipathways_literature_terms_generation import generate_abstract_file_concept_annotations
import matplotlib.pyplot as plt
import seaborn as sns

wikipathway = "WP5372"


# def extract_names_from_ids(file_path, ids):

#     names = {}
#     current_id = None
#     current_name = None

#     with open(file_path, ‘r’) as file:
#         for line in file:
#             line = line.strip()
#             if line.startswith(“id:“):
#                 current_id = line.split(“: “)[1]
#             elif line.startswith(“synonym:“) and “PRO-short-label” in line:
#                 current_name = line.split(“: “)[1]
#                 if current_id in ids:
#                     names[current_id] = current_name.split(‘“’)[1]
#             elif line == “[Term]“:
#                 current_id = None
#                 current_name = None
#     return list(names.values())

# def get_uniprot_id(protein_name):
#     url = “https://rest.uniprot.org/uniprotkb/search”
#     params = {
#         “query”: f’gene_exact:“{protein_name}“’,
#         “format”: “json”,
#         “fields”: “accession,id,gene_names”
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         data = response.json()
#         if data[‘results’]:
#             # Return the first result’s UniProt ID
#             return data[‘results’][0][‘primaryAccession’]
#         else:
#             return “No results found”
#     else:
#         return f”Error: {response.status_code}”

# def uniprot_from_names(names):

#     results = [get_uniprot_id(name) for name in names]
#     return results

def convert_proteins_to_genes(conn,base_table_name,protein_uri,labels,kg_type):

    query = (
        f"""
        WITH subclass_relations AS (
        SELECT subject AS human_protein, object AS protein
        FROM {base_table_name}
        WHERE predicate LIKE '%rdf-schema#subClassOf%'
        AND object LIKE '%{protein_uri}%'
        AND subject LIKE '%PR_%'
        ),
        gene_template_relations AS (
            SELECT subject AS gene, object AS human_protein
            FROM {base_table_name}
            WHERE predicate LIKE '%RO_0002205%'
            AND subject LIKE '%gene%'
            AND object LIKE '%PR_%'
        )
        SELECT gene_template_relations.human_protein, gene_template_relations.gene
        FROM subclass_relations
        JOIN gene_template_relations
        ON subclass_relations.human_protein = gene_template_relations.human_protein;
        """
    )

    print(query)
    result = conn.execute(query).fetchall()

    result_list = [list(t) for t in result]
    for r in result_list:
        s = r[0]
        o = r[1]
        s_label = get_label(labels,s,kg_type)
        o_label = get_label(labels,o,kg_type)
        r[0] = s_label
        r[1] = o_label

    human_protein = result[0][0]
    return human_protein

    # print(query)
    # conn.execute(query)

    # result = conn.execute(
    #     f"""
    #     SELECT "gene","PR" FROM gene_match;
    #     """
    # ).fetchall()

    # Replace IDs with labels so that they can later on be matched to final mechanism to ensure Extra/Original nodes are labeled
    # result_list = [list(t) for t in result]
    # for r in result_list:
    #     s = r[0]
    #     o = r[1]
    #     s_label = get_label(labels,s,kg_type)
    #     o_label = get_label(labels,o,kg_type)
    #     r[0] = s_label
    #     r[1] = o_label

    # # ct = get_table_count(conn, "gene_match")
    # result_df = pd.DataFrame(result_list, columns = ["Original","New"])
    # id_key_df = pd.concat([id_key_df, result_df], ignore_index=True)
    # gene = result[0][0]

    # drop_table(conn, "gene_match")

    # return gene,id_key_df

# #Takes cure in the form PREFIX:ID
# def normalize_node_api_proteins(node_curie):

# 	url = NODE_NORMALIZER_URL + node_curie

# 	# Make the HTTP request to NodeNormalizer
# 	response = requests.get(url, timeout=30)
# 	response.raise_for_status()

# 	# Write response to file if it contains data
# 	entries = response.json()[node_curie]
# 	try:
# 		if len(entries) > 1: #.strip().split("\n")
# 			for iden in entries['equivalent_identifiers']:
# 				if iden['identifier'].split(':')[0] == "PR:":
# 					norm_node = iden['identifier']
# 					return norm_node
# 	#Handle case where node normalizer returns nothing
# 	except TypeError:
# 		return node_curie
	
# 	else:
# 		return node_curie

def main():

#Hardcoded for now to skip terms that are annotated but not in PheKnowLator
    enable_skipping = True

    metadata_file = os.getcwd() + "/Wikipathways_Text_Annotation/Wikipathways_MetaData.csv"

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(all_wikipathways_dir,'pkl','annotated_terms')

    g = create_graph(triples_list_file,labels_file, 'pkl')

    metadata_df = pd.read_csv(metadata_file,sep=',')
    # Using external list of wikipathways instead
    # wikipathways = metadata_df.Pathway_ID.unique()

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])
    id_keys_df = pd.DataFrame(columns = ["Original","New"])


    #Files to read
    gpt4_file = os.getcwd() + "/Wikipathways_Text_Annotation/pfocr_abstracts_GPT4.csv"
    ner_file = os.getcwd() + "/Wikipathways_Text_Annotation/pfocr_abstracts_NER_processed.csv"

    for wikipathway in ["WP5372"]: #ALL_WIKIPATHWAYS:

        for search_type in ["full_text"]:#LITERATURE_SEARCH_TYPES:

            # Search by ID, PMID for abstracts, PMC for full text
            if search_type == "abstract":
                search_id = "PMID"
            elif search_type == "full_text":
                # PMC3514635 missing
                search_id = "PMC"
            
            id = str(metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,search_id].values[0])
            if id == "nan": continue
            #File to read
            id_file = os.getcwd() + "/Wikipathways_Text_Annotation/Concept_Annotations_" + search_type + "/" + id + ".bionlp"

            base_dir = all_wikipathways_dir + '/literature_comparison/' + search_type
            wikipathway_output_dir = all_wikipathways_dir + "/" + wikipathway + "_output/"
            wikipathway_specific_dir = wikipathway_output_dir + search_type

            # Create directories
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(wikipathway_specific_dir, exist_ok=True)


            #output_path = base_dir + '/' + wikipathway + '_Literature_Comparison_Terms.csv'

            #generate_keywords_file(output_path,metadata_df,wikipathway)

            #For Hunter Lab concept annotations
            literature_annotations_df,guiding_term_skipped_nodes = generate_abstract_file_concept_annotations(id_file,g.labels_all,enable_skipping)

            unique_text_nodes = literature_annotations_df["term_id"].unique().tolist()
            unique_text_nodes_updated = []

            # Convert text annotations to relevant proteins from Uniprot
            for p in unique_text_nodes:
                if "PR_" in p:
                    # gene = convert_proteins_to_genes(conn,"edges",p,id_keys_df,g.labels_all,"pkl")
                    # new_protein = normalize_node_api_proteins(gene)
                    new_protein = convert_proteins_to_genes(conn,"edges",p,g.labels_all,'pkl')
                    unique_text_nodes_updated.append(new_protein)
                else:
                     unique_text_nodes_updated.append(p)

            # # Read in terms from new subgraph
            # metapath_subgraph_file = wikipathway_output_dir + "/CosineSimilarity_Metapath_Neighbors/subgraph.csv"
            # metapath_subgraph = pd.read_csv(metapath_subgraph_file,sep="|")
            # unique_subgraph_nodes = pd.concat([metapath_subgraph["S_ID"], metapath_subgraph["O_ID"]]).unique().tolist()

            # Read in terms from original subgraph
            s = pd.read_csv(wikipathway_output_dir + '/_annotated_diagram_Input_Nodes_.csv',sep='|')
            unique_original_subgraph_nodes = list(set(s['source_id'].unique().tolist() + s['target_id'].unique().tolist()))

            # Read in terms from all metapath search files
            evaluation_files_folder = wikipathway_output_dir + "Evaluation_Files"
            unique_metapath_dict = {}
            all_cs_values = []

            # Loop through all files in the folder
            for filename in os.listdir(evaluation_files_folder):
                # Check if the file contains "_substring"
                if "paths_list_CosineSimilarity_Metapath_Neighbors" in filename:
                    # Full file path
                    file_path = os.path.join(evaluation_files_folder, filename)
                    # Read the file into a pandas DataFrame
                    df = pd.read_csv(file_path,sep="|")
                    # Get values from columns 'Entity_1' and 'Entity_3' pairs, average them 
                    # df_dict = df.set_index('Value')['Object'].to_dict()
                    try:
                        df_entity_pairs_mean = df.groupby(['Entity_1', 'Entity_3'])['Value'].mean()
                        unique_metapath_dict.update(df_entity_pairs_mean)
                        # Add all values to running list for histogram
                        all_cs_values.extend(df['Value'].tolist())
                    except KeyError:
                        continue

            overlapping_subgraph_nodes = list(set(unique_original_subgraph_nodes) & set(unique_metapath_dict.values()))
            # Get all unique target nodes for comparison in histogram
            unique_target_text_values = list({t[-1] for t in unique_metapath_dict.keys()})
            overlapping_text_nodes = list(set(unique_text_nodes_updated) & set(unique_target_text_values))
            
            # Find the cs value for each overlapping text node
            overlapping_text_nodes_values = defaultdict(list)
            for (entity_1, entity_3), value in unique_metapath_dict.items():
                if entity_3 in overlapping_text_nodes:
                    overlapping_text_nodes_values[entity_3].append(value)
            overlapping_text_nodes_averages =[sum(values) / len(values) for values in overlapping_text_nodes_values.values()]


            # Build histogram of scores
            sns.kdeplot(all_cs_values, fill=True, color='g', alpha=0.5)
            # Add red lines at specified values
            for value in overlapping_text_nodes_averages:
                plt.axvline(x=value, color='r', linestyle='--')
            plt.xlabel('Protein Score')
            plt.ylabel('Density')
            plt.title('Target Protein Scores')
            plt.show()
            # Translate general proteins into Reactome/Uniprot ones
            # Take average of all target nodes paths per source node 
            # Call out overlapping_text_nodes and their associated score (average of the sum)
            import pdb;pdb.set_trace()

if __name__ == '__main__':
    main()
