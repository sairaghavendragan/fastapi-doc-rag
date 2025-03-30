from haystack import document
from haystack.components.writer import document_writer
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack import Pipeline
import os
import re
import ast

def initialize_document_store():
    return InMemoryDocumentStore(duplicate_documents='skip')

 
def create_preprocessing_pipeline(document_store):
    preprocessing_pipeline = Pipeline()

    document_embedder = SentenceTransformersDocumentEmbedder(model = "sentence-transformers/all-MiniLM-L6-v2")
    document_writer = document_writer(document_store=document_store)
    
    preprocessing_pipeline.add_component("document_embedder", document_embedder)
    preprocessing_pipeline.add_component("document_writer", document_writer)
    preprocessing_pipeline.connect("document_embedder", "document_writer")
    return preprocessing_pipeline

def process_documents (docs_dir):
    document_store = initialize_document_store()
    preprocessing_pipeline = create_preprocessing_pipeline(document_store=document_store)
    documents = load_documents(docs_dir)
    if documents:
        preprocessing_pipeline.run({
    "document_embedder": {"documents": documents}
    })
    return document_store 

def load_documents(docs_dir):
    documents = []
     
    doc_count = 0

    """Load scraped documents from text files"""
 
    for filename in os.listdir(docs_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(docs_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                pages = content.split('=' * 80)

                for page in pages:
                    if not page.strip():
                        continue

                    # Extract metadata and content
                    url_match = re.search(r'url: (.*?)$', page, re.MULTILINE)
                    #print(url_match)
                    title_match = re.search(r'title: (.*?)$', page, re.MULTILINE)
                    content_match = re.search(r'content: ({.*?})\n---' , page, re.MULTILINE | re.DOTALL)

                    if url_match and title_match and content_match:
                        url = url_match.group(1).strip()
                        title = title_match.group(1).strip()
                        content_str = content_match.group(1).strip()

                        try:
                            # Use ast.literal_eval instead of json.loads
                            content_dict = ast.literal_eval(content_str)

                            # Format content for better processing
                            text_content = "\n\n".join(content_dict.get('text', []))
                            code_blocks = []
                            for block in content_dict.get('code_blocks', []):
                                lang = block.get('language', '')
                                code = block.get('code', '')
                                code_blocks.append(f"```{lang}\n{code}\n```")

                            full_content = text_content
                            if code_blocks:
                                full_content += "\n\n" + "\n\n".join(code_blocks)

                            # Create Document directly
                            unique_id = f"{url}_{doc_count}"
                            doc_count += 1
                            documents.append(Document(
                                id=unique_id,
                                content=full_content,
                                meta={"url": url, "title": title}
                            ))
                            #print(f"Loaded document from {filename}")
                             
                        except (SyntaxError, ValueError) as e:
                            print(f"Error parsing content in {filename}: {e}")
    return documents


