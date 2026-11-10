
import httpx

from typing import Literal

from pydantic import BaseModel, ValidationError

from app.llm import generate_response


class RouteDecision(BaseModel):
    route: Literal["knowledge", "support", "both"]


ROUTER_PROMPT = """
You are the Router Agent of Getnet's payment support system.

Your only task is to classify the user's request.

Available routes:

knowledge:
Questions about Getnet products, services, policies,
technical instructions, or general information.

support:
Questions that only require customer-specific data,
such as transaction history, account details, or sales.

both:
Questions requiring customer-specific information
AND Getnet policies, rules, or general documentation.

IMPORTANT RULE:
If the user asks about a personal transaction, sale,
deposit, or account AND references Getnet policies,
settlement rules, or general service conditions,
you MUST classify the request as "both".

Examples:

User: What payment terminals does Getnet offer?
Output: {"route": "knowledge"}

User: Show me my latest transactions.
Output: {"route": "support"}

User: When will my last sale be deposited according
to Getnet settlement policies?
Output: {"route": "both"}

User: Why was my transaction declined according
to Getnet's payment rules?
Output: {"route": "both"}

Return ONLY a valid JSON object.
Do not answer the user's question.
"""


def route_message(message: str) -> RouteDecision:
    try:
        result = generate_response(
            system_prompt=ROUTER_PROMPT,
            user_message=message,
            response_format=RouteDecision.model_json_schema(),
        )

        return RouteDecision.model_validate_json(result)

    except (ValidationError, ValueError, httpx.HTTPError):
        return RouteDecision(route="knowledge")
