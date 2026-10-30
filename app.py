
import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from google import genai

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Initialize Gemini using the API key from .env
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


# Pet database model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    breed = db.Column(db.String(100), nullable=False)


# Create database tables if they do not exist
with app.app_context():
    db.create_all()


# Home page and pet registration
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            species = request.form.get("species", "").strip()
            breed = request.form.get("breed", "").strip()
            age_text = request.form.get("age", "").strip()

            if not name or not species or not breed or not age_text:
                return "Please fill in all pet details.", 400

            age = int(age_text)

            if age < 0 or age > 100:
                return "Please enter a valid pet age.", 400

            pet = Pet(
                name=name,
                species=species,
                age=age,
                breed=breed
            )

            db.session.add(pet)
            db.session.commit()

            return redirect(url_for("home"))

        except ValueError:
            return "Please enter a valid number for pet age.", 400

    pets = Pet.query.order_by(Pet.id.desc()).all()
    return render_template("index.html", pets=pets)


# Gemini AI chatbot endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("message", "")

    if not isinstance(question, str):
        return jsonify({"reply": "Please enter a valid question."}), 400

    question = question.strip()

    if not question:
        return jsonify({"reply": "Please enter a question."}), 400

    if len(question) > 1000:
        return jsonify({
            "reply": "Please keep your question under 1000 characters."
        }), 400

    if client is None:
        return jsonify({
            "reply": "Gemini is not configured. Please check your .env file."
        }), 503

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "You are PawPal, a friendly pet-care chatbot. "
                "Answer pet-care questions in simple, helpful language. "
                "Give general information about pet feeding, grooming, "
                "behaviour, exercise, and everyday care. "
                "Do not diagnose illnesses or prescribe medicines. "
                "For serious symptoms or emergencies, recommend contacting "
                "a veterinarian promptly. Do not recommend unsafe foods "
                "or treatments. If a question is unrelated to pet care, "
                "politely guide the user back to pet-related topics.\n\n"
                f"User question: {question}"
            )
        )

        reply = response.text or (
            "Sorry, I couldn't generate a response. Please try again."
        )

        return jsonify({"reply": reply})

    except Exception:
        app.logger.exception("Gemini API request failed")

        return jsonify({
            "reply": (
                "Sorry, I couldn't reach the AI service. "
                "Please try again shortly."
            )
        }), 502


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
