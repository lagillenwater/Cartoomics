# Load model directly
from transformers import AutoTokenizer, AutoModel
import torch
from torch.nn.functional import cosine_similarity, pairwise_distance

# Function to get embeddings
def get_embeddings(model, tokenizer, sentence):
    encoded_input = tokenizer(sentence, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input)
    return output.last_hidden_state.mean(dim=1)




tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1")

# Define sentences
sentence1 = "IFNG2"
sentence2 = "IFNG1"
sentence3 = "PYROXD2"

# Get embeddings
embeddings1 = get_embeddings(model, tokenizer, sentence1)
embeddings2 = get_embeddings(model, tokenizer, sentence2)
embeddings3 = get_embeddings(model, tokenizer, sentence3)

# Calculate distances
print("Cosine Distance between similar genes (IFNG2, IFNG1):", 1 - cosine_similarity(embeddings1, embeddings2).item())
print("Cosine Distance between dissimilar genes (IFNG2, P53):", 1 - cosine_similarity(embeddings1, embeddings3).item())


###########################################################3

# power transformation function for range increase


# def modified_power_scale(x, xmin, p):
#     """ Scale the distance using a modified power function to amplify differences. """
#     return (x - xmin) ** p

# # Constants
# xmin = 0.001  # Slightly less than our minimum expected value
# p = 0.25  # High power to significantly amplify differences

# # Values
# distance1 = 0.007
# distance2 = 0.008

# # Apply scaling
# scaled_distance1 = modified_power_scale(distance1, xmin, p)
# scaled_distance2 = modified_power_scale(distance2, xmin, p)

# print("Scaled Distance 1:", scaled_distance1)
# print("Scaled Distance 2:", scaled_distance2)




