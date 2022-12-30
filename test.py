from sentence_transformers import SentenceTransformer, util
import torch
import torch.nn as nn
import torch.nn.functional as F

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# sentences = ["AC/DC thunder", "AC/DC - Back In Black (Official Video)"]
# #Compute embedding for both lists
# embedding_1= model.encode(sentences[0], convert_to_tensor=True)
# embedding_2 = model.encode(sentences[1], convert_to_tensor=True)

# print(util.pytorch_cos_sim(embedding_1, embedding_2))

# sentences = ["AC/DC thunder", "AC/DC - Thunderstruck (Official Video)"]
# #Compute embedding for both lists
# embedding_1= model.encode(sentences[0], convert_to_tensor=True)
# embedding_2 = model.encode(sentences[1], convert_to_tensor=True)

# print(util.pytorch_cos_sim(embedding_1, embedding_2))

sentence = "AC/DC thunder"
sentences = [
    "AC/DC - Back In Black (Official Video)",
    "AC/DC - Thunderstruck (Official Video)",
    "Top 20 Best Songs Of A C / D C 💥💥💥 A C / D C Greatest Hits Full Album 2021",
    "AC/DC Greatest Hits | Top 10 Mejores Canciones",
    "AC/DC | ROCK",
]
embedding_1 = model.encode(sentence, convert_to_tensor=True)
embeddings = model.encode(sentences, convert_to_tensor=True)


similarities = []
for embedding in embeddings:
    similarities.append(F.cosine_similarity(embedding_1, embedding, dim=0))

similarities = torch.stack(similarities)
print(similarities)


def find_most_similar(sentence, sentences):
    print(sentence)
    print(sentences)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    pivot_embedding = model.encode(sentence, convert_to_tensor=True)
    embeddings = model.encode(sentences, convert_to_tensor=True)

    similarities = []
    for embedding in embeddings:
        similarities.append(F.cosine_similarity(pivot_embedding, embedding, dim=0))

    similarities = torch.stack(similarities)
    max_idx = torch.argmax(similarities)

    print(similarities)
    print(max_idx)

    return sentences[max_idx]


find_most_similar(sentence, sentences)
