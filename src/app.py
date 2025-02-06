from flask import Flask, request, jsonify
from flask_cors import CORS 
from werkzeug.utils import secure_filename
import os
import spacy

from src.data_process.utils import simple_cleaning, check_label, detected_language
from src.voice_process.hear_voice import process_m4a_file
from config import model_used_path, UPLOAD_FOLDER

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origin": "*"}})


nlp = spacy.load(model_used_path)

@app.route('/api/route', methods=['POST'])
def process_route():
    data = request.json
    text = data.get('text', '')
    responses = []

    if not text: # ARROR CASE IF NOT TEXT : SHOULD NOT CLICK ON BUTTON IF SO USEFUL ? 
        return jsonify({"error": "No text provided"}), 400

    # Detect langage of the text
    is_french = detected_language(text)
    if  is_french : 
        # Clean the text
        text_cleaned = simple_cleaning(text)
        text_cleaned = text_cleaned.lower()

        # Predict entities
        doc = nlp(text_cleaned)
        predicted_entities = [
            {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
            for ent in doc.ents
        ]

        # Check label of entities
        predicted_entities, error = check_label(predicted_entities)
    else : 
        error = ["NOT_FRENCH"]

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

@app.route('/api/convert_audio', methods=['POST'])
def convert_audio():

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné."}), 400

    if file :
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        transcribed_text = process_m4a_file(filepath)

        if transcribed_text:
            return jsonify({"transcribedText": transcribed_text})
        else:
            return jsonify({"error": "Échec de la transcription."}), 500
    else:
        return jsonify({"error": "Format de fichier non autorisé."}), 400

if __name__ == '__main__':
    app.run(debug=True)
