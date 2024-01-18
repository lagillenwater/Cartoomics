from wikinetworks_mod import *
import networkx as nx
import argparse
import os

def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ## Required inputs
    parser.add_argument("--wikipathway",dest="wikipathway",required=True,help="Wikipathways ID (e.g., WP5372), there is no default")
    return(parser)

parser = define_arguments()
args = parser.parse_args()
wikipathway = args.wikipathway

if not os.path.isdir("wikpathways_graphs"):
    os.mkdir("wikipathways_graphs")

os.chdir('./wikipathways_graphs')

if not os.path.isdir(wikipathway):
    os.mkdir(wikipathway)

os.chdir(wikipathway)

__all__ = ["WikiPathways"]
s = WikiPathways()

graph = runParsePathway(s, args.wikipathway)



