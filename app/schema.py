from typing import Annotated,Literal
from pydantic import BaseModel,EmailStr,Field



class TicketCreate(BaseModel):

    customer_name:Annotated[str,Field(description="Name of Customer",min_length=2, max_length=100, examples=["Anuj Sharma"])]
    customer_email:Annotated[EmailStr,Field(description="Email of Customer",examples=["abc@example.com"])]
    subject:Annotated[str,Field(description="Suject of Ticket",max_length=100,min_length=5,examples=["Battery Issue"])]
    description:Annotated[str,Field(description="Description of ticket",max_length=5000,min_length=10,examples=["Hi I am facing a promble regarding batter issue..."])]


class TicketResponse(BaseModel):
    ticket_id: int
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    status: Literal["open", "in_progress", "resolved"]

class TicketAnalysis(BaseModel):

    category:Annotated[Literal["payment","delivery","technical"],Field(description="Category of Ticket",examples=["payment"])]
    priority:Annotated[Literal["low","high","medium","critical"],Field(description="Priority of Ticket",examples=["medium"])]
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str = Field(
        description="A concise summary of the customer's issue"
    )
    suggested_action: str = Field(
        description="The next recommended support action"
    )



class RAGQuestion(BaseModel):
    question: Annotated[str,Field(description="Customer ask about policy",min_length=3 , max_length=2000, examples=["What is Delivery Policy"])]


class AssistantRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description="Customer's support question",
        examples=["What is the status on my ticket-1"]
    )