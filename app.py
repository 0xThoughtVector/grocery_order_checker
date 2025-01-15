#app.py
import os
from flask import Flask, request, jsonify
from PIL import Image
import io

# --- Placeholder for your object detection model ---
# Assume we have a function called 'detect_objects' that takes an image
# and returns a list of (label, confidence) for each object recognized.
# We'll mock it for now.
def detect_objects(image):
    """
    Mock detection function.
    For real usage, integrate your Moondream model code here.
    e.g. results = moondream_model.predict(image)
    Return format: [
       {"label": "Coke 750ml", "confidence": 0.92},
       {"label": "Pepsi 1L", "confidence": 0.85},
       ...
    ]
    """
    # Just return a fake response for demonstration
    return [
        {"label": "Coke 750ml", "confidence": 0.95},
        {"label": "Orange Juice 1L", "confidence": 0.60},  # below threshold
        {"label": "Chips Classic", "confidence": 0.82},
    ]

app = Flask(__name__)

# Hard-coded order for demonstration
ORDER_ITEMS = {
    "Coke 750ml": 2,
    "Chips Classic": 1
    # Example: The user wants 2 Coke 750ml, 1 Chips Classic
}
CONFIDENCE_THRESHOLD = 0.80

@app.route('/')
def index():
    return "Grocery MVP - ESP32 Cam Integration"

@app.route('/upload', methods=['POST'])
def upload():
    """
    Endpoint to receive an image from ESP32 Cam.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Convert the file to an Image for further processing
    image_bytes = file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Detect objects using the model
    detections = detect_objects(image)

    # 2. Compare with the order
    found_counts = {}
    total_detected = 0
    unidentified_count = 0

    for det in detections:
        label = det["label"]
        confidence = det["confidence"]
        total_detected += 1
        
        if confidence < CONFIDENCE_THRESHOLD:
            # Mark as unidentified
            unidentified_count += 1
            continue
        
        # Tally up recognized items
        if label not in found_counts:
            found_counts[label] = 0
        found_counts[label] += 1

    # 3. Figure out missing vs extra
    missing = {}
    extra = {}
    
    # Check items in the order
    for sku, required_qty in ORDER_ITEMS.items():
        found_qty = found_counts.get(sku, 0)
        if found_qty < required_qty:
            missing[sku] = required_qty - found_qty
    
    # Check for extras (any recognized label not in ORDER_ITEMS or over the required quantity)
    for sku, found_qty in found_counts.items():
        required_qty = ORDER_ITEMS.get(sku, 0)
        if found_qty > required_qty:
            extra[sku] = found_qty - required_qty
        elif sku not in ORDER_ITEMS:
            extra[sku] = found_qty

    response = {
        "total_detected": total_detected,
        "unidentified_count": unidentified_count,
        "missing_items": missing,  # e.g. {"Coke 750ml": 1}
        "extra_items": extra,      # e.g. {"Orange Juice 1L": 1}
    }

    return jsonify(response), 200

# Simple endpoint to finalize the order
@app.route('/finalize', methods=['POST'])
def finalize_order():
    """
    In a real system, you'd mark the order as complete in your database.
    Here, we just respond with a message.
    """
    return jsonify({"status": "Order Completed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
