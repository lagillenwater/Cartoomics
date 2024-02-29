#!/bin/bash

mkdir wikipathways_jobs
while read p; do
    echo "$p"
    cat <<EOF > ./wikipathways_jobs/$p.sh
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --time=10:00:00
#SBATCH --partition=amc
#SBATCH --constraint=cpu
#SBATCH --mem=64G
#SBATCH --output=/scratch/alpine/lgillenwater@xsede.org/Cartoomics/wikipathways_jobs/$p-%j.out
#SBATCH --mail-type=END
#SBATCH --mail-user=lucas.bgillenwater@cuanschutz.edu
#SBATCH --job-name=$p



# load necessary modules
module load anaconda
    
cd /scratch/alpine/lgillenwater@xsede.org/Cartoomics
conda activate Cartoomics

python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/${p}_output --knowledge-graph pkl --input-type annotated_diagram --input-substring $p --weights True

EOF
    
    sbatch ./wikipathways_jobs/$p.sh
    squeue --user lgillenwater@xsede.org
    
done < ./wikipathways_graphs/PFOCR_wikipathways_test.txt



 
