from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
import os
import traceback

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

vectorstore = FAISS.load_local(
    "vectorstore/compliance-laws",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(
    search_type="similarity",  # Or try "mmr" for better diversity
    search_kwargs={"k": 6}
)

qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

@app.post("/ask")
async def ask_question(request: Request):
    try:
        body = await request.json()
        question = body.get("question")
        mode = body.get("mode", "chat")

        if not question:
            return JSONResponse(status_code=400, content={"error": "Missing question"})

        if mode == "sop":
            sop_prompt = (
                "You are a compliance assistant trained on Danish financial law. "
                "Draft a structured Standard Operating Procedure (SOP) ONLY using content from the retrieved legal sources. "
                "If no relevant legal basis exists in the sources, respond: 'Der findes ikke tilstrækkeligt grundlag i materialet til at udarbejde en SOP.'\n\n"
                f"Spørgsmål: {question}"
            )
            result = qa_chain.invoke({"question": sop_prompt})

        else:
            grounded_prompt = (
                "Answer ONLY using the retrieved legal documents. "
                "If the answer is not clearly stated in the documents, respond: 'Det fremgår ikke tydeligt af det tilgængelige materiale.'\n\n"
                f"Spørgsmål: {question}"
            )
            result = qa_chain.invoke({"question": grounded_prompt})

        # Extract relevant source snippets
        sources = [
            doc.page_content[:300].strip().replace("\n", " ")
            for doc in result.get("source_documents", [])
        ]

        return {
            "answer": result["answer"],
            "sources": sources
        }

    except Exception as e:
        print("🔥 Internal Server Error:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
