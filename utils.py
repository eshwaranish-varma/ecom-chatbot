import requests
import random
import json # For formatting the request body
import streamlit as st # Import Streamlit to access secrets

# Fetch the API key from Streamlit secrets
# Ensure you set this in your Streamlit Community Cloud app settings
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
# Fallback for local testing if you set it as an environment variable (optional)
# if not OPENROUTER_API_KEY:
#     import os
#     OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
# You can refer to your OpenRouter dashboard or documentation for the exact model identifier.
# Using a common Mistral model often available on OpenRouter.
DEFAULT_MODEL_ID = "mistralai/mistral-7b-instruct"

class ModelGenerationError(Exception):
    """Custom exception for model generation errors."""
    pass

def generate_description(prompt_text, model_id=DEFAULT_MODEL_ID):
    if not OPENROUTER_API_KEY:
        # This error will now primarily appear if the secret isn't set in Streamlit Cloud
        st.error("OpenRouter API key not configured. Please set it in Streamlit Cloud secrets or as an environment variable for local testing.")
        raise ValueError("OpenRouter API key not found. Please ensure it is set in Streamlit Cloud secrets.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # OpenRouter specific headers if any (e.g., for routing or referrals)
        # "HTTP-Referer": "YOUR_SITE_URL", # Optional: Replace with your app's URL or name
        # "X-Title": "GenAI Product Desc Gen", # Optional: Replace with your app's name
    }

    # Construct the payload according to OpenRouter's chat completions API
    # This usually follows OpenAI's format.
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "temperature": round(random.uniform(0.6, 1.0), 2),
        "max_tokens": 150 # Adjust as needed
    }

    try:
        response = requests.post(
            f"{OPENROUTER_API_BASE}/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30 # Add a timeout
        )
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
        
        response_json = response.json()
        
        # Extract the content from the response
        # The exact structure can vary slightly, but typically it's in choices[0].message.content
        if response_json.get("choices") and response_json["choices"][0].get("message"):
            content = response_json["choices"][0]["message"].get("content", "")
            return content.strip()
        else:
            # Fallback or error if the expected structure isn't found
            print(f"Unexpected response structure from OpenRouter: {response_json}")
            raise ModelGenerationError("Failed to parse model response from OpenRouter.")

    except requests.exceptions.HTTPError as e:
        error_details = e.response.text if e.response else "No additional error details."
        error_message = f"OpenRouter API HTTP Error: {e.response.status_code} - {e}. Details: {error_details}"
        print(error_message)
        raise ModelGenerationError(error_message)
    except requests.exceptions.RequestException as e:
        # For other network errors (timeout, connection error, etc.)
        error_message = f"OpenRouter API Request Error: {e}"
        print(error_message)
        raise ModelGenerationError(error_message)
    except Exception as e:
        error_message = f"Generic error calling OpenRouter API: {type(e).__name__} - {e}"
        print(error_message)
        raise ModelGenerationError(error_message)
