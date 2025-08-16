# import os
# import httpx
# from dotenv import load_dotenv
# import json

# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# async def generate_summary(texts: list[str]) -> str:
#     if not texts:
#         return "No content available for summary"
    
#     # Combine texts with clear separators
#     combined_text = "\n\n--- NOTE ---\n\n".join(texts)
    
#     prompt = (
#         "You are an expert note summarizer. Create a concise summary that captures the key points "
#         "and common themes from these user notes. Focus on connecting insights across notes:\n\n"
#         f"{combined_text}"
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
    
#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 GEMINI_URL,
#                 json=payload,
#                 headers=headers
#             )
#             response.raise_for_status()
            
#             # Parse response with error handling
#             data = response.json()
#             if "candidates" not in data or not data["candidates"]:
#                 return "Summary generation failed: No valid response from API"
            
#             return data['candidates'][0]['content']['parts'][0]['text']
            
#     except httpx.HTTPStatusError as e:
#         error_detail = f"HTTP error {e.response.status_code}: {e.response.text}"
#         print(f"Gemini API error: {error_detail}")
#         return f"Summary unavailable: API error ({e.response.status_code})"
#     except Exception as e:
#         print(f"Gemini processing error: {str(e)}")
#         return "Summary unavailable due to processing error"




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
            
            # Parse response with improved error handling
            data = response.json()
            if "candidates" not in data or not data["candidates"]:
                return "Summary generation failed: No valid response from API"
            
            # Safely access nested response structure
            try:
                return data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return "Summary generation failed: Malformed API response"
            
    except httpx.HTTPStatusError as e:
        error_detail = f"HTTP error {e.response.status_code}: {e.response.text}"
        print(f"Gemini API error: {error_detail}")
        return f"Summary unavailable: API error ({e.response.status_code})"
    except Exception as e:
        print(f"Gemini processing error: {str(e)}")
        return "Summary unavailable due to processing error"