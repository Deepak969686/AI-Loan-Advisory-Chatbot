import math


class LoanUtils:
    """
    Loan Utility Functions
    """

    @staticmethod
    def calculate_emi(
        principal: float,
        annual_interest_rate: float,
        tenure_years: int,
    ):

        monthly_rate = annual_interest_rate / (12 * 100)

        months = tenure_years * 12

        if monthly_rate == 0:

            emi = principal / months

        else:

            emi = (
                principal
                * monthly_rate
                * math.pow(1 + monthly_rate, months)
            ) / (
                math.pow(1 + monthly_rate, months) - 1
            )

        total_payment = emi * months

        total_interest = total_payment - principal

        return {
            "monthly_emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
        }