import pandas as pd

def preprocess_input(location, floor_area, bedrooms, bathrooms, floor_no, all_locations):
    """
    Preprocess the input data for prediction
    
    Args:
        location (str): The location of the property
        floor_area (float): The floor area in square feet/meters
        bedrooms (int): Number of bedrooms
        bathrooms (int): Number of bathrooms
        floor_no (int): Floor number
        all_locations (list): List of all possible locations
        
    Returns:
        pd.DataFrame: Preprocessed data ready for prediction
    """
    # First create a dictionary with all zeros for locations
    location_features = {loc: 0 for loc in all_locations}
    # Set the selected location to 1
    if location in location_features:
        location_features[location] = 1
    
    # Create input data with numeric features in the exact order expected by the model
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
    model_feature_order = ['Bedrooms', 'Bathrooms', 'Floor_no', 'Floor_area'] + all_locations
    input_df = input_df[model_feature_order]
    
    return input_df
