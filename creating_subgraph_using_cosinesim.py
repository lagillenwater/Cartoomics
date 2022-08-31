from inputs import *
from create_graph import create_pkl_graph
from assign_nodes import *
from create_subgraph import subgraph_prioritized_path_cs
from visualize_subgraph import output_visualization

def main():

    input_dir,output_dir,embedding_dimensions,weights,search_type = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir)
    
    print("Creating knowledge graph object from inputs.....")

    g = create_pkl_graph(triples_list_file,labels_file)

    print("Mapping between user inputs and KG nodes.......")
    
    s = interactive_search_wrapper(g, input_file, output_dir)

    print("Mapping complete")
    print(s)
    print("Finding subgraph using user input and KG embeddings......")
    
    subgraph = subgraph_prioritized_path_cs(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions)

    print("Outputting visualization......")

    output_visualization(s,subgraph,output_dir)

if __name__ == '__main__':
    main()
