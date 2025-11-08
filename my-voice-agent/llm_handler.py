# llm_handler.py (Refactored)
import os
import requests
from typing import Iterator, Optional

# A simple registry to define providers and their models
PROVIDER_CONFIG = {
    "anthropic": {
        "models": {
            "claude-3-5-sonnet-20241022": {"provider": "anthropic", "api_url": "https://api.anthropic.com/v1/messages"},
            "claude-3-haiku-20240307": {"provider": "anthropic", "api_url": "https://api.anthropic.com/v1/messages"},
        },
        "openrouter": {
            "models": {
                "anthropic/claude-3-opus-20240229": {"provider": "anthropic", "api_url": "https://api.anthropic.com/v1/messages"},
                "google/gemini-2.0-flash-exp": {"provider": "google", "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"},
            }
        },
        "huggingface": {
            "models": {
                "mistralai/Mixtral-8x7B": {"provider": "huggingface", "api_url": "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B"},
                "meta-llama/Meta-Llama-3.1-8B-Instruct": {"provider": "huggingface", "api_url": "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"},
            }
        }
    }
}

class LLMHandler:
    """Handle LLM interactions with a robust provider registry."""

    def __init__(self):
        """Initialize LLM handler with API keys and configurations."""
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        
        self.default_model = os.getenv("PREFERRED_MODEL", "anthropic/claude-3-haiku-20240307")
        
        # This is the improved provider determination logic
        self.provider, self.model_id = self._determine_provider_and_model(self.default_model)
        
        if not self.provider:
            raise ValueError(f"LLM provider could not be determined for model '{self.default_model}'. Check API keys and environment variables.")
    
    def _determine_provider_and_model(self, model_input: str) -> tuple[str, str]:
        """
        Robustly determine the provider and final model ID.
        Searches the provider registry for a matching model.
        """
        for provider_name, provider_data in PROVIDER_CONFIG.items():
            for model_id in provider_data["models"]:
                if model_input.lower().startswith(model_id.lower()) or model_id.lower().startswith(model_id):
                    return provider_name, model_id
        
        # Fallback to OpenRouter if a specific model is requested but not in the registry
        if self.openrouter_key:
            return "openrouter", model_input
        
        raise ValueError(f"Model '{model_input}' is not supported by any configured provider.")

    def generate_streaming(self, prompt: str, model: Optional[str] = None) -> Iterator[str]:
        """
        Generate a streaming response using the configured provider.
        """
        model_to_use = model or self.model_id
        provider_name = PROVIDER_CONFIG[self.provider]["models"][model_to_use]["provider"]
        api_url = PROVIDER_CONFIG[self.provider]["models"][model_to_use]["api_url"]
        
        print(f"Generating response with {self.provider} using model {model_to_use}...")
        
        try:
            if self.provider == "anthropic":
                yield from self._call_anthropic_streaming(prompt, api_url)
            elif self.provider == "huggingface":
                yield from self._call_huggingface_streaming(prompt, api_url)
            elif self.provider == "openrouter":
                yield from self._call_openrouter_streaming(prompt, model_to_use, api_url)
            else:
                raise NotImplementedError(f"Provider '{self.provider}' is not implemented for streaming.")
        except Exception as e:
            yield f"Error during generation with {self.provider}: {str(e)}"
    
    def _call_anthropic_streaming(self, prompt: str, api_url: str) -> Iterator[str]:
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {"model": self.model_id, "max_tokens": 2000, "stream": True, "messages": [{"role": "user", "content": prompt}]}
        
        response = requests.post(api_url, headers=headers, json=data, stream=True, timeout=60)
        response.raise_for_status()
        for line in response.iter_lines():
            line = line.decode('utf-8')
            if line.startswith("data: "):
                line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    chunk = json.loads(line)
                    if chunk.get("type") == "content_block_delta" and chunk.get("delta", {}).get("text"):
                        yield chunk["delta"]["text"]
                except json.JSONDecodeError:
                    continue
    
    def _call_huggingface_streaming(self, prompt: str, api_url: str) -> Iterator[str]:
        headers = {"Authorization": f"Bearer {self.hf_token}", "Content-Type": "application/json"}
        data = {"inputs": prompt, "parameters": {"max_new_tokens": 2000, "stream": True}}
        
        response = requests.post(api_url, headers=headers, json=data, stream=True, timeout=60)
        
        if response.status_code == 503: # Model loading
            yield "Model is loading, please try again in a few moments..."
            return
            
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'token' in chunk:
                        text = chunk.get('token', {}).get('text', '')
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue
    
    def _call_openrouter_streaming(self, prompt: str, model_id: str, api_url: str) -> Iterator[str]:
        headers = {"Authorization": f"Bearer {self.openrouter_key}", "Content-Type": "application/json", "HTTP-Referer": "https://huggingface.co/"}
        data = {"model": model_id, "messages": [{"role": "user", "content": prompt}]}
        
        response = requests.post(api_url, headers=headers, json=data, stream=True, timeout=60)
        response.raise_for_status()
        for line in response.iter_lines():
            if line.startswith("data: "):
                line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    chunk = json.loads(line)
                    if chunk.get("choices") and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if delta.get("content"):
                            yield delta["content"]
                except json.JSONDecodeError:
                    continue

    def get_provider_info(self) -> dict:
        """Get information about the current provider configuration."""
        return {
            "provider": self.provider,
            "model": self.model_id,
            "available_providers": [key for key, value in os.environ.items() if key.endswith('_API_KEY')]
        }