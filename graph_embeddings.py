import os
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import json
import re
import glob
import logging.config
from pythonjsonlogger import jsonlogger

# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})


class Embeddings:

    def __init__(self, triples_file,input_dir,embedding_dimensions, kg_type):
        self.triples_file = triples_file
        self.input_dir = input_dir
        self.embedding_dimensions = embedding_dimensions
        self.kg_type = kg_type

    def check_file_existence(self,kg_type,embeddings_file):
        exists = 'false'
        for fname in os.listdir(self.input_dir + '/' + kg_type):
            if bool(re.search(embeddings_file, fname)):
                exists = 'true'
        return exists

    def generate_graph_embeddings(self,kg_type):

        base_name = self.triples_file.split('/')[-1]
    
        embeddings_file = base_name.split('.')[0] + '_node2vec_Embeddings' + str(self.embedding_dimensions) + '.emb'
       
        #Check for existence of embeddings file
        exists = self.check_file_existence(kg_type,embeddings_file)
        

        if exists == 'true':
            emb = KeyedVectors.load_word2vec_format(self.input_dir + '/' + self.kg_type + '/' + embeddings_file, binary=False)
            if kg_type == 'pkl':
                entity_map = json.load(open(self.input_dir + '/' + self.kg_type + '/' + base_name.replace('Triples_Identifiers','Triples_Integer_Identifier_Map')))
            if kg_type == 'kg-covid19' or kg_type == 'kg-microbe':
                entity_map = json.load(open(self.input_dir + '/' + self.kg_type + '/' + base_name.replace('edges','Triples_Integer_Identifier_Map')))

        #Only generate embeddings if file doesn't exist
        if exists == 'false':
            if self.kg_type == 'pkl':
                output_ints_location = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('Triples_Identifiers','Triples_Integers_node2vecInput')
                output_ints_map_location = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('Triples_Identifiers','Triples_Integer_Identifier_Map')
            if self.kg_type == 'kg-covid19' or self.kg_type == 'kg-microbe':
                output_ints_location = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('edges','Triples_Integers_node2vecInput')

                output_ints_map_location = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('edges','Triples_Integer_Identifier_Map')

            with open(self.triples_file, 'r') as f_in:
                if self.kg_type == 'pkl':
                    kg_data = set(tuple(x.replace('>','').replace('<','').split('\t')) for x in f_in.read().splitlines())
                    f_in.close()
                if self.kg_type == 'kg-covid19' or self.kg_type == 'kg-microbe':
                    kg_data = set(tuple(x.split('\t'))[0:4] for x in f_in.read().splitlines())
                    f_in.close()

            logging.info('Created Triples_Integers_node2vecInput file: %s',output_ints_location) 
            logging.info('Created Triples_Integer_Identifier_Map file: %s',output_ints_map_location) 

            entity_map = {}
            entity_counter = 0
            graph_len = len(kg_data)
             
            ints = open(output_ints_location, 'w', encoding='utf-8')
            ints.write('subject' + '\t' + 'predicate' + '\t' + 'object' + '\n')

            for s, p, o in kg_data:
                subj, pred, obj = s, p, o
                if subj not in entity_map: entity_counter += 1; entity_map[subj] = entity_counter
                if pred not in entity_map: entity_counter += 1; entity_map[pred] = entity_counter
                if obj not in entity_map: entity_counter += 1; entity_map[obj] = entity_counter
                ints.write('%d' % entity_map[subj] + '\t' + '%d' % entity_map[pred] + '\t' + '%d' % entity_map[obj] + '\n')
            ints.close()

                #write out the identifier-integer map
            with open(output_ints_map_location, 'w') as file_name:
                json.dump(entity_map, file_name)

            with open(output_ints_location) as f_in:
                kg_data = [x.split('\t')[0::2] for x in f_in.read().splitlines()]
                f_in.close()

                #print('node2vecInput_cleaned: ',kg_data)
            if self.kg_type == 'pkl':
                file_out = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('Triples_Identifiers','Triples_node2vecInput_cleaned')
            if self.kg_type == 'kg-covid19' or self.kg_type == 'kg-microbe':
                file_out = self.input_dir + '/' + self.kg_type + '/' + base_name.replace('edges','Triples_node2vecInput_cleaned')
                                  

            with open(file_out, 'w') as f_out:
                for x in kg_data[1:]:
                    f_out.write(x[0] + ' ' + x[1] + '\n')
                f_out.close()
            
            logging.info('Created Triples_node2vecInput_cleaned file: %s',file_out) 
                   
            embeddings_out = self.input_dir + '/' + self.kg_type + '/' + embeddings_file

            command = "python sparse_custom_node2vec_wrapper.py --edgelist {} --dim {} --walklen 10 --walknum 20 --window 10 --output {}"
            os.system(command.format(file_out,self.embedding_dimensions, embeddings_out ))

            exists = self.check_file_existence(kg_type,embeddings_file)

                #Check for existence of embeddings file and error if not
            if exists == 'false':
                raise Exception('Embeddings file not generated in input directory: ' + self.input_dir + '/' + self.kg_type + '/' + embeddings_file)
                logging.error('Embeddings file not generated in input directory: %s',self.input_dir + '/' + self.kg_type + '/' + embeddings_file)



            emb = KeyedVectors.load_word2vec_format(self.input_dir + '/' + self.kg_type + '/' + embeddings_file, binary=False)

        return emb,entity_map
