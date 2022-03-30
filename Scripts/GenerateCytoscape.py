#Input a sif file and a node attribute file to generate a cytoscape network visualization of the given mechanism. Sif file is of the format S (source node), P (predicate), O (Target node), "|" delimited, and noa file is of the format Node (PKL Node Label), Attribute (Mechanism, Extra). Must have cytoscape running and py4cytoscape installed.

import pandas as pd
import py4cytoscape as p4c
from py4cytoscape import gen_node_color_map
import argparse
from py4cytoscape import palette_color_brewer_d_RdBu


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--sif-file",dest="SifFile",required=True,help="SifFile")
    parser.add_argument("--noa-file",dest="NoaFile",required=True,help="NoaFile")
    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")

    return parser

def create_network(inputSif,inputNoa,filename):

    sif_df = pd.read_csv(inputSif,sep='|')
    sif_df.columns = ['source','interaction','target']
    noa_df = pd.read_csv(inputNoa,sep='|')
    noa_df.columns = ['id','group']

    p4c.create_network_from_data_frames(noa_df,sif_df,title='Mechanism')

    p4c.set_visual_style('Marquee',network='Mechanism')

    p4c.set_node_color_mapping(**gen_node_color_map('group', mapping_type='d',style_name='Marquee'))
    
    p4c.export_image(filename+'.png',network='Mechanism')


def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    

    sif_file = args.SifFile
    noa_file = args.NoaFile
    output_dir = args.OutputDir

    filename = sif_file.split('.')[0]

    create_network(sif_file,noa_file,filename)

if __name__ == '__main__':
    main()
