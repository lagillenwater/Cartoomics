from Bio import Entrez
import argparse
import pandas as pd
import os

#Define arguments for each required and optional input
def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--entrez_email",dest="entrez_email",required=True,help="Email for account to utilize NCBI E-utilities API. This is the email tied to your NCBI account")
    parser.add_argument("--pmid_file",dest="pmid_file",required=True,help="Table with column corresponding to list of PMID's to perform NER on")
    parser.add_argument("--output_directory",dest="output_directory",required=True,help="output directory to store the article abstracts")

    return parser

def generate_arguments():

    #Generate argument parser and define arguments
    parser = define_arguments()
    args = parser.parse_args()
    entrez_email = args.entrez_email
    pmid_file = args.pmid_file
    output_directory = args.output_directory

    return entrez_email,pmid_file,output_directory

def parse_pmid_file(pmid_file):

    pmid_table= pd.read_csv(pmid_file, sep = ",")
    pmid_table = pmid_table.rename(columns=lambda name: name.strip())
    pmids = pmid_table["PMID"].str.strip().dropna().tolist()
    wikipathways = pmid_table["Wikipathway ID"].str.strip().dropna().tolist()
    return pmids,wikipathways


def get_abstract(pmid,wikipathway):
    # handle = Entrez.efetch(db = "pmc", id = "31911834", retmode = "xml")
    handle = Entrez.efetch(db = "pubmed", id = pmid, rettype= "abstract", retmode = "text")
    # # records = Entrez.read(handle)
    # #keywords =  records['PubmedArticle'][0]['MedlineCitation']['KeywordList'][0]
    # handle.close()

    # # Open a file for writing
    
    file_name = wikipathway + ".txt"
    with open(file_name, 'w', encoding='utf-8') as output_file:
        output_file.write(handle.read())
        # # Write the content of the TextIOWrapper object to the file
        # for key in keywords:
        #     output_file.write(str(key) + '\n')

    print("Wrote abstract for " + pmid + " to " + file_name)


def main():

    entrez_email,pmid_file,output_directory = generate_arguments()
    
    Entrez.email = entrez_email

    pmids,wikipathways = parse_pmid_file(pmid_file)

    os.chdir(output_directory)
    
    for pmid,wikipathway in zip(pmids,wikipathways):
        get_abstract(pmid,wikipathway)

if __name__ == '__main__':
    main()
