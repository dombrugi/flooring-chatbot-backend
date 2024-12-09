import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import spacy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your flooring data from CSV
flooring_data = pd.read_csv('sample_flooring_products.csv')

# Load SpaCy NLP model for better understanding (you can expand it for more complex queries)
nlp = spacy.load("en_core_web_sm")

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower()
    response = ""

    # Use SpaCy to process user input and extract information
    doc = nlp(user_input)

    # Handle 'flooring types' request
    if "flooring types" in user_input or "types" in user_input:
        flooring_types = flooring_data['Type'].unique()
        response = f"We offer the following flooring types: {', '.join(flooring_types)}."

    # Handle 'products under type' request
    elif "products" in user_input or "show me" in user_input:
        flooring_type = None
        # Search for flooring type mentioned in the input (e.g., "hardwood")
        for type_ in flooring_data['Type'].unique():
            if type_.lower() in user_input:
                flooring_type = type_
                break

        if flooring_type:
            products = flooring_data[flooring_data['Type'].str.lower() == flooring_type.lower()]['Product Name']
            response = f"Here are the {flooring_type} products: {', '.join(products)}."
        else:
            response = "Please specify the flooring type (e.g., Hardwood, Tile, Carpet)."

    # Handle price and installation cost queries
    elif "cost" in user_input or "price" in user_input:
        flooring_type = None
        area_size = None

        # Use regex to extract flooring type and area size (sq ft)
        flooring_match = re.search(r'(hardwood|bamboo|tile|carpet|vinyl|stone)', user_input)
        area_match = re.search(r'(\d+)\s*sq\s*ft', user_input)

        if flooring_match:
            flooring_type = flooring_match.group(1).lower()
        if area_match:
            area_size = int(area_match.group(1))

        if not flooring_type or not area_size:
            response = "Please specify both the flooring type and the area size in square feet."
            return jsonify({"response": response})

        # Find the flooring type in the CSV
        product = flooring_data[flooring_data['Type'].str.lower() == flooring_type]
        if product.empty:
            response = f"Sorry, we don't have flooring type '{flooring_type}'. Please choose from {', '.join(flooring_data['Type'].unique())}."
        else:
            # Calculate the total cost
            price_per_sqft = product.iloc[0]['Price per Sq Ft']
            install_cost_per_sqft = product.iloc[0]['Installation Cost per Sq Ft']
            total_cost = (price_per_sqft + install_cost_per_sqft) * area_size
            if area_size < 1000:
                total_cost = max(total_cost, 250)  # Minimum cost for small areas
            response = f"The estimated cost for {area_size} sq ft of {flooring_type} flooring is ${total_cost:.2f}."

    # Provide tips for flooring installation
    elif "tips" in user_input or "installation" in user_input:
        response = (
            "Here are some tips for flooring installation:\n"
            "1. Make sure the subfloor is clean, level, and dry.\n"
            "2. Acclimate flooring materials to the room's temperature and humidity for 48 hours.\n"
            "3. Leave expansion gaps around the edges.\n"
            "4. Follow the manufacturer's installation instructions."
        )

    else:
        # If the input is unrecognized, show what the bot can do
        response = handle_error(user_input)

    return jsonify({"response": response})

# Error handling function
def handle_error(user_input):
    return (
        "I'm sorry, I don't have the information necessary to complete that request. "
        "I am able to assist with the following:\n"
        "1. Providing information about available flooring types.\n"
        "2. Showing products under a specific flooring type.\n"
        "3. Estimating costs based on flooring type and area size.\n"
        "4. Offering tips for flooring installation.\n"
        "Please clarify your request or ask about one of these options."
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)