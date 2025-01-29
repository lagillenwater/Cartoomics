import os
import tarfile
import duckdb
import pandas as pd
import requests

from Subgraph_Analysis import get_node_label
from duckdb_utils import duckdb_load_table
from find_path import convert_to_labels


def import_edges_nodes_files(input_dir, filename, url):

    input_tar_file = input_dir + "/" + filename + ".tar.gz"
    extracted_dir = input_dir + "/" + filename

    if not os.path.exists(extracted_dir):

        try:
            # Send a GET request to the URL
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an error for HTTP errors

            # Save the file locally
            with open(input_tar_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download file: {e}")

        if not os.path.exists(extracted_dir):
            os.makedirs(extracted_dir)
        with tarfile.open(input_tar_file, 'r') as tar:
            tar.extractall(path=extracted_dir)

    edges_df = pd.read_csv(extracted_dir + "/edges.tsv", sep="\t")
    nodes_df = pd.read_csv(extracted_dir + "/nodes.tsv", sep="\t")

    return edges_df

def convert_source_targets(conn, edges_df, input_dir, filename):

    edges_df_labels = pd.DataFrame()
    for i in range(len(edges_df[1:])):
        s = get_node_label(conn, edges_df.iloc[i].loc["subject"])
        # print(edges_df.iloc[i].loc["subject"], s)
        o = get_node_label(conn, edges_df.iloc[i].loc["object"])
        # print(edges_df.iloc[i].loc["object"], o)
        new_row = {
            "source" : s,
            "target" : o
        }
        edges_df_labels = pd.concat([edges_df_labels, pd.DataFrame([new_row])], ignore_index=True)

    edges_df_labels.to_csv(input_dir + "/" + filename + "_example_input.csv", sep="|", index=False)

    return edges_df_labels

def create_txt_file(df, input_dir, filename):

    txt_filename = input_dir + "/" + filename + "_microbes.txt"

    all_microbes = df["subject"].unique().tolist()
    
    with open(txt_filename, "w") as f:
        # Write each item in the list to the file, followed by a newline
        for line in all_microbes:
            f.write(line + "\n")


def main():

    nodes_file = "/Users/brooksantangelo/Documents/Repositories/kg-microbe-paper/src/Input_Files/kg-microbe-biomedical-function-cat/merged-kg_nodes.tsv"
    input_dir = "kg-microbe/experimental_data"

    wallen_etal_filename = "wallen_etal"
    wallen_etal_url = "https://github.com/Knowledge-Graph-Hub/kg-microbe/releases/download/2024-09-28/wallen_etal.tar.gz"

    # Create a DuckDB connection
    conn = duckdb.connect(":memory:")
    conn.execute("PRAGMA memory_limit='64GB'")

    duckdb_load_table(conn, nodes_file, "nodes", ["id", "name"])

    edges_df = import_edges_nodes_files(input_dir, wallen_etal_filename, wallen_etal_url)
    edges_df_labels = convert_source_targets(conn, edges_df, input_dir, wallen_etal_filename)

    create_txt_file(edges_df, input_dir, wallen_etal_filename)

if __name__ == '__main__':
    main()

