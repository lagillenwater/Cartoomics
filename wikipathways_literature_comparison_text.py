from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *
from create_subgraph import compare_subgraph_guiding_terms,get_wikipathways_subgraph
from graph_embeddings import Embeddings
from evaluation_plots_all import visualize_literature_comparison_boxplot_all_pathways,visualize_literature_comparison_scatterplot_all_pathways,visualize_literature_comparison_heatmap_all_pathways
from biomed_RoBERTa import get_embeddings, get_cosine_similarity
from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    ALL_WIKIPATHWAYS,
    LITERATURE_SEARCH_TYPES,
    WIKIPATHWAYS_SUBFOLDER
)

from collections import defaultdict
from transformers import RobertaTokenizer, RobertaModel



def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    #Gets literature comparison terms for many pathways 
    all_pathways_comparisons = {key: {} for key in LITERATURE_SEARCH_TYPES}
    for w in wikipathways:
        for search_type in LITERATURE_SEARCH_TYPES:
            #w_comparison_file = all_wikipathways_dir + "/literature_comparison/" + w + "_literature_comparison_Input_Nodes_.csv"
            w_comparison_file = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER + "/literature_comparison/" + search_type + "/" + w + "_literature_comparison_Input_Nodes_.csv"
            if os.path.exists(w_comparison_file):
                w_comparison_df = pd.read_csv(w_comparison_file, sep = "|")
                #Remove duplicates and unassigned IDs from literature comparison files
                w_comparison_df = w_comparison_df.loc[w_comparison_df['term_id'] != 'none']
                w_comparison_df.drop_duplicates(subset=['term_id'], inplace=True)
                all_pathways_comparisons[search_type][w] = w_comparison_df



                
    # Initialize tokenizer and model
    tokenizer = RobertaTokenizer.from_pretrained('allenai/biomed_roberta_base')
    model = RobertaModel.from_pretrained('allenai/biomed_roberta_base')

    if  pdp == "true" and cosine_similarity=="true":
        algorithms = ["PDP","CosineSimilarity", "Original"]
    elif pdp == "true" and cosine_similarity == "false":
        algorithms = ["PDP", "Original"]
    else:
        algorithms = ["CosineSimilarity", "Original"]


    for search_type in LITERATURE_SEARCH_TYPES:    

        literature_evaluation_comparison = []
        # dict for all text embeddings to ensure that we do not repeat embedding lookup
        text_embeddings = dict()

        # dict for all cosine similarities to avoid recalculating
        cosine_similarities = dict()

        for algorithm in algorithms:

            ner_terms_all_pathways = []
        
            ## Text embeddings for every term in the NER data
            for wikipathway in tqdm(wikipathways):
            
                ner_terms = all_pathways_comparisons[search_type][wikipathway]["term"]
                text_keys = text_embeddings.keys()
        
                for term in ner_terms:
                    ner_terms_all_pathways.append(term)
                    if term not in text_keys:
                        text_embeddings[term] = [get_embeddings(model, tokenizer, term),wikipathway]

            for wikipathway in tqdm(wikipathways):

                if algorithm == "Original":
                    output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'
                    s = pd.read_csv(output_dir + '/_annotated_diagram_Input_Nodes_.csv',sep='|')
                    node_labels = unique_nodes(s[['source','target']])
                elif algorithm == "PDP":
                    output_dir = all_wikipathways_dir + '/' + wikipathway + '_output/PDP'
                    s = pd.read_csv(output_dir + '/Subgraph.csv',sep='|')
                    node_labels = unique_nodes(s[['S','O']])
                elif algorithm == "CosineSimilarity":
                    output_dir = all_wikipathways_dir + '/' + wikipathway + '_output/CosineSimilarity'
                    s = pd.read_csv(output_dir + '/Subgraph.csv',sep='|')
                    node_labels = unique_nodes(s[['S','O']])
                    
                text_keys = text_embeddings.keys()
        
                for node in node_labels:
                    if node not in text_keys:
                        text_embeddings[node] = [get_embeddings(model, tokenizer, node),wikipathway]

                        for term in ner_terms_all_pathways:
                            combined = node + "-" + term
                            path_embedding = text_embeddings[node]
                            ner_embedding = text_embeddings[term]
                            if combined not in cosine_similarities.keys():
                                cosine_similarities[combined] = get_cosine_similarity(path_embedding[0],ner_embedding[0])
                    
                            literature_evaluation_comparison.append([node, term,  cosine_similarities[combined], path_embedding[1], ner_embedding[1], algorithm])

        literature_evaluation_comparison = pd.DataFrame(literature_evaluation_comparison, columns = ['Pathway_Term' , 'NER_Term', 'Cosine_Similarity','Pathway_ID','NER_ID', 'Algorithm'])

        print(literature_evaluation_comparison.shape)
        

        output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'

            #Check for existence of output directory
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
                
        literature_evaluation_comparison.to_csv(output_folder+'/literature_comparison_evaluation_TEXT_' + search_type + '.csv',sep=',',index=False)
        logging.info('Create literature comparison evaluation file: %s',output_folder+'/literature_comparison_evaluation_TEXT_' + search_type + '.csv')


        #     if cosine_similarity == 'true':

        #         subgraph_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph.csv',sep='|')

        #         all_subgraphs_cosine_sim,llm_embeddings = compare_subgraph_guiding_terms(s,subgraph_df,g,all_pathways_comparisons[search_type],kg_type,embeddings,'CosineSimilarity',emb,entity_map,wikipathway,all_subgraphs_cosine_sim,'uris')

        #     #Get original wikipathways edgelist
        # #     wikipathways_subgraph_df = get_wikipathways_subgraph(s)

        # # all_subgraphs_cosine_sim_df = output_literature_comparison_df(all_wikipathways_dir+'/literature_comparison',all_subgraphs_cosine_sim,search_type)
        
        # #Get relative cosine similarity to other pathways
        # all_subgraphs_zscore_df = compare_literature_terms_across_pathways(all_subgraphs_cosine_sim_df)



if __name__ == '__main__':
    main()
