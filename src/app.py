from flask import Flask, request, jsonify
from flask_cors import CORS 
import spacy

from src.data_process.utils import simple_cleaning

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origin": "*"}})


nlp = spacy.load("src/models/model_spacy_vierge/2025-01-17_trained.model")

@app.route('/api/route', methods=['POST'])
def process_route():
    data = request.json
    text = data.get('text', '')

    if not text: # ARROR CASE IF NOT TEXT : SHOULD NOT CLICK ON BUTTON IF SO USEFUL ? 
        return jsonify({"error": "No text provided"}), 400

    text_cleaned = simple_cleaning(text)
    if " d'" in text_cleaned:
        text_cleaned = text_cleaned.replace(" d'", " de ")
    elif " d " in text_cleaned:
        text_cleaned = text_cleaned.replace(" d ", " de ")
    doc = nlp(text_cleaned)
    predicted_entities = [
        {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]

    responses = []
    for cities in predicted_entities:
        responses.append({
            "label": cities["label"],
            "word": text[cities["start"]:cities["end"]][0].upper() + text[cities["start"]:cities["end"]][1:],
        })

    return jsonify({"text": text, "responsesmodel": responses})

if __name__ == '__main__':
    app.run(debug=True)
