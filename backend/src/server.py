"""LangGraph server configuration and startup."""

from fastapi import FastAPI
from langgraph.server import Server

from src.graph import graph, State

# Create FastAPI app
app = FastAPI(
    title="Cloud Pilot Server",
    description="LangGraph server for Cloud Pilot infrastructure generation"
)

# Create LangGraph server with state type
server = Server(
    app,
    agents={
        "agent": graph  # Simplified registration
    },
    state_type=State  # Register state type at top level
)

# Add CORS middleware if needed
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 