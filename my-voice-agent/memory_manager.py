import os
import json
from datetime import datetime # <--- THIS IS THE FIX
import time

class MemoryManager:
    def __init__(self, persistence_file="memory.json"):
        self.persistence_file = persistence_file
        self._load_memory()
        print("MemoryManager initialized.")

    def initialize_user_profile(self, user_id: str):
        if user_id not in self.memory:
            self.memory[user_id] = {
                "created_at": datetime.datetime.now().isoformat(),
                "conversations": []
            }
            self._save_memory()
        return self.memory[user_id]

    def store_conversation(self, user_id: str, message: str, role: str):
        if user_id in self.memory:
            self.memory[user_id]["conversations"].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "role": role,
                "message": message
            })
            self._save_memory()

    def get_relevant_memories(self, user_id: str, query: str, limit: int = 5) -> list:
        print(f"Placeholder: Searching for relevant memories for user '{user_id}' with query '{query}'")
        return []

    def get_user_profile(self, user_id: str) -> dict:
        print(f"Placeholder: Retrieving user profile for '{user_id}'")
        return self.memory.get(user_id, {}).get("profile", {})

    def store_learned_traits(self, user_id: str, traits: dict):
        if user_id in self.memory:
            self.memory[user_id]["profile"] = self.memory.get(user_id, {}).get("profile", {})
            self.memory[user_id]["profile"]["learned_traits"] = json.dumps(traits)
            self._save_memory()

    def get_conversation_count(self, user_id: str) -> int:
        return len(self.memory.get(user_id, {}).get("conversations", []))

    def _load_memory(self):
        if os.path.exists(self.persistence_file):
            with open(self.persistence_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def _save_memory(self):
        with open(self.persistence_file, 'w') as f:
            json.dump(self.memory, f, indent=2)