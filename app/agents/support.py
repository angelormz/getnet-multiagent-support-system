
import json

from app.llm import generate_response
from app.tools.customer import get_customer, get_transactions


SUPPORT_PROMPT = """
You are Getnet's Customer Support Agent.

Use only the simulated customer data provided
by the backend tools.

Rules:
- Never invent transactions, amounts, or dates.
- Never reveal another customer's information.
- If deposit_status is "pending" and deposit_date
  is null, state that no deposit date is confirmed.
- Distinguish pending deposits from completed ones.
- Do not assume that a completed deposit is
  necessarily the customer's latest sale.
- Clearly identify transaction IDs when relevant.
- Explain that customer records are simulated.
- Answer in the same language as the customer.
- Return only the final answer.
- Do not include reasoning or <think> tags.
"""


def handle_support(message: str, user_id: str) -> dict:
    customer = get_customer(user_id)

    if "error" in customer:
        return {
            "answer": "Customer not found.",
            "status": "insufficient_information",
        }

    transactions = get_transactions(user_id)

    context = {
        "customer": customer,
        "transactions": transactions,
    }

    answer = generate_response(
        system_prompt=SUPPORT_PROMPT,
        user_message=(
            f"Customer question: {message}\n\n"
            f"Verified tool data:\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        ),
    )

    return {
        "answer": answer,
        "status": "success",
    }
