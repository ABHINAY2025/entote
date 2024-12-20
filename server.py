from flask import Flask
from flask_cors import CORS
from backend.process import process  # Import API 1 Blueprint from backend
from backend.transform import transform  # Import API 2 Blueprint from backend

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Register Blueprints
app.register_blueprint(process, url_prefix='/api1')  # Prefix for API 1 routes
app.register_blueprint(transform, url_prefix='/api2')  # Prefix for API 2 routes

# Home route
@app.route('/')
def home():
    return {"message": "Welcome to the unified API server!"}, 200

if __name__ == '__main__':
    app.run(debug=True)