"""FastAPI application for Cloud Pilot."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage

from src.graph import graph

app = FastAPI(
    title="Cloud Pilot API",
    description="API for generating and managing Terraform infrastructure",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str

class ChatResponse(BaseModel):
    """Response model for chat messages."""
    messages: List[Dict[str, str]]
    result: Optional[str] = None
    error: Optional[str] = None
    terraform_code: Optional[str] = None

class HumanInputRequest(BaseModel):
    """Request model for human input."""
    prompt: str
    options: List[str]

class HumanInputResponse(BaseModel):
    """Response model for human input."""
    choice: str
    next_action: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Process a chat message and return the response.
    
    Args:
        request: ChatRequest containing the user's message
        
    Returns:
        ChatResponse containing the assistant's response and any generated code
    """
    try:
        # Create initial state with user message
        message = HumanMessage(content=request.message)
        
        # Initialize response
        response = ChatResponse(messages=[])
        
        # Stream responses from graph
        for event in graph.stream({"messages": [message]}):
            for value in event.values():
                if "messages" in value and value["messages"]:
                    # Add each message to the response
                    response.messages.append({
                        "role": "assistant",
                        "content": value["messages"][-1].content
                    })
                
                # Add any terraform code or errors
                if "terraform_code" in value:
                    response.terraform_code = value["terraform_code"]
                if "error" in value:
                    response.error = value["error"]
                if "result" in value:
                    response.result = value["result"]
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/human-input", response_model=HumanInputResponse)
async def human_input_endpoint(request: HumanInputRequest):
    """
    Get human input for a decision point.
    
    Args:
        request: HumanInputRequest containing the prompt and options
        
    Returns:
        HumanInputResponse containing the chosen option and next action
    """
    try:
        # Display prompt and options
        print(f"\n{request.prompt}")
        for i, option in enumerate(request.options, 1):
            print(f"{i}. {option}")
        
        # Get user choice
        choice = input("\nEnter your choice (number): ")
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(request.options):
            chosen_option = request.options[choice_idx]
            
            # Map choices to actions
            action_map = {
                "Apply": "execute",
                "Regenerate": "generate",
                "Cancel": "end"
            }
            
            next_action = action_map.get(chosen_option, "end")
            
            return HumanInputResponse(
                choice=chosen_option,
                next_action=next_action
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid choice"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add CORS middleware if needed
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
