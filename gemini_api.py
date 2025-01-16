#gemini_api.py
"""
gemini_api.py

This module simulates calls to the "gemini-exp-1206" model.
It exposes a function `call_gemini_api(image_data: bytes) -> list[str]`
that returns recognized items in the image as a list of item names.

Edge cases addressed:
- If the model fails to identify items, we return an empty list.
- For demonstration, this is a mock. In a real system, you'd parse the text from Gemini's response.
"""

import random

def call_gemini_api(image_data: bytes) -> list:
    """
    Calls the gemini-exp-1206 model with the given image data.
    Returns a list of recognized item strings.
    
    NOTE: This is a mock. In actual usage, you'd do something like:
    
        response = requests.post(
            "https://gemini.googleapis.com/v1/image:analyze",
            headers={"Authorization": f"Bearer {API_KEY}", ...},
            files={"file": ("image.jpg", image_data, "image/jpeg")},
            ...
        )
        # Then parse the JSON response from Gemini to extract recognized items.
    """
    
    # Randomly decide if no items are recognized (simulating poor detection).
    if random.random() < 0.1:  # 10% chance of returning nothing
        return []

    # Otherwise return a random subset of items to simulate detection.
    sample_items_pool = [
        "Coke 500ml", "Coke 500ml",  # repeated to simulate multiples
        "Chips Classic", "Chips BBQ", 
        "Pepsi 330ml", "Pepsi 330ml", 
        "Water Bottle", "Milk 1L", 
        "Bread Loaf", "Eggs 12-pack"
    ]

    # We'll pick up to 7 random items from the pool for the mock.
    recognized_items = random.sample(sample_items_pool, k=random.randint(1, 7))

    return recognized_items
