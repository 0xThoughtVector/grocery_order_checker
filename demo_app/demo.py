#demo.py
"""
Demo (Replit) App:
 - Single-page web interface that simulates a chat.
 - The user sets an order via "order: <sku>=<qty>, <sku>=<qty>..."
 - Then the user can upload images in subsequent messages.
 - The system responds with recognized items, missing, etc.
 - "finalize" ends the session.
"""

import io
from flask import Flask, render_template_string, request
from .gemini_api import analyze_image_for_items, parse_gemini_response_into_items
from production_app.utils import compare_order

app = Flask(__name__)

# We'll keep session data in a dictionary for each user "session_id"
# In real code, you'd use server-side sessions or a database
SESSIONS = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Grocery Order Demo Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chat-bubble { margin: 10px 0; padding: 10px; border-radius: 5px; width: fit-content; }
        .user-bubble { background-color: #d1e7dd; }
        .system-bubble { background-color: #f8d7da; }
    </style>
</head>
<body>
<h1>Grocery Order Demo Chat</h1>

<div id="chat-container">
    {% for msg in messages %}
      {% if msg["sender"] == "user" %}
        <div class="chat-bubble user-bubble">{{ msg["text"] }}</div>
      {% else %}
        <div class="chat-bubble system-bubble">{{ msg["text"]|safe }}</div>
      {% endif %}
    {% endfor %}
</div>

<form method="POST" enctype="multipart/form-data">
    <p>Type a message or an order command:</p>
    <input type="text" name="user_text" style="width: 300px;" />
    <br/><br/>
    <p>Or upload an image:</p>
    <input type="file" name="image" accept="image/*" />
    <br/><br/>
    <button type="submit">Send</button>
</form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def chat():
    session_id = "demo"  # For a real multi-user scenario, you'd generate or track a user session
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "order_required": {},  # e.g. {"Coke":2,"Chips":1}
            "messages": []
        }

    session_data = SESSIONS[session_id]
    messages = session_data["messages"]

    if request.method == "POST":
        user_text = request.form.get("user_text", "").strip()
        image_file = request.files.get("image", None)

        # Record the user's input
        if user_text or image_file:
            messages.append({"sender": "user", "text": user_text if user_text else "[User uploaded an image]"})

        # 1. Check if user_text is an order definition, e.g.: "order: Coke=2, Chips=1"
        if user_text.lower().startswith("order:"):
            order_str = user_text[len("order:"):].strip()
            # parse this, e.g. "Coke=2, Chips=1"
            order_required = {}
            items = order_str.split(",")
            for it in items:
                it = it.strip()
                if "=" in it:
                    name, qty_str = it.split("=")
                    name = name.strip().title()
                    qty = int(qty_str.strip())
                    order_required[name] = qty
            
            session_data["order_required"] = order_required
            messages.append({
                "sender": "system",
                "text": f"Order set! <br/>Required items: {order_required}"
            })

        # 2. If user uploaded an image, analyze it
        elif image_file:
            image_bytes = image_file.read()
            if not session_data["order_required"]:
                # If no order is set yet, let the user know
                messages.append({
                    "sender": "system",
                    "text": "No order defined yet. Please define an order first."
                })
            else:
                # a) Call Gemini
                gemini_text = analyze_image_for_items(image_bytes)
                recognized_items = parse_gemini_response_into_items(gemini_text)

                # b) Compare
                missing, extra = compare_order(recognized_items, session_data["order_required"])

                # c) Summarize
                sys_response = f"""
                <b>Recognized Items:</b> {recognized_items}<br/>
                <b>Missing Items:</b> {missing}<br/>
                <b>Extra Items:</b> {extra}<br/>
                <b>Total Recognized Count:</b> {sum(recognized_items.values())}<br/>
                """
                messages.append({"sender": "system", "text": sys_response})

        # 3. If user text is "finalize", end the order
        if user_text.lower() == "finalize":
            # You could do any final DB update here
            messages.append({
                "sender": "system",
                "text": "Order finalized! You can start a new order or close this page."
            })
            session_data["order_required"] = {}

    return render_template_string(HTML_PAGE, messages=messages)
