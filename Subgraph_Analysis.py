from collections import defaultdict
import os
import re
import duckdb
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

from visualize_subgraph import output_visualization
from sklearn.feature_extraction.text import TfidfTransformer,TfidfVectorizer

def duckdb_load_table(con, file, table_name, columns):
    """Create a duckDB tables for any given graph."""
    columns_str = ", ".join(columns)

    # Read the subset file into a DuckDB table
    query = (
        f"""
    CREATE OR REPLACE TABLE {table_name} AS
    SELECT {columns_str}
    FROM read_csv_auto('{file}', delim='\t');
    """
    )

    # print(query)
    con.execute(query)

def drop_table(con, table_name):

    query = (
        f"""
        DROP TABLE "{table_name}";
        """
    )

    # print(query)
    con.execute(query)

def create_subject_object_pair_table(con, table_name, base_table_name, subject, object, subject_prefix, predicate_prefix, object_prefix):

    query = (
        f"""
        CREATE TEMPORARY TABLE "{table_name}" AS
        SELECT DISTINCT subject AS "{subject}", predicate, object AS "{object}"
        FROM "{base_table_name}"
        WHERE subject LIKE '{subject_prefix}' AND predicate LIKE '{predicate_prefix}' AND object LIKE '{object_prefix}';
        """
    )

    # print(query)
    con.execute(query).fetchone()

    return table_name

def get_ecs(conn, input_dir, relevant_subgraph_files, output_filename):

    if not os.path.exists(output_filename):
        ec_df = pd.DataFrame(columns = ["Subgraph_Filename", "UniprotKB", "EC"])

        for filename in relevant_subgraph_files:
            file_path = os.path.join(input_dir, filename)

            df = pd.read_csv(file_path, sep = "|")
            uniprot = df[df['O_ID'].str.contains("UniprotKB:", na=False)]["O_ID"].values[0]
            p = "biolink:enables"
            o = "EC:"
            new_table_name = create_subject_object_pair_table(
                conn,
                table_name = "_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)]),
                base_table_name = "edges",
                subject = re.sub(r'[/_]', '', uniprot),
                object = re.sub(r'[/_]', '', o),
                subject_prefix = "%" + uniprot + "%",
                predicate_prefix = "%" + p + "%",
                object_prefix = "%" + o + "%"
            )

            query = (
                f"""
                SELECT * FROM '{"_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)])}';
                """
            )

            result = conn.execute(query).fetchall()
            if len(result) == 0:
                ec = "none"
            else:
                ec = result[0][-1]

            drop_table(conn, "_".join([re.sub(r'[/_]', '', uniprot),re.sub(r'[/_]', '', o)]))

            new_data = {
                "Subgraph_Filename" : filename,
                "UniprotKB" : uniprot,
                "EC" : ec
            }
            new_row = pd.DataFrame([new_data])
            # Concatenate to the main DataFrame
            ec_df = pd.concat([ec_df, new_row], ignore_index=True)

        ec_df.to_csv(output_filename, sep = "|")
    else:
        ec_df = pd.read_csv(output_filename, delimiter="|")

def get_metabolites_and_protein_names(input_dir, relevant_subgraph_files, output_filename):

    metab_df = pd.DataFrame(columns = ["Subgraph_Filename", "UniprotKB", "Metabolite"])

    for filename in relevant_subgraph_files:
        file_path = os.path.join(input_dir, filename)

        df = pd.read_csv(file_path, sep = "|")
        uniprot = df[df['O_ID'].str.contains("UniprotKB:", na=False)]["O"].values[0].strip()
        metabolite = df[df['O_ID'].str.contains("CHEBI:", na=False)]["O"].values[0].strip()
        new_data = {
            "Subgraph_Filename" : filename,
            "UniprotKB" : uniprot,
            "Metabolite" : metabolite
        }
        new_row = pd.DataFrame([new_data])
        # Concatenate to the main DataFrame
        metab_df = pd.concat([metab_df, new_row], ignore_index=True)

    metab_df.to_csv(output_filename, sep = "|")

    return metab_df

def visualize_counts(df, col_of_interest, filename, output_dir):

    # Plot histogram
    # plt.hist(df[col_of_interest], bins=len(df[col_of_interest].unique().tolist()), color='skyblue', edgecolor='black')
    
    # Count occurrences of each unique value
    value_counts = df[col_of_interest].value_counts()

    # Sort the values by frequency in descending order
    sorted_values = value_counts.index.tolist()

    # Sort the column data based on the sorted unique values
    sorted_col = df[col_of_interest].astype('category')
    sorted_col = sorted_col.cat.set_categories(sorted_values, ordered=True)
    sorted_col = sorted_col.sort_values()

    # Plot the histogram
    # plt.hist(sorted_col, bins=len(sorted_values), color='skyblue', edgecolor='black')
    sns.histplot(
        sorted_col,
        bins=len(sorted_values),
        color='blue',
        edgecolor='black',
        kde=False,  # Set to True if you want to show the kernel density estimate
        alpha=0.8  # Slightly transparent bars
    )


    plt.xlabel(col_of_interest)
    plt.ylabel("Count")
    plt.title("Total Unique " + col_of_interest + "s Among All Paths (75)")
    plt.xticks(rotation=75, fontsize = 7)
    plt.subplots_adjust(bottom=0.3)

    plt.tight_layout()
    plt.savefig('./' + output_dir + '/' + col_of_interest + '_' + filename + '_counts_histogram.png', format='png', dpi=300)
    plt.close()

def get_nonredundant_proteome_subgraphs(input_dir):

    uniprot_rhea_chemical_combos = defaultdict(list)
    for filename in os.listdir(input_dir):
        if ("Subgraph_" not in filename) or ("all_subgraphs_combined" in filename) or (".csv" not in filename): continue
        file_path = input_dir + "/" + filename

        df = pd.read_csv(file_path, sep = "|")
        uniprot_name = df[df['O_ID'].str.contains("UniprotKB:", na=False)]["O"].values[0].strip()
        reaction = df[df['O_ID'].str.contains("RHEA:", na=False)]["O_ID"].values[0].strip()
        chemical = df[df['O_ID'].str.contains("CHEBI:", na=False)]["O_ID"].values[0].strip()

        uniprot_rhea_chemical = uniprot_name + "_" + reaction + "_" + chemical
        uniprot_rhea_chemical_combos[uniprot_rhea_chemical].append(filename)

    uniprot_rhea_chemical_combos_used = {k: v for k, v in uniprot_rhea_chemical_combos.items() if len(v) <= 1}
    # Extract values as a flat list
    nonredundant_subgraphs = [item for sublist in uniprot_rhea_chemical_combos_used.values() for item in sublist]

    return nonredundant_subgraphs

def concatenate_all_paths(subgraph_dir):

    combined_df = pd.DataFrame()
    paths_list = []

    # Iterate through files dynamically based on the pattern "Subgraph_*.csv"
    for filename in os.listdir(subgraph_dir):
        if filename.startswith("Subgraph_") and filename.endswith(".csv") and "all_subgraphs_combined" not in filename:
            filepath = os.path.join(subgraph_dir, filename)
            # Read the CSV file
            df = pd.read_csv(filepath, sep = "|")
            
            # Check if S, P, and O columns exist in the current file
            if set(['S', 'P', 'O']).issubset(df.columns):
                subset_df = df[['S', 'P', 'O']]
                # Extract the S, P, and O columns and append to the combined DataFrame
                combined_df = pd.concat([combined_df, subset_df], ignore_index=True)

                # Create a single ordered list of terms by concatenating rows
                path = []
                subset_no_predicate_df = df[['S_ID', 'O_ID']]
                for _, row in subset_no_predicate_df.iterrows():
                    path.extend(row.tolist())
                paths_list.append(path)
            else:
                print(f"Warning: File '{filename}' does not contain all required columns (S, P, O).")

    combined_df.drop_duplicates(inplace=True)
    combined_df.to_csv(subgraph_dir + "/all_subgraphs_combined.csv", index=False)
    return combined_df, paths_list

def get_node_label(con, node_id):

    query = (
        f"""
        SELECT name 
        FROM nodes 
        WHERE id = '{node_id}';
        """
    ) 

    # print(query)
    try:
        result = con.execute(query).fetchone()[0]
    except TypeError:
        return node_id

    return result

def get_important_terms(paths_list, nodes_file, source, target):

    tfIdfVectorizer=TfidfVectorizer(use_idf=True,lowercase=False)

    exclude_nodes = [source, target]

    # For IDs
    processed_results = [
        " ".join(dict.fromkeys(term.replace(":","_") for term in sublist if term not in exclude_nodes))
        for sublist in paths_list
    ]
    # For labels
    # exclude_strings = {"bilophila_wadsworthia_3_1_6", "parkinson_disease"}

    # Process paths_list while excluding the specific strings
    # processed_results = [
    #     " ".join(
    #         dict.fromkeys(
    #             term.strip().replace(" ", "_").replace('=','_').replace('+','_').replace('(','').replace(')','').replace('-','_')
    #             for term in sublist
    #             if term.strip().replace(" ", "_").replace('=','_').replace('+','_').replace('(','').replace(')','').replace('-','_').lower() not in exclude_strings
    #         )
    #     )
    #     for sublist in paths_list
    # ]

    conn = duckdb.connect(":memory:")
    duckdb_load_table(conn, nodes_file, "nodes", ["id", "name"])

    tfIdf = tfIdfVectorizer.fit_transform(processed_results)

    df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names_out(), columns=["TF-IDF"]).reset_index()

    # Rename the column that was the index
    df.rename(columns={"index": "Term"}, inplace=True)

    df = df.sort_values('TF-IDF', ascending=False)

    df['Term'] = df['Term'].apply(lambda x: get_node_label(conn, x.replace("_",":")))

def get_source_target_node(subgraph_dir):

    for filename in os.listdir(subgraph_dir):
        if filename.startswith("Subgraph_") and filename.endswith(".csv") and "all_subgraphs_combined" not in filename:
            filepath = os.path.join(subgraph_dir, filename)
            # Read the CSV file
            df = pd.read_csv(filepath, sep = "|")
            
            source_node = df.iloc[0].loc['S_ID']
            target_node = df.iloc[-1].loc['O_ID']

            return source_node, target_node

def main():

    input_dir = "kg-microbe/kg-microbe"
    # triples_list_file = input_dir + "/merged-kg_edges.tsv"
    # nodes_file = input_dir + "/merged-kg_nodes.tsv"
    triples_list_file = "/Users/brooksantangelo/Documents/Repositories/kg-microbe-paper/src/Input_Files/kg-microbe-biomedical-function-cat/merged-kg_edges_Uniprot_EC.tsv"
    nodes_file = "/Users/brooksantangelo/Documents/Repositories/kg-microbe-paper/src/Input_Files/kg-microbe-biomedical-function-cat/merged-kg_nodes.tsv"

    subgraph_dir = "kg-microbe/outputs/Metapath_nersc"
    ec_filepath = subgraph_dir + "/EC_Uniprot_pairs.csv"

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")
    conn.execute("PRAGMA memory_limit='64GB'")

    duckdb_load_table(conn, triples_list_file, "edges", ["subject", "predicate", "object"])

    # For all subgraphs
    relevant_subgraph_files = [filename for filename in os.listdir(subgraph_dir) if "Subgraph_" in filename and "all_subgraphs_combined" not in filename and ".csv" in filename]
    get_ecs(conn, subgraph_dir, relevant_subgraph_files, ec_filepath)
    metab_df = get_metabolites_and_protein_names(subgraph_dir, relevant_subgraph_files, subgraph_dir + "/Metabolite_Uniprot_Label_pairs.csv")

    visualize_counts(metab_df, "Metabolite", "All_Subgraphs", subgraph_dir)
    visualize_counts(metab_df, "UniprotKB", "All_Subgraphs", subgraph_dir)

    # For filtered subgraphs
    nonredundant_proteomes_subgraph_files = get_nonredundant_proteome_subgraphs(subgraph_dir)

    get_ecs(conn, subgraph_dir, nonredundant_proteomes_subgraph_files, ec_filepath)
    metab_df = get_metabolites_and_protein_names(subgraph_dir, nonredundant_proteomes_subgraph_files, subgraph_dir + "/Metabolite_NonRedundant_Proteomes_counts_histogram.csv")

    visualize_counts(metab_df, "Metabolite", "NonRedundant_Proteomes", subgraph_dir)
    visualize_counts(metab_df, "UniprotKB", "NonRedundant_Proteomes", subgraph_dir)

    combined_df, paths_list = concatenate_all_paths(subgraph_dir)

    source_node, target_node = get_source_target_node(subgraph_dir)

    get_important_terms(paths_list, nodes_file, source_node, target_node)

    # cs_noa_df = output_visualization(combined_df,combined_df,subgraph_dir,"all_subgraphs_combined")


if __name__ == '__main__':
    main()
