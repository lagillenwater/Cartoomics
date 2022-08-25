# Cartoomics Figure Generation 

This Cartoomics repository consists of a workflow written in python that can generate an interaction network using a given knowledge graph from a user derived description of a cartoon image. The goal of this workflow is to generate complete and detailed pathway diagrams using the vast information contained within a knowledge graph.

## Getting Started

These instructions will provide the necessary environments, programs with installation instructions, and input files in order to run the creating_subgraph_using_cosinesim.py script, which will run this workflow from end to end.

The path search algorithms available are:

- Shortest Path Search: find the shortest path between each source and target node (may not be identical each time)
- Cosine similarity Prioritization: prioritize all shortest paths between each source and target node by maximizing total cosine similarity of the start and all intermediate nodes to the target node in each path
- Path Degree Product Prioritization: prioritize all shortest paths between each source and target node by maximizing path degree product of all nodes in each path

This ReadMe currently describes the Cosine similarity Prioritization algorithm.

### Prerequisites
The following software or software packages must be installed, as detailed in the requirements.txt:
```
- Python (any version later than 3.6)
- python-igraph (any version later than 0.9.10)
- gensim (any version later than 4.2.0)
- py4cytoscape (any version later than 1.3.0)
- Cytoscape (any version later than 3.8.0)
```

Ensure that Cytoscape is open and running on your computer before continuing.

## Running the Script

### Input Directory

The following files must exist in the input directory:

| File                              | Assumptions                                       | Substring Required in Filename
|-----------------------------------|---------------------------------------------------|---------------------------------------------------
| Triples file                      | txt file of all graph triples as <uri>, header is | PheKnowLator_v3.0.2_full_instance_relationsOnly_
|                                   | Subject, Predicate, Object (tab delimited)        | OWLNETS_Triples_Identifiers                                                 
|                                   |                                                   |                                                   
| Labels file                       | <br>txt file of graph labels with headers that at | <br>PheKnowLator_v3.0.2_full_instance_relationsOnly_
|                                   | least include Identifier (<uri>), Label (name).   | OWLNETS_NodeLabels
|                                   | (tab delimited?)                                  |
|-----------------------------------|---------------------------------------------------|---------------------------------------------------
| Input file                        | csv file of all node pairs that exist in original | _example_input
|                                   | <br>pathway figure, header is source, target      |
|                                   | <br>(“|” delimited)                               |
|-----------------------------------|---------------------------------------------------|---------------------------------------------------
| nodevectors_node2vec.py           | script                                            | nodevectors_node2vec.py
|-----------------------------------|---------------------------------------------------|---------------------------------------------------
| sparse_custom_node2vec_wrapper.py | script                                            | sparse_custom_node2vec_wrapper.py
|-----------------------------------|---------------------------------------------------|---------------------------------------------------

### Defaults
  
The following values will be used if not otherwise specified:
- embedding dimensions: embeddings of the knowledge graph will be generated using node2vec of dimension 128, unless otherwise specified
  --embedding-dimensions <int>
- weights: edges will not be weighted unless otherwise specified. Any edges specified will be weighted lower/more important in the path search.
  --weights "[edge_1, edge_2]"
- search type: the shortest path algorithm used (contained within the python-igraph package) will search for paths in all directions, unless otherwise specified
  --search-type one

### Command Line Argument 
  
To run the script, execute the following command once the input directory is prepared:
  
```
python creating_subgraph_using_cosinesim.py --input-dir INPUTDIR --output-dir OUTPUTDIR
```
*Note that the specified output directory must already exist
 
## Expected Outputs
  
The creating_subgraph_using_cosinesim.py script will always generate the following files:
  
### Subgraph
  
A .csv file which shows all source and target nodes found in the path search that include the original example cartoon (Input file above) and any intermediate nodes found in the path search.

```
S|P|O
insulin receptor (human)|subClassOf|insulin receptor
insulin receptor (human)|participates_in|Insulin receptor signalling cascade
```
  
### Subgraph Attributes

A .noa file which specifies which input nodes are from the original example cartoon (Input file above) and which were intermediate nodes found in the path search. 
  
```
Node|Attribute
insulin receptor (human)|Extra
insulin receptor|Mechanism
```

### Subgraph Visualization
  
A .png file generated in cytoscape with all nodes found in the path search, colored by original nodes and intermediate nodes.

The creating_subgraph_using_cosinesim.py script will also generate the following intermediate files:
  
### Files generated for embeddings:
 
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integers_node2vecInput
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned
- PheKnowLator_v3_node2vec_Embeddings<DIM>.emb (where <DIM> is the # dimensions specified)
  
*Note if the above files already exist in the output directory when running the script, the embeddings will not be re-generated.
  


# Software Design
  
Below is a class diagram describing the architecture of this workflow.
  
<img width="1017" alt="Screen Shot 2022-08-25 at 9 24 11 AM" src="https://user-images.githubusercontent.com/70932395/186705860-6982c26c-2b62-4dbc-9508-7f5de828849e.png">

