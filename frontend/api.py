import requests

BASE_URL = "https://ai-loan-advisory-chatbot-qp37.onrender.com"


class LoanAPI:
    """
    Frontend API Wrapper
    """

    @staticmethod
    def health():
        response = requests.get(
            f"{BASE_URL}/health"
        )
        return response.json()

    # ==========================================
    # Upload Documents
    # ==========================================

    @staticmethod
    def upload_documents(files):

        file_data = []

        for file in files:

            file_data.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        "application/pdf"
                    )
                )
            )

        response = requests.post(
            f"{BASE_URL}/upload",
            files=file_data
        )

        return response.json()

    # ==========================================
    # Chat
    # ==========================================

    @staticmethod
    def chat(question):

        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "question": question
            }
        )

        return response.json()

    # ==========================================
    # EMI Calculator
    # ==========================================

    @staticmethod
    def calculate_emi(
        principal,
        annual_interest_rate,
        tenure_years
    ):

        response = requests.post(
            f"{BASE_URL}/emi",
            json={
                "principal": principal,
                "annual_interest_rate": annual_interest_rate,
                "tenure_years": tenure_years
            }
        )

        return response.json()

    # ==========================================
    # List Documents
    # ==========================================

    @staticmethod
    def documents():

        response = requests.get(
            f"{BASE_URL}/documents"
        )

        return response.json()

    # ==========================================
    # Reindex
    # ==========================================

    @staticmethod
    def reindex():

        response = requests.post(
            f"{BASE_URL}/reindex"
        )

        return response.json()