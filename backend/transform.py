from flask import Blueprint, request, jsonify
import logging
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import stanza
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize blueprint for API 1
transform = Blueprint('transform', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize models
nlp = None
tokenizer = None
model = None

# Initialize Stanza Telugu pipeline
try:
    nlp = stanza.Pipeline('te', verbose=False)
except Exception as e:
    logging.error(f"Failed to initialize Stanza model: {e}")

# Initialize mBART model and tokenizer for translation
model_checkpoint = "aryaumesh/english-to-telugu"
try:
    tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
    model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)
except Exception as e:
    logging.error(f"Failed to initialize mBART model or tokenizer: {e}")

# Function to check model initialization
def check_model_initialized():
    return nlp is not None and tokenizer is not None and model is not None

# Translation function
def translate_to_telugu(text):
    if not text.strip():
        return ""
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Route: Home (API 1 description)
@transform.route('/')
def home():
    return jsonify({"message": "Welcome to API 1 - NLP Services!"})

# Route: Translate English to Telugu
@transform.route('/translate', methods=['POST'])
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
        translated_text = translate_to_telugu(text)
        return jsonify({"translated_text": translated_text})
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({"error": "Translation failed"}), 500

# Route: Part-of-Speech (POS) Tagging
@transform.route('/pos', methods=['POST'])
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
        translated_text = translate_to_telugu(text)
        doc = nlp(translated_text)
        results = [{"token": word.text, "pos": word.upos} for sentence in doc.sentences for word in sentence.words]
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error during POS tagging: {e}")
        return jsonify({"error": "Could not fetch POS tags"}), 500

# Route: Extract and Translate Keywords
@transform.route('/translate_keywords', methods=['POST'])
def translate_keywords():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500
    try:
        # Extract keywords using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = list(zip(feature_names, tfidf_matrix.toarray()[0]))
        sorted_words = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:6]

        # Translate top keywords to Telugu
        translated_keywords = []
        for word, score in sorted_words:
            translated_text = translate_to_telugu(word)
            translated_keywords.append({
                "keyword": word,
                "translated_keyword": translated_text,
                "score": score
            })
        return jsonify({"keywords": translated_keywords})
    except Exception as e:
        logging.error(f"Error during keyword translation: {e}")
        return jsonify({"error": "Could not process keywords"}), 500
    
    # Route: Translate Multiple Texts from English to Telugu
@transform.route('/translate_multiple', methods=['POST'])
def translate_multiple():
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or empty JSON payload"}), 400

    # Extract the two texts from the request body
    text1 = data.get('text1', '').strip()
    text2 = data.get('text2', '').strip()

    # Ensure both texts are provided
    if not text1 or not text2:
        return jsonify({"error": "Both text1 and text2 must be provided"}), 400

    # Check if the models are initialized
    if not check_model_initialized():
        return jsonify({"error": "Model initialization failed"}), 500

    try:
        # Translate both text1 and text2
        translated_text1 = translate_to_telugu(text1)
        translated_text2 = translate_to_telugu(text2)

        # Return both translations in the response
        return jsonify({
            "translated_text1": translated_text1,
            "translated_text2": translated_text2
        })
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({"error": "Translation failed"}), 500

