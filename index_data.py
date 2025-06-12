from dotenv import load_dotenv
load_dotenv()


import json
import os
from tqdm import tqdm
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


#  $env:AIPROXY_TOKEN = "your_aiproxy_token_here"  Set your AI Proxy token here

# Load TDS and Discourse data
def load_data():
    with open("data/tds_content.json", encoding="utf-8") as f:
        tds_data = json.load(f)
    with open("data/discourse_forum_posts.json", encoding="utf-8") as f:
        discourse_data = json.load(f)
    return tds_data, discourse_data

# Convert TDS + Discourse into Document chunks
def chunk_data(tds_data, discourse_data):
    docs = []

    # For TDS, set source to actual topic URL saved in scrape
    for topic in tqdm(tds_data, desc="TDS"):
        # Expecting each topic dict to have 'url' from updated scrape code
        url = topic.get("url", "https://tds.s-anand.net")
        doc = Document(
            page_content=topic["content"],
            metadata={"title": topic["title"], "source": url}
        )
        docs.append(doc)

    for post in tqdm(discourse_data, desc="Discourse"):
        source = post.get("topic_url", "Unknown")
        title = post.get("title", source)
        doc = Document(
            page_content=post["content"],
            metadata={"title": title, "source": f"Discourse: {source}"}
        )
        docs.append(doc)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

# Embed text using OpenAI embeddings via AI Proxy
def embed_text(docs):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("AIPROXY_TOKEN"),
        base_url="https://aiproxy.sanand.workers.dev/openai/v1"
    )
    return FAISS.from_documents(docs, embeddings)

# Save FAISS index locally
def save_index(index, path="vectorstore"):
    os.makedirs(path, exist_ok=True)
    index.save_local(path)

# Run the indexing pipeline
def index_data():
    print("🔍 Chunking and preparing data...")
    tds_data, discourse_data = load_data()
    all_chunks = chunk_data(tds_data, discourse_data)

    print(f"✍️ Embedding {len(all_chunks)} chunks...")
    vectorstore = embed_text(all_chunks)

    print("💾 Saving vectorstore...")
    save_index(vectorstore)

    print("✅ Indexing complete!")

if __name__ == "__main__":
    index_data()
