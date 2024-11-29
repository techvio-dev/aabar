import pinecone
import json

# Initialize Pinecone with your API key
with open('apis_keys.json') as f:
    data = json.load(f)
api_key = data["pinecone"]["api_key"]
pinecone.init(api_key=api_key)

# Create or connect to an index
index_name = 'water-laws'

# Get the index
index = pinecone.Index(index_name)

from openai import OpenAI
import numpy as np

client = OpenAI(api_key='YOUR_OPENAI_API_KEY')

def generate_embeddings(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def upsert_documents(documents):
    # Prepare vectors for Pinecone
    vectors = []
    for i, doc in enumerate(documents):
        embedding = generate_embeddings(doc)
        vectors.append((
            f"doc_{i}",  # unique ID
            embedding,   # vector representation
            {"text": doc}  # metadata
        ))
    
    # Upsert to Pinecone
    index.upsert(vectors)
    
def retrieve_relevant_context(query, top_k=3):
    # Generate embedding for query
    query_embedding = generate_embeddings(query)
    
    # Perform vector search
    results = index.query(
        query_embedding, 
        top_k=top_k,
        include_metadata=True
    )
    
    # Extract relevant contexts
    contexts = [
        result['metadata']['text'] 
        for result in results['matches']
    ]
    
    return contexts

# RAG completion function
def generate_rag_response(query):
    # Retrieve relevant contexts
    contexts = retrieve_relevant_context(query)
    
    # Prepare prompt with context
    prompt = f"""
    Context: {' '.join(contexts)}
    
    Question: {query}
    
    Answer the question using only the provided context:
    """
    
    # Generate response using OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

# Index some documents
documents = [
    "Pinecone is a vector database for machine learning.",
    "RAG combines retrieval and generation to improve AI responses.",
    "Vector embeddings represent text as dense numerical vectors."
]
upsert_documents(documents)

# Perform RAG
query = "What is Pinecone used for?"
response = generate_rag_response(query)
print(response)