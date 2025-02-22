import time
import random
from validation_hub_sdk.client import ValidationClient
import asyncio
from datetime import datetime

class TestAgent:
    def __init__(self, api_url: str):
        self.client = ValidationClient(api_url)
        self.agent_id = "test_agent_1"
        self.test_user_id = "test_user_1"
        
    def generate_test_action(self) -> dict:
        """Generate a random test action"""
        action_types = ["email_draft", "social_post", "code_change", "data_query"]
        action_type = random.choice(action_types)
        
        content_templates = {
            "email_draft": "Dear {}, \n\nThis is a test email about {}.\n\nBest regards,\nAI Agent",
            "social_post": "Exciting news! {} just happened in the world of {}! #AI #Tech",
            "code_change": "def update_{}():\n    # TODO: Implement {} logic\n    pass",
            "data_query": "SELECT * FROM {} WHERE {} = True;"
        }
        
        subjects = ["AI", "Machine Learning", "Data Science", "Python", "Cloud Computing"]
        topics = ["recent developments", "best practices", "future trends", "optimization"]
        
        content = content_templates[action_type].format(
            random.choice(subjects),
            random.choice(topics)
        )
        
        return {
            "action_type": action_type,
            "content": content,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "priority": random.choice(["low", "medium", "high"]),
                "category": random.choice(subjects)
            }
        }

    async def submit_and_monitor_action(self):
        """Submit an action and monitor its status"""
        action = self.generate_test_action()
        
        print(f"\n🤖 Submitting {action['action_type']} action...")
        try:
            validation_id = self.client.submit_action(
                agent_id=self.agent_id,
                user_id=self.test_user_id,
                action_type=action["action_type"],
                content=action["content"],
                metadata=action["metadata"]
            )
            print(f"✅ Action submitted! Validation ID: {validation_id}")
            
            # Monitor the status
            while True:
                status, feedback = self.client.get_validation_status(validation_id)
                print(f"📊 Current status: {status}")
                if feedback:
                    print(f"💬 Feedback received: {feedback}")
                
                if status in ["approved", "rejected"]:
                    print(f"🏁 Final status: {status}")
                    break
                    
                await asyncio.sleep(5)  # Check every 5 seconds
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    agent = TestAgent("http://localhost:8000")
    
    print("🚀 Starting test agent...")
    
    # Submit a few test actions
    tasks = []
    for _ in range(3):  # Submit 3 actions
        tasks.append(agent.submit_and_monitor_action())
        await asyncio.sleep(2)  # Wait 2 seconds between submissions
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 