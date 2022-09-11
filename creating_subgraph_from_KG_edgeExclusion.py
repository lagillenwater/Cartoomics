from inputs import *
from create_graph import create_graph
from assign_nodes import *
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from create_subgraph import user_defined_edge_weights
from visualize_subgraph import output_visualization
from evaluation import *

def main():

    input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type,pdp_weight = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    print("Subsetting knowledge graph with edge exclusion algorithm......")

    igraph_edge_exclusion = user_defined_edge_weights(g.edgelist, g.igraph) 
    
    print("Mapping between user inputs and KG nodes.......")
    
    #The same subgraph can be used for both edge exclusion and original graph with the same graph, as edges are unaffected by this step
    s = interactive_search_wrapper(g, input_file, output_dir)

    print("Mapping complete")
    print(s)

    
    #Perform each prioritization algorithm for each graph type

    #######Original Graph#######
    print("Finding subgraph using user input and KG embeddings for Cosine Similarity......")
    
    subgraph_cs,path_total_cs = subgraph_prioritized_path_cs(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions)

    print("Outputting CS visualization......")

    cs_noa_df = output_visualization(s,subgraph_cs,output_dir+'/CosineSimilarity')

    print("Finding subgraph using user input for PDP......")

    subgraph_pdp,path_pdp = subgraph_prioritized_path_pdp(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,pdp_weight,output_dir)
    
    print("Outputting PDP visualization......")

    pdp_noa_df = output_visualization(s,subgraph_pdp,output_dir+'/PDP')
    

    #######Edge Exclusion Graph#######

    print("Finding subgraph using user input and KG embeddings for Cosine Similarity (Edge Exclusion)......")
    
    subgraph_cs,path_total_cs = subgraph_prioritized_path_cs(s,igraph_edge_exclusion,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions)

    print("Outputting CS visualization (Edge Exclusion)......")

    cs_noa_df = output_visualization(s,subgraph_cs,output_dir+'/CosineSimilarity_EdgeExclusion')

    print("Finding subgraph using user input for PDP (Edge Exclusion)......")

    subgraph_pdp,path_pdp = subgraph_prioritized_path_pdp(s,igraph_edge_exclusion,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,pdp_weight,output_dir)
    
    print("Outputting PDP visualization (Edge Exclusion)......")

    pdp_noa_df = output_visualization(s,subgraph_pdp,output_dir+'/PDP_EdgeExclusion')

if __name__ == '__main__':
    main()
