from gpt4all import GPT4All
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle

#load the embeddings model
embeddings_model = SentenceTransformer('all-MiniLM-L6-v2', )

#load the faiss index and chunks
index = faiss.read_index('logs_index.faiss')

#load the chunks
with open('logs_chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

#load the GPT4All model
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", n_ctx=2048)


#Retrieval function
# def retrieve_logs(question, k=5):
#     q_emb = embedder.encode([question]).astype("float32")
#     distances, indices = index.search(q_emb, k)
#     return "\n".join([chunks[i] for i in indices[0]])

# ...existing code...
def retrieve_logs(question, k=2):
    # use the correct SentenceTransformer instance and ensure a 2D float32 vector
    q_emb = embeddings_model.encode([question])
    q_emb = np.asarray(q_emb, dtype="float32")
    if q_emb.ndim == 1:
        q_emb = q_emb.reshape(1, -1)
    distances, indices = index.search(q_emb, k)
    return "\n".join([chunks[i] for i in indices[0]])


#Ask question
question = "Why are we getting HTTP 503 errors?"

context = retrieve_logs(question)

prompt = f"""
You are a senior SRE engineer.

Analyze logs and answer the question.

Question:
{question}

Logs:
{context}

Give:
- Root cause
- Evidence
- Fix
"""

with model.chat_session():
    response = model.generate(
        prompt,
        max_tokens=512,
        temp=0.0
    )

print(response)