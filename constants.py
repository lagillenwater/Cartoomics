"""Constants"""

WIKIPATHWAYS_SUBFOLDER = 'wikipathways_graphs'
WIKIPATHWAYS_METADATA_FILESTRING = '_datanodeDF.csv'
WIKIPATHWAYS_PREFIX = 'WikiPathways'
NODE_PREFIX_MAPPINGS = {
    'Ensembl' : 'Ensembl',
    'HMDB' : 'HMDB',
    'Entrez Gene' : 'NCBIGene',
    'KEGG Compound' : 'KEGG.COMPOUND',
    'PubChem-compound' : 'PUBCHEM.COMPOUND',
    'Uniprot-TrEMBL' : 'UniProtKB',
    'HGNC' : 'HGNC',
    'ChEBI' : 'CHEBI'
}
WIKIPATHWAYS_UNKNOWN_PREFIXES = ['Unknown',WIKIPATHWAYS_PREFIX,'Pfam','Wikidata','InterPro','Enzyme Nomenclature']


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

ALL_WIKIPATHWAYS = ['WP4532', 'WP4533', 'WP4534', 'WP4535', 'WP4537', 'WP4538', 'WP4539', 'WP4540','WP4541', 'WP4542', 'WP4553', 'WP4562', 'WP4564', 'WP4565', 'WP4760', 'WP4829', 'WP4856', 'WP5283', 'WP5358', 'WP5368', 'WP5372', 'WP5373', 'WP5382', 'WP5385']

PHEKNOWLATOR_BROAD_NODES_DICT = {
    'protein_coding_gene': 'http://purl.obolibrary.org/obo/SO_0001217',
    'Gene expression (Transcription)': 'https://reactome.org/content/detail/R-HSA-74160',
    'Generic Transcription Pathway': 'https://reactome.org/content/detail/R-HSA-212436',
    'Metabolism': 'https://reactome.org/content/detail/R-HSA-1430728',
    'Developmental Biology': 'https://reactome.org/content/detail/R-HSA-1266738',
    'gene': 'http://purl.obolibrary.org/obo/SO_0000704',
    'Metabolism of proteins': 'https://reactome.org/content/detail/R-HSA-392499',
    'tag': 'http://purl.obolibrary.org/obo/SO_0000324',
    'engineered': 'http://purl.obolibrary.org/obo/SO_0000783',
    'transcript': 'http://purl.obolibrary.org/obo/SO_0000673',
    'protein binding': 'http://purl.obolibrary.org/obo/GO_0005515',
    'Homo sapiens protein': 'http://purl.obolibrary.org/obo/PR_000029067',
}