from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from vector_search import similarity_search
from typing import List
from rich import print

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

def retrieve_and_generate_response(query: str, num_retrievals: int = 5) -> str:
    """
    Retrieve relevant documents using similarity search and generate a response
    using a retrieval-augmented generation (RAG) approach.

    Args:
        query (str): The user query for which to generate a response.
        num_retrievals (int): Number of documents to retrieve for augmentation.

    Returns:
        str: The generated response from the LLM.
    """
    # Step 1: Retrieve relevant documents using similarity search
    print(f"Performing similarity search for query: {query}")
    retrieved_docs = similarity_search(query, n=num_retrievals)

    # Step 2: Format the retrieved documents into a single context
    context = "\n".join([f"{doc.page_content}" for doc in retrieved_docs])
    print(f"Retrieved {len(retrieved_docs)} documents for augmentation.")

    # Step 3: Create a chat prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant specialized in finance and stock analysis. Use the provided context to generate accurate responses. Based on the following context: {context}, Generate an  indepth analsyis answer for the user.",
            ),
            ("human", "{query}"),
        ]
    )

    # Step 4: Chain the prompt with the LLM
    chain = prompt_template | llm

    # Step 5: Invoke the chain with context and query
    try:
        print("Generating response...")
        response = chain.invoke({"context": context, "query": query})
        print("Response generation completed.")
        return response.content
    except Exception as e:
        print(f"Error during response generation: {e}")
        return "An error occurred while generating the response."

# Example Usage
if __name__ == "__main__":
    # Sample query
    user_query = "What are the latest insights on Apple's stock performance?"

    # Retrieve and generate response
    output = retrieve_and_generate_response(user_query, num_retrievals=10)
    print("\nGenerated Response:\n", output)
