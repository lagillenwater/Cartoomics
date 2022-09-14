import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd
  
def edge_count(df_fig1, df_fig2, df_fig3):
    
    # define axis
    df_fig1 = pd.read_csv(df_fig1)
    X0 = df_fig1['Edge_Type']
    Y0 = df_fig1['cs']
    Z0 = df_fig1['pdp']
    
    df_fig2 = pd.read_csv(df_fig2)
    X1 = df_fig2['Edge_Type']
    Y1 = df_fig2['cs']
    Z1 = df_fig2['pdp']
    
    df_fig3 = pd.read_csv(df_fig3)
    X2 = df_fig3['Edge_Type']
    Y2 = df_fig3['cs']
    Z2 = df_fig3['pdp']
      
    X_axis = np.arange(len(X1))
    
    figure, axis = plt.subplots(3, 1)
    figure.set_size_inches(14.5, 14)
    
    axis[0].bar(np.arange(len(X0)) - 0.2, Y0, 0.4, label = 'cs')
    axis[0].bar(np.arange(len(X0)) + 0.2, Z0, 0.4, label = 'pdp')
    axis[0].set_xticks(np.arange(len(X0)), X0, rotation = 12, ha="right", fontsize=10)
    axis[0].set_title("Figure1")
    
    
    axis[1].bar(np.arange(len(X1)) - 0.2, Y1, 0.4, label = 'cs')
    axis[1].bar(np.arange(len(X1)) + 0.2, Z1, 0.4, label = 'pdp')
    axis[1].set_xticks(np.arange(len(X1)), X1, rotation = 12, ha="right", fontsize=10)
    axis[1].set_title("Figure2")
    
    axis[2].bar(np.arange(len(X2)) - 0.2, Y2, 0.4, label = 'cs')
    axis[2].bar(np.arange(len(X2)) + 0.2, Z2, 0.4, label = 'pdp')
    axis[2].set_xticks(np.arange(len(X2)), X2, rotation = 12, ha="right", fontsize=10)
    axis[2].set_title("Figure3")
    
    plt.xlabel("Edge Type")
    plt.ylabel("Number of edges")
    plt.subplots_adjust(hspace=0.5)
    plt.suptitle("Number of unique edges found using CS and PDP", fontsize=30)
    plt.style.context('grayscale')
    
    for ax in axis.flat:
        ax.set(ylabel='Number of edges')
        ax.legend()
    
    plt.savefig("./output/edge_type_comparison.jpg", dpi=200)



# the path of data
df_fig1 = "./graph_inputs/edge_type_comparison1.csv"
df_fig2 = "./graph_inputs/edge_type_comparison2.csv"
df_fig3 = "./graph_inputs/edge_type_comparison3.csv"

#call the function
figure = edge_count(df_fig1, df_fig2, df_fig3)
