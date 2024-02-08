from wikinetworks_mod import *
import networkx as nx
import argparse
import os
import requests
from bs4 import BeautifulSoup


def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ## Required inputs
    parser.add_argument("--wikipathway",dest="wikipathway",required=False,help="Wikipathways ID (e.g., WP5372), there is no default")
    parser.add_argument("--pfocr_url",dest="pfocr_url",required=False,help="pfocr url (e.g., https://pfocr.wikipathways.org/figures/PMC6943888__40035_2019_179_Fig1_HTML.html), there is no default")
    return(parser)

def get_wikipathway_from_pfocr_url(pfocr_url):
    response = requests.get(pfocr_url)
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the image tag
    image_tag = soup.find('img', alt='WikiPathways')
    # Extract the message attribute
    if image_tag:
        message_attr = image_tag.get('src')
        # Extracting the part after 'message='
        wikipathway = message_attr.split('message=')[1].split('&')[0]
        print("Wikipathway:", wikipathway)
        return(wikipathway)
    else:
        print("Wikipathway not found.")
    

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
    pfocr_url = args.pfocr_url

    all_wikipathways_dir = os.getcwd() + "/wikipathways_graphs"

    #Gets wikpathway from pfocr_url
    wikipathway = get_wikipathway_from_pfocr_url(pfocr_url)
    
    #Downloads wikipathway diagrams as edgelists
    download_wikipathways_edgelist(all_wikipathways_dir,wikipathway)

    #Converts wikipathway diagram edgelists to format necessary for subgraph generation
    convert_wikipathways_input(all_wikipathways_dir,wikipathway)

if __name__ == '__main__':
    main()


