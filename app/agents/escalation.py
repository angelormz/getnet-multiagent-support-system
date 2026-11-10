import re
from app.tools.tickets import create_ticket

ESCALATION_RULES = {
    "human_requested": [
        r"\b(hablar|comunicarme|contactar)\s+con\s+(una?\s+)?(persona|humano|agente|asesor|operador)\b",
        r"\b(agente humano|asesor humano|atención humana)\b",
        r"\b(human agent|live agent|real person)\b",
    ],
    "suspected_fraud": [
        r"\b(fraude|fraudulento|fraud)\b",
        r"\b(cargo|transacci[oó]n|compra)\s+no\s+reconocid[ao]\b",
        r"\b(unauthorized charge|unauthorized transaction)\b",
    ],
    "manual_review": [
        r"\b(escalar|escalamiento|escalate)\b",
        r"\b(revisi[oó]n humana|revisi[oó]n manual|manual review)\b",
        r"\b(reembolso|refund|contracargo|chargeback)\b",
    ],
}


def evaluate_escalation(message: str) -> dict:
    """
    Detect requests requiring human review.
    """

    for reason, patterns in ESCALATION_RULES.items():
        for pattern in patterns:
            if re.search(
                pattern,
                message,
                flags=re.IGNORECASE,
            ):
                return {
                    "requires_escalation": True,
                    "reason": reason,
                }

    return {
        "requires_escalation": False,
        "reason": None,
    }



def handle_escalation(
    message: str,
    user_id: str,
) -> dict:

    evaluation = evaluate_escalation(message)

    if not evaluation["requires_escalation"]:
        return {
            "requires_escalation": False,
            "status": "success",
        }

    ticket = create_ticket(
        user_id=user_id,
        message=message,
        reason=evaluation["reason"],
    )

    return {
        "requires_escalation": True,
        "case_id": ticket["ticket_id"],
        "user_id": user_id,
        "reason": evaluation["reason"],
        "status": "pending_human_review",
        "answer": (
            "Tu solicitud requiere revisión humana. "
            f"Se registró el caso {ticket['ticket_id']} "
            "en nuestro sistema de demostración. "
            "No se ha enviado a un operador real."
        ),
    }
