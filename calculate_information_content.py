
import os

import subprocess
import pandas as pd

from assign_nodes import convert_to_uri


def compute_information_content(ontology,information_content_dir):

    filename = information_content_dir + "/" + ontology + ".csv"

    if not os.path.exists(filename):
        lowercase_ontology = ontology.lower()

        # Run the command and capture its output
        print('running oak for ',ontology)
        command = "runoak -i sqlite:obo:" + lowercase_ontology + " information-content -p i i^" + ontology + ":"
        output = subprocess.check_output(command, shell=True, text=True)

        # Split the output into lines
        lines = output.strip().split('\n')

        # Initialize an empty list to store rows of data
        data = []

        # Parse each line and extract term ID and information content
        for line in lines[1:]:
            term_id, info_content = line.split('\t')
            data.append({'Term ID': term_id, 'Information Content': float(info_content)})

        # Output for ontology
        df = pd.DataFrame(data)
        uri_df = pd.DataFrame(columns=df.columns)
        # Convert all curies to uri
        uri_df["Term ID"] = df["Term ID"].apply(
            lambda x: convert_to_uri(x)
        )
        uri_df["Information Content"] = df["Information Content"].values

        uri_df.to_csv(filename,sep=',',index=False)
    
    else:
        uri_df = pd.read_csv(filename,sep = ',')

    return uri_df

def filter_terms_using_information_content(df,ontology,threshold,information_content_dir):

    filename = information_content_dir + "/" + ontology + "_excluded" + ".csv"

    if ontology == "SO":
        threshold = 1.0

    # Exclude the bottom X% of 'Term ID's based on 'Information Content' according to threshold
    #term_ids_to_exclude_df = (df.sort_values(by='Information Content', ascending=True)
    #        .head(int(len(df) * threshold)))
    # Calculate the range of values in the 'Information Content' column
    information_content_range = df['Information Content'].max() - df['Information Content'].min()
    # Calculate the threshold based on the range of values
    threshold_value = df['Information Content'].min() + threshold * information_content_range
    # Filter the DataFrame to get all rows with 'Information Content' less than or equal to the threshold
    term_ids_to_exclude_df = df[df['Information Content'] <= threshold_value]
    
    term_ids_to_exclude_df.to_csv(filename,sep = ',',index=False)
    term_ids_to_exclude = term_ids_to_exclude_df['Term ID'].tolist()
    
    return term_ids_to_exclude

def drop_low_information_content_nodes(exclusion_nodes,ontology,output_dir,threshold):

    information_content_dir = output_dir + "/information_content"
    # Create directory
    os.makedirs(information_content_dir, exist_ok=True)

    df = compute_information_content(ontology,information_content_dir)
    ontology_exclude_nodes = filter_terms_using_information_content(df,ontology,threshold,information_content_dir)
    exclusion_nodes.extend(ontology_exclude_nodes)

    return exclusion_nodes
