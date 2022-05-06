#Input an input directory with a sif file and a node attribute file to generate a cytoscape network visualization of the given mechanism. Sif file is of the format S (source node), P (predicate), O (Target node), "|" delimited, and noa file is of the format Node (PKL Node Label), Attribute (Mechanism, Extra). Must have cytoscape running and py4cytoscape installed.

import pandas as pd
import py4cytoscape as p4c
from py4cytoscape import gen_node_color_map
import argparse
from py4cytoscape import palette_color_brewer_d_RdBu


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--input-dir",dest="InputDir",required=True,help="InputDir")
    parser.add_argument("--mechanism-filename",dest="MechanismFilename",required=True,help="MechanismFilename")

    return parser

def create_network(inputSif,inputNoa,filename):

    sif_df = pd.read_csv(inputSif,sep='|')
    sif_df.columns = ['source','interaction','target']
    noa_df = pd.read_csv(inputNoa,sep='|')
    noa_df.columns = ['id','group']

    p4c.create_network_from_data_frames(noa_df,sif_df,title=filename)

    p4c.set_visual_style('Marquee',network=filename)

    p4c.set_node_color_mapping(**gen_node_color_map('group', mapping_type='d',style_name='Marquee'))

    #p4c.set_edge_label_mapping('interaction')
    
    p4c.export_image(filename+'.png',network=filename)


def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    
    input_dir = args.InputDir
    mechanism_filename = args.MechanismFilename

    sif_file = input_dir + '/' + mechanism_filename + '.csv'
    noa_file = input_dir + '/' + mechanism_filename + '_attributes.noa'

    create_network(sif_file,noa_file,mechanism_filename)

if __name__ == '__main__':
    main()
