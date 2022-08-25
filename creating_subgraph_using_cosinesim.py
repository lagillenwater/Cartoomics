from inputs import *
from create_graph import create_pkl_graph
from assign_nodes import *
from create_subgraph import subgraph_prioritized_path_cs
from visualize_subgraph import output_visualization

def main():

    input_dir,output_dir,embedding_dimensions,weights,search_type = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir)
    
    g = create_pkl_graph(triples_list_file,labels_file)

    #Interactively assign node
    u = read_user_input(input_file)
    n = unique_nodes(u)
    s = search_nodes(n,g,u)
    create_input_file(s,output_dir)

    subgraph = subgraph_prioritized_path_cs(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,s,embedding_dimensions)

    output_visualization(s,subgraph,output_dir)

if __name__ == '__main__':
    main()