from backend.loan_utils import LoanUtils

emi = LoanUtils.calculate_emi(
    principal=500000,
    annual_interest_rate=8.5,
    tenure_years=10,
)

print(emi)

eligibility = LoanUtils.check_eligibility(
    age=28,
    monthly_income=70000,
    credit_score=760,
    loan_amount=2500000,
)

print(eligibility)