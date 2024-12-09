import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your flooring data from CSV
flooring_data = pd.read_csv('sample_flooring_products.csv')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    intent_name = req['queryResult']['intent']['displayName']

    # Handle cost estimation intent
    if intent_name == "Cost Estimation":
        flooring_type = None
        area_size = None

        # Extract flooring type and area size from the parameters
        parameters = req['queryResult']['parameters']
        flooring_type = parameters.get('flooring_type')
        area_size = parameters.get('area_size')

        if flooring_type and area_size:
            # Find the flooring type in the CSV
            product = flooring_data[flooring_data['Type'].str.lower() == flooring_type.lower()]
            if not product.empty:
                price_per_sqft = product.iloc[0]['Price per Sq Ft']
                install_cost_per_sqft = product.iloc[0]['Installation Cost per Sq Ft']
                total_cost = (price_per_sqft + install_cost_per_sqft) * area_size
                if area_size < 1000:
                    total_cost = max(total_cost, 250)
                response_text = f"The estimated cost for {area_size} sq ft of {flooring_type} flooring is ${total_cost:.2f}."
            else:
                response_text = f"Sorry, we don't have flooring type '{flooring_type}'. Please choose from the available types."

        else:
            response_text = "Please specify both the flooring type and the area size in square feet."

        return jsonify({
            "fulfillmentText": response_text
        })

    return jsonify({"fulfillmentText": "Sorry, I didn't understand that."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)