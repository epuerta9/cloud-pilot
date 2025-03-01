"""FastAPI implementation for Cloud Pilot."""

from typing import Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from uuid import uuid4

from src.graph import build_example_graph
from src.state import CloudPilotState
from src.constants import ACTION_GENERATE

app = FastAPI()

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


@app.post("/ai-assist/invoke")
async def start_flow(request: TaskRequest) -> FlowResponse:
    """Start a new flow with the given task."""
    flow_id = str(uuid4())

    # Initialize the graph
    graph = build_example_graph()

    # Create initial state
    initial_state = {
        "task": request.task,
        "terraform_code": "",
        "terraform_file_path": "",
        "result": "",
        "error": "",
        "next_action": ACTION_GENERATE,
    }

    try:
        # Start streaming the graph with our interrupt handler
        async for event in graph.astream(
            initial_state,
            {"configurable": {
                "flow_id": flow_id,
                "interrupt": lambda data, state: handle_interrupt(data, state, flow_id)
            }}
        ):
            print(event)

            if flow_id in pending_interactions:
                # We hit an interrupt, extract the data
                interrupt_data = event.get("interrupt_data", {})
                return FlowResponse(
                    flow_id=flow_id,
                    status="waiting_for_input",
                    question=interrupt_data.get("question"),
                    plan_output=interrupt_data.get("plan_output"),
                    terraform_code=interrupt_data.get("terraform_code")
                )

            # Flow completed
            return FlowResponse(
                flow_id=flow_id,
                status="completed",
                result=event.get("result", "")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/flow/{flow_id}/respond")
async def handle_user_response(flow_id: str, response: UserResponse) -> FlowResponse:
    """Handle user response for a pending interaction."""
    if flow_id not in pending_interactions:
        raise HTTPException(status_code=404, detail="No pending interaction found for this flow ID")

    try:
        # Get the stored state and future
        state = flow_states[flow_id]
        future = pending_interactions[flow_id]

        # Complete the future with the user's response
        future.set_result(response.approved)

        # Clean up
        del pending_interactions[flow_id]
        del flow_states[flow_id]

        # Continue the flow
        graph = build_example_graph()
        async for event in graph.astream(
            state,
            {"configurable": {
                "flow_id": flow_id,
                "interrupt": lambda data, state: handle_interrupt(data, state, flow_id)
            }}
        ):
            if flow_id in pending_interactions:
                # We hit another interrupt
                interrupt_data = event.get("interrupt_data", {})
                return FlowResponse(
                    flow_id=flow_id,
                    status="waiting_for_input",
                    question=interrupt_data.get("question"),
                    plan_output=interrupt_data.get("plan_output"),
                    terraform_code=interrupt_data.get("terraform_code")
                )

            # Flow completed
            return FlowResponse(
                flow_id=flow_id,
                status="completed",
                result=event.get("result", "")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))