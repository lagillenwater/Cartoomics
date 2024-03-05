from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

#python evaluation_plots_all.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP5283','WP4535','WP5358','WP5385','WP4829','WP4564','WP4565','WP4532','WP4534','WP4539','WP4562']" --enable-skipping True


def read_edge_type_file(all_dfs,output_dir):

    edge_type_comparison_file = output_dir + '/Evaluation_Files/edge_type_comparison.csv'

    df = pd.read_csv(edge_type_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs

def read_ontology_type_file(all_dfs,output_dir):

    intermediate_nodes_comparison_file = output_dir + '/Evaluation_Files/intermediate_nodes_comparison.csv'

    df = pd.read_csv(intermediate_nodes_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs

#Generates histogram with N number of categories by pathway, where lists are the input
def edge_type_comparison(output_dir,df):

    df = pd.melt(df, id_vars='Edge_Type', value_vars=['cs', 'pdp'],var_name='Algorithm',value_name='Value')

    plt_file = output_dir + '/edge_type_comparison.png'
    sns_plot = sns.barplot(df, x='Edge_Type', y = 'Value',hue='Algorithm',errorbar=None).set_title("Edge Type Comparison for all Wikipathway Diagrams")
    plt.legend(title='Algorithm', loc='upper right', labels=['Cosine Similarity', 'Path-Degree Product'])
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def intermediate_nodes_comparison(output_dir,df):

    df = pd.melt(df, id_vars='Ontology_Type', value_vars=['cs', 'pdp'],var_name='Algorithm',value_name='Value')

    plt_file = output_dir + '/intermediate_nodes_comparison.png'
    sns_plot = sns.barplot(df, x='Ontology_Type', y = 'Value',hue='Algorithm',errorbar=None).set_title("Ontology Type Comparison for all Wikipathway Diagrams")
    plt.legend(title='Algorithm', loc='upper right', labels=['Cosine Similarity', 'Path-Degree Product'])
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def main():

    #python wikipathways_converter.py --knowledge-graph pkl --input-type annotated_diagram --pfocr-urls-file True --enable-skipping True

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    '''triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)'''

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    all_edge_type_dfs = pd.DataFrame(columns = ['Edge_Type','cs','pdp'])

    all_ontology_type_dfs = pd.DataFrame(columns = ['Ontology_Type','cs','pdp'])

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'

        all_edge_type_dfs = read_edge_type_file(all_edge_type_dfs,output_dir)

        all_ontology_type_dfs = read_ontology_type_file(all_ontology_type_dfs,output_dir)

        #all_dfs = pd.merge(all_dfs, df, on='Edge_Type')

        
    edge_type_comparison(all_wikipathways_dir,all_edge_type_dfs)

    intermediate_nodes_comparison(all_wikipathways_dir,all_ontology_type_dfs)

if __name__ == '__main__':
    main()        

