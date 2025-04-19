import os
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Load OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set.")

# Folders
pdf_folder = Path("compliance_pdfs")
output_folder = Path("vectorstore/compliance-laws")
output_folder.mkdir(parents=True, exist_ok=True)

# Chunking config
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=250,
     separators=["\n\n", "\n", ".", " ", ""]
)

all_chunks = []

# 📘 Load all PDFs with filename & page number as metadata
for pdf_path in pdf_folder.glob("*.pdf"):
    print(f"📄 Loading {pdf_path.name}")
    loader = PyPDFLoader(str(pdf_path))
    raw_docs = loader.load()

    for doc in raw_docs:
        doc.metadata["source"] = pdf_path.name
        doc.metadata["page"] = doc.metadata.get("page", "ukendt side")

    chunks = splitter.split_documents(raw_docs)
    all_chunks.extend(chunks)

print(f"🧩 Total chunks created: {len(all_chunks)}")

# 🧠 Add glossary chunk (optional)
glossary = Document(
    page_content="""
Morarente: Den rente, som en kreditor kan opkræve, når en betaling er forsinket. 
Ofte omtalt som 'rente ved forsinket betaling'. Reguleres typisk af renteloven.

Rykkerprocedure: En proces for at sende betalingspåmindelser til skyldnere. 
Normalt gives mindst 10 dages mellemrum mellem rykkerbreve, før yderligere inkassoskridt tages.

Inkasso: Den juridiske og administrative proces ved inddrivelse af gæld, 
reguleret bl.a. af inkassoloven og forbrugeraftaleloven.

KYC: Kundekendskabsproces.

Know your customer: Kundekendskabsproces.
""",
    metadata={"source": "glossary", "page": "N/A"}
)
all_chunks.append(glossary)

# 🔐 Embed and store
print("🔗 Generating embeddings...")
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = FAISS.from_documents(all_chunks, embedding_model)

# 💾 Save
vectorstore.save_local(str(output_folder))
print(f"✅ Vectorstore saved to: {output_folder}")
