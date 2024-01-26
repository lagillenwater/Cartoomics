#! /bin/bash

# python creating_subgraph_from_KG.py --input-dir ./IM_Inputs/IL-1RA-Glutamate --output-dir ./IM_Outputs/IL-1RA-Glutamate --knowledge-graph pkl --input-type annotated_diagram

#Command to run test dataset
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_TestGraph  --output-dir ./Outputs_TestGraph --knowledge-graph pkl --input-type annotated_diagram

#Command to test pfocr input
#python creating_subgraph_from_KG.py --input-dir ./pfocr_tests --output-dir ./pfocr_tests --knowledge-graph pkl --input-type pathway_ocr --pfocr_url https://pfocr.wikipathways.org/figures/PMC5095497__IMM-149-423-g007.html

#Command to run annotated diagram input
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Neuroinflammation  --output-dir ./Test_Data/Outputs_Neuroinflammation --knowledge-graph pkl --input-type annotated_diagram

#Command to test metapaths generation
#python creating_metapaths_from_KG.py --input-dir ./metapath_tests --output-dir ./metapath_tests --knowledge-graphs "['pkl']" --num-iterations 1 --batch-size 1 --node-input1 gene --node-input2 mondo

#Command to plot metapaths generated above
#python Paths_Distribution_Plot.py --directory ./metapath_tests --min-counts 1 --node-input1 gene --node-input2 disease

#Command to test guiding term input
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Neuroinflammation  --output-dir ./Test_Data/Outputs_Neuroinflammation --knowledge-graph pkl --input-type annotated_diagram --guiding-term True
python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Covid19  --output-dir ./Test_Data/Inputs_Covid19 --knowledge-graph kg-covid19 --input-type annotated_diagram --guiding-term True

