# FastAPI Documentation RAG with Gemini

This project is a Retrieval-Augmented Generation (RAG) system that answers questions about FastAPI using the official documentation and Google's Gemini models.

## Key Features

*   Answers questions about FastAPI based on official documentation.
*   Uses Gemini models for question answering.
*   Retrieval augmented generation using Haystack and Sentence Transformers.
*   Interactive command-line interface for querying.

## Setup

1.  **Clone the repository:** `git clone <repository_url>`
2.  **Install dependencies:** `pip install -r requirements.txt`
3.  **Set Google API Key:** Create a `.env` file with `GOOGLE_API_KEY=YOUR_API_KEY_HERE`.
4.  **Scrape documentation:** `python scraper.py`
5.  **Process documents and create document store (run once):** `python gemini_rag.py`

## Usage
Run the scraper.py to scrape official documentation 

Run the interactive script: `python gemini_rag.py`

Enter queries when prompted, e.g., "How do I define query parameters in FastAPI?". Type `exit` to quit.

 

## Project Files

*   **`gemini_rag.py`:** Main RAG script - loads data, sets up pipeline, queries Gemini, and runs interactive mode.
*   **`preprocessing_pipeline.py`:** Sets up Haystack preprocessing pipeline for documents.
*   **`scraper.py`:** Crawls and scrapes FastAPI documentation website.
*   **`requirements.txt`:** Python dependencies.

## Models and Libraries

*   **LLM:** Google Gemini (default: `gemini flash 2.0`)
*   **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
*   **Libraries:** Haystack-ai, Google Generative AI, BeautifulSoup4, requests, python-dotenv

## Potential Improvements 

*   Persistent document store (e.g., Elasticsearch).
*   API endpoint for web service access.
*   Direct repo integration of target library

 
