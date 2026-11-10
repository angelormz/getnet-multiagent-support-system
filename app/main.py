
from fastapi import FastAPI, HTTPException

from app.schemas import ChatRequest, ChatResponse
from app.agents.router import route_message
from app.agents.support import handle_support
from app.agents.knowledge import handle_knowledge
from app.agents.escalation import handle_escalation


app = FastAPI(
    title="Getnet Multi-Agent Support System",
    description="Multi-agent customer support API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):


    # Se evalua el escalamiento antes del routing.
    escalation = handle_escalation(
        message=request.message,
        user_id=request.user_id,
    )

    if escalation["requires_escalation"]:
        return ChatResponse(
            answer=escalation["answer"],
            agents_used=["escalation"],
            sources=[],
            status="pending_human_review",
        )


    # 1. Router Agent: clasifica la consulta.
    decision = route_message(request.message)

    # 2. Customer Support Agent
    if decision.route == "support":

        result = handle_support(
            message=request.message,
            user_id=request.user_id,
        )

        return ChatResponse(
            answer=result["answer"],
            agents_used=["router", "support"],
            sources=[],
            status=result["status"],
        )

    # 3. Knowledge Agent
    elif decision.route == "knowledge":

        result = handle_knowledge(
            message=request.message,
        )

        return ChatResponse(
            answer=result["answer"],
            agents_used=["router", "knowledge"],
            sources=result["sources"],
            status=result["status"],
        )

    # 4. Both: coordinación entre agentes
    elif decision.route == "both":

        support_result = handle_support(
            message=request.message,
            user_id=request.user_id,
        )

        knowledge_result = handle_knowledge(
            message=request.message,
        )

        combined_answer = (
            "Información de tu cuenta:\n"
            f"{support_result['answer']}\n\n"
            "Información general de Getnet:\n"
            f"{knowledge_result['answer']}"
        )

        statuses = [
            support_result["status"],
            knowledge_result["status"],
        ]

        if "error" in statuses:
            final_status = "error"
        elif "insufficient_information" in statuses:
            final_status = "insufficient_information"
        else:
            final_status = "success"

        return ChatResponse(
            answer=combined_answer,
            agents_used=[
                "router",
                "support",
                "knowledge",
            ],
            sources=knowledge_result["sources"],
            status=final_status,
        )

    # 5. Protección ante una ruta inesperada.
    raise HTTPException(
        status_code=500,
        detail=f"Unexpected router decision: {decision.route}",
    )
