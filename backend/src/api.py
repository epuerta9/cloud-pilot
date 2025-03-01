"""FastAPI implementation for Cloud Pilot."""

from typing import Dict, Optional, Any, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import asyncio
from uuid import uuid4

from src.graph import build_example_graph
from src.state import CloudPilotState
from src.constants import ACTION_GENERATE, ACTION_APPROVE_PLAN
from langgraph.types import Command

app = FastAPI()
active_connections: Set[WebSocket] = set()

# Store for pending interactions
pending_interactions: Dict[str, asyncio.Future] = {}
# Store for flow states
flow_states: Dict[str, CloudPilotState] = {}

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

@app.websocket("/ws/ai-assist")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)

    try:
        graph = build_example_graph()
        while True:
            # Wait for messages from the client
            message = await websocket.receive_json()
            print('websocket message: ', message)

            # Initialize the graph and state
            flow_id = str(uuid4())

            if message.get("type") == "new_task":
                # Start a new flow
                flow_id = str(uuid4())
                task = message.get("task")
                print(f"starting new flow: flow_id={flow_id}, task={task}")
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

    except WebSocketDisconnect:
        active_connections.remove(websocket)
