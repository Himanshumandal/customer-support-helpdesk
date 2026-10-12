from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from app.services.ticket_repository import get_ticket_status
from app.services.document_service import ask_support_question

load_dotenv()

llm=ChatOpenAI(model="gpt-5-mini",temperature=0.8)


@tool
def check_ticket_status(ticket_id: str) -> str:

    """Look up the current status of a saved support ticket by ID.
        Accepts a numeric ID such as 1 or a formatted ID such as TICKET-1.
    """

    return get_ticket_status(ticket_id=ticket_id);


@tool
def search_support_policy(question: str) -> str:
    """Search the company's support-policy documents for answers
    about refunds, delivery, returns, and other support policies.
    Use this tool when a customer asks about company policies.
    """
    return ask_support_question(question)

   

support_agent=create_agent(
    model='gpt-4o-mini',
    tools=[check_ticket_status,search_support_policy],
     system_prompt="""
    You are a customer support assistant.

    Rules:
    1. For ticket-status questions, use check_ticket_status.
    2. For questions about company policies, use search_support_policy.
    3. Never invent ticket statuses or company policies.
    4. If a tool reports that information is unavailable,
       explain that clearly to the customer.
    5. Give concise, friendly and professional answers.
    """
)

def ask_support_agent(question: str) -> str:
    result = support_agent.invoke(
        {
            "messages": [
                {"role": "user", "content": question}
            ]
        }
    )

    return result["messages"][-1].content




if __name__ == "__main__":
    questions = [
        "What is the status of TICKET-1?",
        "Within how many days can a customer request a refund?",
    ]

    for question in questions:
        print(f"\nCustomer: {question}")
        answer = ask_support_agent(question)
        print(f"Agent: {answer}")
