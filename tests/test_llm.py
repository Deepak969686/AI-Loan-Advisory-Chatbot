from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

response = llm.invoke("Say Hello")

print(response.content)