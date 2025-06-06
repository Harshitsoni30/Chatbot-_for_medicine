import os
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.chroma import ChromaDb
from phi.embedder.google import GeminiEmbedder
from phi.tools.newspaper4k import Newspaper4k
import uuid
from fastapi import HTTPException
from phi.knowledge.combined import CombinedKnowledgeBase
import uuid
import httpx
import os
from app.models.users import get_bot_by_id

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
DJANGO_API_URL = os.getenv("DJANGO_API_URL")


# Knowledge Base Setup
# knowledge combine knowledge for user uploaded and system uploded pdf
def load_combined_knowledge_base(file_path: str):

    system_vector_database = ChromaDb(
        collection="System_knowledge_base",
        embedder=GeminiEmbedder(api_key=GEMINI_API_KEY)
    )

    system_knowledge_base = PDFKnowledgeBase(
        path="app\\data\\system_data\\Harshit_Soni_Bio (2).pdf",
        vector_db=system_vector_database,
        reader=PDFReader(ignore_images=True, skip_empty=True)
    )

    collection_name = f"uploaded_pdf{uuid.uuid4()}"

    user_vector_database = ChromaDb(
        collection=collection_name,
        embedder=GeminiEmbedder(api_key=GEMINI_API_KEY)
    )

    user_knowledge_base = PDFKnowledgeBase(
        path=file_path,
        vector_db=user_vector_database,
        reader=PDFReader(ignore_images=True, skip_empty=True)
    )

    
    system_knowledge_base.load(upsert=False)
    user_knowledge_base.load(upsert=True)
   

    combined_vector_db = ChromaDb(
        collection=f"combined_konwledge_base_{uuid.uuid4()}",
        embedder=GeminiEmbedder(api_key=GEMINI_API_KEY)
    )

    
    combined_kb = CombinedKnowledgeBase(
        sources=[system_knowledge_base, user_knowledge_base],
        vector_db=combined_vector_db
    )

    combined_kb.load(upsert=False)
    return combined_kb
    
    
async def create_agent(knowledge: CombinedKnowledgeBase):
    data = await get_bot_by_id(1)
    prompt_text = data.get("prompt_text", "")
    model_name = data.get("model_name","")
    description = data.get("description","")

    agent= Agent(
        name="AI Assistance",
        model=Gemini(id=model_name),
        tools=[DuckDuckGo(), Newspaper4k()],
        description=description,
        instructions=[prompt_text],
        add_references=True,
        markdown=True,
        knowledge_base =knowledge,
       
    ) 
    return agent
