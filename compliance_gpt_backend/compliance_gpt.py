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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

vectorstore = FAISS.load_local(
    "vectorstore/compliance-laws",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

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
                "As a compliance assistant trained on Danish financial law, please draft a practical and informative "
                "Standard Operating Procedure (SOP) that outlines how to handle the following task in alignment with relevant regulation:\n\n"
                + question
            )
            result = qa_chain.invoke({"question": sop_prompt})
        else:
            result = qa_chain.invoke({"question": question})

        # Collect source document snippets
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
