"""FastAPI implementation for Cloud Pilot."""

from typing import Dict, Optional, Any, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
from uuid import uuid4

from src.graph import build_example_graph
from src.state import CloudPilotState
from src.constants import ACTION_GENERATE, ACTION_APPROVE_PLAN
from src.agents.architecture_agent import ArchitectureAgent
from langgraph.types import Command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

active_connections: Set[WebSocket] = set()

# Store for pending interactions
pending_interactions: Dict[str, asyncio.Future] = {}
# Store for flow states
flow_states: Dict[str, CloudPilotState] = {}
# Initialize the architecture agent
architecture_agent = ArchitectureAgent()

class TaskRequest(BaseModel):
    task: str

class UserResponse(BaseModel):
    approved: bool

class FlowResponse(BaseModel):
    flow_id: str
    status: str
    result: Optional[str] = None
    question: Optional[str] = None
    plan_output: Optional[str] = None
    terraform_code: Optional[str] = None

def handle_interrupt(interrupt_data: Dict[str, Any], state: CloudPilotState, flow_id: str) -> bool:
    """Handle interrupts from the langgraph flow by storing state and creating a future."""
    # Store the state
    flow_states[flow_id] = state
    # Create a future for the response
    future = asyncio.Future()
    pending_interactions[flow_id] = future
    # Return a placeholder - the actual response will come later
    return False

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("Starting Cloud Pilot API")
    logger.info("WebSocket endpoint available at: /ws/ai-assist")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check request received")
    return {"status": "ok", "websocket_endpoint": "/ws/ai-assist"}

@app.websocket("/ws/ai-assist")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"WebSocket connection request received from {websocket.client}")
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for {websocket.client}")
        active_connections.add(websocket)
        
        # Send an initial connection confirmation message
        await websocket.send_json({
            "type": "connection_status",
            "status": "connected",
            "message": "WebSocket connection established successfully"
        })
        logger.info(f"Sent connection confirmation to {websocket.client}")

        try:
            graph = build_example_graph()
            while True:
                # Wait for messages from the client
                try:
                    message = await websocket.receive_json()
                    logger.info(f'WebSocket message received from {websocket.client}: {message}')
                    
                    # Initialize the graph and state
                    flow_id = str(uuid4())

                    if message.get("type") == "new_task":
                        # Check if this is an architecture mode request
                        mode = message.get("mode", "normal")
                        task = message.get("message", "")
                        
                        logger.info(f"Processing task: mode={mode}, task={task}")
                        
                        if mode in ["architect", "deploy"]:
                            # Handle architecture mode request
                            logger.info(f"Processing architecture mode request: mode={mode}, task={task}")
                            
                            # Process the message with the architecture agent
                            response = architecture_agent.process_message(task, mode)
                            
                            # Send the response back to the client
                            await websocket.send_json({
                                "type": "progress",
                                "flow_id": flow_id,
                                "data": {
                                    "results": {
                                        "message": response["message"],
                                        "structuredContent": {
                                            "title": f"Architecture Recommendation ({mode.capitalize()} Mode)",
                                            "sections": [
                                                {
                                                    "type": "heading",
                                                    "content": f"Architecture Recommendation ({mode.capitalize()} Mode)",
                                                    "metadata": {"level": 1}
                                                },
                                                {
                                                    "type": "text",
                                                    "content": response["message"]
                                                }
                                            ]
                                        }
                                    }
                                }
                            })
                            logger.info(f"Sent architecture response for mode={mode}")
                        else:
                            # Start a new flow for normal mode
                            flow_id = str(uuid4())
                            task = message.get("message", "")
                            logger.info(f"Starting new flow: flow_id={flow_id}, task={task}")
                            initial_state = {
                                "task": task,
                                "terraform_code": "",
                                "terraform_file_path": "",
                                "result": "",
                                "error": "",
                                "next_action": ACTION_APPROVE_PLAN,
                            }

                            try:

                                async for event in graph.astream(
                                    initial_state,
                                    {"configurable": {
                                        "flow_id": flow_id,
                                        "thread_id": flow_id,
                                    }}
                                ):
                                    print('graph event: ', event)
                                    print('is interrupt?', '__interrupt__' in event)

                                    if '__interrupt__' in event:
                                        # If this is a user interrupt, send the question to the client
                                        interrupt_data = event['__interrupt__'][0].value
                                        await websocket.send_json({
                                            "type": "confirmation",
                                            "flow_id": flow_id,
                                            "status": "waiting_for_input",
                                            "question": interrupt_data.get("question"),
                                            "plan_output": interrupt_data.get("plan_output"),
                                            "terraform_json": interrupt_data.get("terraform_json"),
                                        })
                                        break

                                    else:
                                        # Send progress event to the client
                                        await websocket.send_json({
                                            "type": "progress",
                                            "flow_id": flow_id,
                                            "data": event
                                        })

                            except Exception as e:
                                print(f"error: {e}")
                                await websocket.send_json({
                                    "type": "error",
                                    "flow_id": flow_id,
                                    "error": str(e)
                                })

                    elif message.get("type") == "user_response":
                        # Handle user response to an interrupt
                        flow_id = message.get("flow_id")
                        approved = message.get("approved")

                        if flow_id not in pending_interactions:
                            await websocket.send_json({
                                "type": "error",
                                "error": "No pending interaction found for this flow ID"
                            })
                            continue

                        try:
                            # Get the stored state and future
                            state = flow_states[flow_id]
                            future = pending_interactions[flow_id]

                            # Complete the future with the user's response
                            future.set_result(approved)

                            # Clean up
                            del pending_interactions[flow_id]
                            del flow_states[flow_id]

                            # Continue the flow
                            graph = build_example_graph()
                            async for event in graph.astream(
                                state,
                                {"configurable": {
                                    "flow_id": flow_id,
                                    "interrupt": lambda data, state: handle_interrupt(data, state, flow_id),
                                    "thread_id": flow_id,
                                }}
                            ):
                                if flow_id in pending_interactions:
                                    # We hit another interrupt
                                    interrupt_data = event.get("interrupt_data", {})
                                    await websocket.send_json({
                                        "type": "interrupt",
                                        "flow_id": flow_id,
                                        "status": "waiting_for_input",
                                        "question": interrupt_data.get("question"),
                                        "plan_output": interrupt_data.get("plan_output"),
                                        "terraform_code": interrupt_data.get("terraform_code")
                                    })
                                    break
                                else:
                                    # Send progress event to the client
                                    await websocket.send_json({
                                        "type": "progress",
                                        "flow_id": flow_id,
                                        "data": event
                                    })

                        except Exception as e:
                            print(f"error: {e}")
                            await websocket.send_json({
                                "type": "error",
                                "flow_id": flow_id,
                                "error": str(e)
                            })

                    elif message.get("type") == "confirmation":
                        flow_id = message.get("flow_id")
                        print(f"confirmation: flow_id={flow_id}")
                        approved = message.get("approved")

                        for chunk in graph.stream(Command(resume={"approved": approved}), config={"configurable": {"thread_id": flow_id}}):
                            await websocket.send_json({
                                "type": "progress",
                                "flow_id": flow_id,
                                "data": chunk
                            })
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Error processing message: {str(e)}"
                    })
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for {websocket.client}")
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket connection: {str(e)}", exc_info=True)
            try:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Server error: {str(e)}"
                })
            except:
                pass
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {str(e)}", exc_info=True)
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed for {websocket.client if hasattr(websocket, 'client') else 'unknown client'}")
