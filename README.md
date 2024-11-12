# **Financial Market Insights RAG System**
## Overview

### Problem Statement

In the fast-paced world of finance, information changes by the minute. Investors, analysts, and finance professionals need access to the latest market data and insights to make informed decisions. However, traditional sources of financial news and data often lack the ability to deliver insights in real time or tailored to specific user questions. Information such as breaking news, stock performance updates, and corporate announcements may not be readily accessible in a centralized way, and large language models (LLMs) typically lack real-time access to this data. This gap can lead to outdated insights and suboptimal decisions, especially when relying solely on static knowledge from LLMs.

### Solution

Our solution is a **Real-Time Financial Market Insights Retrieval-Augmented Generation (RAG) System** that provides users with up-to-date answers to their finance-related questions, driven by the latest data scraped from reputable finance sources. By combining a robust RAG pipeline with a daily web scraping job, we ensure that the data used for insights is current and relevant.

Here’s how the system works:
- **Scraping and Data Storage**: Each day, a **Scrapy** job scrapes the latest financial data (e.g., stock prices, market news, company updates) from popular finance websites. This data is stored in **MongoDB Atlas**, which serves as a reliable storage for both raw data and vector embeddings.
- **Embedding and Vector Search**: The scraped data is processed using **Amazon Bedrock embeddings**, which generate vector representations of the text data. These embeddings are stored in **MongoDB Atlas Vector Store**, allowing for fast, similarity-based retrieval of relevant information.
- **RAG Pipeline for Real-Time Insights**: We use **LangChain** to orchestrate the retrieval-augmented generation process. When a user asks a question, LangChain searches the MongoDB Vector Store to find the most relevant recent information and uses **OpenAI** to generate a coherent answer based on that data.
- **Interactive Frontend with Reflex**: Users interact with the system via a user-friendly **Reflex** frontend. This web application allows users to input their finance-related questions and receive real-time answers, providing an intuitive experience that makes complex data easy to access and understand.

### Benefits

This RAG system empowers users to:
- Access up-to-date financial insights tailored to their specific questions.
- Make informed investment and business decisions based on the latest available data.
- Gain a competitive advantage by staying informed in a rapidly changing market.

## Project Features

- **Daily Data Scraping**: Scrapes financial data daily from popular finance websites (like Yahoo Finance or Bloomberg) using **Scrapy**, ensuring users receive the most recent information.
- **Embedding and Storage**: Uses **Amazon Bedrock embeddings** to generate vector embeddings for each data point, stored in **MongoDB Atlas Vector Store** for efficient, similarity-based retrieval.
- **Real-Time Retrieval and Answer Generation**: Utilizes **LangChain** to build a RetrievalQA pipeline, retrieving relevant information from MongoDB Atlas and generating responses with **OpenAI**.
- **Streamlit Frontend**: A user-friendly **Streamlit** interface allows users to ask questions and receive answers about the financial market.
- **Logging and Monitoring**: **LangSmith** provides logging and tracing to monitor interactions and ensure the system performs effectively.

## Tech Stack

- **MongoDB Atlas** (Vector Store): Primary data store and vector storage for fast, similarity-based retrieval.
- **Amazon Bedrock Embeddings**: Generates embeddings for financial data to be stored in MongoDB Atlas.
- **OpenAI**: Language model used to generate responses based on retrieved data.
- **LangChain**: Framework to handle the RAG pipeline, integrating retrieval, LLM, and embedding components.
- **LangSmith**: For logging and tracing interactions in the pipeline.
- **Scrapy**: Web scraping tool to gather fresh financial data daily.
- **Reflex**: Frontend framework for the user interface.

## Architecture

The project is built around a **Retrieval-Augmented Generation (RAG)** architecture. The pipeline is designed as follows:

1. **Data Collection**:
   - **Scrapy Spider** runs daily to fetch the latest financial news, stock prices, and company updates.
   - Data is stored in **MongoDB Atlas**.

2. **Embedding Generation**:
   - **Amazon Bedrock embeddings** are used to create vector representations of the text data.
   - These embeddings are stored in **MongoDB Atlas Vector Store** for fast, similarity-based search.

3. **Retrieval-Augmented Generation Pipeline**:
   - **LangChain** is used to build the RetrievalQA chain, retrieving relevant documents based on user queries.
   - The retrieved documents are passed to **OpenAI**, which generates answers based on the data.
   - **LangSmith** logs and monitors each interaction to ensure performance.

4. **Frontend Interface**:
   - **Reflex** provides an interactive UI for users to input questions and receive answers in real-time.

## Installation and Setup

### Prerequisites

- **Python 3.8+**
- **MongoDB Atlas** account with vector storage enabled
- **Amazon Bedrock** account for embedding generation
- **OpenAI API Key** for retrieval and generation
- **LangSmith** account for tracing and logging
- **Reflex** for the frontend

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/hallelx2/mongodb-ai-hackathon.git
   cd mongodb-ai-hackathon
   ```

2. **Install dependencies**:

   ```bash
   # Install `pipenv` for managing the virtual environment
   pip3 install pipenv # For macOS and Linux users
   pip install pipenv # For windows users

   # Create the virtual environent and activate it
   pipenv shell
   # Install all the dependencies from the pipfile
   pipenv install
   ```

3. **Environment Configuration**:

   Create a `.env` file to store your configuration variables:

   ```plaintext
   MONGO_URI="your_mongodb_atlas_uri"
   DB_NAME="your_database_name"
   AMAZON_BEDROCK_API_KEY="your_amazon_bedrock_api_key"
   OPENAI_API_KEY="your_openai_api_key"
   LANGSMITH_API_KEY="your_langsmith_api_key"
   ```

4. **Setup MongoDB Collection and Index**:

   - In MongoDB Atlas, create a collection (e.g., `news`) and enable vector indexing for fast retrieval.
   - Ensure the `embedding` field is indexed for similarity search.

### Running the Application

1. **Run the Scrapy Spider**:

   ```bash
   scrapy crawl finance_news
   ```

   This command will scrape financial news and store it in MongoDB. Schedule this script with **cron** or **Celery** to ensure daily scraping.

2. **Embed and Store Data**:

   After running the spider, generate and store embeddings for the newly scraped data:

   ```bash
   python embed_and_store.py
   ```

3. **Start the Streamlit Application**:

   ```bash
   streamlit run main.py
   ```

   This command will start the frontend. Access the app at `http://localhost:8501`.

---

## Usage

- **Step 1**: Open the Streamlit app and enter a question in the input box. For example, "What are the latest updates on Tesla stock?" or "How did the stock market perform today?"
- **Step 2**: The RAG pipeline retrieves relevant documents from MongoDB, processes them with OpenAI, and returns a generated response.
- **Step 3**: View the answer on the Streamlit app, which displays real-time insights based on the latest scraped data.

## Project Files

- `financial_scraper/spiders/finance_news_spider.py`: Scrapy spider to collect financial data daily.
- `embed_and_store.py`: Script to generate embeddings with Amazon Bedrock and store them in MongoDB.
- `rag_pipeline.py`: Defines the RAG pipeline using LangChain and LangSmith for monitoring.
- `main.py`: Streamlit frontend for user interaction.
- `.env`: Configuration file (not included for security reasons).

## Key Considerations

- **Data Freshness**: The Scrapy spider runs daily to ensure the data is up-to-date, which is crucial for timely financial insights.
- **Scalability**: MongoDB Atlas and Amazon Bedrock support scaling as data grows, ensuring efficient embedding storage and retrieval.
- **Monitoring**: LangSmith logging and tracing enable effective monitoring and debugging of the RAG pipeline.
- **Privacy and Security**: Environment variables (API keys, MongoDB URI) are stored securely and not hard-coded in the codebase.

## Future Improvements

1. **Enhanced Scraping Coverage**: Expand the Scrapy spider to pull data from more sources.
2. **Sentiment Analysis**: Use sentiment analysis on news articles to provide positive or negative sentiment indicators.
3. **Performance Optimization**: Explore batch processing for embedding generation and retrieval to improve performance with large data volumes.
4. **User Authentication**: Add user authentication to control access to the financial insights.

## Conclusion

This Financial Market RAG System combines the power of **MongoDB Atlas Vector Store**, **Amazon Bedrock embeddings**, and **OpenAI’s** language model to provide real-time, accurate financial insights. By leveraging **LangChain** for retrieval orchestration and **LangSmith** for monitoring, this project serves as a scalable and robust solution for the finance domain, where timely data is essential. The user-friendly **Streamlit** interface makes it accessible to a broad audience, from casual users to financial analysts.

This project demonstrates the capabilities of MongoDB Atlas Vector Store and Amazon Bedrock embeddings in delivering high-quality, real-time information for a dynamic and rapidly changing domain like finance.

---

**Built with 💚 for the MongoDB AI Hackathon.**
