from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.prompts.ticketprompt import reply_prompt,ticketprompt,urgent_reply_prompt,standard_reply_prompt
from app.schema import TicketAnalysis
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnableBranch,RunnablePassthrough

load_dotenv()


model=ChatOpenAI(model="gpt-5-mini",temperature=0.9);

structured_llm=model.with_structured_output(TicketAnalysis);
str_parser=StrOutputParser();




ticket_anaylsis_chain=ticketprompt|structured_llm
customer_anaylsis_chain=reply_prompt|model|str_parser

process_chain=RunnableParallel(
    analysis=ticket_anaylsis_chain,
    reply=customer_anaylsis_chain
)

def analyze_ticket(description: str) -> TicketAnalysis:
    return ticket_anaylsis_chain.invoke(
        {"description": description}
    )


def generate_customer_reply(description:str)->str:

    result=process_chain.invoke({"description":description})

    return result;


urget_reply=urgent_reply_prompt|model|str_parser
standard_reply=standard_reply_prompt|model|str_parser

reply_branch=RunnableBranch(
    (
        lambda x:x["analysis"].priority in ["high","critical"],
        urget_reply
    ),
    standard_reply
)

ticket_context_chain = RunnablePassthrough.assign(
    analysis=ticket_anaylsis_chain
)

ticket_routing_chain = (
    ticket_context_chain
    | RunnablePassthrough.assign(
        reply=reply_branch
    )
)

def route_ticket(description: str) -> dict:
    return ticket_routing_chain.invoke(
        {"description": description}
    )


