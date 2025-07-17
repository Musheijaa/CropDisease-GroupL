from fastapi import FastAPI,Request #type: ignore
from pydantic import BaseModel #type: ignore
from langchain_core.prompts import ChatPromptTemplate #type: ignore
from langchain_groq import ChatGroq #type: ignore
from fastapi.middleware.cors import CORSMiddleware  #type: ignore # You can switch to ChatOpenAI, etc.
from dotenv import load_dotenv #type: ignore
load_dotenv()
import os


assert os.getenv("GROQ_API_KEY")

# --- FastAPI setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Input schema ---
class ChatRequest(BaseModel):
    question: str

# --- LangChain setup ---
system_message = """
You are Nova, an intelligent AI assistant specialized in helping farmers with precise and practical advice focused on Uganda and the broader African farming context.
Your expertise includes crops, livestock, soil health, pest and disease management, and sustainable farming practices.
When answering:
- Provide concise, clear, and actionable responses grounded in best agricultural practices suitable for smallholder farmers.
- Use simple, easy-to-understand language tailored for farmers in Uganda and similar African environments.
- Prioritize practical advice that farmers can readily apply.
- If appropriate, suggest relevant tools, methods, or farming tips specific to the region.
- When the answer involves multiple steps, recommendations, or items, format your response as a clear, well-structured list for easy reading.
- Always focus on precision and relevance to local farming conditions and challenges.
Maintain a friendly and supportive tone, helping farmers improve their productivity and sustainability effectively.
"""


# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{question}")
])

# Load the model (using Groq - adjust key in your .env or config)
llm = ChatGroq(model="llama3-8b-8192", temperature=0.2)

# Chain the prompt to the model
chain = prompt | llm

# --- Chat endpoint ---
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = chain.invoke({"question": request.question})
        return {"response": response.content}
    except Exception as e:
        return {"error": str(e)}

# --- Root route ---
@app.get("/")
def root():
    return {"message": "AI Farming Assistant API is running!"}
