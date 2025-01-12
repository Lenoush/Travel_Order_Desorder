from flask import Flask, request, jsonify
from flask_cors import CORS 
import spacy

app = Flask(__name__)
# CORS(app, origins=["http://localhost:8080"]) 
CORS(app, resources={r"/api/*": {"origins": "*"}})


nlp = spacy.load("src/models/model_spacy_vierge/2025-01-12_trained.model")

@app.route('/api/route', methods=['POST'])
def process_route():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    doc = nlp(text)
    predicted_entities = [
        {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]

    responses = []
    for cities in predicted_entities:
        responses.append({
            "label": cities["label"],
            "word": text[cities["start"]:cities["end"]]
        })

    return jsonify({"text": text, "responsesmodel": responses})

if __name__ == '__main__':
    app.run(debug=True)
