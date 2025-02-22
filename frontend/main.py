import streamlit as st
import requests
import json
from typing import Dict, List

API_URL = "http://localhost:8000"  # Update with your API URL

st.title("AI Action Validation Hub")

def load_pending_validations() -> List[Dict]:
    """Fetch pending validations from the API"""
    try:
        response = requests.get(f"{API_URL}/validations", params={"status": "pending"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to load validations: {str(e)}")
        return []

def register_reviewer_webhook():
    """Register this UI instance for webhook notifications of new actions"""
    try:
        # In practice, you'd need to set up a proper webhook endpoint
        # This is just for demonstration
        webhook_url = "https://my-reviewer-webhook.example.com"
        response = requests.post(
            f"{API_URL}/reviewers/webhook",
            json={
                "reviewer_id": "streamlit_ui",
                "callback_url": webhook_url
            }
        )
        response.raise_for_status()
    except Exception as e:
        st.error(f"Failed to register webhook: {str(e)}")

# Register for webhooks when the app starts
register_reviewer_webhook()

st.header("Pending Validations")

# Add a refresh button
if st.button("🔄 Refresh"):
    st.experimental_rerun()

validations = load_pending_validations()
if not validations:
    st.info("No pending validations")

for action_id, validation in validations.items():
    request = validation["request"]
    with st.expander(f"Action: {request['action_type']} (ID: {action_id})"):
        st.write(f"Agent ID: {request['agent_id']}")
        st.write(f"User ID: {request['user_id']}")
        st.text_area("Content", request['content'], height=100, key=action_id)
        
        # Display metadata if present
        if request.get('metadata'):
            st.json(request['metadata'])
        
        col1, col2 = st.columns(2)
        feedback = st.text_area("Feedback", "", key=f"feedback_{action_id}")
        
        if col1.button("Approve", key=f"approve_{action_id}"):
            try:
                response = requests.post(
                    f"{API_URL}/validate/{action_id}/review",
                    json={"status": "approved", "feedback": feedback}
                )
                response.raise_for_status()
                st.success("Action approved!")
                st.experimental_rerun()  # Refresh the UI
            except Exception as e:
                st.error(f"Failed to approve: {str(e)}")
                
        if col2.button("Reject", key=f"reject_{action_id}"):
            try:
                response = requests.post(
                    f"{API_URL}/validate/{action_id}/review",
                    json={"status": "rejected", "feedback": feedback}
                )
                response.raise_for_status()
                st.success("Action rejected!")
                st.experimental_rerun()  # Refresh the UI
            except Exception as e:
                st.error(f"Failed to reject: {str(e)}") 