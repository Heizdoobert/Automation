#pixon/image_ocr.py
import os
import base64
import requests
import cv2
import numpy as np
import time
from dotenv import load_dotenv

load_dotenv()

AI_KEY = os.getenv("AI_KEY")
AI_MODEL = os.getenv("AI_MODEL", "openrouter/free")
AI_SITE_URL = os.getenv("AI_SITE_URL", "http://localhost")
AI_SITE_NAME = os.getenv("AI_SITE_NAME", "Airtest Automation")

def find_all_text_with_ai(img_array: np.ndarray, max_retries: int =3) -> list:
    """
    Send image to AI and return extracted text lines.
    """
    if not AI_KEY:
        print("Warning: AI_KEY not set, cannot use AI")
        return []

    _, buffer = cv2.imencode('.png', img_array)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    headers = {
            "Authorization": f"Bearer {AI_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": AI_SITE_URL,
            "X-Title": AI_SITE_NAME,
            }

    payload = {
            "model": AI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": "Extract all visible text from this image. Return each text line as a separate string in a Python list format. Example: ['ADS', 'Level: 5', '0%']. Only return the list, no extra text or explanation."
                            },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64, {img_base64}"}
                            }
                        ]
                    }
                ],
            "max_tokens": 10000,
            "temperature": 0,
            }
    for attempt in range(max_retries):
        try:
            response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30
                    )
            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Rate limit hit, waitting {wait_time}s before retry {attempt+1}/{max_retries}")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content'].strip()

            if content.startswith('[') and content.endswith(']'):
                import ast
                texts = ast.literal_eval(content)
                if isinstance(texts, list):
                    return [str(t) for t in texts]
            return [line.strip() for line in content.split('\n') if line.strip()]
        except requests.exceptions.Timeout:
            print(f"AI OCR request timed out after 30s (attempt {attempt+1}/{max_retries}")
            if attempt == max_retries -1:
                return []
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"AI OCR request failed (attempt {attempt+1}): {e}")
            if attempt == max_retries -1:
                return []
            time.sleep(1)
        except Exception as e:
            print(f"AI OCR failed: {e}")
            return []
    return []
