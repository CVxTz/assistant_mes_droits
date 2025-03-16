import logging
import os
import pathlib
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, AnyMessage
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from assistant_mes_droits.agent.agent import AgentState, build_agent

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dot_env_path = Path(__file__).parents[2] / ".env"
if dot_env_path.is_file():
    load_dotenv(dotenv_path=dot_env_path)

REDIS_URI = os.environ.get("REDIS_URI")

if not REDIS_URI:
    logger.error("REDIS_URI environment variable is not set.")
    raise ValueError("REDIS_URI environment variable is not set.")

limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URI)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run at startup
    Initialise the Client and add it to request.state
    """
    agent = build_agent()

    yield {"agent": agent}


app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production!
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: List[AnyMessage]


async def generate_response(agent, messages: List[AnyMessage]) -> AnyMessage:
    try:
        for message in messages:
            logger.info(f"Received message: {message}")
        state = AgentState(messages=messages)
        result = agent.invoke(state)
        return result["messages"][-1]
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return AIMessage(content="Je ne peux pas répondre a votre question.")


async def reset_conversation(request: Request) -> Dict[str, Any]:
    try:
        logger.info("Conversation reset requested.")
        # Implement conversation reset logic here if needed.
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting conversation: {e}"
        )


static_file_path = pathlib.Path(__file__).parent / "static"

# Load index.html once at startup
try:
    with open(static_file_path / "index.html") as f:
        index_html_content = f.read()
except FileNotFoundError:
    logger.error("index.html not found at startup.")
    index_html_content = None


# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    if index_html_content:
        return HTMLResponse(content=index_html_content)
    else:
        raise HTTPException(status_code=404, detail="index.html not found")


@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    agent = request.state.agent
    response = await generate_response(agent=agent, messages=chat_request.messages)
    return response


@app.post("/reset")
async def reset(request: Request) -> Dict[str, Any]:
    return await reset_conversation(request)


@app.get("/robots.txt")
async def robots_txt():
    content = """User-agent: *
Disallow: /chat
Disallow: /reset

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /

User-agent: *
Disallow: /static/
"""
    return Response(content=content, media_type="text/plain")


# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=static_file_path),
    name="static",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
