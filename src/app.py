from flask import Flask, request, jsonify
from flask_cors import CORS 
import spacy

from src.data_process.utils import simple_cleaning, check_label, detected_language

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origin": "*"}})


nlp = spacy.load("src/models/model_spacy_vierge/2025-01-17_trained.model")

@app.route('/api/route', methods=['POST'])
def process_route():
    data = request.json
    text = data.get('text', '')
    responses = []

    if not text: # ARROR CASE IF NOT TEXT : SHOULD NOT CLICK ON BUTTON IF SO USEFUL ? 
        return jsonify({"error": "No text provided"}), 400

    # Deectect langage of the text
    is_french = detected_language(text)
    if  is_french : 
        # Clean the text
        text_cleaned = simple_cleaning(text)

        # Predict entities
        doc = nlp(text_cleaned)
        predicted_entities = [
            {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
            for ent in doc.ents
        ]

        # Check label of entities
        predicted_entities, error = check_label(predicted_entities)
    else : 
        error = ["The language of the text is not French"]

    if error == []:
        # Format the responses
        for cities in predicted_entities:
            responses.append({
                "label": cities["label"],
                "word": text_cleaned[cities["start"]:cities["end"]][0].upper() + text_cleaned[cities["start"]:cities["end"]][1:],
            })
    else :
        responses = error

    return jsonify({"text": text, "responsesmodel": responses})

if __name__ == '__main__':
    app.run(debug=True)
