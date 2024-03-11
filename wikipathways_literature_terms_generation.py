import os
import csv
import pandas as pd
import argparse
from assign_nodes import convert_to_uri,normalize_node_api,create_skipped_node_file
from graph_similarity_metrics import get_wikipathways_graph_files
from create_graph import create_graph

from constants import (
    PKL_SUBSTRINGS,
    PKL_OBO_URI,
    WIKIPATHWAYS_SUBFOLDER
)

#Generates unannotated file of terms from manually curated keywords
def generate_keywords_file(output_path,metadata_df,wikipathway):

    terms = metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,'Keywords'].values[0].split(';')

    df = pd.DataFrame(terms,columns=['term'])

    df.to_csv(output_path,index=False)

#Generates annotated file using concept annotations
def generate_abstract_file(pmid,all_wikipathways_dir,wikipathway,labels,enable_skipping):

    df = pd.DataFrame(columns = ['term','term_label','term_id'])
    wikipathway_output_dir = all_wikipathways_dir + "/" + wikipathway + "_output"
    df_file = wikipathway_output_dir + "/_literature_comparison_Input_Nodes_.csv"

    pmid_file = os.getcwd() + "/Wikipathways_Text_Annotation/Concept_Annotations/" + pmid + ".bionlp"
    pmid_df = pd.read_csv(pmid_file,header=None,sep='\t')
    pmid_df.columns = [['TermID','Term_Info','Label']]

    guiding_term_skipped_nodes = []

    for i in range(len(pmid_df)):
        annotated_terms = {}
        use_node = True
        
        curie = pmid_df.iloc[i].loc['Term_Info'].iloc[0].split(' ')[0]
        #Remove _CC, _BP from GO terms
        if "GO_" in curie:
            id = curie.split(":")[1]
            curie = "GO_" + id
        curie = curie.replace('_',":")
        #Transform to known ontogies if needed
        curie = normalize_node_api(curie)
        uri = convert_to_uri(curie)

        if enable_skipping:
            #Ensure that uri is in PheKnowLator
            try:
                label = labels.loc[labels['entity_uri'] == uri,'label'].values[0]
            except IndexError:
                guiding_term_skipped_nodes.append(pmid_df.iloc[i].loc['Label'].values[0])
                use_node = False

        if use_node:
            #Add term
            annotated_terms['term'] = pmid_df.iloc[i].loc['Label'].iloc[0]
            #Add term_label
            annotated_terms['term_label'] = pmid_df.iloc[i].loc['Label'].iloc[0]
            #Add term_id
            annotated_terms['term_id'] = uri
            d = pd.DataFrame([annotated_terms])
            df = pd.concat([d,df])

    #Creates a skipped_node file per input diagram
    if enable_skipping:
        create_skipped_node_file(guiding_term_skipped_nodes,wikipathway_output_dir,'guidingTerms')

    df = df.drop_duplicates()
    df.to_csv(df_file,sep='|',index=False)

def main():

    #Hardcoded for now to skip terms that are annotated but not in PheKnowLator
    enable_skipping = True

    metadata_file = os.getcwd() + "/Wikipathways_Text_Annotation/Wikipathways_MetaData.csv"

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(all_wikipathways_dir,'pkl','annotated_terms')

    g = create_graph(triples_list_file,labels_file, 'pkl')

    metadata_df = pd.read_csv(metadata_file,sep=',')
    wikipathways = metadata_df.Pathway_ID.unique()

    for wikipathway in wikipathways:

        base_dir = all_wikipathways_dir + '/literature_comparison'

        output_path = base_dir + '/' + wikipathway + '_Literature_Comparison_Terms.csv'

        #generate_keywords_file(output_path,metadata_df,wikipathway)

        pmid = str(metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,'PMID'].values[0])

        generate_abstract_file(pmid,all_wikipathways_dir,wikipathway,g.labels_all,enable_skipping)

if __name__ == '__main__':
    main()



