"""Gemini LLM Client with structured output support."""

import json
import os
import typing
from typing import Any, Type

import google.generativeai as genai
from pydantic import BaseModel


class LLMClient:
    """Client for interacting with Google Gemini API with structured outputs."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        
        # Use a model that supports structured outputs well
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a text response from the LLM."""
        
        # Gemini handles system prompts a bit differently (as system_instruction in newer versions
        # or just part of the prompt). For simplicity and compatibility, we'll prepend it if possible
        # or use the system_instruction if initializing a new model instance.
        
        # Re-initializing model with system prompt for this call if needed, 
        # but standard way is often just to include it in the chat or config.
        # simpler approach:
        
        full_content = []
        if system_prompt:
             # System instructions are best set at model creation, but for single-turn 
             # variable system prompts, we can just prepend it.
             # Or use the system_instruction argument if we create a new model instance.
             # Let's try the cleaner `system_instruction` way.
             model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        else:
             model = self.model

        response = model.generate_content(prompt)
        return response.text

    def generate_structured(
        self, prompt: str, response_model: Type[BaseModel], system_prompt: str = ""
    ) -> BaseModel:
        """Generate a structured response using Pydantic model."""
        
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
        )

        if system_prompt:
            model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        else:
            model = self.model

        # Configure safety settings to avoid blocking standard queries
        safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        }

        try:
            response = model.generate_content(
                prompt, 
                generation_config=generation_config,
                safety_settings=safety_settings
            )
        except Exception as e:
            print(f"❌ Gemini Generation Error: {e}")
            raise ValueError(f"Gemini API failed to generate content: {e}")

        # Check if response was blocked
        if not response.parts and response.prompt_feedback:
            print(f"❌ Gemini blocked the response: {response.prompt_feedback}")
            raise ValueError("Gemini blocked the response due to safety settings.")
            
        print(f"DEBUG RAW RESPONSE: {response.text}")
        
        # Debugging aid
        # print(f"DEBUG RESPONSE: {response.text}")

        # The response text should be JSON that matches the schema
        text = response.text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(text)
            
            # 2024-02-04: Fix for Gemini returning a list of steps instead of the full object
            if isinstance(data, list):
                # We assume the list contains the steps. 
                # We need to construct the expected object.
                # Since we don't have the summary/expected_output, we'll generate placeholders
                # or infer them.
                print(f"⚠️ Gemini returned a list, wrapping in expected structure...")
                data = {
                    "task_summary": "Task execution plan (auto-generated)",
                    "steps": data,
                    "expected_output": "Final result of the steps"
                }
            
            # 2024-02-04: Fix for Gemini returning 'plan' instead of 'steps'
            elif isinstance(data, dict):
                if "steps" not in data and "plan" in data:
                    print(f"⚠️ Gemini used 'plan' key instead of 'steps', mapping it...")
                    data["steps"] = data.pop("plan")
                
                # Ensure all required keys exist
                if "task_summary" not in data:
                    data["task_summary"] = "Task execution plan"
                if "expected_output" not in data:
                     data["expected_output"] = "Execution results"

            return response_model.model_validate(data)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            print(f"❌ Failed Text: {text}")
            raise ValueError(f"Failed to decode JSON from LLM: {text[:100]}...")

        try:
            # Handle double-encoded JSON (if data is a string)
            if isinstance(data, str):
                try:
                    print("⚠️ Data is a string, attempting second decode...")
                    data = json.loads(data)
                except:
                    pass

            # Helper function to recursively clean keys
            def clean_keys(obj):
                if isinstance(obj, dict):
                    # Strip whitespace, single quotes, double quotes from keys
                    return {k.strip().strip('"').strip("'"): clean_keys(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_keys(i) for i in obj]
                else:
                    return obj

            data = clean_keys(data)
            
            # 2024-02-04: Fix for Gemini returning a list of steps
            if isinstance(data, list):
                print(f"⚠️ Gemini returned a list, wrapping in expected structure...")
                data = {
                    "task_summary": "Task execution plan (auto-generated)",
                    "steps": data,
                    "expected_output": "Final result of the steps"
                }
            
            # 2024-02-04: Fix for Gemini returning 'plan' instead of 'steps'
            elif isinstance(data, dict):
                # Handle keys that might have extra quotes or newlines
                # (Already handled by the strip above, but let's be safe)
                
                if "steps" not in data and "plan" in data:
                    print(f"⚠️ Gemini used 'plan' key instead of 'steps', mapping it...")
                    data["steps"] = data.pop("plan")
                
                # Check for "response" wrapper
                if "steps" not in data and "response" in data and isinstance(data["response"], dict):
                     print(f"⚠️ Gemini wrapped response in 'response', unwrapping...")
                     data = data["response"]

                # Ensure all required keys exist
                if "task_summary" not in data:
                    data["task_summary"] = "Task execution plan"
                if "expected_output" not in data:
                     data["expected_output"] = "Execution results"

            print(f"DEBUG VALIDATING DATA: {json.dumps(data, indent=2)}")
            return response_model.model_validate(data)

        except Exception as e:
            print(f"❌ Validation Logic Error: {e}")
            print(f"❌ Data Type: {type(data)}")
            print(f"❌ Data: {data}")
            raise ValueError(f"Failed to validate/process JSON data: {e}")

    def generate_json(self, prompt: str, system_prompt: str = "") -> dict[str, Any]:
        """Generate a JSON response from the LLM."""
        
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )

        if system_prompt:
            model = genai.GenerativeModel(self.model_name, system_instruction=system_prompt)
        else:
            model = self.model

        response = model.generate_content(prompt, generation_config=generation_config)
        return json.loads(response.text)
