from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from create_subgraph import  subgraph_prioritized_path_guiding_term
from create_subgraph import user_defined_edge_exclusion
from graph_similarity_metrics import *
from assign_nodes import normalize_node_api,convert_to_uri,get_label
from find_path import get_uri
from create_subgraph import get_wikipathways_subgraph
from evaluation import output_idf_metrics
from wikipathways_converter import get_wikipathways_list
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def process_idf_file(file,labels,kg_type):

    cols = ['idf','curie']

    df = pd.read_csv(file,sep=',',header=None, names=cols)

    df['uri'] = 'none'
    df['label'] = 'none'
    for i in range(len(df)):
        curie = df.iloc[i].loc['curie']
        #Transform to known ontogies if needed
        curie = normalize_node_api(curie)
        uri = convert_to_uri(curie)
        df.iloc[i].loc['uri'] = uri
        df.iloc[i].loc['label'] = get_label(labels,uri,kg_type)

    return df

def get_subgraph_idf(subgraphs_idf_metrics,labels,kg_type,subgraph_df,idf_df,wikipathway,algorithm):

    #Structure of subgraphs_idf_metrics: Pathway_ID,Algorithm,Node,IDF

    unique_nodes = list(subgraph_df.S.unique()) + list(subgraph_df.O.unique())

    for node in unique_nodes:
        node_uri = get_uri(labels,node,kg_type)
        idf = idf_df.loc[idf_df['uri'] == node_uri,'idf'].values[0]
        subgraphs_idf_metrics.append([wikipathway,algorithm,node,idf])

    return subgraphs_idf_metrics

def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    idf_file = os.getcwd() + "/Wikipathways_Text_Annotation/concept_idf.sorted.csv"

    idf_df = process_idf_file(idf_file,g.labels_all,kg_type)

    #List for all idf metrics
    subgraphs_idf_metrics = []

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'
        
        if cosine_similarity == 'true':

            subgraph_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph.csv',sep='|')

            subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,subgraph_df,idf_df,wikipathway,'CosineSimilarity')

        if pdp == 'true':

            subgraph_df = pd.read_csv(output_dir + '/PDP/Subgraph.csv',sep='|')

            subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,subgraph_df,idf_df,wikipathway,'PDP')

        #Get original wikipathways edgelist
        wikipathways_subgraph_df = get_wikipathways_subgraph(s)

        subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,wikipathways_subgraph_df,idf_df,wikipathway,'original')

        #Output files and visualization for edge and node type evaluations
        idf_file = output_idf_metrics(all_wikipathways_dir,subgraphs_idf_metrics)


if __name__ == '__main__':
    main()