from wikinetworks_mod import *
import networkx as nx
import argparse
import os

def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ## Required inputs
    parser.add_argument("--wikipathway",dest="wikipathway",required=True,help="Wikipathways ID (e.g., WP5372), there is no default")
    return(parser)

def download_wikipathways_edgelist(w_dir,wikipathway):

    if not os.path.exists(w_dir+"/"+wikipathway):
        os.makedirs(w_dir+"/"+wikipathway)

    os.chdir(w_dir+"/"+wikipathway)

    __all__ = ["WikiPathways"]
    s = WikiPathways()

    graph = runParsePathway(s, wikipathway)
    

def convert_wikipathways_input(all_wikipathways_dir,wikipathway):


    wikipathways_edgelist = pd.read_csv(all_wikipathways_dir + '/' + wikipathway + '/' + wikipathway + '_edgeList.csv')

    edgelist_df = wikipathways_edgelist[['Source', 'Target']]
    edgelist_df = edgelist_df.rename(columns={'Source' : 'source', 'Target': 'target'})

    if not os.path.exists(all_wikipathways_dir+ '/annotated_diagram'):
        os.makedirs(all_wikipathways_dir+ '/annotated_diagram')

    edgelist_df.to_csv(all_wikipathways_dir + '/annotated_diagram/' + wikipathway + '_example_input.csv',sep='|',index=False)


def main():

    parser = define_arguments()
    args = parser.parse_args()
    wikipathway = args.wikipathway

    all_wikipathways_dir = os.getcwd() + "/wikipathways_graphs"

    #Downloads wikipathway diagrams as edgelists
    download_wikipathways_edgelist(all_wikipathways_dir,wikipathway)

    #Converts wikipathway diagram edgelists to format necessary for subgraph generation
    convert_wikipathways_input(all_wikipathways_dir,wikipathway)

if __name__ == '__main__':
    main()


