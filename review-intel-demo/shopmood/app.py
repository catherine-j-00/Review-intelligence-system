
import os
from datetime import date
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()
app = Flask(__name__)

# Existing Review Intelligence backend
REVIEW_API_URL = os.getenv(
    "REVIEW_API_URL",
    "http://127.0.0.1:5000/api/customer/reviews"
)
SHOPMOOD_API_KEY = os.getenv("SHOPMOOD_API_KEY", "")

# ShopMood's own product data
# Replace example brands with your actual product information.
PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 1999,
        "icon": "🎧",
        "brand": "SoundMax",
        "category": "Electronics",
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 3499,
        "icon": "⌚",
        "brand": "TimeTech",
        "category": "Electronics",
    },
    {
        "id": 3,
        "name": "Backpack",
        "price": 899,
        "icon": "🎒",
        "brand": "UrbanCarry",
        "category": "Accessories",
    },
    {
        "id": 4,
        "name": "Coffee Mug",
        "price": 299,
        "icon": "☕",
        "brand": "HomeStyle",
        "category": "Home & Kitchen",
    },
    {
        "id": 5,
        "name": "Desk Lamp",
        "price": 749,
        "icon": "💡",
        "brand": "BrightHome",
        "category": "Home & Kitchen",
    },
    {
        "id": 6,
        "name": "Running Shoes",
        "price": 2499,
        "icon": "👟",
        "brand": "RunFlex",
        "category": "Footwear",
    },
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/products")
def products():
    return jsonify(PRODUCTS)



@app.route("/api/reviews/<int:pid>", methods=["GET"])
def get_reviews(pid):
    """Retrieve paginated reviews from Review Intelligence."""
    product = next(
        (p for p in PRODUCTS if p["id"] == pid),
        None
    )

    if product is None:
        return jsonify(error="Invalid product"), 404

    if not SHOPMOOD_API_KEY:
        return jsonify(error="Review service is not configured"), 503

    try:
        limit = int(request.args.get("limit", 5))
        offset = int(request.args.get("offset", 0))

        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError
    except ValueError:
        return jsonify(error="Invalid limit or offset"), 400

    params = {
        "product_name": product["name"],
        "limit": limit,
        "offset": offset,
    }

    if product.get("brand"):
        params["brand"] = product["brand"]

    try:
        response = requests.get(
            REVIEW_API_URL,
            params=params,
            headers={"X-ShopMood-Key": SHOPMOOD_API_KEY},
            timeout=20,
        )

        try:
            result = response.json()
        except ValueError:
            result = {}

        if not response.ok:
            return jsonify(
                error=result.get(
                    "error", "Could not retrieve reviews"
                )
            ), response.status_code

    except requests.RequestException:
        app.logger.exception("Could not retrieve product reviews")
        return jsonify(error="Review service is unavailable"), 503

    # The Review Intelligence API returns a paginated object.
    if not isinstance(result, dict) or not isinstance(
        result.get("reviews"), list
    ):
        return jsonify(
            error="Unexpected response from Review Intelligence"
        ), 502

    return jsonify({
        "reviews": [
            {
                "name": "Customer",
                "text": r.get("review_text", ""),
                "review_date": r.get("review_date"),
                "sentiment": r.get("sentiment"),
                "emotion": r.get("emotion"),
                "confidence": r.get("confidence"),
            }
            for r in result["reviews"]
        ],
        "total": result.get("total", 0),
        "has_more": result.get("has_more", False),
    }), 200



@app.route("/api/reviews/<int:pid>", methods=["POST"])
def add_review(pid):
    """Send a customer review to the existing analysis backend."""
    product = next(
        (p for p in PRODUCTS if p["id"] == pid),
        None
    )

    if product is None:
        return jsonify(error="Invalid product"), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="A JSON object is required"), 400

    text = (data.get("text") or "").strip()

    if not text:
        return jsonify(error="Review text is required"), 400

    if len(text) > 5000:
        return jsonify(error="Review is too long"), 400

    if not SHOPMOOD_API_KEY:
        app.logger.error("SHOPMOOD_API_KEY is not configured")
        return jsonify(error="Review service is not configured"), 503

    payload = {
        "review_text": text,
        "product_name": product["name"],
        "brand": product.get("brand", ""),
        "category": product.get("category", ""),
        "review_date": date.today().isoformat(),
    }

    try:
        response = requests.post(
            REVIEW_API_URL,
            json=payload,
            headers={"X-ShopMood-Key": SHOPMOOD_API_KEY},
            timeout=15,
        )
    except requests.RequestException:
        app.logger.exception("Review Intelligence API unavailable")
        return jsonify(error="Review service is unavailable"), 503

    if response.status_code == 201:
        result = response.json()

        return jsonify({
            "text": text,
            "sentiment": result.get("sentiment"),
            "emotion": result.get("emotion"),
            "confidence": result.get("confidence"),
        }), 201

    if response.status_code == 400:
        try:
            return jsonify(
                error=response.json().get("error", "Invalid review")
            ), 400
        except ValueError:
            pass

    app.logger.error(
        "Review Intelligence API returned status %s",
        response.status_code,
    )
    return jsonify(error="Could not save review"), 502


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
        use_reloader=False,
    )
