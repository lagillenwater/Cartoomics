import numpy as np
import matplotlib.pyplot as plt
import pandas as pd




def arv(df1, df2, df3, df4, df5, df6):
    
    df1 = pd.read_csv(df1, encoding='latin-1')
    arr1 = df1.to_numpy() 
    df2 = pd.read_csv(df2, encoding='latin-1')
    arr2 = df2.to_numpy()
    df3 = pd.read_csv(df3, encoding='latin-1')
    arr3 = df3.to_numpy()
    df4 = pd.read_csv(df4, encoding='latin-1')
    arr4 = df4.to_numpy()
    df5 = pd.read_csv(df5, encoding='latin-1')
    arr5 = df5.to_numpy()
    df6 = pd.read_csv(df6, encoding='latin-1')
    arr6 = df6.to_numpy()
    
    # fake data
    # np.random.seed(19680801)
    # data = np.random.lognormal(size=(37, 2))
    labels = list(['CS','PDP'])
    fs = 10  # fontsize
    
    # meanline = True,
    
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(9, 6), sharey=True)
    axs[0, 0].boxplot(df1, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    axs[0, 0].set_title('Mean Geodesic \n Figure1', fontsize=fs)
    
    axs[0, 1].boxplot(df2, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    axs[0, 1].set_title('Mean Geodesic \n Figure2', fontsize=fs)
    
    axs[0, 2].boxplot(df3, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    axs[0, 2].set_title('Mean Geodesic \n Figure3', fontsize=fs)
    
    axs[1, 0].boxplot(df4, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    tufte_title = 'Average Degree \n Figure1'
    axs[1, 0].set_title(tufte_title, fontsize=fs)   
    
    axs[1, 1].boxplot(df5, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    axs[1, 1].set_title('Average Degree \n Figure2', fontsize=fs)
    
    axs[1, 2].boxplot(df6, labels=labels, widths = 0.3, sym = 'b+', showmeans = True, meanline = True, vert = False)
    axs[1, 2].set_title('Average Degree \n Figure3', fontsize=fs)
    
    
    fig.subplots_adjust(hspace=0.5)
    
    
    plt.savefig("./output/average_comparison.jpg", dpi=100)


# the path of data
df1 = "./graph_inputs/Mean_Geodesic1.csv"
df2 = "./graph_inputs/Mean_Geodesic2.csv"
df3 = "./graph_inputs/Mean_Geodesic3.csv"
df4 = "./graph_inputs/Average_Degree1.csv"
df5 = "./graph_inputs/Average_Degree2.csv"
df6 = "./graph_inputs/Average_Degree3.csv"

#call the function
figure = arv(df1, df2, df3, df4, df5, df6)

