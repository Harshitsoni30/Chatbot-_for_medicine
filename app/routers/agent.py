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
import os


load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

def load_combined_knowledge_base(file_path: str):

    system_vector_database = ChromaDb(
        collection="System_knowledge_base",
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )

    system_knowledge_base = PDFKnowledgeBase(
        path="app\data\system_data\Harshit_Soni_Bio (2).pdf",
        vector_db=system_vector_database,
        reader=PDFReader(ignore_images=True, skip_empty=True)
    )

    collection_name = f"uploaded_pdf{uuid.uuid4()}"

    user_vector_database = ChromaDb(
        collection=collection_name,
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )

    user_knowledge_base = PDFKnowledgeBase(
        path=file_path,
        vector_db=user_vector_database,
        reader=PDFReader(ignore_images=True, skip_empty=True)
    )

    
    system_knowledge_base.load(upsert=True)
    user_knowledge_base.load(upsert=True)
   

    combined_vector_db = ChromaDb(
        collection=f"combined_konwledge_base_{uuid.uuid4()}",
        embedder=GeminiEmbedder(api_key=gemini_api_key)
    )

    
    combined_kb = CombinedKnowledgeBase(
        sources=[system_knowledge_base, user_knowledge_base],
        vector_db=combined_vector_db
    )

    
    combined_kb.load(upsert=True)
    return combined_kb

def create_agent(knowledge: CombinedKnowledgeBase):
    agent= Agent(
        name="AI Assistance",
        model=Gemini(id="gemini-1.5-flash"),
        tools=[DuckDuckGo(), Newspaper4k()],
        description="An AI assistant to answer questions from your uploaded PDF or basic query.",
        instructions=[
            """
            Information Retrieval Priority:
            1. Knowledge Base Search:
                - Search both system and user-uploaded PDFs
                - Share all information (both private and public )
                - Provide complete and accurate details
            
            2. Web Search (if knowledge base lacks information):
                - Search top 5 relevant links via DuckDuckGo
                - Extract and analyze content using Newspaper4k
                - Skip unavailable URLs
                - Filter out:
                    * Video links
                    * Promotional content
                    * Redundant information
            
            Response Guidelines:
            1. Structure:
                - Use step-by-step format
                - Include clear headings
                - Add bullet points or numbered lists
                - Use code blocks for technical content
            
            2. Writing Style:
                - Be clear and concise
                - Focus on actionable information
                - Maintain friendly, conversational tone
                - Avoid filler words ("here", "etc.", "kind of")
            
            3. Context Awareness:
                - Build on previous conversation
                - Avoid repeating information
                - Use knowledge base only when relevant
            
            4. Interaction Protocol:
                - Greet: "Hey!", "Hi there!"
                - Thanks: "Sure!", "You're welcome!"
                - Farewell: "Take care!", "Catch you later!"
                - Handle negative messages with calm professionalism
            """
        ],
        add_references=True,
        markdown=True,
        knowledge_base =knowledge,
       
    )
    # agent.print_response("when Harshit join valere ")
    
    return agent
