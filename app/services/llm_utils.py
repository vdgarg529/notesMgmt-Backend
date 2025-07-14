# # # llm_utils.py
# import os
# import httpx
# from dotenv import load_dotenv

# load_dotenv()  # Load environment variables

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# async def generate_summary(texts: list[str]) -> str:
#     """
#     Generates a summary of multiple text notes using Gemini API
#     """
#     if not texts:
#         return "No content available for summary"
    
#     prompt = (
#         "You are an expert note summarizer. Create a concise summary that captures the key points "
#         "and common themes from these user notes:\n\n" +
#         "\n\n---\n\n".join(texts)
#     )
    
#     payload = {
#         "contents": [{
#             "parts": [{"text": prompt}]
#         }],
#         "generationConfig": {
#             "temperature": 0.3,
#             "maxOutputTokens": 512
#         }
#     }
    
#     headers = {"Content-Type": "application/json"}
#     params = {"key": GEMINI_API_KEY}
    
#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 GEMINI_URL,
#                 json=payload,
#                 headers=headers,
#                 params=params
#             )
#             response.raise_for_status()
#             data = response.json()
#             return data['candidates'][0]['content']['parts'][0]['text']
            
#     except Exception as e:
#         # Handle errors gracefully
#         print(f"Gemini API error: {str(e)}")
#         return "Summary unavailable due to processing error"




# llm_utils_async.py

# import os, asyncio
# import httpx
# from dotenv import load_dotenv

# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# async def generate_summary(texts: list[str]) -> str:
#     if not texts or not API_KEY:
#         return "Summary unavailable."

#     prompt = "Summarize briefly:\n\n" + "\n\n".join(texts)
#     async with httpx.AsyncClient(timeout=10) as client:
#         resp = await client.post(
#             f"{API_URL}?key={API_KEY}",
#             json={"contents":[{"parts":[{"text":prompt}]}]},
#         )
#     if resp.status_code == 200:
#         return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
#     raise RuntimeError(f"Gemini error {resp.status_code}: {resp.text}")




# llm_utils.py
import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

async def generate_summary(texts: list[str]) -> str:
    if not texts:
        return "No content available for summary"
    
    # Combine texts with clear separators
    combined_text = "\n\n--- NOTE ---\n\n".join(texts)
    
    prompt = (
        "You are an expert note summarizer. Create a concise summary that captures the key points "
        "and common themes from these user notes. Focus on connecting insights across notes:\n\n"
        f"{combined_text}"
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 512
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GEMINI_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            # Parse response with error handling
            data = response.json()
            if "candidates" not in data or not data["candidates"]:
                return "Summary generation failed: No valid response from API"
            
            return data['candidates'][0]['content']['parts'][0]['text']
            
    except httpx.HTTPStatusError as e:
        error_detail = f"HTTP error {e.response.status_code}: {e.response.text}"
        print(f"Gemini API error: {error_detail}")
        return f"Summary unavailable: API error ({e.response.status_code})"
    except Exception as e:
        print(f"Gemini processing error: {str(e)}")
        return "Summary unavailable due to processing error"