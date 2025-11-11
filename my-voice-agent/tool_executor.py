import os
import requests

class ToolExecutor:
    def __init__(self):
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not self.n8n_webhook_url:
            print("Warning: N8N_WEBHOOK_URL not set.")

    def execute_tools(self, message: str) -> str:
        if not self.n8n_webhook_url:
            return "n8n integration not configured."
        try:
            resp = requests.post(self.n8n_webhook_url, json={"message": message}, timeout=30)
            resp.raise_for_status()
            if resp.headers.get("content-type", "").startswith("application/json"):
                # Expecting n8n to return {"result": ...}
                return resp.json().get("result", str(resp.json()))
            return resp.text
        except Exception as e:
            return f"Error contacting n8n workflow: {str(e)}"