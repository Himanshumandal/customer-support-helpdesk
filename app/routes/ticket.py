
from fastapi import APIRouter,HTTPException,status
from app.schema import TicketCreate,TicketResponse,AssistantRequest,RAGQuestion
from app.services.ticket_service import generate_customer_reply,route_ticket
from app.services.document_service import ask_support_question
from app.services.tools_services import ask_support_agent
from app.services.ticket_repository import (
    create_ticket as save_ticket,
    get_all_tickets,
    get_ticket_by_id,
)

router=APIRouter(
    prefix="/api/v1",
    tags=["Ticket"]
);

@router.post(
    "/ticket",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_Ticket(request:TicketCreate):

    ticket_store= save_ticket(request);
    return ticket_store;

@router.post("/ask-policy")
def ask_policy(request: RAGQuestion):
    try:
        answer = ask_support_question(request.question)

        return {
            "question": request.question,
            "answer": answer,
        }

    except Exception as exc:
        print(f"RAG error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not answer the support-policy question.",
        ) from exc


@router.post('/ticket/analyze')
def anaylze_ticket(request:TicketCreate):
    try:
        reply= generate_customer_reply(request.description)
        return {"reply":reply}
    except Exception as e:

        print(f"Ticket analysis error: {e}")

        raise HTTPException(
            status_code=502,
            detail="AI ticket analysis failed.",
        ) from e

@router.post("/ticket/route")
def route_customer_ticket(request: TicketCreate):
    try:
        return route_ticket(request.description)

    except Exception as exc:
        print(f"Ticket routing error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Ticket routing failed.",
        ) from exc


@router.get("/ticket",response_model=list[TicketResponse])
def getall_Ticket():

    return get_all_tickets();

@router.get("/ticket/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int):
    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@router.post("/assistant")
def support_assistant(request: AssistantRequest):

    try:
        answer=ask_support_agent(request.question);

        return {
            "question":request.question,
            "answer": answer
        }

    except Exception as exc:
        print(f"Support agent error: {exc}")

        raise HTTPException(
            status_code=502,
            detail="The support assistant could not process your request.",
        ) from exc
