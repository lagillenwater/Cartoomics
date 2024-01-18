import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tqdm
from collections import defaultdict 
import argparse
import logging.config
from pythonjsonlogger import jsonlogger
import sys

#Evaluates all patterns that were first generated from shortest path subgraphs of an entity-entity search, and outputs a plot of how many unique paths there are per iteration

#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--directory",dest="Directory",required=True,help="Directory")

    parser.add_argument("--min-counts",dest="MinCounts",required=False,default=10,help="MinCounts")

    parser.add_argument("--node-input1",dest="NodeInput1",required=True,help="NodeInput1")

    parser.add_argument("--node-input2",dest="NodeInput2",required=True,help="NodeInput2")


    return parser

def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    
    directory = args.Directory
    min_counts = args.MinCounts
    node_input1 = args.NodeInput1
    node_input2 = args.NodeInput2

    metapath_dir = '/MetapathEvaluation/'
    metapath_outdir = directory + metapath_dir
    if not os.path.isdir(metapath_outdir):
        os.makedirs(metapath_outdir)

    #For search of mulitple files within only 1 directory of #_Pattern_Counts_Full per iteration
    unique_df = pd.DataFrame(columns=['Pattern'])
    full_df = pd.DataFrame(columns=['Pattern','Count'])
    unique_paths_df = pd.DataFrame(columns=['Total_Unique_Paths'])

    unique_per_it = pd.DataFrame(columns=['Unique_Paths'])
    ct = 0

    counter = defaultdict()

    it_ct = 0
    os.chdir(directory + metapath_dir)
    for patterns_file in tqdm.tqdm(os.listdir()):
        if 'Pattern_Counts_Full.csv' in patterns_file:
            df = pd.read_csv(patterns_file,delimiter=',')
            unique_df = pd.concat([unique_df,df],ignore_index=True)
            #To get number of unique paths for this iteration
            unique_df = unique_df.drop_duplicates(subset=['Pattern'])
            ct += len(unique_df)
            #Total unique paths across iterations
            unique_paths_df.loc[len(unique_paths_df)] = len(unique_df)
            #To get count of each unique path for all iterations so far
            full_df = pd.concat([full_df,df],ignore_index=True)

            #Unique paths for this iteration  
            unique_per_it.loc[it_ct] = len(df.drop_duplicates(subset=["Pattern"]))

            it_ct += 1

    if len(full_df) == 0:
        print('No files of the #_Pattern_Counts_Full.csv naming convention found, ensure that files are first created.')
        logging.error('No files of the #_Pattern_Counts_Full.csv naming convention found, ensure that files are first created.')
        sys.exit(1)

    full_df.to_csv("full_df.csv")
    unique_paths_df.to_csv("unique_paths_df.csv")

    #Only plot paths with count > a given number
    full_df = full_df[full_df["Count"] > int(min_counts)]

    fig = plt.gcf()

    # Change seaborn plot size
    fig.set_size_inches(20, 16)
    node_pair = node_input1 + "-" + node_input2

    sns.boxplot(x = full_df['Pattern'], y = full_df['Count'])
    sns.stripplot(x = full_df['Pattern'], y = full_df['Count'])
    plt.xticks(rotation=90)
    plt.title("Count of Unique Paths per Iteration of " + node_pair + " Pairs (Count > " + str(min_counts)+ ")",fontsize = 24)
    plt.xlabel("Pattern",fontsize = 18)
    plt.ylabel("Count",fontsize = 18)
    plt.savefig("PathsDistribution.png",bbox_inches='tight')
    plt.clf()



    #To find point where number of unique paths reduces rate of increase
    '''from kneed import KneeLocator, DataGenerator

    k = KneeLocator(unique_paths_df.index,unique_paths_df['Total_Unique_Paths'],curve='concave',direction='increasing')
    k_elbow = round(k.elbow, 3)
    paths_k = unique_paths_df.iloc[k_elbow].loc['Total_Unique_Paths']'''

    fig = plt.gcf()

    # Change seaborn plot size
    fig.set_size_inches(12, 8)

    sns.scatterplot(data=unique_paths_df, x=unique_paths_df.index, y="Total_Unique_Paths")

    #Add point where number of unique paths reduces rate of increase from above
    '''plt.axvline(x=k_elbow)
    plt.text(2*len(unique_paths_df)/3, max(unique_paths_df['Total_Unique_Paths'])/2,'Optimal # Unique Paths (k='+str(k_elbow)+'): '+str(paths_k), fontsize = 12)'''

    plt.title("Total Unique Paths per Iteration of " + node_pair + " Pairs",fontsize = 24)
    plt.xlabel("Iteration",fontsize = 18)
    plt.ylabel("Total Unique Paths",fontsize = 18)
    plt.savefig("UniquePaths.png",bbox_inches='tight')
    plt.clf()

    fig = plt.gcf()

    plt.style.use('seaborn-v0_8')
    plt.hist(unique_per_it,bins=len(unique_per_it), facecolor = '#929591', edgecolor='#000000')
    plt.title("Distribution of Unique Paths for Each Iteration of " + node_pair + " Pairs",fontsize = 24)
    plt.xlabel("# Unique Paths",fontsize = 18)
    plt.ylabel("Count",fontsize = 18)
    plt.savefig("UniquePathsHistogram.png",bbox_inches='tight')

if __name__ == '__main__':
    main()

