from create_subgraph import subgraph_prioritized_path_cs
from create_graph import create_pkl_graph
from inputs import *

def main():

    input_dir,output_dir,embedding_dimensions,weights,search_type = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir)
    
    g = create_pkl_graph(triples_list_file,labels_file)

    p = subgraph_prioritized_path_cs(input_file,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions)

    print(p)

if __name__ == '__main__':
    main()