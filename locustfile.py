import random
import uuid
from locust import HttpUser, task, between

class AIGatewayUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
    
        self.email = f"test_{uuid.uuid4()}@example.com"
        self.password = "SecurePass123!"

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(2)
    def ai_chat_mock(self):
        payload = {
            "model": "mock-model",
            "messages": [
                {"role": "user", "content": "Hello, this is a load test!"}
            ]
        }
      
        self.client.post("/api/v1/ai/chat", json=payload)