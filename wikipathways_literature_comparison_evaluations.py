from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *
from create_subgraph import compare_subgraph_guiding_terms,get_wikipathways_subgraph
from graph_embeddings import Embeddings
from evaluation_plots_all import visualize_literature_comparison_boxplot,visualize_literature_comparison_scatterplot,visualize_literature_comparison_heatmap

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def main():

    #python wikipathways_literature_comparison_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP5283','WP4535','WP5358','WP5385','WP4829','WP4564','WP4565','WP4532','WP4534','WP4539','WP4562']" --enable-skipping True

    #python wikipathways_literature_comparison_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP5385','WP4760']" --enable-skipping True

    #python wikipathways_literature_comparison_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP5283','WP4535','WP5358','WP5385','WP4829','WP4564','WP4565','WP4532','WP4534','WP4539','WP4562','WP5283','WP4535','WP5358','WP5385','WP4829','WP4564','WP4565','WP4532','WP4534','WP4539','WP4562','WP4533','WP4542','WP4540','WP4541','WP4760','WP5373','WP4538','WP4553','WP4537','WP5382','WP5368','WP4856']" --enable-skipping True
    #removed ,'WP5372'

    '''kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    #List for all cosine sim values to each guiding term
    all_subgraphs_cosine_sim = []

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'
    
        print("Getting KG embeddings for Cosine Similarity......")

        e = Embeddings(triples_list_file,input_dir,embedding_dimensions,kg_type)
        emb,entity_map = e.generate_graph_embeddings(kg_type)

        print("Mapping between user inputs and KG nodes.......")
        
        comparison_terms_df = interactive_search_wrapper(g, labels_file, output_dir, 'literature_comparison', kg_type, enable_skipping, input_dir, wikipathway)

        s = pd.read_csv(output_dir + '/_annotated_diagram_Input_Nodes_.csv',sep='|')

        if cosine_similarity == 'true':

            subgraph_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph.csv',sep='|')

            all_subgraphs_cosine_sim = compare_subgraph_guiding_terms(s,subgraph_df,g,comparison_terms_df,kg_type,'CosineSimilarity',emb,entity_map,wikipathway,all_subgraphs_cosine_sim,'labels')

        if pdp == 'true':

            subgraph_df = pd.read_csv(output_dir + '/PDP/Subgraph.csv',sep='|')

            all_subgraphs_cosine_sim = compare_subgraph_guiding_terms(s,subgraph_df,g,comparison_terms_df,kg_type,'PDP',emb,entity_map,wikipathway,all_subgraphs_cosine_sim,'labels')

        #Get original wikipathways edgelist
        wikipathways_subgraph_df = get_wikipathways_subgraph(s)
        all_subgraphs_cosine_sim = compare_subgraph_guiding_terms(s,wikipathways_subgraph_df,g,comparison_terms_df,kg_type,'Original',emb,entity_map,wikipathway,all_subgraphs_cosine_sim,'uris')
        
    all_subgraphs_cosine_sim_df = output_literature_comparison_df(all_wikipathways_dir+'/literature_comparison',all_subgraphs_cosine_sim)'''

    all_subgraphs_cosine_sim_df = pd.read_csv('/Users/brooksantangelo/Documents/HunterLab/Cartoomics/git/Cartoomics/wikipathways_graphs/literature_comparison/Evaluation_Files/literature_comparison_evaluation.csv',sep=',')

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    visualize_literature_comparison_boxplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir)

    visualize_literature_comparison_scatterplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir)

    #Transform data to get average cosine similarity across all terms per Pathway and Algorithm
    term_averages_cosine_sim_df = all_subgraphs_cosine_sim_df.groupby(['Pathway_ID','Algorithm'],as_index=False).agg({'Average_Cosine_Similarity':'mean'})

    visualize_literature_comparison_heatmap(term_averages_cosine_sim_df,all_wikipathways_dir)


if __name__ == '__main__':
    main()