import os
import requests
from flask import Blueprint, request, jsonify
from transformers import MarianMTModel, MarianTokenizer, pipeline

# Directly add your AssemblyAI API key here
ASSEMBLYAI_API_KEY = 'ccaefa4a4f9843c0814fc2769eeca026'  # Replace with your actual API key

# Create a Blueprint for API 2
process = Blueprint('process', __name__)

# Load the MarianMT translation model manually
def load_translation_model(source_lang="en", target_lang="te"):
    model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    return model, tokenizer

# Function to translate text
def translate_text(text, source_lang="en", target_lang="te"):
    # Load translation model
    model, tokenizer = load_translation_model(source_lang, target_lang)

    # Tokenize and translate the text
    translated = tokenizer(text, return_tensors="pt", padding=True)
    translated_output = model.generate(**translated)
    translated_text = tokenizer.decode(translated_output[0], skip_special_tokens=True)
    return translated_text

# Sentiment analysis function
def analyze_sentiment(text):
    sentiment_classifier = pipeline('text-classification', model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)
    result = sentiment_classifier(text)
    sentiments = {
        "joy": 0,
        "anger": 0,
        "sadness": 0,
        "fear": 0,
        "neutral": 0,
        "surprise": 0,
        "disgust": 0,
        "love": 0,
    }
    for r in result[0]:
        label = r['label']
        score = r['score']
        if label in sentiments:
            sentiments[label] = score

    positive_score = sentiments.get("joy", 0)
    negative_score = sentiments.get("sadness", 0) + sentiments.get("anger", 0) + sentiments.get("fear", 0) + sentiments.get("disgust", 0)

    if positive_score >= 0.495 or positive_score <= 0.509:
        overall_sentiment = "neutral"
    elif positive_score > negative_score:
        overall_sentiment = "positive"
    else:
        overall_sentiment = "negative"

    return sentiments, overall_sentiment

# Summarization function
def summarize_text(text):
    summarization_pipeline = pipeline("summarization")
    try:
        summary = summarization_pipeline(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except ValueError as e:
        return str(e)

# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()
    
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json',
    }
    upload_response = requests.post(
        'https://api.assemblyai.com/v2/upload', 
        headers=headers, 
        data=audio_data
    )

    audio_url = upload_response.json()['upload_url']
    
    transcript_request = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        json={'audio_url': audio_url},
        headers=headers
    )
    
    transcript_id = transcript_request.json()['id']
    
    while True:
        transcript_response = requests.get(
            f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
            headers=headers
        )
        if transcript_response.json()['status'] == 'completed':
            return transcript_response.json()['text']
        elif transcript_response.json()['status'] == 'failed':
            raise Exception("Transcription failed.")

# Route to process audio
@process.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    try:
        transcript = transcribe_audio(file_path)
        sentiments, overall_sentiment = analyze_sentiment(transcript)
        summary = summarize_text(transcript)

        return jsonify({
            "transcript": transcript,
            "sentiments": sentiments,
            "overall_sentiment": overall_sentiment,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to process text
@process.route('/process_text', methods=['POST'])
def process_text():
    if 'text' not in request.json:
        return jsonify({"error": "No text provided"}), 400
    
    text = request.json['text']

    try:
        translated_text = translate_text(text, source_lang="en", target_lang="te")
        sentiments, overall_sentiment = analyze_sentiment(text)
        summary = summarize_text(text)

        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "sentiments": sentiments,
            "overall_sentiment": overall_sentiment,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
