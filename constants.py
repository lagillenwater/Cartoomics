"""Constants"""

WIKIPATHWAYS_SUBFOLDER = 'wikipathways_graphs'
WIKIPATHWAYS_METADATA_FILESTRING = '_datanodeDF.csv'
WIKIPATHWAYS_PREFIX = 'Wikipathways'
NODE_PREFIX_MAPPINGS = {
    'Ensembl' : 'Ensembl',
    'HMDB' : 'HMDB',
    'Entrez Gene' : 'NCBIGene',
    'KEGG Compound' : 'KEGG.COMPOUND',
    'PubChem-compound' : 'PUBCHEM.COMPOUND',
    'Uniprot-TrEMBL' : 'UniProtKB',
    'HGNC' : 'HGNC'
}


NODE_NORMALIZER_URL = 'https://nodenormalization-sri.renci.org/1.4/get_normalized_nodes?curie='

PKL_PREFIXES = ['NCBIGene','CHEBI']
PKL_GENE_URI = 'http://www.ncbi.nlm.nih.gov/gene/'
PKL_OBO_URI = 'http://purl.obolibrary.org/obo/'

"""Constants for prefix mappings."""

#PKL
PKL_SUBSTRINGS = {
    'gene':'/gene/',
    'mondo':'/MONDO_',
    'chebi':'/CHEBI_',
    'pr':'/PR_',
    'pw':'/PW_',
    'hp':'/HP_',
    'vo':'/VO_',
    'efo':'/EFO_',
    'ncbitaxon':'/NCBITaxon_',
    'go':'/GO_',
    'nbo':'/NBO_',
    'so':'/SO_',
    'chr':'/CHR_',
    'reactome':'/R-HSA-',
    'uberon':'/UBERON_',
    'mpath':'/MPATH_',
    'pato':'/PATO_',
    'snp':'/snp/',
    'ncit':'/NCIT_',
    'caro':'/CARO_',
    'ecto':'/ECTO_',
    'cl':'/CL_',
    'ensembl':'ensembl.org/',
}

#KG-Covid19
KGCOVID19_SUBSTRINGS = {
    'gene':'/hgnc/',
    'mondo':'MONDO:',
    'chebi':'CHEBI:',
    'pr':'PR:',
    'hp':'HP:',
    'ncbitaxon':'/NCBITaxon_',
    'go':'GO:',
    'uberon':'UBERON:',
    'caro':'CARO:',
    'cl':'CL:',
    'bspo':'BSPO:',
    'bto':'BTO:',
    'fma':'FMA:',
    'ma':'MA:',
    'mpo':'MPO:',
    'oba':'OBA:',
    'pato':'PATO:',
    'plana':'PLANA:',
    'uberon':'UBERON:',
    'upheno':'UPHENO:',
    'wbbt':'WBbt:',
    'zp':'ZP:',
    'ensembl':'ENSEMBL:',
    'chembl':'CHEMBL:',
    'ecocore':'ECOCORE:',
    'mfomd':'MFOMD:',
    'bfo':'BFO:'
}
