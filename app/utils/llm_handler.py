import httpx
import json
from typing import Optional

class LLMHandler:
    def __init__(self):
        self.ollama_url = "http://ollama:11434"
        self.model = "codellama"

    async def _ensure_model_exists(self) -> bool:
        """Check if model exists and pull if it doesn't"""
        try:
            async with httpx.AsyncClient() as client:
                # First check if model exists
                response = await client.post(
                    f"{self.ollama_url}/api/pull",
                    json={"name": self.model},
                    timeout=60.0
                )
                print(f"Model pull response: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            print(f"Error ensuring model exists: {e}")
            return False

    async def get_explanation(self, sql_code: str) -> str:
        try:
            # Ensure model is available
            if not await self._ensure_model_exists():
                return "Error: Failed to load the required model"

            chunks = self._split_sql(sql_code)
            full_explanation = []

            for chunk in chunks:
                prompt = self._create_prompt(chunk)
                explanation = await self._get_llm_response(prompt)
                if explanation and not explanation.startswith("Error"):
                    full_explanation.append(explanation)
                else:
                    print(f"Failed to get explanation for chunk: {chunk}")

            if not full_explanation:
                return "Error: Could not generate explanation"
                
            return "\n".join(full_explanation)
        except Exception as e:
            print(f"Error in get_explanation: {e}")
            return f"Error: {str(e)}"

    async def _get_llm_response(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                print(f"LLM Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "response" in result:
                        return result["response"]
                    print(f"Unexpected response format: {result}")
                    return "Error: Unexpected response format"
                else:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                    print(f"Error from LLM: {error_message}")
                    return f"Error: {error_message}"
                    
        except httpx.TimeoutException:
            print("Request to LLM timed out")
            return "Error: Request timed out"
        except Exception as e:
            print(f"Exception in _get_llm_response: {e}")
            return f"Error: {str(e)}"

    # ... rest of your methods remain the same ...
