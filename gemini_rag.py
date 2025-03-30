import os
import google.generativeai as genai
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack import Pipeline
import pickle
from .preprocessing_pipeline import process_documents
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
client  = genai.Client(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')

def load_document_store():
    store_path = os.path.join(os.getcwd(), 'document_store.pkl')
    if os.path.exists(store_path):
        with open(store_path, 'rb') as file:
            document_store = pickle.load(file)
        return document_store       
    else:
        docs_dir = os.path.join(os.getcwd () , 'docs')
        document_store = process_documents(docs)
        with open(store_path, 'wb') as file:
            pickle.dump(document_store, file)
        return document_store

def create_retrieval_pipeline(document_store):
    """Create a retrieval pipeline using Haystack components"""
    retriever = InMemoryEmbeddingRetriever(document_store=document_store)
    query_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")

    retrieval_pipeline = Pipeline()
    retrieval_pipeline.add_component("query_embedder", query_embedder)
    retrieval_pipeline.add_component("retriever", retriever)
    retrieval_pipeline.connect("query_embedder", "retriever")
    
    return retrieval_pipeline

def format_retrieved_documents(documents, max_length=8000):
    """Format retrieved documents for the LLM context"""
    context = []
    current_length = 0
    
    for doc in documents:
        # Extract content based on type
        if isinstance(doc.content, dict):
            text_content = ' '.join(doc.content.get('text', []))
            code_blocks = doc.content.get('code_blocks', [])
            
            doc_text = text_content
            for block in code_blocks:
                if block['code'].strip():
                    doc_text += f"\n\n```{block['language']}\n{block['code']}\n```"
        else:
            doc_text = doc.content
        
        # Add metadata
        doc_entry = f"URL: {doc.meta.get('url', 'N/A')}\nTitle: {doc.meta.get('title', 'N/A')}\n\n{doc_text}"
        
        # Check if adding this document would exceed max length
        if current_length + len(doc_entry) > max_length:
            # If we already have some context, stop adding more
            if context:
                break
            # If this is the first document, truncate it
            doc_entry = doc_entry[:max_length]
        
        context.append(doc_entry)
        current_length += len(doc_entry)
    
    return "\n\n---\n\n".join(context)    

def query_gemini(query, context, model="gemini-2.0-flash"):
    """Query the Gemini model with retrieved context"""
    try:
        #model = genai.GenerativeModel(model)
        
        prompt = f"""You are an expert FastAPI assistant. Answer the following question based on the provided documentation context.
        
                    Question: {query}

                    Context:
                    {context}

                    Instructions:
                    1. Answer the question based only on the provided context
                    2. If the context doesn't contain relevant information, say "I don't have enough information to answer this question"
                    3. Include code examples when relevant
                    4. Format your response using markdown
                    5. Be concise but thorough
                    """
        
        response = client.models.generate_content(model = model,contents = prompt)
        return response.text
    except Exception as e:
        return f"Error querying Gemini: {str(e)}"

def fastapi_rag(query, top_k=3):
    """Complete RAG pipeline for FastAPI documentation"""
    # Load document store
    
    
    # Retrieve relevant documents
    print(f"Query: {query}")
    results = retrieval_pipeline.run({
        "query_embedder": {"text": query},
        "retriever": {"top_k": top_k}
    })
    
    retrieved_docs = results["retriever"]["documents"]
    print(f"Retrieved {len(retrieved_docs)} documents")
    
    # Format documents for context
    context = format_retrieved_documents(retrieved_docs)
    
    # Query Gemini with context
    answer = query_gemini(query, context)
    
    return {
        "query": query,
        "answer": answer,
        "sources": [{"url": doc.meta.get("url"), "title": doc.meta.get("title")} for doc in retrieved_docs]
    }

if __name__ == "__main__":
    document_store = load_document_store()
    
    # Create retrieval pipeline
    retrieval_pipeline = create_retrieval_pipeline(document_store)

    while True:
        user_query = input("Enter your query (or 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        result = fastapi_rag(user_query)
        print("\nAnswer:")
        print(result["answer"])
        print("-"*40) 
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source['title']} ({source['url']})")

    # Test queries
     