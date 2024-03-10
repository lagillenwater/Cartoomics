import os
import csv
import pandas as pd
import argparse
from assign_nodes import convert_to_uri,normalize_node_api

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
def generate_abstract_file(pmid,all_wikipathways_dir,wikipathway):

    df = pd.DataFrame(columns = ['term','term_label','term_id'])
    df_file = all_wikipathways_dir + "/" + wikipathway + "_output" + "/_literature_comparison_Input_Nodes_.csv"

    pmid_file = os.getcwd() + "/Wikipathways_Text_Annotation/Concept_Annotations/" + pmid + ".bionlp"
    pmid_df = pd.read_csv(pmid_file,header=None,sep='\t')
    pmid_df.columns = [['TermID','Term_Info','Label']]

    for i in range(len(pmid_df)):
        annotated_terms = {}
        #Add term
        annotated_terms['term'] = pmid_df.iloc[i].loc['Label']
        #Add term_label
        annotated_terms['term_label'] = pmid_df.iloc[i].loc['Label']
        #Add term_id
        curie = pmid_df.iloc[i].loc['Term_Info'].iloc[0].split(' ')[0]
        #Remove _CC, _BP from GO terms
        if "GO_" in curie:
            id = curie.split(":")[1]
            curie = "GO_" + id
        curie = curie.replace('_',":")
        #Transform to known ontogies if needed
        curie = normalize_node_api(curie)
        annotated_terms['term_id'] = convert_to_uri(curie)
        d = pd.DataFrame(annotated_terms)
        df = pd.concat([d,df])

    df = df.drop_duplicates()
    df.to_csv(df_file,sep='|',index=False)

def main():

    metadata_file = os.getcwd() + "/Wikipathways_Text_Annotation/Wikipathways_MetaData.csv"

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    metadata_df = pd.read_csv(metadata_file,sep=',')
    wikipathways = metadata_df.Pathway_ID.unique()

    for wikipathway in wikipathways:

        base_dir = all_wikipathways_dir + '/literature_comparison'

        output_path = base_dir + '/' + wikipathway + '_Literature_Comparison_Terms.csv'

        #generate_keywords_file(output_path,metadata_df,wikipathway)

        pmid = str(metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,'PMID'].values[0])

        generate_abstract_file(pmid,all_wikipathways_dir,wikipathway)

if __name__ == '__main__':
    main()



