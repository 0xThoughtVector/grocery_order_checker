"""
Handles calls to the Gemini API. 
We use google-generativeai library with the provided "gemini-exp-1206" model.
We'll parse the textual response to get item names.
"""

import base64
import google.generativeai as genai
from config import Config

# Initialize the Gemini model on import
genai.configure(api_key=Config.GEMINI_API_KEY)

def analyze_image_for_items(image_bytes: bytes) -> str:
    """
    Calls the Gemini model with the given image, asking for a *list* of items 
    recognized in the image (text). Returns the raw text from the model.
    """
    # Prepare image as base64
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

    # Make a prompt that tries to get a clean list of items
    prompt_text = (
        "List all grocery items you see in the image. "
        "If you see multiple of the same item, mention it multiple times or "
        "indicate the count. Use bullet points or lines so it's easier to parse."
    )

    # Make the request using the new API
    model = genai.GenerativeModel('gemini-exp-1206')  # Keep your original model name
    response = model.generate_content(
        contents=[
            {
                "parts": [
                    {"mime_type": "image/jpeg", "data": encoded_image},
                    {"text": prompt_text}
                ]
            }
        ]
    )

    # Return the response text
    return response.text

def parse_gemini_response_into_items(text_response: str) -> dict:
    """
    A naive parser to turn Gemini's textual listing of items into a dict:
       e.g. {
           'Coke': 2,
           'Chips': 1
       }
    We handle some common patterns, but this is *highly subject* to how the model
    formats the text. 
    """

    # We'll do a line-by-line parse. 
    # If we see a line like "- 2 Coke" or "• Coke (2)" or "Coke x2" we'll attempt to parse.
    # This is a trivial example, you can refine it with regex or AI-based parsing.
    lines = text_response.split("\n")
    recognized_dict = {}

    for line in lines:
        line = line.strip("•-•* ")  # remove bullet chars
        if not line:
            continue
        
        # We look for something like "Coke x2" or "2 Cokes" or "Coke (2)"
        # We'll do a quick attempt with regex for any digit, then item name
        # If no digit is found, assume 1
        import re
        match = re.search(r"(\d+)\s*x?\s*([a-zA-Z0-9\s]+)", line)
        if match:
            qty_str, item_str = match.groups()
            item_str = item_str.strip()
            qty = int(qty_str)
        else:
            # Attempt "([a-zA-Z\s]+)\s*\(?(\d+)\)?"
            match2 = re.search(r"([a-zA-Z0-9\s]+)\s*\(?(\d+)\)?", line)
            if match2:
                item_part, qty_str = match2.groups()
                item_str = item_part.strip()
                qty = int(qty_str)
            else:
                # If no pattern found, assume entire line is item with quantity=1
                item_str = line.strip()
                qty = 1
        
        # Standardize item name to Title Case, or your store's canonical form
        # For real production, you might do fuzzy matching or SKU-based synonyms
        item_str = item_str.title()

        # Accumulate in dictionary
        if item_str in recognized_dict:
            recognized_dict[item_str] += qty
        else:
            recognized_dict[item_str] = qty

    return recognized_dict
