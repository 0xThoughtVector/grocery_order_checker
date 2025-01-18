"""
Main Flask app for production:
 - /upload  -> POST with 'order_id' and 'image' file, returns JSON of match results.
"""

import io
from flask import Flask, request, jsonify
from config import Config
from db import get_order_by_id
from gemini_api import analyze_image_for_items, parse_gemini_response_into_items
from utils import compare_order

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Receives an image file from the ESP32 camera and an 'order_id'.
    The 'order_id' parameter is used to fetch the required items from the DB.
    Then calls Gemini for item recognition, compares with the order, returns JSON.
    """
    # 1. Retrieve the order_id
    order_id = request.form.get("order_id", type=int)
    if not order_id:
        return jsonify({"error": "Missing or invalid order_id"}), 400
    
    # 2. Get the order from DB
    order_required = get_order_by_id(order_id)
    if not order_required:
        return jsonify({"error": f"No order found for id={order_id}"}), 404
    
    # 3. Get the image from the form data
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()

    # 4. Call Gemini
    gemini_text = analyze_image_for_items(image_bytes)
    
    # 5. Parse recognized items
    recognized_items = parse_gemini_response_into_items(gemini_text)
    
    # 6. Compare recognized vs. required
    missing, extra = compare_order(recognized_items, order_required)

    # 7. Build the response
    response_data = {
        "order_id": order_id,
        "recognized_items": recognized_items,  # e.g. {"Coke":2,"Chips":1}
        "missing_items": missing,
        "extra_items": extra,
        "total_recognized_items": sum(recognized_items.values()),
        "gemini_raw_response": gemini_text  # for debugging / optional
    }
    
    return jsonify(response_data), 200


@app.route('/finalize/<int:order_id>', methods=['POST'])
def finalize_order(order_id):
    """
    Indicate the order is completed. 
    In real production, you'd update DB status or notify another system.
    """
    # For now, just return a message.
    # You could do: db.mark_order_complete(order_id)
    return jsonify({"message": f"Order {order_id} has been finalized."}), 200


if __name__ == '__main__':
    # For production, run via WSGI server (gunicorn, uwsgi).
    # For dev, we can do:
    app.run(host='0.0.0.0', port=5000, debug=True)
