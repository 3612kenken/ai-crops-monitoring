from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load datasets
storm_path = os.path.join('dataset', 'historical-storm-dataset.csv')
yield_path = os.path.join('dataset', 'yield.csv')
storm_df = pd.read_csv(storm_path)
try:
    yield_df = pd.read_csv(yield_path)
except:
    yield_df = pd.DataFrame(columns=['year', 'area', 'yield'])

# Utility: Estimate crop damage percent by wind speed
def estimate_crop_damage_percent(wind_kph):
    if wind_kph <= 61:
        return '0–10%'
    elif 62 <= wind_kph <= 88:
        return '10–30%'
    elif 89 <= wind_kph <= 117:
        return '30–50%'
    elif 118 <= wind_kph <= 157:
        return '50–70%'
    elif wind_kph >= 158:
        return '70–100%'
    return '0%'

# Mock ML prediction function
def predict_yield(area, year):
    # Replace with actual ML model inference
    np.random.seed(hash(area+str(year)) % 100000)
    return float(np.random.randint(2000, 6000))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict-yield', methods=['POST'])
def api_predict_yield():
    data = request.json
    area = data.get('area')
    year = data.get('year')
    if not area or not year:
        return jsonify({'error': 'Missing area or year'}), 400
    pred = predict_yield(area, year)
    return jsonify({'area': area, 'year': year, 'predicted_yield': pred})

@app.route('/grouped-yield', methods=['GET'])
def api_grouped_yield():
    # Group by area and year, predict yield for each
    areas = yield_df['area'].unique() if not yield_df.empty else ['Area1', 'Area2']
    years = yield_df['year'].unique() if not yield_df.empty else [2020, 2021]
    results = []
    for area in areas:
        for year in years:
            pred = predict_yield(area, year)
            results.append({'area': area, 'year': year, 'predicted_yield': pred})
    return jsonify(results)

@app.route('/estimate-crop-damage', methods=['GET'])
def api_estimate_crop_damage():
    wind = request.args.get('wind', type=float)
    if wind is None:
        return jsonify({'error': 'Missing wind parameter'}), 400
    damage = estimate_crop_damage_percent(wind)
    return jsonify({'wind_kph': wind, 'estimated_crop_damage_percent': damage})

@app.route('/predict-yield-by-damage', methods=['POST'])
def predict_yield_by_damage():
    data = request.get_json()
    area = data.get('area')
    year = data.get('year')
    damage_percent = data.get('damage_percent')
    # TODO: Replace this with your actual yield prediction logic/model
    # For demonstration, assume base yield is 100, and yield decreases linearly with damage
    try:
        base_yield = 100  # Replace with actual lookup/model
        predicted_yield = base_yield * (1 - float(damage_percent) / 100.0)
        return jsonify({
            'area': area,
            'year': year,
            'damage_percent': damage_percent,
            'predicted_yield': round(predicted_yield, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
