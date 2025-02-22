from fastapi import FastAPI, HTTPException
from .models.validation import (
    ValidationRequest, 
    ValidationResponse,
    ValidationStatus,
    ValidationReview,
    WebhookRegistration
)
import uuid
import httpx
import asyncio

#TODO: Add logging, permissions (access to certain validation requests), rate limiting, etc.
#TODO: Implement message queue (Redis/RabbitMQ) between Hub and webhooks to improve reliability and scalability of notifications (new actions → UI, reviews → agents).

# Initialize FastAPI application for the AI Action Validation Hub
# This service handles validation requests and reviews for AI actions
app = FastAPI(title="AI Action Validation Hub")

# In-memory storage for prototype (will be replaced with PostgreSQL)
validations = {} # validations: Dictionary storing validation records keyed by action_id
agent_webhooks = {} # agent_webhooks: Dictionary storing webhook URLs keyed by agent_id
reviewer_webhooks = {} # reviewer_webhooks: Dictionary storing webhook URLs for review UIs

@app.post("/validate", response_model=ValidationResponse)
async def submit_validation(request: ValidationRequest):
    """
    Submit a new validation request for an AI action.
    Intended for AI Agents to submit actions requiring validation.
    Notifies registered review UIs of new pending actions via webhook.
    
    Args:
        request (ValidationRequest): The validation request containing action details
            including agent_id, user_id, action_id, action_type, content and metadata
            
    Returns:
        ValidationResponse: Contains the generated validation_id and initial pending status
    """
    validation_id = f"val_{uuid.uuid4().hex[:8]}"
    validations[request.action_id] = {
        "status": "pending",
        "request": request.dict(),
        "validation_id": validation_id
    }
    
    # Notify all registered review UIs of new pending action
    for reviewer_url in reviewer_webhooks.values():
        async with httpx.AsyncClient() as client:
            try:
                await client.post(reviewer_url, json={
                    "event": "new_pending_action",
                    "action_id": request.action_id,
                    "validation_id": validation_id
                })
            except Exception:
                # Log webhook delivery failure but don't block the response
                pass
                
    return ValidationResponse(validation_id=validation_id, status="pending")

@app.get("/validate/{action_id}", response_model=ValidationStatus)
async def get_validation_status(action_id: str):
    """
    Get the current status of a validation request.
    Intended for AI Agents to check the status of their submitted actions.
    
    Args:
        action_id (str): The unique identifier of the action to check
        
    Returns:
        ValidationStatus: The current status and any feedback for the validation
        
    Raises:
        HTTPException: 404 if the action_id is not found
    """
    if action_id not in validations:
        raise HTTPException(status_code=404, detail="Validation not found")
    validation = validations[action_id]
    return ValidationStatus(
        status=validation["status"],
        feedback=validation.get("feedback")
    )

@app.post("/validate/{action_id}/review")
async def review_validation(action_id: str, review: ValidationReview):
    """
    Submit a review for a validation request.
    Intended for Review UI to approve/reject actions.
    Notifies the submitting AI Agent of the review result via webhook.
    
    Args:
        action_id (str): The unique identifier of the action to review
        review (ValidationReview): The review details including status and optional feedback
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if the action_id is not found
    """
    if action_id not in validations:
        raise HTTPException(status_code=404, detail="Validation not found")
    
    validations[action_id]["status"] = review.status
    validations[action_id]["feedback"] = review.feedback
    
    # Notify agent of review result via webhook
    agent_id = validations[action_id]["request"]["agent_id"]
    if agent_id in agent_webhooks:
        async with httpx.AsyncClient() as client:
            try:
                await client.post(agent_webhooks[agent_id], json={
                    "event": "action_reviewed",
                    "action_id": action_id,
                    "status": review.status,
                    "feedback": review.feedback
                })
            except Exception:
                # Log webhook delivery failure but don't block the response
                pass
    
    return {"message": "Action reviewed successfully"}

@app.get("/validations")
async def list_validations(status: str = None):
    """
    Get all validations, optionally filtered by status.
    Intended for Review UI to fetch pending or other actions.
    
    Args:
        status (str, optional): Filter by status (e.g., "pending", "approved", "rejected")
        
    Returns:
        dict: Dictionary of validation records, filtered by status if specified
    """
    if status:
        return {k: v for k, v in validations.items() if v["status"] == status}
    return validations

@app.post("/agents/webhook")
async def register_webhook(registration: WebhookRegistration):
    """
    Register a webhook URL for an agent to receive validation updates.
    Intended for AI Agents to register for review result notifications.
    
    Args:
        registration (WebhookRegistration): Contains agent_id and callback_url
        
    Returns:
        dict: Success message confirming webhook registration
    """
    agent_webhooks[registration.agent_id] = registration.callback_url
    return {"message": "Webhook registered successfully"}

@app.post("/reviewers/webhook")
async def register_reviewer_webhook(registration: WebhookRegistration):
    """
    Register a webhook URL for review UI to receive notifications of new pending actions.
    Intended for Review UI to register for new action notifications.
    
    Args:
        registration (WebhookRegistration): Contains reviewer_id and callback_url
        
    Returns:
        dict: Success message confirming webhook registration
    """
    reviewer_webhooks[registration.reviewer_id] = registration.callback_url
    return {"message": "Reviewer webhook registered successfully"}