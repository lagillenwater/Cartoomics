import argparse
import os


#Define arguments for each required and optional input
def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--input-dir",dest="InputDir",required=True,help="InputDir")

    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")

    parser.add_argument("--knowledge-graph",dest="KG",required=True,help="Knowledge Graph: either 'pkl' for PheKnowLator or 'kg-covid19' for KG-Covid19")

    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = False)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")

    return parser

# Wrapper function
def generate_arguments():

    #Generate argument parser and define arguments
    parser = define_arguments()
    args = parser.parse_args()

    input_dir = args.InputDir
    output_dir = args.OutputDir
    kg_type = args.KG
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight

    return input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type

### Download knowledge graph files

## need gsutil to download pheknowlator files
def check_gsutil():
    output = os.popen('gsutil -v')
    output = output.read()
    if output == '':
        gsutil = False
    else:
        gsutil = True
    return(gsutil)

## isntall gsutil software
def install_gsutil():
    os.system("pip install gsutil")

## downloading pheknowlator files from current build and storing in chosen directory

### NB: Change directory based on reformating of file structure?

def download_pkl(kg_dir):
    if not check_gsutil():
        install_gsutil()
    os.system(' gsutil -m cp \
  "gs://pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt" \
  "gs://pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt" \
  ' + kg_dir)


## downloading the KG-COVID19
def download_kg19(kg_dir):
    os.system('wget https://kg-hub.berkeleybop.io/kg-covid-19/current/kg-covid-19.tar.gz -P ' + kg_dir)
    os.system('tar -xvzf ' + kg_dir + "kg-covid-19.tar.gz -C " + kg_dir)



def get_graph_files(input_dir,output_dir, kg_type):

    fname  = [v for v in os.listdir(input_dir) if 'example_input' in v]
    if len(fname) == 1:
        input_file = input_dir + '/' + fname[0]
    else:
        raise Exception('Missing or duplicate file in input directory: ' + '_example_input')

    if kg_type == "pkl":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.exists(kg_dir):
            os.mkdir(kg_dir)
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
            download_kg19(kg_dir)



        
        existence_dict = {
            'merged-kg_edges':'false',
            'merged-kg_nodes':'false'
        }


        for k in list(existence_dict.keys()):
            for fname in os.listdir(kg_dir):
                if k in fname:
                    if k == 'merged-kg_edges':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'merged-kg_nodes':
                        labels_file = input_dir + '/' + kg_type + '/' + fname 
                    existence_dict[k] = 'true'

    #Check for existence of all necessary files, error if not

    #### Add exception
    for k in existence_dict:
        if existence_dict[k] == 'false':
            raise Exception('Missing file in input directory: ' + k)

    #Check for existence of output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return triples_list_file,labels_file,input_file
