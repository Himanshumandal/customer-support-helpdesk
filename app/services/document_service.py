
from pathlib import Path
import shutil

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


# ==========================================
# 1. Project paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

POLICY_FILE = BASE_DIR / "app" / "docs"/ "policy.txt"
VECTORSTORE_DIR = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "support_policies"


# ==========================================
# 2. Initialize models
# ==========================================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


# ==========================================
# 3. Load documents
# ==========================================

def load_support_documents():
    if not POLICY_FILE.exists():
        raise FileNotFoundError(
            f"Policy document not found: {POLICY_FILE}"
        )

    loader = TextLoader(
        str(POLICY_FILE),
        encoding="utf-8",
    )

    return loader.load()


# ==========================================
# 4. Split documents into chunks
# ==========================================

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        length_function=len,
    )

    return text_splitter.split_documents(documents)


# ==========================================
# 5. Build and persist the vector store
# ==========================================

def build_vector_store():
    documents = load_support_documents()
    chunks = split_documents(documents)

    if not chunks:
        raise ValueError("No document chunks were created.")

    # Rebuild the generated index to avoid duplicate chunks
    # when this indexing function is run again.
    if VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)

    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTORSTORE_DIR),
    )

    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Vector store saved at: {VECTORSTORE_DIR}")

    return vector_store


# ==========================================
# 6. Load the existing vector store
# ==========================================

def get_vector_store():
    if not VECTORSTORE_DIR.exists():
        raise RuntimeError(
            "Vector store not found. Build the index first."
        )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )


# ==========================================
# 7. Create the retriever
# ==========================================

def get_retriever():
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )


# ==========================================
# 8. Format retrieved documents
# ==========================================

def format_docs(documents):
    return "\n\n".join(
        document.page_content
        for document in documents
    )


# ==========================================
# 9. Create the RAG prompt
# ==========================================

rag_prompt = ChatPromptTemplate.from_template(
    """
    You are a customer support assistant.

    Answer the customer's question using only the
    information in the provided support policy context.

    Rules:
    - Do not invent company policies.
    - If the answer is not present in the context,
      say that the available policy documents do not
      contain enough information to answer.
    - Never promise a refund or claim an action is complete
      unless the context explicitly supports it.
    - Be polite, clear, and concise.

    Support policy context:
    {context}

    Customer question:
    {question}

    Answer:
    """
)


# ==========================================
# 10. Create the RAG chain
# ==========================================

def create_rag_chain():
    retriever = get_retriever()

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# ==========================================
# 11. Ask a question
# ==========================================

def ask_support_question(question: str) -> str:
    rag_chain = create_rag_chain()

    return rag_chain.invoke(question)


# ==========================================
# 12. Build the index when run directly
# ==========================================

if __name__ == "__main__":
    build_vector_store()
