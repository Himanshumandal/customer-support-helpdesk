from fastapi import FastAPI
from app.routes.ticket import router as ticket_router

app=FastAPI(
    title="Customer Support AI Helpdesk",
    description="Customer support ticket management and AI assistance",
    version="1.0.0",
)

@app.get("/",tags=["General"])
def home():
    return {
        "message": "Customer Support AI Helpdesk is running"
    }

@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy"}


app.include_router(ticket_router);