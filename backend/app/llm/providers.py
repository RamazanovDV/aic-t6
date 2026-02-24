import json

import requests

from app.llm.base import BaseProvider, LLMResponse, Message


API_KEY_MASK = "[API_KEY_MASKED]"


class GenericOpenAIProvider(BaseProvider):
    def chat(self, messages: list[Message], system_prompt: str | None = None, debug: bool = False) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": 0.7,
        }

        debug_request = None
        debug_response = None
        
        if debug:
            debug_request = {
                "url": self.url,
                "method": "POST",
                "headers": {**headers, "Authorization": f"Bearer {API_KEY_MASK}"},
                "body": payload,
            }

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        usage = {}
        if "usage" in data:
            usage = {
                "input_tokens": data["usage"].get("prompt_tokens", 0),
                "output_tokens": data["usage"].get("completion_tokens", 0),
                "total_tokens": data["usage"].get("total_tokens", 0),
            }

        if debug:
            debug_response = data

        return LLMResponse(
            content=content,
            model=self.model,
            usage=usage,
            debug_request=debug_request,
            debug_response=debug_response,
        )

    def list_models(self) -> list[str]:
        try:
            base_url = self.url
            if "/chat/completions" in base_url:
                base_url = base_url.split("/chat/completions")[0]
            elif "/messages" in base_url:
                base_url = base_url.split("/messages")[0]
            elif "/v1" in base_url:
                base_url = base_url.split("/v1")[0]
            
            models_url = f"{base_url}/v1/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.get(models_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def get_provider_name(self) -> str:
        return "generic"


class OpenAIProvider(GenericOpenAIProvider):
    def chat(self, messages: list[Message], system_prompt: str | None = None, debug: bool = False) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": 0.7,
        }

        debug_request = None
        debug_response = None
        
        if debug:
            debug_request = {
                "url": self.url,
                "method": "POST",
                "headers": {**headers, "Authorization": f"Bearer {API_KEY_MASK}"},
                "body": payload,
            }

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        usage = {}
        if "usage" in data:
            usage = {
                "input_tokens": data["usage"].get("prompt_tokens", 0),
                "output_tokens": data["usage"].get("completion_tokens", 0),
                "total_tokens": data["usage"].get("total_tokens", 0),
            }

        if debug:
            debug_response = data

        return LLMResponse(
            content=content,
            model=self.model,
            usage=usage,
            debug_request=debug_request,
            debug_response=debug_response,
        )

    def get_provider_name(self) -> str:
        return "openai"


class AnthropicProvider(BaseProvider):
    def chat(self, messages: list[Message], system_prompt: str | None = None, debug: bool = False) -> LLMResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})

        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": [{"type": "text", "text": msg.content}]})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": 4096,
        }

        debug_request = None
        debug_response = None
        
        if debug:
            debug_request = {
                "url": self.url,
                "method": "POST",
                "headers": {**headers, "x-api-key": API_KEY_MASK},
                "body": payload,
            }

        response = requests.post(self.url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()
        content = data["content"][0]["text"]
        
        usage = {}
        if "usage" in data:
            usage = {
                "input_tokens": data["usage"].get("input_tokens", 0),
                "output_tokens": data["usage"].get("output_tokens", 0),
                "total_tokens": data["usage"].get("input_tokens", 0) + data["usage"].get("output_tokens", 0),
            }

        if debug:
            debug_response = data

        return LLMResponse(
            content=content,
            model=self.model,
            usage=usage,
            debug_request=debug_request,
            debug_response=debug_response,
        )

    def list_models(self) -> list[str]:
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            }
            base_url = self.url
            if "/messages" in base_url:
                base_url = base_url.split("/messages")[0]
            elif "/v1" in base_url:
                base_url = base_url.split("/v1")[0]
            models_url = f"{base_url}/v1/models"
            response = requests.get(models_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def get_provider_name(self) -> str:
        return "anthropic"


class OllamaProvider(BaseProvider):
    def chat(self, messages: list[Message], system_prompt: str | None = None, debug: bool = False) -> LLMResponse:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key and self.api_key != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
        }

        debug_request = None
        debug_response = None
        
        if debug:
            debug_headers = {**headers}
            if "Authorization" in debug_headers:
                debug_headers["Authorization"] = f"Bearer {API_KEY_MASK}"
            debug_request = {
                "url": self.url,
                "method": "POST",
                "headers": debug_headers,
                "body": payload,
            }

        response = requests.post(self.url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        content = data["message"]["content"]

        if debug:
            debug_response = data

        return LLMResponse(
            content=content,
            model=self.model,
            usage={},
            debug_request=debug_request,
            debug_response=debug_response,
        )

    def list_models(self) -> list[str]:
        try:
            base_url = self.url.split("/v1")[0] if "/v1" in self.url else self.url
            models_url = f"{base_url}/api/tags"
            response = requests.get(models_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def get_provider_name(self) -> str:
        return "ollama"
