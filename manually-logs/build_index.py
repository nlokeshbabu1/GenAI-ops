from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import pickle

FILE_PATH = "latest-saas.logs"

#load the logs 

with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    logs = f.read()

# Split logs into chunks

def chunk_logs(logs, chunk_size=1000):
    return [logs[i:i+chunk_size] for i in range(0, len(logs), chunk_size)]

print("Total chunks:", len(chunk_logs(logs)))

# Create embeddings model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(chunk_logs(logs))
embeddings = np.array(embeddings).astype('float32')

#create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

#save faiss index and chunks
faiss.write_index(index, 'logs_index.faiss')

#save chunks
with open('logs_chunks.pkl', 'wb') as f:
    pickle.dump(chunk_logs(logs), f)

print("Index and chunks saved successfully.")