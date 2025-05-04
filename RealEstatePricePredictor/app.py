import os
import json
import logging
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Load the trained model
try:
    with open('attached_assets/trained_model.pkl', 'rb') as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Load location data from JSON file
try:
    with open('attached_assets/column_names.json', 'r') as f:
        locations = json.load(f)
    logger.info(f"Loaded {len(locations)} locations")
except Exception as e:
    logger.error(f"Error loading locations: {e}")
    locations = []

@app.route('/')
def home():
    return render_template('index.html', locations=locations)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data from request
        data = request.get_json()
        logger.debug(f"Received prediction request with data: {data}")
        
        # Extract features
        location = data.get('location')
        floor_area = float(data.get('floor_area'))
        bedrooms = int(data.get('bedrooms'))
        bathrooms = int(data.get('bathrooms'))
        floor_no = int(data.get('floor_no'))
        
        # Input validation
        if not location or location not in locations:
            return jsonify({'error': 'Invalid location'}), 400
        
        if floor_area <= 0:
            return jsonify({'error': 'Floor area must be greater than 0'}), 400
            
        if bedrooms <= 0:
            return jsonify({'error': 'Number of bedrooms must be greater than 0'}), 400
            
        if bathrooms <= 0:
            return jsonify({'error': 'Number of bathrooms must be greater than 0'}), 400
            
        if floor_no < 0:
            return jsonify({'error': 'Floor number cannot be negative'}), 400
        
        # Prepare data according to the exact order the model expects
        # First create a DataFrame with all zeros for locations
        location_features = {loc: 0 for loc in locations}
        # Set the selected location to 1
        if location in location_features:
            location_features[location] = 1
        
        # Create the input data with numeric features in the exact order expected by the model
        input_data = {
            'Bedrooms': bedrooms,
            'Bathrooms': bathrooms,
            'Floor_no': floor_no,
            'Floor_area': floor_area,
        }
        # Add the location features
        input_data.update(location_features)
        
        # Create DataFrame with these features
        input_df = pd.DataFrame([input_data])
        
        # Ensure the columns are in the exact order the model expects
        model_feature_order = ['Bedrooms', 'Bathrooms', 'Floor_no', 'Floor_area'] + locations
        input_df = input_df[model_feature_order]
        
        logger.debug(f"Preprocessed input features: {input_df.head()}")
        
        # Make prediction
        if model:
            prediction = model.predict(input_df)[0]
            # Format prediction to 2 decimal places
            formatted_prediction = round(float(prediction), 2)
            logger.info(f"Prediction: {formatted_prediction}")
            return jsonify({'prediction': formatted_prediction})
        else:
            return jsonify({'error': 'Model not loaded'}), 500
            
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
