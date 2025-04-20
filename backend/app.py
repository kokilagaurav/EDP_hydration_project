from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS to allow requests from the frontend

# Load the pre-trained ML model, label encoder, and scaler
model = joblib.load('hydration_model.pkl')  # Replace with the actual model file path
scaler = joblib.load('scaler.pkl')          # Replace with the actual scaler file path
label_encoder = joblib.load('label_encoder.pkl')  # Replace with the actual label encoder file path

def predict_hydration_status(gsr, ir, accel_magnitude, gyro_magnitude, magnetometer_magnitude):
    # Combine all features into a single list
    features = [gsr, ir, accel_magnitude, gyro_magnitude, magnetometer_magnitude]
    # Scale the input features
    scaled_features = scaler.transform([features])  # Ensure the input matches the scaler's expected format
    # Predict using the ML model
    prediction = model.predict(scaled_features)
    # Decode the prediction to get the label
    hydration_status = label_encoder.inverse_transform(prediction)
    return hydration_status[0]  # Return the decoded label

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    data = request.json
    gsr = data.get('gsr')
    ir = data.get('ir')
    accel_magnitude = data.get('Accel Magnitude')
    gyro_magnitude = data.get('Gyro Magnitude')
    magnetometer_magnitude = data.get('Magnetometer Magnitude')

    print('Received Sensor Data:')
    print(f'GSR: {gsr}, IR: {ir}, Accel Magnitude: {accel_magnitude}, Gyro Magnitude: {gyro_magnitude}, Magnetometer Magnitude: {magnetometer_magnitude}')

    # Predict hydration status
    try:
        hydration_status = predict_hydration_status(gsr, ir, accel_magnitude, gyro_magnitude, magnetometer_magnitude)
        return jsonify({'hydration_status': hydration_status}), 200
    except Exception as e:
        print(f'Error during prediction: {e}')
        return jsonify({'error': 'Prediction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
