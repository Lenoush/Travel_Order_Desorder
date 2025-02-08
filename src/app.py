from flask import Flask, request, jsonify
from flask_cors import CORS 
from werkzeug.utils import secure_filename
import os
import spacy

from src.data_process.utils import simple_cleaning, check_label, detected_language
from src.path_finding.dijkstra import load_and_merge_data, build_graph, get_fastest_route_for_city, load_graph, \
    save_graph
from src.voice_process.hear_voice import process_m4a_file
from config import model_used_path, UPLOAD_FOLDER, DIJKSTRA_Route

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origin": "*"}})

nlp = spacy.load(model_used_path)


print("Loading data and building graph...")
stops, stop_times, trips, routes, calendar_dates, commune_stations = load_and_merge_data()
if os.path.exists(DIJKSTRA_Route):
    print("Loading graph from file...")
    graphique_dijkstra = load_graph(DIJKSTRA_Route)
else:
    print("Building graph...")
    graphique_dijkstra = build_graph(stops, stop_times, trips, routes)
    save_graph(graphique_dijkstra, DIJKSTRA_Route)

@app.route('/api/route', methods=['POST'])
def process_route():
    data = request.json
    text = data.get('text', '')
    responses = []
    error_nlp = []
    itinerary = []
    error_route = []

    # Detect langage of the text
    is_french = detected_language(text)
    if is_french:
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
        predicted_entities, error_nlp = check_label(predicted_entities)
    else:
        error_nlp.append("NOT_FRENCH")

    # Get the cities from NLP model
    cities_for_route = {"DEPART": None, "ARRIVEE": None, "CORRESPONDANCE": []}
    if not error_nlp:
        # Formate the responses
        for cities in predicted_entities:
            label = cities["label"]
            word = text_cleaned[cities["start"]:cities["end"]][0].upper() + text_cleaned[cities["start"]:cities["end"]][1:]
            responses.append({
                "label": label,
                "word": word,
            })
            if label == "DEPART":
                cities_for_route["DEPART"] = word
            elif label == "ARRIVEE":
                cities_for_route["ARRIVEE"] = word
            elif label == "CORRESPONDANCE":
                cities_for_route["CORRESPONDANCE"].append(word)

        # Get the fastest route
        if not cities_for_route["CORRESPONDANCE"]:
            # Without correspondance
            if cities_for_route["DEPART"] and cities_for_route["ARRIVEE"]:
                route_part, error_route = get_fastest_route_for_city(graphique_dijkstra, commune_stations, cities_for_route["DEPART"], cities_for_route["ARRIVEE"])
                itinerary.append(route_part)
        else:
            # With correspondance
            prev_stop = cities_for_route["DEPART"]
            for correspondance in cities_for_route["CORRESPONDANCE"]:
                route_part, error_ = get_fastest_route_for_city(graphique_dijkstra, commune_stations, prev_stop, correspondance)
                prev_stop = correspondance
                itinerary.append(route_part)
                error_route.append(error_)

            route_part, error_ = get_fastest_route_for_city(graphique_dijkstra, commune_stations, prev_stop, cities_for_route["ARRIVEE"])
            itinerary.append(route_part)
            error_route.append(error_)

        print("Itinerary: ", itinerary)

    return jsonify({"text": text, "responsesmodel": responses, "itinerary": itinerary, "error_nlp": error_nlp, "error_route": error_route})

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
