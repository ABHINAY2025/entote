from flask import Flask, request, jsonify
from flask_cors import CORS
import stanza
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app)

# Initialize models with error handling
nlp = None
tokenizer = None
model = None

# Try to initialize the Stanza Telugu model
try:
    nlp = stanza.Pipeline('te', verbose=False)  # Initialize Telugu NLP pipeline
except Exception as e:
    logging.error(f"Failed to initialize Stanza model: {e}")

# Try to initialize the mBART model and tokenizer for translation (English to Telugu)
model_checkpoint = "aryaumesh/english-to-telugu"
try:
    tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
    model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)
except Exception as e:
    logging.error(f"Failed to initialize mBART model or tokenizer: {e}")

# Check if models are initialized before processing any requests
def check_model_initialized():
    if nlp is None or tokenizer is None or model is None:
        return False
    return True

# Function to translate text using mBART model
def translate_to_telugu(text):
    """
    Translates English text to Telugu using the mBART model.
    """
    if not text.strip():
        return ""
    
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the NLP API!"})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500

    try:
        # Translate the text from English to Telugu using the mBART model
        translated_text = translate_to_telugu(text)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({"error": "Translation failed"}), 500

@app.route('/pos', methods=['POST'])
def pos_tagging():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500

    try:
        # Translate the text from English to Telugu using the mBART model
        translated_text = translate_to_telugu(text)

        # Use Stanza to perform POS tagging on the translated Telugu text
        doc = nlp(translated_text)

        # Extract POS tags for each word in the translated sentence
        results = [{"token": word.text, "pos": word.upos} for sentence in doc.sentences for word in sentence.words]
        return jsonify(results)
    
    except Exception as e:
        logging.error(f"Error during POS tagging: {e}")
        return jsonify({"error": "Could not fetch POS tags"}), 500

@app.route('/translate_keywords', methods=['POST'])
def translate_keywords():
    """
    Extracts keywords from the input text using TF-IDF and translates them to Telugu.
    """
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    text = data.get("text", "").strip()
    if not text:
        logging.error("No text provided")
        return jsonify({"error": "No text provided"}), 400

    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500

    try:
        # Extract keywords using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')  # Remove English stopwords
        tfidf_matrix = vectorizer.fit_transform([text])  # Single input string as a list

        # Extract feature names (words) and their TF-IDF scores
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = list(zip(feature_names, tfidf_matrix.toarray()[0]))

        # Log the raw TF-IDF scores for all features
        logging.debug(f"Raw TF-IDF Scores: {tfidf_scores}")

        # Sort words by their score in descending order
        sorted_words = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)

        if not sorted_words:
            logging.error("No keywords found")
            return jsonify({"error": "No keywords found"}), 400

        # Select the top 6 keywords to ensure variety
        keywords_with_scores = sorted_words[:6]

        # Log the extracted keywords and scores for debugging
        logging.debug(f"Extracted Keywords: {keywords_with_scores}")

        # Translate keywords into Telugu
        translated_keywords = []
        for word, score in keywords_with_scores:
            # Translate to Telugu using the translate_to_telugu function
            translated_text = translate_to_telugu(word)
            logging.debug(f"Translated '{word}' to Telugu as '{translated_text}'")
            translated_keywords.append({"keyword": word, "translated_keyword": translated_text, "score": score})

        return jsonify({"keywords": translated_keywords})

    except Exception as e:
        logging.error(f"Error during keyword translation: {e}")
        return jsonify({"error": "Could not process keywords"}), 500

@app.route('/translate_multiple', methods=['POST'])
def translate_multiple():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    text1 = data.get('text1', '').strip()
    text2 = data.get('text2', '').strip()

    if not text1 or not text2:
        return jsonify({"error": "Both text1 and text2 must be provided"}), 400

    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500

    try:
        # Translate both text1 and text2 from English to Telugu using the mBART model
        translated_text1 = translate_to_telugu(text1)
        translated_text2 = translate_to_telugu(text2)

        return jsonify({
            "translated_text1": translated_text1,
            "translated_text2": translated_text2
        })
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({"error": "Translation failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
