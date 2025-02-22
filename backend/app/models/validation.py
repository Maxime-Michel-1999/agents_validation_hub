from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel

class ValidationRequest(BaseModel):
    agent_id: str
    user_id: str
    action_id: str
    action_type: str
    content: str
    metadata: Dict

class ValidationResponse(BaseModel):
    validation_id: str
    status: str

class ValidationStatus(BaseModel):
    status: str
    feedback: Optional[str] = None

class ValidationReview(BaseModel):
    status: str
    feedback: Optional[str] = None

class WebhookRegistration(BaseModel):
    agent_id: str
    callback_url: str 