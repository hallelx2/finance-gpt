from frontend.rag.model import FinancialAnswer, NewsItem
from frontend.rag.utils import (
    extract_tickers_from_query,
    format_news_for_context,
    rank_news_by_relevance,
)
from frontend.rag.vector_search import similarity_search
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from rich import print

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Initialize the structured output parser
parser = PydanticOutputParser(pydantic_object=FinancialAnswer)


def retrieve_and_generate_response(
    query: str, num_retrievals: int = 5
) -> FinancialAnswer:
    """
    Retrieve relevant documents using similarity search and generate a structured response
    using a retrieval-augmented generation (RAG) approach.

    Args:
        query (str): The user query for which to generate a response.
        num_retrievals (int): Number of documents to retrieve for augmentation.

    Returns:
        FinancialAnswer: The structured response from the LLM.
    """
    try:
        # Step 1: Extract tickers from the query
        print(f"Extracting tickers from query: {query}")
        ticker_extraction = extract_tickers_from_query(query)
        print(
            f"Extracted tickers: {ticker_extraction.tickers} (confidence: {ticker_extraction.confidence:.2f})"
        )

        # Step 2: Retrieve relevant documents using similarity search
        print(f"Performing similarity search for query: {query}")
        retrieved_docs = similarity_search(query, n=num_retrievals)
        print(f"Retrieved {len(retrieved_docs)} documents for augmentation.")

        # Step 3: Convert retrieved documents to news items format
        news_items = []
        for doc in retrieved_docs:
            # Extract information from document metadata and content
            metadata = doc.metadata
            content = doc.page_content

            # Parse content to extract headline and summary
            # Assuming content format: "Headline: ... Summary: ... Ticker: ..."
            headline = ""
            summary = ""
            ticker = metadata.get("ticker", "")

            if "Headline:" in content:
                parts = content.split("Summary:")
                if len(parts) >= 2:
                    headline = parts[0].replace("Headline:", "").strip()
                    summary_part = parts[1].split("Ticker:")[0].strip()
                    summary = summary_part

            news_items.append(
                {
                    "headline": headline or "No headline available",
                    "summary": summary or "No summary available",
                    "ticker": ticker,
                    "source": metadata.get("source", "Unknown"),
                    "relevance_score": getattr(doc, "relevance_score", 0.0),
                }
            )

        # Step 4: Rank news items by relevance
        ranked_news = rank_news_by_relevance(
            news_items, query, ticker_extraction.tickers
        )

        # Step 5: Format context for LLM
        context = format_news_for_context(ranked_news)

        # Step 6: Create a structured prompt template
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert financial analyst specializing in stock market analysis and investment insights.
                Your task is to provide comprehensive, accurate, and actionable financial analysis based on the latest market data.

                Based on the following context from recent financial news and data, provide a structured analysis that includes:
                1. A clear, concise summary answering the user's question
                2. Key insights and important points (as bullet points)
                3. The most relevant news items with their details
                4. All stock tickers mentioned in your analysis
                5. Overall market sentiment (positive/negative/neutral)
                6. Your confidence level in the analysis (0.0 to 1.0)
                7. Brief market outlook if relevant

                Context from recent financial news:
                {context}

                User's query type: {query_type}
                Extracted tickers: {tickers}

                {format_instructions}

                Be objective, data-driven, and provide specific examples from the news when possible.
                If information is limited, acknowledge this in your confidence score.
                """,
                ),
                ("human", "{query}"),
            ]
        )

        # Step 7: Create the chain with structured output
        chain = prompt_template | llm | parser

        # Step 8: Invoke the chain with all necessary parameters
        print("Generating structured response...")
        response = chain.invoke(
            {
                "context": context,
                "query": query,
                "query_type": ticker_extraction.query_type,
                "tickers": (
                    ", ".join(ticker_extraction.tickers)
                    if ticker_extraction.tickers
                    else "None specified"
                ),
                "format_instructions": parser.get_format_instructions(),
            }
        )

        # Step 9: Enhance the response with additional metadata
        if isinstance(response, FinancialAnswer):
            # Ensure mentioned_tickers includes extracted tickers
            all_tickers = set(response.mentioned_tickers + ticker_extraction.tickers)
            response.mentioned_tickers = list(all_tickers)

            # Convert news items to structured format
            structured_news = []
            for item in ranked_news[:5]:  # Top 5 most relevant
                structured_news.append(
                    NewsItem(
                        headline=item["headline"],
                        summary=item["summary"],
                        ticker=item["ticker"],
                        source=item["source"],
                        relevance_score=item.get("relevance_score", 0.0),
                    )
                )
            response.top_news = structured_news

        print("Structured response generation completed.")
        return response

    except Exception as e:
        print(f"Error during response generation: {e}")
        # Return a fallback structured response
        return FinancialAnswer(
            summary=f"I apologize, but I encountered an error while processing your query: {str(e)}",
            key_insights=["Unable to process query due to technical error"],
            top_news=[],
            mentioned_tickers=[],
            sentiment="neutral",
            confidence_score=0.0,
            market_outlook="Unable to provide outlook due to error",
        )


def generate_simple_response(query: str) -> str:
    """
    Generate a simple string response (for backward compatibility).

    Args:
        query (str): The user query

    Returns:
        str: Simple text response
    """
    structured_response = retrieve_and_generate_response(query)
    return structured_response.summary


# Example Usage
if __name__ == "__main__":
    # Sample queries
    test_queries = [
        "What are the latest insights on Apple's stock performance?",
        "How is Tesla doing in the market today?",
        "What's the overall market sentiment for tech stocks?",
        "Should I invest in MSFT or GOOGL?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Generate structured response
        response = retrieve_and_generate_response(query, num_retrievals=3)

        print(f"\nSummary: {response.summary}")
        print(f"Key Insights: {response.key_insights}")
        print(f"Mentioned Tickers: {response.mentioned_tickers}")
        print(f"Sentiment: {response.sentiment}")
        print(f"Confidence: {response.confidence_score}")
        print(f"Top News Count: {len(response.top_news)}")

        if response.top_news:
            print("\nTop News:")
            for i, news in enumerate(response.top_news[:3], 1):
                print(f"{i}. {news.headline} ({news.ticker})")
