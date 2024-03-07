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

#Generates boxplot of each 
def visualize_literature_comparison_boxplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir):

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'
    algorithms = all_subgraphs_cosine_sim_df.Algorithm.unique()

    plt_file = output_folder + '/Literature_Comparison_all_terms_boxplot.png'
    sns_plot = sns.boxplot(data=all_subgraphs_cosine_sim_df, x='Pathway_ID', y = 'Average_Cosine_Similarity',hue='Algorithm').set_title("Cosine Similarity of subgraph to All Associated Literature Terms")
    sns.stripplot(data=all_subgraphs_cosine_sim_df, x="Pathway_ID", y="Average_Cosine_Similarity",
              hue="Algorithm", hue_order=algorithms, dodge=True)
    plt.legend(title='Average_Cosine_Similarity', loc='upper right', labels=algorithms)
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def visualize_literature_comparison_scatterplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir):

    terms = all_subgraphs_cosine_sim_df.Term.unique()
    pathways = all_subgraphs_cosine_sim_df.Pathway_ID.unique()

    for pathway in pathways:

        df = all_subgraphs_cosine_sim_df.loc[all_subgraphs_cosine_sim_df['Pathway_ID'] == pathway]

        plt_file = all_wikipathways_dir + '/' + pathway + '_output/Evaluation_Files/Literature_Comparison_all_terms_scatterplot.png'
        sns_plot = sns.scatterplot(data=all_subgraphs_cosine_sim_df, x='Algorithm', y = 'Average_Cosine_Similarity',hue='Term').set_title("Cosine Similarity of " + pathway + " Subgraph to All Associated Literature Terms")
        plt.legend(title='Term', loc='upper right', labels=terms)
        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)



