#Outputs the patterns of edgelist that describe the shortest path between a specific set of pairs (microbe - metabolie). Skim only lists each edge type once, full lists every occurance of an edge type in the shortest path found. 

import csv
import pandas as pd
import argparse
import os
import glob
from collections import Counter


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--directory",dest="Directory",required=True,help="Directory")
    parser.add_argument("--full-or-skim",dest='FullOrSkim',required=False,help="FullOrSkim",default='skim')

    return parser

###Read in all files
def process_files(csv_file,full_or_skim):

    pathway_df = pd.read_csv(csv_file,sep='|')

    #Only return pattern if it exists
    if len(pathway_df) > 0:

        pattern = pathway_df.iloc[0].loc['P']

        if full_or_skim == 'skim':
            for i in range(1,len(pathway_df)):
                if pathway_df.iloc[i].loc['P'] not in pattern:
                    pattern = pattern + " --- " + pathway_df.iloc[i].loc['P']
        
        elif full_or_skim == 'full':
            for i in range(1,len(pathway_df)):
                pattern = pattern + " --- " + pathway_df.iloc[i].loc['P']

    else:
        pattern = 'none'
        
    name = csv_file.split('.csv')[0]

    return pattern,name

def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    
    directory = args.Directory
    full_or_skim = args.FullOrSkim
    
    csv_files = glob.glob(os.path.join(directory, "*mechanism.csv"))

    patterns_all = []
    names_all = []

    for f in csv_files:

        pattern,name = process_files(f,full_or_skim)
        if pattern != 'none':
            patterns_all.append(pattern)
            names_all.append(name)

    #Get count of each pattern
    patterns_count = dict(Counter(patterns_all))

    #Create df of Pattern/Name/count
    patterns_all_df = pd.DataFrame({'Pattern':patterns_all})
    patterns_all_df['Name'] = names_all
    counts = []
    for i in range(len(patterns_all_df)):
        counts.append(patterns_count[patterns_all_df.iloc[i].loc['Pattern']])
        #d = {}
        #p = patterns_all_df.iloc[i].loc['Pattern']
        #d['Count'] = patterns_count[p]

        #patterns_all_df = patterns_all_df.append(d,ignore_index=True)

    patterns_all_df['Count'] = counts
    patterns_all_df = patterns_all_df.sort_values(by=['Pattern','Count'])
    #patterns_df = pd.DataFrame.from_dict(patterns_count, orient='index',columns = ['Count'])
    #patterns_df.reset_index(inplace=True)
    #patterns_df = patterns_df.rename(columns = {'index':'Pattern'})

    if full_or_skim == 'skim':
        patterns_all_df.to_csv(directory+'/Pattern_Counts_Skim.csv',sep=',',index=False)
    elif full_or_skim == 'full':
        patterns_all_df.to_csv(directory+'/Pattern_Counts_Full.csv',sep=',',index=False)
  
if __name__ == '__main__':
    main()
