"""
Reflex — Flask backend
Member 4 owns this file. Run with: python app.py
"""
from flask import Flask, render_template, request, jsonify
import models

app = Flask(__name__)

# Initialize the database as soon as the app module loads.
# This runs both when you do `python app.py` locally AND when
# a production server like gunicorn imports this file — gunicorn
# never executes the `if __name__ == "__main__":` block below.
models.init_db()

# Order status must move through, one step at a time, no skipping.
STATUS_ORDER = ["PENDING", "ASSIGNED", "PICKED_UP", "DELIVERED"]

# ---------------------------------------------------------------------------
# Page routes (render the HTML each persona sees)
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/retailer")
def retailer_page():
    return render_template("retailer.html")

@app.route("/dispatcher")
def dispatcher_page():
    return render_template("dispatcher.html")

@app.route("/rider")
def rider_page():
    return render_template("rider.html")

# ---------------------------------------------------------------------------
# API routes (the frozen Day 1 contract)
# ---------------------------------------------------------------------------

@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    """List deliveries. Optional query params: ?status=PENDING&riderId=1"""
    status_filter = request.args.get("status")
    rider_id_filter = request.args.get("riderId")
    deliveries = models.get_all_deliveries(status=status_filter, rider_id=rider_id_filter)
    return jsonify(deliveries)

@app.route("/deliveries/<int:delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    delivery = models.get_delivery(delivery_id)
    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404
    return jsonify(delivery)

@app.route("/deliveries", methods=["POST"])
def create_delivery():
    data = request.get_json(force=True) or {}
    required = ["customerName", "phone", "address", "itemDescription"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    delivery = models.create_delivery(
        customer_name=data["customerName"],
        phone=data["phone"],
        address=data["address"],
        item_description=data["itemDescription"],
    )
    return jsonify(delivery), 201

@app.route("/riders", methods=["GET"])
def get_riders():
    return jsonify(models.get_all_riders())

@app.route("/deliveries/<int:delivery_id>/assign", methods=["POST"])
def assign_delivery(delivery_id):
    data = request.get_json(force=True) or {}
    rider_id = data.get("riderId")
    if not rider_id:
        return jsonify({"error": "riderId is required"}), 400

    delivery = models.get_delivery(delivery_id)
    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404
    if delivery["status"] != "PENDING":
        return jsonify({"error": f"Cannot assign a delivery with status {delivery['status']}"}), 409

    rider = models.get_rider(rider_id)
    if rider is None:
        return jsonify({"error": "Rider not found"}), 404

    updated = models.assign_rider(delivery_id, rider_id)
    return jsonify(updated)

@app.route("/deliveries/<int:delivery_id>/status", methods=["PATCH"])
def update_status(delivery_id):
    """
    Moves a delivery forward exactly one status step.
    This is enforced here, server-side — not just hidden in the UI —
    so calling the API directly can't skip a step either.
    """
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "status is required"}), 400

    delivery = models.get_delivery(delivery_id)
    if delivery is None:
        return jsonify({"error": "Delivery not found"}), 404

    if new_status not in STATUS_ORDER:
        return jsonify({"error": f"Unknown status: {new_status}"}), 400

    current_index = STATUS_ORDER.index(delivery["status"])
    expected_next = STATUS_ORDER[current_index + 1] if current_index + 1 < len(STATUS_ORDER) else None

    if new_status != expected_next:
        return jsonify({
            "error": (
                f"Invalid transition: cannot move from {delivery['status']} to {new_status}. "
                f"Next valid status is {expected_next or 'none — already DELIVERED'}."
            )
        }), 409

    updated = models.update_status(delivery_id, new_status)
    return jsonify(updated)

if __name__ == "__main__":
    app.run(debug=True)
