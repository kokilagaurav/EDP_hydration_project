from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS to allow requests from the frontend

# Load the pre-trained ML model, label encoder, and scaler
model = joblib.load('hydration_model.pkl')  # Replace with the actual model file path
scaler = joblib.load('scaler.pkl')          # Replace with the actual scaler file path
label_encoder = joblib.load('label_encoder.pkl')  # Replace with the actual label encoder file path

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
        print(f"Raw model prediction: {prediction}")  # Debug: Print raw prediction

        # Decode the prediction to get the label
        hydration_status = label_encoder.inverse_transform(prediction)[0]
        print(f"Decoded hydration status: {hydration_status}")  # Debug: Print decoded label
        
        return hydration_status
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
        return jsonify({'hydration_status': hydration_status}), 200
    except Exception as e:
        print(f'Error during prediction: {e}')
        return jsonify({'error': 'Prediction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

