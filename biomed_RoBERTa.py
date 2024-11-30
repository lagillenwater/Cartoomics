# from transformers import RobertaTokenizer, RobertaModel
import torch
from torch.nn.functional import cosine_similarity, pairwise_distance

# Function to get embeddings
def get_embeddings(model, tokenizer, sentence):
    encoded_input = tokenizer(sentence, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input)
    return output.last_hidden_state.mean(dim=1)

# function to find cosine similarity
def get_cosine_similarity(embedding1,embedding2):
    return(cosine_similarity(embedding1,embedding2).item())

# # Initialize tokenizer and model
# tokenizer = RobertaTokenizer.from_pretrained('allenai/biomed_roberta_base')
# model = RobertaModel.from_pretrained('allenai/biomed_roberta_base')




# # Define sentences
# sentence1 = "SKI"
# sentence2 = "SMAD1"
# sentence3 = "PYROXD2"

# # Define sentences
# sentence1 = "NCBI:6497"
# sentence2 = "NCBI:4086"
# sentence3 = "NCBI:84795"


# # Define sentences
# sentence1 = "STAT1"
# sentence2 = "IFNG"
# sentence3 = "PYROXD2"

# # Get embeddings
# embeddings1 = get_embeddings(model, tokenizer, sentence1)
# embeddings2 = get_embeddings(model, tokenizer, sentence2)
# embeddings3 = get_embeddings(model, tokenizer, sentence3)

# # Calculate distances
# print("Cosine Distance between", sentence1, "and", sentence2, ":",  1 - cosine_similarity(embeddings1, embeddings2).item())
# print("Cosine Distance between", sentence1, "and", sentence3, ":",   1 - cosine_similarity(embeddings1, embeddings3).item())

