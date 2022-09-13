import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd
  
def edge_count(df_fig1, df_fig2, df_fig3):
    
    # define axis
    cartton1 = pd.read_csv(df_fig1)
    X0 = cartton1['Edge_Type']
    Y0 = cartton1['cs']
    Z0 = cartton1['pdp']
    
    cartton2 = pd.read_csv(df_fig2)
    X1 = cartton2['Edge_Type']
    Y1 = cartton2['cs']
    Z1 = cartton2['pdp']
    
    cartoon3 = pd.read_csv(df_fig3)
    X2 = cartoon3['Edge_Type']
    Y2 = cartoon3['cs']
    Z2 = cartoon3['pdp']
      
    X_axis = np.arange(len(X1))
    
    figure, axis = plt.subplots(3, 1)
    figure.set_size_inches(14.5, 14)
    
    axis[0].bar(X_axis - 0.2, Y0, 0.4, label = 'cs')
    axis[0].bar(X_axis + 0.2, Z0, 0.4, label = 'pdp')
    axis[0].set_title("CS")
    
    
    axis[1].bar(X_axis - 0.2, Y1, 0.4, label = 'cs')
    axis[1].bar(X_axis + 0.2, Z1, 0.4, label = 'pdp')
    axis[1].set_title("PDP")
    
    axis[2].bar(X_axis - 0.2, Y2, 0.4, label = 'cs')
    axis[2].bar(X_axis + 0.2, Z2, 0.4, label = 'pdp')
    axis[2].set_title("Edge Exlusion")
    
    plt.xticks(X_axis, X1, rotation = 45, ha="right")
    plt.xlabel("Edge Type")
    plt.ylabel("Number of edges")
    plt.suptitle("Number of unique edges found using CS and PDP", fontsize=30)
    
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
