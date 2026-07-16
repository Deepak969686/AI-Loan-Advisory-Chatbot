from backend.chatbot import LoanChatbot

bot = LoanChatbot()

response = bot.ask(
    "What is the minimum age for a home loan?"
)

print(response["answer"])

print()

print(response["sources"])