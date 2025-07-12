from frontend.rag.model import DocumentModel
from uuid import uuid4
from decouple import config
from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from frontend.rag.document_retriever import FinnHubScraper
from typing import List
from tqdm import tqdm


def get_mongo_collection(collection_name: str, db_name: str = "financegpt_db"):
    """
    Retrieves or creates a MongoDB collection.

    Args:
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.

    Returns:
        pymongo.collection.Collection: The MongoDB collection instance.
    """
    client = MongoClient(config("MONGODB_URI", default=None))
    print(f"[INFO] Connected to MongoDB: {db_name}, Collection: {collection_name}")
    return client[db_name][collection_name]


def initialize_vector_store():
    """
    Initializes the MongoDB Atlas vector store for semantic search.

    Returns:
        MongoDBAtlasVectorSearch: The initialized vector store instance.
    """
    print("[INFO] Initializing vector store...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    print("[INFO] Embedding model initialized.")

    vector_store = MongoDBAtlasVectorSearch(
        collection=get_mongo_collection("financegpt_vectorstores"),
        embedding=embeddings,
        index_name="finance-gpt-index-vectorstores",
        relevance_score_fn="cosine",
    )
    print("[INFO] Vector store initialized successfully.")
    return vector_store


def bulk_check_duplicates(
    document_urls: List[str], collection_name: str = "financenews_documents"
) -> List[str]:
    """
    Checks for duplicate URLs in bulk.

    Args:
        document_urls (List[str]): List of document URLs to check.
        collection_name (str): The name of the collection to query.

    Returns:
        List[str]: A list of URLs that already exist in the database.
    """
    collection = get_mongo_collection(collection_name)
    existing_docs = collection.find({"url": {"$in": document_urls}}, {"url": 1})
    existing_urls = {doc["url"] for doc in existing_docs}
    print(f"[INFO] Found {len(existing_urls)} duplicate documents.")
    return list(existing_urls)


def store_documents(search_tickers: List[str]):
    """
    Scrapes financial documents, stores them in the database, and updates the vector store.

    Args:
        search_tickers (List[str]): List of stock tickers to search for.
    """
    print("[INFO] Starting document scraping process...")
    vector_store = initialize_vector_store()
    scraper = FinnHubScraper(tickers=search_tickers)
    scraped_documents = scraper.run()
    print(f"[INFO] Scraped {len(scraped_documents)} documents.")

    document_collection = get_mongo_collection("financenews_documents")

    # Extract URLs and check duplicates in bulk
    urls = [doc["url"] for doc in scraped_documents]
    duplicate_urls = set(bulk_check_duplicates(urls))

    # Filter non-duplicate documents
    non_duplicate_docs = [
        DocumentModel(**doc)
        for doc in scraped_documents
        if doc["url"] not in duplicate_urls
    ]
    print(f"[INFO] {len(non_duplicate_docs)} new documents to be added.")

    # Bulk insert into MongoDB
    if non_duplicate_docs:
        docs_to_insert = [doc.model_dump() for doc in non_duplicate_docs]
        document_collection.insert_many(docs_to_insert)
        print(f"[INFO] Inserted {len(docs_to_insert)} new documents into MongoDB.")

        # Prepare documents for vector store
        vector_documents = [
            Document(
                page_content=f"Headline: {doc.headline} Summary: {doc.summary} Ticker: {doc.ticker}",
                metadata={"source": doc.url, "ticker": doc.ticker},
            )
            for doc in non_duplicate_docs
        ]

        # Add documents to vector store in bulk
        uuids = [str(uuid4()) for _ in range(len(vector_documents))]
        for doc, doc_id in tqdm(
            zip(vector_documents, uuids),
            desc="Embedding documents",
            unit="doc",
            total=len(vector_documents),
        ):
            vector_store.add_documents(documents=[doc], ids=[doc_id])
        print("[INFO] All documents added to vector store successfully.")
    else:
        print("[INFO] No new documents to insert.")


def similarity_search(query: str, n: int = 5) -> List[Document]:
    """
    Performs a similarity search using the vector store.

    Args:
        query (str): The search query.
        n (int): Number of results to return.

    Returns:
        List[Document]: A list of documents matching the query.
    """
    print(f"[INFO] Performing similarity search for query: '{query}'")
    vector_store = initialize_vector_store()
    results = vector_store.similarity_search(query, k=n)
    print(f"[INFO] Retrieved {len(results)} results from similarity search.")
    return results


if __name__ == "__main__":
    try:
        # Example query and tickers
        query = "What is the best place to invest today?"
        tickers = ["AAPL", "TSLA"]

        # Store documents and perform a similarity search
        store_documents(tickers)
        search_results = similarity_search(query)

        # Display results
        print("\n[INFO] Search Results:")
        for result in search_results:
            print(result.page_content)
    except Exception as main_error:
        print(f"[ERROR] An error occurred: {main_error}")
