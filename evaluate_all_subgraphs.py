from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *

def main():

    
    input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type,pdp_weight = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)
    
    print("Outputting Evaluation......")

    input_nodes,subgraph_cs,cs_noa_df,path_total_cs = get_subgraph_dfs(output_dir,'CosineSimilarity')
    input_nodes,subgraph_pdp,pdp_noa_df,path_pdp = get_subgraph_dfs(output_dir,'PDP')

    ranked_prioritization_df = ranked_comparison(output_dir=output_dir,cs=path_total_cs,pdp=path_pdp)

    path_length_df = path_length_comparison(output_dir,input_nodes,g.labels_all,search_type,cs=subgraph_cs,pdp=subgraph_pdp)

    num_nodes_df = num_nodes_comparison(output_dir=output_dir,cs=subgraph_cs,pdp=subgraph_pdp)

    edge_types_df = edge_type_comparison(output_dir=output_dir,cs=subgraph_cs,pdp=subgraph_pdp)

    intermediate_nodes_df = intermediate_nodes_comparison(output_dir,g.labels_all,kg_type,cs=cs_noa_df,pdp=pdp_noa_df)

if __name__ == '__main__':
    main()
