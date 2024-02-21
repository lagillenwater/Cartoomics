



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import argparse
import glob
import logging.config
from pythonjsonlogger import jsonlogger
from inputs import *

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
    parser.add_argument("--knowledge-graph",dest="KG",required=True,help="Knowledge Graph: either 'pkl' for PheKnowLator or 'kg-covid19' for KG-Covid19")

    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = False)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")

    parser.add_argument("--input-type",dest="InputType",required=True,help="InputType: either 'annotated_diagram','pathway_ocr', or 'experimental_data'")

    parser.add_argument("--pfocr_url",dest="PfocrURL",required=False, help="The URL for the PFOCR annotated figure (example, 'https://pfocr.wikipathways.org/figures/PMC5095497__IMM-149-423-g007.html'")

    parser.add_argument("--cosine-similarity",dest="CosineSimilarity",required=False,default='true',help="Search for paths using Cosine Similarity.",type = str)

    parser.add_argument("--pdp",dest="PDP",required=False,default='true',help="Search for paths using PDP.",type = str)
    
    parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,default=False,help="Search for paths using Guiding Term(s).",type = bool)

    parser.add_argument("--input-substring",dest="InputSubstring",required=False,default='none',help="Substring to use in example_input.")
    
    ###CHECK THIS ONE
    #parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,help="Search for paths using Guiding Term specified.",type = str)

    ## Required inputs for wikipathways diagrams
    parser.add_argument("--wikipathways",dest="Wikipathways",required=False,help="List of Wikipathways IDs (example input: '['WP5372']'), there is no default")
    
    parser.add_argument("--pfocr_urls",dest="PfocrUrls",required=False,help="List of pfocr urls (e.g., '['https://pfocr.wikipathways.org/figures/PMC6943888__40035_2019_179_Fig1_HTML.html']'), there is no default")
    
    parser.add_argument("--pfocr-urls-file",dest="PfocrUrlsFile",required=False,default=False,help="Specifies existance of file with list of pfocr urls",type=bool)

    parser.add_argument("--enable-skipping",dest="EnableSkipping",required=False,default=False,help="Enables option to skip nodes when exact match or synonym is not found.",type=bool)

    return(parser)

# Wrapper function
def generate_graphsim_arguments():

    #Generate argument parser and define arguments
    parser = define_graphsim_arguments()
    args = parser.parse_args()
    kg_type = args.KG
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight
    input_type = args.InputType
    cosine_similarity = args.CosineSimilarity
    pdp = args.PDP
    guiding_term = args.GuidingTerm
    input_substring = args.InputSubstring

    wikipathways = args.Wikipathways
    pfocr_urls = args.PfocrUrls
    pfocr_urls_file = args.PfocrUrlsFile
    enable_skipping = args.EnableSkipping

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    if cosine_similarity not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    if pdp not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    return kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping

#Same as get_graph_files except does not get input example file, done later, and no pfocr_url or experimental dataset is possible
def get_wikipathways_graph_files(input_dir,kg_type,input_type, guiding_term = False, input_substring = 'none'):

    #Search for annotated diagram input
    # if input_type == 'annotated_diagram':
    #     folder = input_dir+'/annotated_diagram'
    #     if not os.path.isdir(folder):
    #         raise Exception('Missing folder input directory: ' + folder)
    #         logging.error('Missing folder input directory: ' + folder)
        
    # #Check for existence of guiding_terms file only
    # if guiding_term:
    #     guiding_term_file = input_dir + '/Guiding_Terms.csv'
    #     if not os.path.isfile(guiding_term_file):
    #         raise Exception('Missing file in input directory: ' + guiding_term_file)
    #         logging.error('Missing file in input directory: ' + guiding_term_file)

    if kg_type == "pkl":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.exists(kg_dir):
            os.mkdir(kg_dir)
        if len(os.listdir(kg_dir)) < 2:
            download_pkl(kg_dir)


        existence_dict = {
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':'false',
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':'false',
        }
        
        
        for k in list(existence_dict.keys()):
            for fname in os.listdir(kg_dir):
                if k in fname:
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':
                        labels_file = input_dir + '/' + kg_type + '/' + fname
                    existence_dict[k] = 'true'
    
    if kg_type == "kg-covid19":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.exists(kg_dir):
            os.mkdir(kg_dir)
        if len(os.listdir(kg_dir)) < 2:
            download_kg19(kg_dir)
        
        existence_dict = {
            'merged-kg_edges.':'false',
            'merged-kg_nodes.':'false'
        }


        for k in list(existence_dict.keys()):
            for fname in os.listdir(kg_dir):
                if k in fname:
                    if k == 'merged-kg_edges.':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'merged-kg_nodes.':
                        labels_file = input_dir + '/' + kg_type + '/' + fname 
                    existence_dict[k] = 'true'

    #Check for existence of all necessary files, error if not

    #### Add exception
    for k in existence_dict:
        if existence_dict[k] == 'false':
            raise Exception('Missing file in input directory: ' + k)
            logging.error('Missing file in input directory: %s',k)
            

    return triples_list_file,labels_file


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

def compare_wikipathways_subgraphs(wikipathway_diagrams,subgraph_type,all_wikipathways_dir):

    all_subgraph_types = []
    pathways = []
    jaccard = []
    overlap = []
    edit = []
    for wikipathway in wikipathway_diagrams:

        w_file = all_wikipathways_dir + '/' + wikipathway + '/' + wikipathway + '_edgeList.csv'

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output/'
        subgraph_file_path = subgraph_type + '/Subgraph.csv'
        
        #Subgraph type must be CosineSimilarity, PDP, or GuidingTerm_<specified_term> to match current output structure
        w_subgraph_file = output_dir + subgraph_file_path

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

    results_file = all_wikipathways_dir + '/Graph_Similarity_Metrics.csv'
    results_df.to_csv(results_file,sep=',',index=False)
    logging.info('Created graph similarity metrics csv file: %s',results_file)

    return results_df

#Generates histogram with N number of categories by pathway, where lists are the input
def visualize_graph_metrics(df,w_dir,subgraph_type):
    
    ax = df.plot(x="Pathway", y=['Jaccard','Overlap'], kind="bar", rot=0)
    plt.title("Graph Similarity Metrics for Wikipathways Diagrams and "+ subgraph_type,fontsize = 18)
    plt_file = all_wikipathways_dir + '/' + subgraph_type + '_Graph_Similarity_Metrics_Jaccard_Overlap.png'
    plt.savefig(plt_file)

    logging.info('Created png: %s',plt_file)

    ax = df.plot(x="Pathway", y=['Edit Distance'], kind="bar", rot=0)
    plt.title("Graph Similarity Metrics for Wikipathways Diagrams and "+ subgraph_type,fontsize = 18)
    plt_file = all_wikipathways_dir + '/' + subgraph_type + '_Graph_Similarity_Metrics_Edit_Distance.png'
    plt.savefig(plt_file)

    logging.info('Created png: %s',plt_file)

