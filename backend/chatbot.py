from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import (
    GOOGLE_API_KEY,
    LLM_MODEL
)

from backend.rag import RAGPipeline

class LoanChatbot:
    """
    AI Loan Advisory Chatbot
    """

    def __init__(self, rag_pipeline):

        self.rag = rag_pipeline

        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an AI Loan Advisory Assistant.

Your job is to answer ONLY using the provided loan policy context.

RULES

1. Never make up information.

2. Never guess.

3. If the answer is NOT available in the context,
reply exactly:

"I couldn't find this information in the uploaded loan documents."

4. Answer professionally.

5. Use bullet points whenever appropriate.

6. Mention eligibility conditions if available.

7. Mention loan limits if available.

8. Never mention information outside the context.
                    """
                ),
                (
                    "human",
                    """
Context:

{context}

----------------------------------------

Question:

{question}

Answer:
                    """
                )
            ]
        )

        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

    # =========================================================
    # Ask Question
    # =========================================================

    def ask(self, question: str):

        try:

            search_result = self.rag.search(question)

            context = search_result["context"]

            sources = search_result["sources"]

            if len(context.strip()) == 0:

                return {
                    "answer":
                    "I couldn't find this information in the uploaded loan documents.",
                    "sources": []
                }
            
            
            print("=" * 80)
            print("QUESTION:")
            print(question)

            print("=" * 80)
            print("CONTEXT:")
            print(context[:5000])   # print first 5000 characters

            print("=" * 80)

            answer = self.chain.invoke(
                {
                    "context": context,
                    "question": question
                }
            )

            return {
                "answer": answer,
                "sources": sources
            }

        except Exception as e:

            return {
                "answer": f"Error : {str(e)}",
                "sources": []
            }

    # =========================================================
    # Format Sources
    # =========================================================

    @staticmethod
    def format_sources(sources):

        if not sources:
            return "No sources found."

        formatted = []

        for source in sources:

            formatted.append(
                f"• {source['source']} (Page {source['page']})"
            )

        return "\n".join(formatted)

    # =========================================================
    # Pretty Response
    # =========================================================

    def ask_pretty(self, question):

        response = self.ask(question)

        return f"""
{response['answer']}

-------------------------------------

Sources

{self.format_sources(response['sources'])}
"""