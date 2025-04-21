from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from tensorflow.keras.models import load_model  # Import TensorFlow's load_model
import numpy as np  # Import numpy for array operations

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS to allow requests from the frontend

# Load the pre-trained ML model, label encoder, and scaler
model = load_model('dehydration_ann_model.h5')  # Use TensorFlow's load_model for .h5 files
scaler = joblib.load('scaler.pkl')          # Replace with the actual scaler file path
label_encoder = joblib.load('label_encoder.pkl')  # Replace with the actual label encoder file path

# Add debugging logs to ensure the label encoder classes are loaded correctly
print(f"Label encoder classes: {label_encoder.classes_}")  # Debug: Print label encoder classes

# Ensure the label encoder has the correct classes
if not hasattr(label_encoder, 'classes_') or len(label_encoder.classes_) == 0:
    print("Error: Label encoder classes are not loaded correctly.")
    raise ValueError("Label encoder classes are missing or invalid.")

def predict_hydration_status(gsr, accel_magnitude, gyro_magnitude, magnetometer_magnitude, ir):
    try:
        # Validate input data
        if None in [gsr, accel_magnitude, gyro_magnitude, magnetometer_magnitude, ir]:
            print("Error: One or more input values are missing.")
            return "Unknown"

        # Combine all features into a single list
        features = [gsr, accel_magnitude, gyro_magnitude, magnetometer_magnitude, ir]
        print(f"Input features before scaling: {features}")  # Debug: Print raw input features

        # Scale the input features
        scaled_features = scaler.transform([features])  # Ensure the input matches the scaler's expected format
        print(f"Scaled features: {scaled_features}")  # Debug: Print scaled features

        # Predict using the ML model
        prediction = model.predict(scaled_features)  
        print(f"Raw model prediction shape: {prediction.shape}, values: {prediction}")  # Debug: Print raw prediction

        # Get the class index with the highest probability using a safer approach
        try:
            # Get the prediction and find the max probability index
            pred_array = prediction[0]  # Get first row of prediction (it's a 2D array)
            predicted_class_index = int(np.argmax(pred_array))
            print(f"Predicted class index: {predicted_class_index}")
            
            # Get the corresponding class label
            hydration_status = label_encoder.classes_[predicted_class_index]
            print(f"Decoded hydration status: {hydration_status}")
            
            return hydration_status
            
        except Exception as e:
            print(f"Error during class prediction: {e}")
            
            # Fallback method if the above fails
            print("Trying fallback method...")
            try:
                # Manual method to find the max probability index
                pred_array = prediction[0]
                max_val = -1
                max_idx = 0
                for i, val in enumerate(pred_array):
                    if val > max_val:
                        max_val = val
                        max_idx = i
                return label_encoder.classes_[max_idx]
            except:
                return "Unknown"
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Unknown"  # Fallback to "Unknown" if any error occurs

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    try:
        data = request.json
        gsr = data.get('gsr')
        accel_magnitude = data.get('accel')
        gyro_magnitude = data.get('gyro')
        magnetometer_magnitude = data.get('mag')
        ir = data.get('ir')

        print('Received Sensor Data:')
        print(f'GSR: {gsr}, Accel Magnitude: {accel_magnitude}, Gyro Magnitude: {gyro_magnitude}, Magnetometer Magnitude: {magnetometer_magnitude}, IR: {ir}')
        print(f"Label encoder classes: {label_encoder.classes_}")  # Debug: Print label encoder classes

        # Ensure all inputs are numeric
        try:
            gsr = float(gsr)
            accel_magnitude = float(accel_magnitude)
            gyro_magnitude = float(gyro_magnitude)
            magnetometer_magnitude = float(magnetometer_magnitude)
            ir = float(ir)
        except ValueError as ve:
            print(f"Error converting inputs to float: {ve}")
            return jsonify({'error': 'Invalid input data'}), 400

        # Predict hydration status
        hydration_status = predict_hydration_status(gsr, accel_magnitude, gyro_magnitude, magnetometer_magnitude, ir)
        print(f"Final hydration status sent to frontend: {hydration_status}")  # Debug: Print final hydration status
        return jsonify({'hydration_status': hydration_status}), 200
    except Exception as e:
        print(f'Error during prediction: {e}')
        return jsonify({'error': 'Prediction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

