from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)


'''def read_edge_type_file(all_dfs,output_dir):

    edge_type_comparison_file = output_dir + '/Evaluation_Files/edge_type_comparison.csv'

    df = pd.read_csv(edge_type_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs'''

'''def read_ontology_type_file(all_dfs,output_dir):

    intermediate_nodes_comparison_file = output_dir + '/Evaluation_Files/intermediate_nodes_comparison.csv'

    df = pd.read_csv(intermediate_nodes_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs'''

#Generates histogram with N number of categories by pathway, where lists are the input
def edge_type_comparison_visualization(output_dir,df):

    algorithm_labels = df.Algorithm.unique()

    output_folder = output_dir+'/node_edge_evaluation'

    #df = pd.melt(df, id_vars='Edge_Type', value_vars=algorithm_labels,var_name='Algorithm',value_name='Value')

    plt_file = output_folder + '/edge_type_comparison.png'
    sns_plot = sns.barplot(df, x='Edge_Type', y = 'Percent_Edges',hue='Algorithm',errorbar=None).set_title("Edge Type Comparison for all Wikipathway Diagrams")
    plt.legend(title='Algorithm', loc='upper right', labels=algorithm_labels)
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def intermediate_nodes_comparison_visualization(output_dir,df):

    algorithm_labels = df.Algorithm.unique()

    output_folder = output_dir+'/node_edge_evaluation'

    #df = pd.melt(df, id_vars='Ontology_Type', value_vars=algorithm_labels,var_name='Algorithm',value_name='Value')

    plt_file = output_folder + '/intermediate_nodes_comparison.png'
    sns_plot = sns.barplot(df, x='Ontology_Type', y = 'Percent_Nodes',hue='Algorithm',errorbar=None).set_title("Ontology Type Comparison for all Wikipathway Diagrams")
    plt.legend(title='Algorithm', loc='upper right', labels=algorithm_labels)
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

#Generates histogram with N number of categories by pathway, where lists are the input
def visualize_graph_similarity_metrics(results_file,all_wikipathways_dir):
    
    results_df = pd.read_csv(results_file,sep=',')
    algorithms = results_df.Algorithm.unique()

    for algorithm in algorithms:

        df = results_df.loc[results_df['Algorithm'] == algorithm]

        plt_file = all_wikipathways_dir + '/graph_similarity/' + algorithm + '_Graph_Similarity_Metrics_Jaccard_Overlap.png'
        sns_plot = sns.barplot(df, x='Pathway_ID', y = 'Score',hue='Metric',errorbar=None).set_title("Graph Similarity Metrics for Wikipathways Diagrams and "+ algorithm)
        plt.legend(title='Metrics', loc='upper right', labels=['Jaccard', 'Overlap'])
        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)

