from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
import traceback
from pathlib import Path

# Load API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment.")

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM and embedder setup
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.4,
    openai_api_key=OPENAI_API_KEY
)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Load vectorstore
vectorstore = FAISS.load_local(
    "vectorstore/compliance-laws",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 14}
    #search_type="mmr",  
    #search_kwargs={"k": 14, "lambda_mult": 0.8}
)

# Chain setup
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# Endpoint: List available laws
@app.get("/laws")
async def list_available_laws():
    pdf_folder = Path("compliance_pdfs")
    laws = []
    for pdf_file in pdf_folder.glob("*.pdf"):
        name = pdf_file.stem.replace("_", " ").capitalize()
        laws.append(name)
    return {"laws": sorted(laws)}

# Endpoint: Ask questions or generate SOPs
@app.post("/ask")
async def ask_question(request: Request):
    try:
        body = await request.json()
        question = body.get("question")
        mode = body.get("mode", "chat")

        if not question:
            return JSONResponse(status_code=400, content={"error": "Missing question"})

        # Mode: SOP generation
        if mode == "sop":
            sop_prompt = (
                "You are a compliance assistant trained on Danish financial law. "
                "Draft a structured Standard Operating Procedure (SOP) ONLY using content from the retrieved legal sources. "
                "If no relevant legal basis exists in the sources, respond: 'Der findes ikke tilstrækkeligt grundlag i materialet til at udarbejde en SOP.'\n\n"
                f"Spørgsmål: {question}"
            )
            result = qa_chain({"query": sop_prompt})

        # Mode: regular question
        else:
            grounded_prompt = (
                "You are a compliance assistant trained on Danish financial law. "
                "Assume all questions to be referring to the retrieved legal documents. So, openended questions like 'Hvad er ...?' should be interpreted as 'Hvordan defineres ... i lovgivningen?' "
                "Answer ONLY using the retrieved legal documents. If the answer is defined as a list or categories in the law, provide the complete list from the documents."
                "If the answer is not clearly stated in the documents, respond: 'Det fremgår ikke tydeligt af det tilgængelige materiale, "
                "prøv eventuelt at omformuler dit spørgsmål og vær mere specifik. F.eks. Hvad er hvidvask => Hvordan defineres hvidvask i lovgivningen?'\n\n"
                f"Spørgsmål: {question}"
            )
            result = qa_chain({"query": grounded_prompt})

        # Extract rich source metadata
        sources = []
        for doc in result.get("source_documents", []):
            name = doc.metadata.get("source", "ukendt dokument").replace(".pdf", "").replace("_", " ").capitalize()
            page = doc.metadata.get("page", "ukendt side")
            snippet = doc.page_content.strip().replace("\n", " ")[:300]
            sources.append({
                "title": name,
                "page": page,
                "snippet": snippet
            })

        return {
            "answer": result["result"],
            "sources": sources
        }

    except Exception as e:
        print("🔥 Internal Server Error:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
