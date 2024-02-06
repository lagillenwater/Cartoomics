



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import argparse
import glob
import logging.config
from pythonjsonlogger import jsonlogger


# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})

def define_graphsim_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ## Required inputs
    parser.add_argument("--cosine-similarity",dest="CosineSimilarity",required=False,default='true',help="Search for paths using Cosine Similarity.",type = str)

    parser.add_argument("--pdp",dest="PDP",required=False,default='true',help="Search for paths using PDP.",type = str)
    
    parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,help="Search for paths using Guiding Term specified.",type = str)

    parser.add_argument("--wikipathway-diagrams",dest="wikipathway_diagrams",required=True,help="List of wikipathway diagrams to evaluate, example input '['WP554','WP5373']'")

    return(parser)

# Wrapper function
def generate_graphsim_arguments():

    #Generate argument parser and define arguments
    parser = define_graphsim_arguments()
    args = parser.parse_args()
    cosine_similarity = args.CosineSimilarity
    pdp = args.PDP
    guiding_term = args.GuidingTerm
    wikipathway_diagrams = args.wikipathway_diagrams

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    if cosine_similarity not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    if pdp not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    return cosine_similarity,pdp,guiding_term,wikipathway_diagrams

#Creates igraph object and a list of nodes
def create_igraph_graph(edgelist_df,edgelist_type):

    #Edgelist generation for subgraphs produced with cartoomics
    if edgelist_type == 'subgraph':
        edgelist_df = edgelist_df[['S','O','P']]
        #Remove gene descriptions in parentheses such as " (human)"
        edgelist_df['S'] = edgelist_df['S'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()
        edgelist_df['O'] = edgelist_df['O'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()

        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    #Edgelist generation for wikipathways diagrams
    if edgelist_type == 'wikipathways':
        edgelist_df = edgelist_df[['Source',  'Target', 'edgeID']]
        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    g_nodes = g.vs()['name']

    return g 

#Networkx graph format is necessary for graph edit distance calculation
def create_networkx_graph(edgelist_df,edgelist_type):

    if edgelist_type == 'subgraph':
        edgelist_df = edgelist_df[['S','O','P']]
        #Remove gene descriptions in parentheses such as (human)
        edgelist_df['S'] = edgelist_df['S'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()
        edgelist_df['O'] = edgelist_df['O'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()

        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    if edgelist_type == 'wikipathways':
        edgelist_df = edgelist_df[['Source',  'Target', 'edgeID']]
        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})


    g = nx.from_pandas_edgelist(edgelist_df, 'S', 'O')

    return g

def jaccard_sim(g1,g2):

    g_intersection = intersection([g1,g2],keep_all_vertices=False)
    g_union = union([g1,g2])

    j = g_intersection.vcount() / g_union.vcount()

    return j

def overlap_sim(g1,g2):

    g_intersection = intersection([g1,g2], keep_all_vertices=False)
    g_min = min([g1.vcount(),g2.vcount()])

    o = g_intersection.vcount() / g_min

    return o

def compare_wikipathways_subgraphs(wikipathway_diagrams,subgraph_type):

    all_subgraph_types = []
    pathways = []
    jaccard = []
    overlap = []
    edit = []
    for p in wikipathway_diagrams:

        w_file = os.getcwd() + '/wikipathways_graphs/' + p + '/' + p + '_edgeList.csv'
        w_dir = os.getcwd() + '/wikipathways_graphs'

        #Subgraph type must be CosineSimilarity, PDP, or GuidingTerm_<specified_term> to match current output structure
        w_subgraph_file = os.getcwd() + '/wikipathways_graphs/' + p + '_output/' + subgraph_type + '/Subgraph.csv'


        df_1 = pd.read_csv(w_file,sep=',')
        df_2 = pd.read_csv(w_subgraph_file,sep='|')

        g_1 = create_igraph_graph(df_1,'wikipathways')
        g_2 = create_igraph_graph(df_2,'subgraph')

        j = jaccard_sim(g_1,g_2)

        o = overlap_sim(g_1,g_2)

        #Calculate graph edit distance, which requires networkx graph
        g_1 = create_networkx_graph(df_1,'wikipathways')
        g_2 = create_networkx_graph(df_2,'subgraph')

        e = nx.graph_edit_distance(g_1,g_2) 

        all_subgraph_types.append(subgraph_type)
        pathways.append(p)
        jaccard.append(j)
        overlap.append(o)
        edit.append(e)

    results_df = pd.DataFrame(columns=['SubgraphType','Pathway','Jaccard','Overlap','Edit Distance'])
    results_df['SubgraphType'] = all_subgraph_types
    results_df['Pathway'] = pathways
    results_df['Jaccard'] = jaccard
    results_df['Overlap'] = overlap
    results_df['Edit Distance'] = edit

    results_file = os.getcwd() + '/wikipathways_graphs/'+'Graph_Similarity_Metrics.csv'
    results_df.to_csv(results_file,sep=',',index=False)
    logging.info('Created graph similarity metrics csv file: %s',results_file)

    return results_df,w_dir

#Generates histogram with N number of categories by pathway, where lists are the input
def visualize_graph_metrics(df,w_dir,subgraph_type):
    
    ax = df.plot(x="Pathway", y=['Jaccard','Overlap'], kind="bar", rot=0)
    plt.title("Graph Similarity Metrics for Wikipathways Diagrams and "+ subgraph_type,fontsize = 18)
    plt_file = w_dir + '/' + subgraph_type + '_Graph_Similarity_Metrics_Jaccard_Overlap.png'
    plt.savefig(plt_file)

    logging.info('Created png: %s',plt_file)

    ax = df.plot(x="Pathway", y=['Edit Distance'], kind="bar", rot=0)
    plt.title("Graph Similarity Metrics for Wikipathways Diagrams and "+ subgraph_type,fontsize = 18)
    plt_file = w_dir + '/' + subgraph_type + '_Graph_Similarity_Metrics_Edit_Distance.png'
    plt.savefig(plt_file)

    logging.info('Created png: %s',plt_file)

