import requests
import joblib
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
import warnings

# Suppress warnings for a cleaner output
warnings.filterwarnings('ignore')

# --- 1. CONFIGURATION ---


API_URL = "http://127.0.0.1:8000/api/mongodb/records/latest"


PROCESSOR_FILE = "preprocessor.pkl"
MODEL_FILE = "agroyield_model.h5"

# These lists MUST match your training notebook exactly
numerical_columns = [
    'Crop_Year', 'Area', 'Production', 'Annual_Rainfall', 'Fertilizer', 
    'Pesticide', 'Fertilizer_per_Area', 'Pesticide_per_Area', 
    'Production_per_Area', 'Decade'
]
categorical_columns = [
    'Crop', 'Season', 'State', 'Rainfall_Category', 'Area_Category'
]
feature_columns = numerical_columns + categorical_columns

# --- 2. DEFINE FUNCTIONS ---

def load_prediction_tools(processor_path, model_path):
    """Loads the preprocessor and the trained model from disk."""
    try:
        preprocessor = joblib.load(processor_path)
        print("✅ Preprocessor loaded successfully.")
    except FileNotFoundError:
        print(f"❌ Error: '{processor_path}' not found. Did you upload it to the Colab files panel?")
        return None, None
        
    try:
        # Load the Keras model
        model = keras.models.load_model(model_path, compile=False)
        print("✅ TensorFlow model loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading model '{model_path}': {e}")
        return None, None
        
    return preprocessor, model

def fetch_data_from_api(url):
    """Fetches the latest data entry from the FastAPI."""
    print(f"Attempting to fetch data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises an error for bad responses
        data = response.json()
        print(f"Data fetched from API: {data}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from API: {e}")
        print("   (Make sure the URL is correct and your teammate's server is running.)")
        return None

def prepare_data(data_dict, preprocessor):
    """
    Performs the *exact* same preprocessing and feature engineering
    from your notebook on the new data.
    """
    try:
        print("Starting data preparation...")
        
        # --- NEW MAPPING STEP ---
        # Map API keys (like 'crop_name') to the keys your ML model expects (like 'Crop')
        # This fixes the schema mismatch.
        mapped_data = {
            'Crop': data_dict.get('crop_name'),
            'State': data_dict.get('state_name'),
            'Season': data_dict.get('season_name'),
            'Crop_Year': data_dict.get('crop_year'), # API uses 'crop_year'
            'Area': data_dict.get('area'),
            'Production': data_dict.get('production'),
            'Annual_Rainfall': data_dict.get('annual_rainfall'),
            'Fertilizer': data_dict.get('fertilizer'),
            'Pesticide': data_dict.get('pesticide')
        }
        
        # 1. Convert the *mapped* dictionary into a DataFrame
        df = pd.DataFrame([mapped_data])

        # 2. Re-create all engineered features
        print("Engineering features...")
        
        # --- String stripping (important!) ---
        df['Crop'] = df['Crop'].str.strip()
        df['Season'] = df['Season'].str.strip()
        df['State'] = df['State'].str.strip()
        
        # --- Type conversion and efficiency features ---
        # Ensure all values are numeric
        df['Area'] = pd.to_numeric(df['Area'], errors='coerce')
        df['Fertilizer'] = pd.to_numeric(df['Fertilizer'], errors='coerce')
        df['Pesticide'] = pd.to_numeric(df['Pesticide'], errors='coerce')
        df['Production'] = pd.to_numeric(df['Production'], errors='coerce')
        df['Annual_Rainfall'] = pd.to_numeric(df['Annual_Rainfall'], errors='coerce')
        df['Crop_Year'] = pd.to_numeric(df['Crop_Year'], errors='coerce')
        
        # Add a small number (1e-6) to avoid division by zero
        df['Fertilizer_per_Area'] = df['Fertilizer'] / (df['Area'] + 1e-6)
        df['Pesticide_per_Area'] = df['Pesticide'] / (df['Area'] + 1e-6)
        df['Production_per_Area'] = df['Production'] / (df['Area'] + 1e-6)
        
        # --- Categorical features ---
        df['Rainfall_Category'] = pd.cut(df['Annual_Rainfall'],
                                         bins=[0, 1000, 1500, 2000, float('inf')], 
                                         labels=['Low', 'Medium', 'High', 'Very High'],
                                         right=False)
        
        df['Area_Category'] = pd.cut(df['Area'],
                                     bins=[0, 10000, 50000, 100000, float('inf')], 
                                     labels=['Small', 'Medium', 'Large', 'Very Large'],
                                     right=False)
        
        # --- Temporal feature ---
        df['Decade'] = (df['Crop_Year'].astype(int) // 10) * 10
        
        # 3. Ensure all columns are in the correct order
        print("Re-ordering columns...")
        # (feature_columns list must be defined at the top of your script)
        df = df[feature_columns]

        # 4. Use the LOADED preprocessor to transform the data
        print("Applying StandardScaler and OneHotEncoder...")
        X_processed = preprocessor.transform(df)
        
        print(f"✅ Data prepared successfully. Final shape: {X_processed.shape}")
        return X_processed

    except Exception as e:
        print(f"❌ Error in prepare_data: {e}")
        return None

# --- 3. RUN THE SCRIPT ---
print("--- Running Crop Yield Prediction Script ---")

# Load tools
preprocessor, model = load_prediction_tools(PROCESSOR_FILE, MODEL_FILE)

if preprocessor and model:
    # Fetch data
    latest_data = fetch_data_from_api(API_URL)
    
    if latest_data:
        # Prepare data
        if '_id' in latest_data: # Remove Mongo's ID if it exists
            del latest_data['_id']
            
        input_data = prepare_data(latest_data, preprocessor)
        
        if input_data is not None:
            # Make prediction
            try:
                prediction = model.predict(input_data)
                print("---------------------------------")
                print(f"🎉 PREDICTION MADE (Yield): {prediction[0][0]:.4f}")
                print("---------------------------------")
            except Exception as e:
                print(f"❌ Error during model.predict: {e}")