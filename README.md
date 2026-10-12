Customer Support AI Helpdesk
An AI-powered customer support backend built with FastAPI, LangChain, OpenAI, and Chroma. The project combines traditional ticket APIs with a tool-calling AI agent that can look up ticket statuses and answer questions using support-policy documents.
Project status: Learning project / work in progress. Review the implementation and security notes below before deploying publicly.

Features
- Ticket API: Create tickets and retrieve one ticket or a list of tickets.
- AI ticket assistance: Generate customer replies and route/analyze tickets using LangChain chains.
- Tool-calling agent: Uses LangChain's create_agent() API.
- Ticket-status tool: Looks up ticket status from the SQLite ticket repository.
- Policy-search tool: Uses the existing RAG pipeline to answer questions from support-policy documents.
- Retrieval-Augmented Generation (RAG): Loads text policy files, splits them into chunks, creates embeddings, stores them in Chroma, retrieves relevant chunks, and generates grounded answers.
- Interactive API documentation: FastAPI Swagger UI.
Tech stack
- Python 3.11+
- FastAPI and Uvicorn
- LangChain and LangGraph's agent runtime (through LangChain's create_agent API)
- OpenAI chat model (gpt-4o-mini, as configured in the project)
- OpenAI embeddings (text-embedding-3-small, as configured in the RAG service)
- Chroma vector store
- SQLite for local ticket persistence
- uv for dependency and environment management
- python-dotenv for environment configuration
Architecture
Client / Swagger UI
        |
        v
     FastAPI
        |
        +----------------------+
        |                      |
        v                      v
 Ticket API              Assistant API
        |                      |
        v                      v
 SQLite ticket DB       LangChain agent
                               |
                    +----------+----------+
                    |                     |
                    v                     v
             Ticket-status tool    Policy-search tool
                    |                     |
                    v                     v
             SQLite repository       RAG pipeline
                                          |
                                Policy text files -> chunks
                                          |
                                OpenAI embeddings -> Chroma
                                          |
                                Retrieved context -> LLM answer
Project structure
The exact filenames may vary as the project evolves. The following represents the main components used in the project:
customer_support/
├── app/
│   ├── main.py
│   ├── schema.py
│   ├── routes/
│   │   └── tickets.py
│   ├── services/
│   │   ├── ticket_service.py
│   │   ├── ticket_repository.py
│   │   ├── document_service.py
│   │   ├── rag_service.py
│   │   └── tools_service.py
│   └── docs/
│       └── data/
│           └── support_policy.txt
├── data/
│   └── chroma_db/            # Generated local vector index; do not commit
├── .env                      # Local secrets; do not commit
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
Prerequisites
- Python 3.11 or a compatible version supported by the dependencies.
- uv installed.
- An OpenAI API key with access to the configured models.
Setup
1. Clone the repository
After the project is pushed to GitHub, clone it using your repository URL:
git clone YOUR_REPOSITORY_URL
cd customer_support
2. Install dependencies
From the project root:
uv sync
If uv sync reports missing dependencies, add the packages required by the current project using uv add and commit the updated pyproject.toml and uv.lock.
3. Configure environment variables
Create a .env file in the project root:
OPENAI_API_KEY=your_openai_api_key_here
Never commit your real .env file or publish API keys. A safe .env.example may contain placeholder values only.
4. Prepare the support-policy knowledge base
Place policy .txt files in the directory used by your document-loading code (currently app/docs/data/). Build or initialize the Chroma index using the project's existing RAG setup before asking policy questions if the index has not already been created.
Generated vector-store files are local artifacts and should not be committed.
5. Start the API
uv run uvicorn app.main:app --reload
Open Swagger UI:
- http://127.0.0.1:8000/docs
API endpoints
The following routes have been implemented during development. Confirm the current router and schemas if you change endpoint names or prefixes.
Method	Endpoint	Purpose
POST	/api/v1/ticket	Create a support ticket
GET	/api/v1/ticket	List saved tickets
GET	/api/v1/ticket/{ticket_id}	Retrieve a ticket by ID
POST	/api/v1/ticket/analyze	Generate a customer reply from a ticket description
POST	/api/v1/ticket/route	Analyze/route a ticket using the LangChain workflow
POST	/api/v1/ask-policy	Ask a question against support-policy documents
POST	/api/v1/assistant	Ask the tool-calling support agent


All request fields and response formats are defined by the Pydantic schemas in the application. Use /docs to inspect the live API contract.
Example: create a ticket
The exact required fields depend on TicketCreate. The current router uses these fields:
{
  "customer_name": "Example Customer",
  "customer_email": "customer@example.com",
  "subject": "Refund question",
  "description": "I would like to know whether my order is eligible for a refund."
}
Example: ask the assistant
{
  "conversation_id": "example-session-1",
  "question": "What is the status of TICKET-1?"
}
Use a ticket ID that actually exists in your local database. The assistant can also answer policy questions through the policy-search tool.
How the agent works
The LangChain agent has access to two tools:
1. check_ticket_status — queries the ticket repository for the current ticket status.
2. search_support_policy — invokes the RAG question-answering pipeline for company-policy questions.
The model selects a tool based on the customer's request. The agent runtime executes the tool and uses its result to produce the final answer. Tool outputs are data, not a replacement for API authorization or business rules.
RAG workflow
1. Load support-policy text documents.
2. Split documents into overlapping chunks.
3. Generate embeddings using the configured OpenAI embedding model.
4. Store chunks and embeddings in Chroma.
5. Retrieve relevant chunks for a customer question.
6. Ask the chat model to answer using retrieved context and avoid inventing policy details.
Keep policy documents accurate and current. Review retrieval quality before relying on answers in a production support environment.
Development notes
- Run the API with uv run uvicorn app.main:app --reload.
- Test endpoints interactively at /docs.
- Run the project's modules with uv run python -m package.module when they provide a module-level test entry point.
- Keep pyproject.toml and uv.lock under version control for reproducible dependency installation.
- Add automated tests for ticket persistence, missing ticket IDs, agent tool selection, and RAG grounding as the project grows.
Security and limitations
This project is intended for learning and further development, not as a production-ready customer-support system.
Before deploying:
- Protect secrets: keep .env out of Git and rotate any key that has been exposed.
- Add authentication and authorization: users must not access other customers' tickets or conversations by guessing IDs.
- Validate agent actions: do not let the model perform ticket changes or other side effects without server-side checks.
- Protect personal data: minimize logging of customer details and define retention/deletion policies.
- Handle API failures and limits: add timeouts, retries where appropriate, rate limiting, and clear error handling.
- Use persistent infrastructure deliberately: local SQLite is suitable for development; evaluate PostgreSQL and managed storage for concurrent production workloads.
- Treat conversation memory as a future task: persistent LangGraph checkpointing and long-term user memory have intentionally not been implemented yet.
- Avoid committing local artifacts: do not commit .env, SQLite databases, virtual environments, or generated Chroma data.
Roadmap
- [x] FastAPI ticket endpoints
- [x] LangChain ticket-analysis/reply workflows
- [x] RAG over support-policy documents
- [x] Tool-calling support agent
- [x] Ticket-status tool connected to SQLite
- [x] Agent exposed through FastAPI
- [ ] Automated tests and CI
- [ ] Persistent LangGraph conversation checkpointing
- [ ] Authenticated customer sessions and authorization
- [ ] React frontend integration
- [ ] Production logging, monitoring, and deployment configuration
License
No license has been selected yet. Add a LICENSE file before publishing if you want to explicitly define how others may use, modify, and distribute the project.