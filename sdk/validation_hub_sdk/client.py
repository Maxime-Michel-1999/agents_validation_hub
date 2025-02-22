import requests
from typing import Optional, Tuple, Dict, List
import uuid

#TODO: Enable multiple modality (or markdown format) for content.s

class ValidationClient:
    """Client for interacting with the AI Action Validation Hub"""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize the validation client.
        
        Args:
            api_url: Base URL of the validation hub API
            api_key: Optional API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    def submit_action(
        self,
        agent_id: str,
        user_id: str,
        action_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Submit an action for validation.
        
        Args:
            agent_id: Identifier of the submitting agent
            user_id: Identifier of the user the action is for
            action_type: Type of action being validated
            content: Content of the action
            metadata: Optional metadata about the action
            
        Returns:
            str: The validation ID assigned to this request
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Generate a unique action_id instead of using id(content)
        action_id = f"{action_type}_{uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{self.api_url}/validate",
            headers=self.headers,
            json={
                "agent_id": agent_id,
                "user_id": user_id,
                "action_id": action_id,
                "action_type": action_type,
                "content": content,
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        return response.json()["validation_id"]
    
    def get_validation_status(self, action_id: str) -> Tuple[str, Optional[str]]:
        """
        Get the current status and feedback for a validation request.
        
        Args:
            action_id: The ID of the action to check
            
        Returns:
            Tuple[str, Optional[str]]: The status and any feedback
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.get(
            f"{self.api_url}/validate/{action_id}",
            headers=self.headers
        )
        response.raise_for_status()
        result = response.json()
        return result["status"], result.get("feedback")
    
    def register_webhook(self, agent_id: str, callback_url: str) -> bool:
        """
        Register a webhook to receive validation updates.
        
        Args:
            agent_id: Identifier of the agent registering the webhook
            callback_url: URL where validation updates should be sent
            
        Returns:
            bool: True if registration was successful
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.post(
            f"{self.api_url}/agents/webhook",
            headers=self.headers,
            json={
                "agent_id": agent_id,
                "callback_url": callback_url
            }
        )
        response.raise_for_status()
        return True

    def list_validations(self, status: Optional[str] = None) -> Dict:
        """
        List all validations, optionally filtered by status.
        
        Args:
            status: Optional status to filter by (e.g., "pending", "approved", "rejected")
            
        Returns:
            Dict: Dictionary of validation records
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params = {"status": status} if status else {}
        response = requests.get(
            f"{self.api_url}/validations",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json() 